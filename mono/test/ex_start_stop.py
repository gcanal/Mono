#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 15:28:50 2017

@author: robert
"""

from scapy.all import IP,sendrecv, ICMP, utils, STP, Ether, Dot3, Dot1Q, ARP, IPv6, TCP
import mono
import MySQLdb
import threading
import sys
import mono_config as mc
#Test the start/stop functions of the MONO api mono.run_session mono.give_stop_order


db = MySQLdb.connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)
print "#### Add Session"
id_session = mono.add_session({"name":"Robert Session", "iface":"wlan0"}, db)
print "created session with id " + str(id_session)
res = mono.run_session(id_session, db)
print (" Successfully started session" if res else " Failed to start session")

def check_session_active():
    print "is_session active " + str(mono.is_session_active())
    print "current session is " + str(mono.get_current_session_id())

def give_stop_order():
    print "give stop order"
    mono.set_run_order(False)
    check_session_active()
    return


print "waiting 15 second before giving stop order"
threading.Timer(15, give_stop_order, ()).start()
print "waiting 17 second before checking if session is active"
threading.Timer(17, check_session_active, ()).start()