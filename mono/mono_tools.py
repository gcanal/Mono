
import sys
import logging
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors

### Be extra carefull, table_name should not come from user input
def generic_update(table_name, dic,db, id_name, id_value, forbidden_keys = ()):
    cursor = db.cursor(cursors.DictCursor)
    params = ()
    sql = ""
    try:
        sql = "UPDATE " + table_name+ " SET "
        for key in dic:
            if key not in forbidden_keys:
                sql += key + "=%s, "
                params += (dic[key],)
        sql = sql[:-2]
        sql += " WHERE "+ id_name + "=%s "
        params += (id_value,)
        cursor.execute(sql, params)
        db.commit()
    except Exception as e:
        print (str(e))
        if hasattr(cursor, '_last_executed'):
            l = logging.getLogger("mono_tools")
            l.error(cursor._last_executed)
        db.rollback()
        raise 

#use the cursor (querry should already be executed) to return an array of objects/dictionaries to be jsonified
def select_to_objects(cursor):
    rows = [x for x in cursor]
    cols = [x[0] for x in cursor.description]
    objects = []
    for row in rows:
        obj = {}
        for prop, val in zip(cols, row):
            obj[prop] = val
        objects.append(obj)
    #json.dumps(objects)
    return objects

def handle_db_exception(e, db, cursor):
    print (str(e))
    if hasattr(cursor, '_last_executed'):
        l = logging.getLogger("mono_tools")
        l.error(cursor._last_executed)
    db.rollback()
