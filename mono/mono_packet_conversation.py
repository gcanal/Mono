#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:00:17 2017

@author: robert
"""
import sys
import logging
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors

from . import mono_tools

#API to deal with the PACKET_CONVERSATION table

#remove all the packet_conversation lines in the table with the given id_session
def remove_packetconversations(id_session, db):
    l = logging.getLogger("mono_packet_conversation")
    l.info("remove all packet_conversation from session %d"%(id_session,))
    cursor = db.cursor()
    try:
        sql = "DELETE FROM PACKETS_CONVERSATIONS WHERE id_session = %s"
        cursor.execute(sql, (id_session, ))
        db.commit()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise
#t
#returns all packets from conversation
def get_packets_from_conversation(id_conversation, conv_type, db):
    cursor = db.cursor(cursors.DictCursor)
    try:
        sql = "SELECT * FROM PACKETS_CONVERSATIONS pc INNER JOIN PACKETS p  ON pc.id_packet = p.id_packet\
        WHERE pc.id_conversation = %s AND pc.conversation_type=%s "
        cursor.execute(sql, (id_conversation, conv_type))
        db.commit()
        return cursor.fetchall()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise

#returns the packet_conversation id of the newly inserted row
def add_packetconversation(id_session, id_packet, id_conv, conv_type, db):
    cursor = db.cursor()
    try:
        sql =  "INSERT INTO PACKETS_CONVERSATIONS (id_session, id_packet, id_conversation, conversation_type) "
        sql += "VALUES (%s,%s,%s,%s) "
        cursor.execute(sql, (id_session, id_packet, id_conv, conv_type))
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise


def get_packetconversation(id_pc, db):
    cursor = db.cursor(cursors.DictCursor)
    try:
        sql =  "SELECT * FROM PACKETS_CONVERSATIONS WHERE id_pc=%s "
        cursor.execute(sql, (id_pc, ))
        result = cursor.fetchone()
        db.commit()
        return result
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise

#helper function (for test only)
def remove_packetconversation(id_packet_conversation, db):
    cursor = db.cursor()
    l = logging.getLogger("mono_packet_conversation")
    l.debug("Remove packet_conversation with id "+str(id_packet_conversation))
    try:
        sql =  "DELETE FROM PACKETS_CONVERSATIONS WHERE id_pc=%s "
        cursor.execute(sql, (id_packet_conversation,))
        db.commit()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise

#Call the functions where needed
