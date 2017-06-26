#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 17:43:57 2017

@author: robert
"""
import sys
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors

from . import mono_tools 
import logging 
RECORDING          = 0  #true if we want scapy magic
DECRYPTING         = 0 #true if we want MITM magic
ID_CURRENT_SESSION = 0 #current id_session

logger = logging.getLogger("mono_param")

#Deprecated
def set_recording(recording, db):
    set_int_param("recording", recording, db)
    logging.getLogger("mono_param").debug("recording set to %s" % (recording))

def get_recording(db):
    return get_int_param("recording", db)

def set_decrypting(decrypting, db):
    set_int_param("decrypting", decrypting, db)
    logging.getLogger("mono_param").debug("decrypting set to %s" % (decrypting))

def get_decrypting(db):
    return get_int_param("decrypting", db)

def set_id_session(id_session, db):
    set_int_param("id_session", id_session, db)
    logging.getLogger("mono_param").debug("id_session set to %s" % (id_session))

def get_id_session(db):
    return get_int_param("id_session", db)

#set current id_session
def set_int_param(param_name, param_value, db):
    try:
        cursor = db.cursor()
        sql = "UPDATE PARAMS SET value_int = %s  WHERE name=%s"
        # Execute the SQL command
        cursor.execute(sql, (param_value, param_name))
        db.commit()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 

#set current id_session
def set_str_param(param_name, param_value, db):
    try:
        cursor = db.cursor()
        sql = "UPDATE PARAMS SET value_str = %s WHERE name=%s"
        # Execute the SQL command
        cursor.execute(sql, (param_value, param_name))
        db.commit()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 

#set current id_session
def get_int_param(param_name, db):
    try:
        cursor = db.cursor(cursors.DictCursor)
        sql = "SELECT value_int FROM PARAMS WHERE name=%s"
        # Execute the SQL command
        cursor.execute(sql, (param_name,))
        db.commit()
        param = cursor.fetchone()
        return param["value_int"]
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 

#set current id_session
def get_str_param(param_name, db):
    try:
        cursor = db.cursor(cursors.DictCursor)
        sql = "SELECT value_str FROM PARAMS WHERE name=%s"
        # Execute the SQL command
        cursor.execute(sql,(param_name,))
        db.commit()
        param = cursor.fetchone()
        return param["value_str"]
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 