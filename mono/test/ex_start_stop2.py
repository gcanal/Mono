#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 15:34:52 2017

@author: robert
"""
from scapy.all import IP,sendrecv, ICMP, utils, STP, Ether, Dot3, Dot1Q, ARP, IPv6, TCP
import mono
import MySQLdb
import threading
import sys
import mono_config as mc

#TODO do a test program 


db = MySQLdb.connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db

print "TEST get interfaces"
print (mono.get_interfaces())

print "#### Add Session"
id_session = mono.add_session({"name":"Robert Session", "iface":"wlan0"}, db)
print "new session inserted with id %d"%id_session
sess = mono.get_session(id_session, db)
print sess
print "#### Update session"
sess['name'] = "Session by Jean Claude"; sess["iface"] = "eth0"
id_session = mono.update_session(sess, db)
print (mono.get_session(db, id_session))
print "#### Get all sessions"
print (mono.get_sessions(db))
print "#### Start session %s"%id_session
mono.start_session(id_session)
print "### receive 8 packets: testing session_callback and packet_into_db"

def threaded_sniff():
    sendrecv.sniff(iface="wlan0", prn=mono.session_callback(db), store=0, count=0) #filter="tcp"


print(mono.get_packets(45,1, db))
print "exiting"
sys.exit()
print "exited"

is_recording = False
def start_stop_recording():
    global is_recording
    global id_session
    
    is_recording = not is_recording
    if is_recording: 
        mono.ID_CURRENT_SESSION = id_session
        print "######################## Recording"
    else:
        print "######################## STOP recording"
        mono.ID_CURRENT_SESSION = -1
try:
    print "launching sniffer "
    sniffer = threading.Thread(target = threaded_sniff)#args = (arg1,)
    sniffer.daemon = True
    sniffer.start()
    print "sniffer started"
    threading.Timer(5, start_stop_recording, ()).start()
    threading.Timer(10, start_stop_recording, ()).start()
    threading.Timer(15, start_stop_recording, ()).start()
except (KeyboardInterrupt, SystemExit):
  print '\n! Received keyboard interrupt, quitting threads.\n'
  sys.exit()



#mono.stop_session()

#db.close()

