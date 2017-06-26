#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 09:59:10 2017

@author: robert
"""
import sys
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors
import logging
class MonoDatatables:

    Columns_names = {}

################## SUPER WARNING  ##################
#        self.filter_names = ()
#        self.filter_values = ()
#        self.filter_counter_names = ()
#        self.filter_counter_values = ()
#MUST BE WHITELISTED
#####################################################

    ## Warning TABLE_NAME should not come from user input
    ## Warning columns names must be checked against a white list if they 
    # come from user input
    #self.db_info = {"host":"localhost","user":"mono","passwd":"a87__Er33","db":"mono"}
    #Runs the queries and place the result in the self.resultData attribute
    def __init__( self, request, index, table, db_handler):
        l = logging.getLogger("mono_datatable")
        l.debug("datatable -> call constructor")
        self.data = request.get_json() #data = request.get_json()
        l.debug("request received from client")
        l.debug(self.data)
        #data.columns=[{data: "id_packet", name: "", searchable: true, orderable: true, search: {value: "", regex: false}},...]
        self.columns = [o["data"] for o in self.data["columns"]]
        l.debug("creating columns names")
        l.debug(self.columns)
        self.index = index
        #table is a dictionnary
        #like {"name":"PACKETS_CONVERSATIONS", "as": "pc", "join":[{"name":"PACKETS", "as":"p", "on":on}]}
        self.table = table
        if (not "as" in self.table):
            self.table["as"] = ""
        if (not "join" in self.table):
            self.table["join"] = []
        self.dbh = db_handler
        
        # results from the db
        self.resultData = None
        # total in the table after filtering
        self.cardinalityFiltered = 0
        # total in the table unfiltered
        self.cardinality = 0
        self.params = ()
        self.valid_columns = False

        #to add filter (for instance id_session=3)
        self.filter_names = ()
        self.filter_values = ()
        self.filter_counter_names = ()
        self.filter_counter_values = ()

        self.hash = self.get_table_hash()
        #run queries if and only if the columns have been validated

    ## Warning TABLE_NAME should not come from user input
    def validate_columns(self):
        #Here other possibilities to get columns names of a given table
        # mysql_query('DESCRIBE '.$table);
        # mysql_query('SHOW COLUMNS FROM tableName'); 
        #sql = "select column_name from information_schema.columns where table_name=" + self.table
        l = logging.getLogger("mono_datatable")
        if not (self.hash  in MonoDatatables.Columns_names  and len (MonoDatatables.Columns_names[self.hash]) > 0):
            l.info("validate_columns: create whitelist for table " + self.table["name"])
            MonoDatatables.Columns_names[self.hash] = []
            col_names = self.get_colunms_of_table(self.table["name"])
            self.prefix_column_names(self.table, col_names)
            MonoDatatables.Columns_names[self.hash] += col_names
            for j in self.table["join"]:
                res = self.get_colunms_of_table(j["name"])
                self.prefix_column_names(j, res)
                MonoDatatables.Columns_names[self.hash] += res
        else:
            l.debug("validate_columns: whitelist already exist ")
            pass
            #whitelist_already exist
        l.debug(MonoDatatables.Columns_names)
        for col in self.columns:
            if not (col in MonoDatatables.Columns_names[self.hash]):
                l.error("!!!!!!!!!!!column %s is not valid"%(col,))
                self.valid_columns = False
                return False
        self.valid_columns = True
        return True
    
    #transforms the table attribute into a hash 
    #{"name":"PACKETS_CONVERSATIONS", "as": "pc", "join":[{"name":"PACKETS", "as":"p", "on":on}
    #--> self.hash = PACKETS_CONVERSATIONS__PACKETS
    def get_table_hash(self):
        hash = self.table["name"]
        for j in self.table["join"]:
            hash += "__"+j["name"]
        return hash
    
    #prefix all the columns in col_names with "as" parameter of the table
    def prefix_column_names(self, table, col_names):
        if (len(table["as"]) > 0):
            for i in range(len(col_names)):
                col_names[i] = table["as"] + "." + col_names[i]
            

    #returns the list of the column names of the given table
    #the tableName argument is a string, not a dictionnary
    def get_colunms_of_table(self, tableName):
        sql = "SHOW COLUMNS FROM " + tableName 
        dataCursor = self.dbh.cursor(cursors.DictCursor)
        dataCursor.execute(sql)
        res = dataCursor.fetchall()
        col_names = []
        for line in res:
               col_names.append(line["Field"])
        return col_names

    #column name is TRUSTED (not a user input)
    #TO add elements in where clause
    #Obviously if you have a datatable per session, you will add a filter on
    #id_session
    #as_count_filter : set to true to perform the filter while counting the 
    #elements as well
    def add_filter(self, column_name, value, as_count_filter):
        self.filter_names += (column_name,)
        self.filter_values += (value,)
        if (as_count_filter):
            self.add_count_filter(column_name, value)


    #column name is TRUSTED (not a user input)
    #To add elements in where clause of COUNT query to get total number of item
    #in the datatable 
    def add_count_filter(self, column_name, value):
        self.filter_counter_names += (column_name,)
        self.filter_counter_values += (value,)

    # Output the JSON required for DataTables
    # The run_queries must have been called before
    def output_result( self ):
        output = {}
        #number of records before applying the filter
        output['iTotalRecords'] = str(self.cardinality) 
        #number of records after applying the filter
        output['iTotalDisplayRecords'] = str(self.cardinalityFiltered)
        #place the result in the aaData attribute
        output['aaData'] = self.resultData
        return output

    #Method to update one field (e.g. selected) in all the line of the datatable
    #Not efficient but versatile
    #d is a dictionary of parameters. It should have the following attributes:
    # table_name, id_key, col_name, col_value
    def update_rows(self, d):
        l = logging.getLogger("mono_datatable")
        l.debug(d)
        def cb(data):
            #global d
            cursor = self.dbh.cursor(cursors.DictCursor)
            l = logging.getLogger("mono_datatable")
            l.debug("from the callback")
            l.debug(d)
            l.debug(data)
            l.debug("update row %s=%s to value %s=%s in table %s"%(d["id_key"],data[d["id_key"]], d["col_name"],  d["col_value"], d["table_name"]))
            sql = "UPDATE " + d["table_name"] + " SET " + d["col_name"] + "= %s WHERE "+ d["id_key"] + " = %s"
            try:
                #UPDATE PACKETS SET selected = %s  WHERE id_packet = %s
                cursor.execute(sql, (d["col_value"], data[d["id_key"]], ))
                self.dbh.commit()
            except Exception:
                if hasattr(cursor, '_last_executed'):
                    l.error(cursor._last_executed)
                self.dbh.rollback()
                raise 
        #use the callback 
        self.callback_on_rows(cb)

    #Generic method to play a callback on all the lines currently in the datatable
    #taking filtering into account
    def callback_on_rows(self, cb):
        l = logging.getLogger("mono_datatable")
        dataCursor = self.dbh.cursor(cursors.DictCursor)
        if (not self.validate_columns()):
            return
        #perform the update action for all the columns
        start = 0; length = 50 ; #start and length 
        found = True, 
        while (found):
            found = False
            self.params = () # will be modified by the filtering method
            sql =  self.selecting() + " " + self.filtering() + " " + self.paging(force_start = start, force_length = length)
            dataCursor.execute(sql, self.params)
            if hasattr(dataCursor, '_last_executed'):
                l.debug("in callback_on_rows, fetching data")
                l.debug(dataCursor._last_executed)
            self.params = ()
            data = dataCursor.fetchall()
            for d in data:
                found = True
                cb(d)#call the callback on the data
            start += length 
        
    # runs the SQL and calls the selecting, filtering, ordering and paging methods
    #queries are run, only if columns are valid
    def run_queries(self):
        l = logging.getLogger("mono_datatable")
        #Run queries only if columns names are valid
        if (not self.validate_columns()):
            return
        dataCursor = self.dbh.cursor(cursors.DictCursor) # replace the standard cursor with a dictionary cursor only for this query
        self.params = ()
        #use the SQL_CALC_FOUND_ROWS option to later use the FOUND_ROWS() fn
        sql = self.selecting() + " " + self.filtering() + " " + self.ordering() + " " + self.paging()
        dataCursor.execute(sql, self.params)
        if hasattr(dataCursor, '_last_executed'):
            l.debug("run sql query")
            l.debug(dataCursor._last_executed)
        self.resultData = dataCursor.fetchall()
        l.debug("Get resultData")
        l.debug(self.resultData)

        # Computing filtered Count 
        cardinalityFilteredCursor = self.dbh.cursor()
        # For a SELECT with a LIMIT clause, FOUND_ROWS() returns 
        #the number of rows that would be returned were there no LIMIT clause 
        cardinalityFilteredCursor.execute( """
            SELECT FOUND_ROWS()
        """ )
        self.cardinalityFiltered = cardinalityFilteredCursor.fetchone()[0]

        # Computing Total (unfiltered) Count 
        cardinalityCursor = self.dbh.cursor()
        sql_count = "SELECT COUNT(%s) FROM %s %s" % (self.index, self.table["name"], self.table["as"])
        if (len(self.filter_counter_names) > 0): #we add a where close for counting 
            sql_count +=" WHERE "
            for name in self.filter_counter_names:
                sql_count += (name+ "=%s AND ")
            sql_count = sql_count[:-4]
        cardinalityCursor.execute(sql_count, self.filter_counter_values)
        self.cardinality = cardinalityCursor.fetchone()[0]

    def selecting(self):
        sql = "SELECT SQL_CALC_FOUND_ROWS %(columns)s" % dict(columns=', '.join(self.columns),)
        sql += " FROM " + self.table["name"] + " " + self.table["as"] + " "
        for j in self.table["join"]:
            sql += " INNER JOIN " + j["name"] + " " + j["as"] + " "
            sql += "ON " + j["on"]
        return sql

    def filtering(self):
        l = logging.getLogger("mono_datatable")
        l.debug("creating filter string")
        filter_string = ""
        added_filters = (len(self.filter_names) > 0)
        if (added_filters):
            filter_string = " WHERE "
            for name in self.filter_names:
                filter_string += (name + "=%s AND ") 
            filter_string = filter_string[:-4]
            self.params += self.filter_values
            added_filters = True
        if ( 'search' in self.data and "value" in self.data["search"] and self.data['search']["value"] != "" ):
            filter_string += (" AND ( " if added_filters else " WHERE ( ")
            for i in range( len(self.columns) ):
                #filter_string += "%s LIKE '%%%s%%' OR " % (self.columns[i], self.data['search']["value"])
                #assuming that only one is searchable
                if (self.data["columns"][i]["searchable"]):
                    filter_string += self.columns[i] + " LIKE %s OR " #columns are trusted
                    self.params += ("%" + self.data['search']["value"] + "%",)
            filter_string = filter_string[:-3]
            filter_string += " )"
        l.debug(filter_string)
        return filter_string

    #sanitized: user's input are checked against white list 
    #order direction is either asc or desc
    def ordering( self):
        l = logging.getLogger("mono_datatable")
        order = ""
        if ("order" in self.data and len(self.data["order"]) > 0):
            direction = self.data["order"][0]["dir"]
            col = self.columns[int(self.data['order'][0]['column'])]
            #sanitatization
            if (direction.upper() == 'ASC' or direction.upper() == 'DESC'):
                order = "ORDER BY %s %s " % (col, direction)
        l.debug("creating order string")
        l.debug(order)
        return order

    #sanitized: we test if the user inputs (start and length) are integers
    def paging(self, force_start = -1, force_length = -1):
        l = logging.getLogger("mono_datatable")
        start = 0
        length = 10
        if ( 'start' in self.data and isinstance(self.data["start"], ( int, ))):
            start = self.data["start"]
        if ( 'length' in self.data and isinstance(self.data["length"], (int, )) ):
            length = self.data["length"]
        if (force_start >= 0):
            start = force_start
        if (force_length > 0):
            length = force_length
        limit = "LIMIT %s, %s" % (start, length)
        l.debug("creating limit string")
        l.debug(limit)
        return limit

