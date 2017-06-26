#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:31:29 2017

@author: robert
"""
import unittest
import sys
if sys.version_info > (3, 3):
    from pymysql import connect
    from pymysql import Warning
else:
    from MySQLdb import connect
    from MySQLdb import Warning
import warnings

#ways to execute this test_file
#python -m mono.tests.test_file.py ( __name__ ='__main__' and package ='mono.tests')
#python tests/test_file.py ( __name__ ='__main__' and package = None)
#imported from another module ( __name__ ='mono.tests.test_packets' and package ='mono.tests')

if  __package__ != 'mono.test': #is None
    import sys
    from os import path
    sys.path.append( path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from mono import mono_session
from mono import mono_packet
from mono import mono_config as mc

class PacketsTestCase(unittest.TestCase):

    #tests api functions add_session and get_session
    def test_add_packet(self):
        print("\n#test packet")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        print("creating session")
        id_session = mono_session.add_session({"name":"test_add_packet", "iface":"wlan0"}, db)
        print("create dummy ping packet")
        ip1 = "133.29.243.23"
        ip2 = "192.168.30.33"
        packet1 = mono_packet.create_ping_packet(ip_dst=ip1, ip_src=ip2)
        p_summary1 = mono_packet.packet_summary(packet1)

        print("insert and retrieve packet from db ")
        id_packet = mono_packet.packet_into_db(packet1, id_session, db)
        packet2 = mono_packet.get_scapy_packet_from_id(id_packet, db)
        p_summary2 = mono_packet.packet_summary(packet2)
        print(packet1.command())
        print(packet2.command())
        #TODO solve problem with packet length -> done johnny boy 
        self.assertEqual(bytes(packet1), bytes(packet2))
        self.assertEqual(packet2.command(), packet2.command())
        print("Removing session")
        mono_session.remove_session(id_session, db)
        db.close();


    def test_select_packet(self):
        print("\n#test select packet")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        packet1 = mono_packet.create_ping_packet()
        id_packet = mono_packet.packet_into_db(packet1, 0, db)
        self.assertEqual(mono_packet.is_packet_selected(id_packet, db), 0)
        mono_packet.select_packet(id_packet, 1, db)
        self.assertEqual(mono_packet.is_packet_selected(id_packet, db), 1)
        mono_packet.select_packet(id_packet, False, db)
        self.assertEqual(mono_packet.is_packet_selected(id_packet, db), 0)
        mono_packet.select_packet(id_packet, True, db)
        self.assertEqual(mono_packet.is_packet_selected(id_packet, db), 1)
        #clean
        mono_packet.delete_packet_from_db(id_packet, db)
        db.close()

    def test_select_all_packets_session(self):
        print("\n#test select_all_packets_session")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        id_session = 0
        mono_session.remove_session(id_session, db)
        print("create first packet and select it")
        packet1 = mono_packet.create_ping_packet()
        id_packet1 = mono_packet.packet_into_db(packet1, id_session, db)
        mono_packet.select_packet(id_packet1, 1, db)
        self.assertEqual(mono_packet.are_packets_selected_in_session(id_session, db), True)
        print("create second packet and select it ") 
        packet2 = mono_packet.create_ping_packet()
        id_packet2 = mono_packet.packet_into_db(packet2, 0, db)
        mono_packet.select_packet(id_packet2, True, db)
        self.assertEqual(mono_packet.are_packets_selected_in_session(id_session, db), True)
        print("unselect one packet")
        mono_packet.select_packet(id_packet2, False, db)
        self.assertEqual(mono_packet.are_packets_selected_in_session(id_session, db), False)
        print("unselect all packets")
        mono_packet.select_packet(id_packet1, False, db)
        self.assertEqual(mono_packet.are_packets_selected_in_session(id_session, db), False)
        print("select all packets at the same time")
        mono_packet.set_selected_all_packets_in_session(id_session, True, db)
        self.assertEqual(mono_packet.are_packets_selected_in_session(id_session, db), True)
        print("unselect all packets at the same time - None of them should be selected")
        mono_packet.set_selected_all_packets_in_session(id_session, False, db)
        self.assertEqual(mono_packet.are_packets_selected_in_session(id_session, db), False)
        self.assertEqual(mono_packet.is_packet_selected(id_packet1, db), False)
        self.assertEqual(mono_packet.is_packet_selected(id_packet2, db), False)
        #clean
        mono_session.remove_session(id_session, db)


#Runs alls the packet tests
#To use it
#suite = unittest.TestSuite()
#suite.addTest(conv_suite()) # add case
#runner = unittest.TextTestRunner()
#runner.run(suite)
def packet_suite():
    suite = unittest.TestSuite()
    suite.addTest(PacketsTestCase("test_add_packet"))
    suite.addTest(PacketsTestCase("test_select_packet"))
    suite.addTest(PacketsTestCase("test_select_all_packets_session"))
    return suite

if __name__ == '__main__':
    #unittest.main() #to run all tests at once

    #show mysql warnings as exception
    warnings.filterwarnings('error', category=Warning)

    #configure and run test suite
    suite = unittest.TestSuite()
    #suite.addTest(PacketsTestCase("test_add_packet"))  # add one unit test
    suite.addTest(PacketsTestCase("test_select_packet"))  # add one unit test
    suite.addTest(PacketsTestCase("test_select_all_packets_session"))  # add one unit test
    #suite.addTest(packet_suite()) # add case
    runner = unittest.TextTestRunner()
    runner.run(suite)
