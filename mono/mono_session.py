#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 15:34:08 2017
@author: robert
"""
#from scapy.all import sendrecv
#from scapy.all import utils # for export/import_object

import scapy
from scapy.all import *
from scapy.all import Ether, IP
#from scapy.all import Raw, ICMP, Ether, STP, Dot3, Dot1Q, ARP, IPv6, sendrecv, utils
#IP, UDP,TCP, ICMP
#from scapy.all import *

#import dateutil.parser
import datetime
import logging
import threading
import netifaces # for the get_interfaces method
import sys
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors
from . import mono_conversation
from . import mono_tools
from . import mono_packet
from . import mono_constant
from . import mono_packet_conversation
from . import mono_param
from . import mono_mitm

mono_param.ID_CURRENT_SESSION = -1;
RUN_ORDER = False;

def get_ifaces():
    return  netifaces.interfaces()
#use for testing


def get_sessions(db):
    cursor = db.cursor()
    sql = "SELECT * FROM SESSIONS "
    # Execute the SQL command
    cursor.execute(sql)
    # Fetch all the rows in a list of lists.
    #results = cursor.fetchall()
    return mono_tools.select_to_objects(cursor)

def get_session(id_session, db):
    l = logging.getLogger("mono_session")
    l.debug("getting session of id %s"%id_session)
    cursor = db.cursor(cursors.DictCursor)
    sql = "SELECT * FROM SESSIONS WHERE id_session = %s "
    # Execute the SQL command
    cursor.execute(sql,(id_session, ) ) 
    #INFO: (y) is not a tuple - it is an int in parenthesis, adding comma (y,) makes it a tuple
    # Fetch all the rows in a list of lists.
    #results = cursor.fetchall()
    res = cursor.fetchone()
    return res


#TODO take care of date
#Note that this is using a comma, not % (which would be a direct string substitution, not escaped). Don't do this:
#c.execute("""SELECT spam, eggs, sausage FROM breakfast
#          WHERE price < %s""" % (max_price,))

def add_session(session, db):
    #We create the session date
    session["date"] = datetime.datetime.now().isoformat()
    try:
        sql = "INSERT INTO SESSIONS (name, iface,date) \
           VALUES (%s, %s, %s)"
        cursor = db.cursor()
        cursor.execute(sql, (session["name"], session["iface"], session["date"]) ) #safe sql querry
        db.commit()
        id_sess = cursor.lastrowid
        l = logging.getLogger("mono_session")
        l.info("add sesssion %s with name %s on iface %s   (%s)"%(id_sess, session["name"],session["iface"], session["date"]))
        return id_sess
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise
        return -1;

def update_session(sess, db):
    # this_column=x, that_column=y
    try:
        l = logging.getLogger("mono_session")
        l.debug("update session id=%s to {name=%s, iface=%s, date=%s}\
        "%(sess['id_session'], sess['name'], sess['iface'], sess['date']))
        sql = "UPDATE SESSIONS SET name = %s, iface = %s, date = %s  WHERE id_session = %s"
        params = (sess["name"], sess["iface"],sess['date'], int(sess['id_session']) ) 
        cursor = db.cursor()
        cursor.execute(sql, params) #safe sql querry
        db.commit()
        return int(sess['id_session'])
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise
        return -1;


#tested
#delete a session and all its packets and all the conversations
def remove_session(id_session, db):
    l = logging.getLogger("mono_session")
    l.info("removing session %d"%(id_session,))
    cursor = db.cursor()
    try:
        sql = "DELETE FROM PACKETS WHERE id_session = %s"
        cursor.execute(sql, (id_session, ))
        db.commit()
        sql = "DELETE FROM SESSIONS WHERE id_session = %s"
        cursor.execute(sql, (id_session, ))
        db.commit()
        #Remove all conversations in the session
        mono_conversation.remove_conversations(id_session, db, mono_constant.IPV4_CONVERSATION_TYPE)
        mono_conversation.remove_conversations(id_session, db, mono_constant.UDP_CONVERSATION_TYPE)
        mono_conversation.remove_conversations(id_session, db, mono_constant.TCP_CONVERSATION_TYPE)
        #Remove links between conversation and packets
        mono_packet_conversation.remove_packetconversations(id_session, db)
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise


def session_to_pcap(id_session, fileName, db):
    l = logging.getLogger("mono_session")
    l.debug("session_to_pcap")
    id_packets_plain = mono_packet.packets_to_pcap(id_session, fileName, db)# returns a list of id but we don't need it
    conv_type = mono_constant.UDP_CONVERSATION_TYPE
    id_packets1 = mono_conversation.conversations_to_pcap(id_session, conv_type, fileName, db, True, ())
    conv_type = mono_constant.TCP_CONVERSATION_TYPE
    id_packets2 = mono_conversation.conversations_to_pcap(id_session, conv_type, fileName, db, True, ())
    id_packets1.extend(id_packets2)
    conv_type = mono_constant.IPV4_CONVERSATION_TYPE
    mono_conversation.conversations_to_pcap(id_session, conv_type, fileName, db, True, id_packets1)
    conv_type = mono_constant.MITM_CONVERSATION_TYPE
    mono_conversation.conversations_to_pcap(id_session, conv_type, fileName, db, True, id_packets_plain)
    #EVOL In the future, APPLIS_CONVERSATION_TYPE

