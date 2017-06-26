#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 5 16:31:29 2017

@author: robert
"""

#ways to execute this test_file
#python -m mono.tests.test_file.py ( __name__ ='__main__' and package ='mono.tests')
#python tests/test_file.py ( __name__ ='__main__' and package = None)
#imported from another module ( __name__ ='mono.tests.test_conversations' and package ='mono.tests')

if  __package__ != 'mono.tests': #is None
    import sys
    from os import path
    sys.path.append( path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from scapy.all import IP
import MySQLdb
import warnings
from mono import mono_conversations as mono_conv
from mono import mono_packets
from mono import mono_config as mc

from MySQLdb import cursors
def keep_only_id_packet(tuple):
    for dic in tuple:
        for key in dic.keys():
            pass
            #del dic["packet"]
            #if key != "id_packet":
                #pass
                #del dic[key]
    return tuple

def execute_safe(id_packet, db):
    cursor = db.cursor(cursors.DictCursor)
    try:
        sql = "SELECT * FROM PACKETS WHERE id_packet = %s"
        cursor.execute(sql, (id_packet, ))
        print "executing safe sql"
        if hasattr(cursor, '_last_executed'):
            print(cursor._last_executed)
        db.commit()
        return keep_only_id_packet(cursor.fetchall())
    except Exception as e:
        print (str(e))
        if hasattr(cursor, '_last_executed'):
            print(cursor._last_executed)
        db.rollback()
        raise

def execute_unsafe(id_packet, db):
    cursor = db.cursor(cursors.DictCursor)
    try:
        sql = "SELECT * FROM PACKETS WHERE id_packet = %s"
        cursor.execute(sql%(id_packet, ))
        print "executing unsafe sql"
        if hasattr(cursor, '_last_executed'):
            print(cursor._last_executed)
        db.commit()
        return keep_only_id_packet(cursor.fetchall())
    except Exception as e:
        print (str(e))
        if hasattr(cursor, '_last_executed'):
            print(cursor._last_executed)
        db.rollback()
        raise
        
def test_injection():
    db = MySQLdb.connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)
    id_packet = "3400 OR 1=1"
    print "\n########## Injection based on 1=1 with id_packet = %s ########## "%id_packet
    ret1 = execute_unsafe(id_packet, db)#SELECT * FROM PACKETS WHERE id_packet = 3400 OR 1=1
    print(ret1)
    ret2 = execute_safe(id_packet, db) #SELECT * FROM PACKETS WHERE id_packet = '3400 OR 1=1'
    print(ret2)
    id_packet = "3400' OR 1=1; --"
    print "\n########## Injection based on 1=1 + closing quote with id_packet = %s ########## "%id_packet
    ret2 = execute_safe(id_packet, db) #SELECT * FROM PACKETS WHERE id_packet = '3400\' OR 1=1; --'
    print(ret2)
    id_packet = "3400; DROP TABLE PACKETS2"
    print "\n########## Injection based on batched SQL statement (does not work) with id_packet = %s ########## "%id_packet
    ret2 = execute_safe(id_packet, db)
    print(ret2)
    print "THE LAST TEST RAISES AN EXCEPTION"
    ret1 = execute_unsafe(id_packet, db)
    print(ret1)

def without_whitelisting():
    #THIS SHOWS why we need whitelisting with column and table names
   db = MySQLdb.connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)
   cursor = db.cursor() #db.cursor(cursors.DictCursor)
   cols = ["id_packet", "ip_src", "ip_dest"] #from user input
   table_name = "PACKETS"
   id_packet = 3400 #from user input
   query = "SELECT %s, %s, %s FROM %s"
   params = (cols[0], cols[1], cols[2], table_name)
   try:
        cursor.execute(query, params) 
        rows = cursor.fetchall()
        print(cursor._last_executed)
        print (rows)
   except Exception as e:
        print (str(e))
        if hasattr(cursor, '_last_executed'):
            print(cursor._last_executed)
        db.rollback()
        raise

def with_whitelisting():
    #THIS SHOWS why we need whitelisting with column and table names

   db = MySQLdb.connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)
   cursor = db.cursor() #db.cursor(cursors.DictCursor)
   cols_input = ["id_packet", "ip_src", "ip_dst"] #from user input
   cols = cols_input ############## WHITELISTING
   query="SELECT %s FROM PACKETS LIMIT 5" %(', '.join(cols),)

   try:
        cursor.execute(query) 
        rows = cursor.fetchall()
        print(cursor._last_executed)
        print (rows)
   except Exception as e:
        print (str(e))
        if hasattr(cursor, '_last_executed'):
            print(cursor._last_executed)
        db.rollback()
        raise
   
if __name__ == '__main__':
    #show mysql warnings as exception
    warnings.filterwarnings('error', category=MySQLdb.Warning)
    #test_injection()
    #without_whitelisting()
    with_whitelisting()


    #id_packet = "3400 union select 1,2,3,4,5,6,7,8,9,10,11,12,13,14"
    #id_packet = "3400' OR 1=1; --"

