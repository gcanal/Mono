#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:31:29 2017

@author: robert
"""
import unittest

import warnings
import sys

#ways to execute this test_file
#python -m mono.tests.test_file.py ( __name__ ='__main__' and package ='mono.tests')
#python tests/test_file.py ( __name__ ='__main__' and package = None)
#imported from another module ( __name__ ='mono.tests.test_packets' and package ='mono.tests')

if  __package__ != 'mono.test': #is None
    from os import path
    sys.path.append( path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from mono import mono_session
from mono import mono_packet
from mono import mono_config as mc
from mono import mono_conversation as mono_conv
from mono import mono_packet_conversation as mono_pc

if sys.version_info > (3, 3):
    from pymysql import Warning
    from pymysql import connect 
else:
    from MySQLdb import Warning
    from MySQLdb import connect 


#TESTS for mono_packet_conversation.py

class PacketConversationTestCase(unittest.TestCase):

    def test_add_pc(self):
        print("\n#test_add_pc")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        id_session = 0
        conv_type = 0
        #Fresh start
        mono_session.remove_session(id_session, db)
        mono_pc.remove_packetconversations(id_session, db)

        # create packets 
        packet1 = mono_packet.create_ping_packet(ip_src="192.168.0.33", ip_dst="192.168.0.1")
        packet2 = mono_packet.create_ping_packet(ip_src="192.168.0.6", ip_dst="192.168.0.7")
        packet3 = mono_packet.create_ping_packet(ip_src="192.168.0.1", ip_dst="192.168.0.33")
        # insert packets into db
        id_packet1 = mono_packet.packet_into_db(packet1, id_session, db)
        id_packet2 = mono_packet.packet_into_db(packet2, id_session, db)
        id_packet3 = mono_packet.packet_into_db(packet3, id_session, db)
        # create conversations (packet 1 and 3 belong to the same conversation)
        conv1 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
        conv2 = mono_conv.get_or_create_conv(packet2, db, conv_type, id_session)
        conv3 = mono_conv.get_or_create_conv(packet3, db, conv_type, id_session)
        id_conv1 = conv1["id_conversation"]
        id_conv2 = conv2["id_conversation"]
        id_conv3 = conv3["id_conversation"]

        #testing the function  add_packetconversation
        #Add link between packet and conversation
        id_pc1 = mono_pc.add_packetconversation(id_session, id_packet1, id_conv1, conv_type, db)
        id_pc2 = mono_pc.add_packetconversation(id_session, id_packet2, id_conv2, conv_type, db)
        id_pc3 = mono_pc.add_packetconversation(id_session, id_packet3, id_conv3, conv_type, db)
        #see if db insertion worked
        pk_from_conv1 =  mono_pc.get_packets_from_conversation(id_conv1, conv_type, db)
        pk_from_conv2 =  mono_pc.get_packets_from_conversation(id_conv2, conv_type, db)
        self.assertEqual(len(pk_from_conv1), 2)
        self.assertEqual(id_conv1, id_conv3)
        self.assertEqual(len(pk_from_conv2), 1)
        ppacket2 = pk_from_conv2[0]
        self.assertEqual(ppacket2["id_packet"], id_packet2)
        self.assertEqual(ppacket2["id_conversation"], id_conv2)
        self.assertEqual(ppacket2["conversation_type"], conv_type)
        #test remove_packetconversation
        mono_pc.remove_packetconversation(id_pc2, db)
        #test get_packets_from_conversation
        pk_from_conv1 =  mono_pc.get_packets_from_conversation(id_conv1, conv_type, db)
        self.assertEqual(len(pk_from_conv2), 1)
        #test remove_packetconversations (with an s)
        #We remove all packetconversations, dictionnaries should be empty
        mono_pc.remove_packetconversations(id_session, db)
        pk_from_conv1 =  mono_pc.get_packets_from_conversation(id_conv1, conv_type, db)
        pk_from_conv2 =  mono_pc.get_packets_from_conversation(id_conv2, conv_type, db)
        self.assertEqual(len(pk_from_conv1), 0)
        self.assertEqual(len(pk_from_conv2),0)

        print("Clean up")
        #delete session
        mono_session.remove_session(id_session, db)
        #delete packets
        mono_packet.delete_packet_from_db(id_packet1, db)
        mono_packet.delete_packet_from_db(id_packet2, db)
        mono_packet.delete_packet_from_db(id_packet3, db)

        db.close();


#Runs alls the packet tests
#To use it
#suite = unittest.TestSuite()
#suite.addTest(conv_suite()) # add case
#runner = unittest.TextTestRunner()
#runner.run(suite)
def packet_conversation_suite():
    suite = unittest.TestSuite()
    suite.addTest(PacketConversationTestCase("test_add_pc"))
    return suite

if __name__ == '__main__':
    #unittest.main() #to run all tests at once
    #show mysql warnings as exception
    warnings.filterwarnings('error', category=Warning)
    #configure and run test suite
    suite = unittest.TestSuite()
    suite.addTest(PacketConversationTestCase("test_add_pc"))  # add one unit test
    #suite.addTest(packet_suite()) # add case
    runner = unittest.TextTestRunner()
    runner.run(suite)