def session_callback(db):
    def callback(packet):
        l = logging.getLogger("mono_session.callback")
        l.debug("packet callback")
        #print (packet.summary())
        if (is_session_active() and get_run_order()):
            id_packet = mono_packet.packet_into_db(packet, mono_param.ID_CURRENT_SESSION, db)
            mono_conversation.add_packet_to_conversations(id_packet, packet, db, mono_param.ID_CURRENT_SESSION)
            """
            #small debug 
            packet2 = mono_packet.packet_from_db(id_packet, db)
            print "packet1_time: %f packet_time2 %f"%(packet.time, packet2.time)
            print "packet1_time: %s packet_time2 %s"%(format(packet.time, '.10f'), format(packet2.time, '.10f') )
            
            print "type1 %s type2 %s"%(type(packet.time),type(packet2.time))
            if (packet.time == packet2.time):
                print " temps egaux"
            else:
                print " ################## TEMPS DIFFERENTS ######################
            utils.wrpcap('packets_%s.pcap'%(ID_CURRENT_SESSION,), packet, append=True)  #appends packet to output file
            utils.wrpcap('packets_%s_2.pcap'%(ID_CURRENT_SESSION,) , packet2, append=True)  #appends packet to output file
            print(packet.command())
            print(packet2.command())
            """
        else:
            return;
    return callback

#define getters and setters (if one day we want to go SQL with global vars)
def is_session_active():
    return (mono_param.ID_CURRENT_SESSION > 0)

def get_run_order():
    global RUN_ORDER
    return RUN_ORDER

#Raise a stop flag for the scapy stop_callback
#and send a last packet on the monitored interface so that the stop callback
#is called immediately
def stop_session(db):
    #if no session is active, there's is nothing to do
    if (not is_session_active()): 
        return
    l = logging.getLogger("mono_session")
    l.info("stop_session: set run order to false")
    set_run_order(False)
    sess = get_session(mono_param.ID_CURRENT_SESSION, db)
    #send a last scapy packet to the current interface to close the session
    #(the stop callback should be called one more time)
    l.info("stop_session: send last packet to iface " + sess["iface"])
    if ("iface" in sess):
        sendp(Ether()/IP(dst="1.2.3.4",ttl=(1,4)), iface=sess["iface"]) #scapy.sendrecv.sendp

def set_run_order(order):
    global RUN_ORDER
    RUN_ORDER = order

def set_session_active(id_session, db):
    mono_param.ID_CURRENT_SESSION = id_session
    mono_param.set_id_session(id_session, db)
    if id_session > 0:
        mono_param.set_recording(1, db)
    else:
        mono_param.set_recording(0, db)

def get_current_session_id():
    return mono_param.ID_CURRENT_SESSION

#used as the stop filter function for the sniff
def stop_fn(db):
    def stop_callback(packet):
        if not get_run_order():
            #before exiting set current session as inactive
            l = logging.getLogger("mono_session")
            l.info("last call of the stop callback -> Set active =-1")
            set_session_active(-1, db)
            mono_conversation.stop_conversations()
            mono_mitm.stop_mitm()
            return True # True means we want to exit
        else: #no STOP ORDER -> keep running
            return False
    return stop_callback

def threaded_sniff(session, db):
     l = logging.getLogger("mono_session")
     l.info("launching sniff on iface " + str(session['iface']) + " for session " + str(session['id_session']) + " " + str(session['name']) )
     scapy.sendrecv.sniff(iface=session["iface"], prn=session_callback(db), store=0, count=0, stop_filter=stop_fn(db)) #filter="tcp" #scapy.sendrecv.sniff

#return True if it has been possible to launch new Run session
#db connector passed as argument must be ALWAYS ON
def run_session(id_session, db):
    l = logging.getLogger("mono_session")
    #if session is already running, we return true.
    id_cur_sess = get_current_session_id()
    if (id_cur_sess == id_session):
        l.warn("In run session : -> Session is already active")
        return True
    #if another session is already running, we return false
    elif (is_session_active()):
        l.warn("In run session : -> Another session is active %d"%(id_cur_sess,))
        return False
    else:
        try:
            l.info("run_session --> Start sniffer and sets session as active") 
            set_run_order(True)
            sess = get_session(id_session, db)
            sniffer = threading.Thread(target = threaded_sniff, args = (sess, db))#args = (arg1,)
            sniffer.daemon = True
            sniffer.start()
            set_session_active(id_session, db)
            return True
        except Exception as e:
            set_run_order(False)
            l.critical("impossible to run session Exception caught")
            l.critical(str(e))
            raise

#unselect all packets and all conversations
#TODO write tests
def unselect_all(id_session, db):
    mono_packet.set_selected_all_packets_in_session(id_session, 0, db)
    conv_type = mono_constant.UDP_CONVERSATION_TYPE
    mono_conversation.set_selected_all_conversation_of_type(id_session, conv_type, 0, db)
    conv_type = mono_constant.TCP_CONVERSATION_TYPE
    mono_conversation.set_selected_all_conversation_of_type(id_session, conv_type, 0, db)
    conv_type = mono_constant.IPV4_CONVERSATION_TYPE
    mono_conversation.set_selected_all_conversation_of_type(id_session, conv_type, 0, db)
    conv_type = mono_constant.MITM_CONVERSATION_TYPE
    mono_conversation.set_selected_all_conversation_of_type(id_session, conv_type, 0, db)
