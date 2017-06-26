#  #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:31:29 2017

@author: robert
"""

#ways to execute this test_file
#python -m mono.tests.test_file.py ( __name__ ='__main__' and package ='mono.tests')
#python tests/test_file.py ( __name__ ='__main__' and package = None)
#imported from another module ( __name__ ='mono.tests.test_conversations' and package ='mono.tests')

if  __package__ != 'mono.test': #is None
    import sys
    from os import path
    sys.path.append( path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from scapy.all import IP

import sys
if sys.version_info > (3, 3):
    from pymysql import connect
    from pymysql import Warning
else:
    from MySQLdb import connect
    from MySQLdb import Warning

import warnings
from mono import mono_conversation as mono_conv
from mono import mono_packet
from mono import mono_config as mc


class ConversationsTestCase(unittest.TestCase):

    #what should be tested: 
    #for each conv_type
    #packets p1 and p2 are added to the same IP conversations if and only if
    # (c1) p1.ip_src != p1.ip_dst p2.ip_src != p2.ip_dst
    # (c2) (p1.ip_src == p2.ip_src and p1.ip_dst == p2.ip_dst) 
    #             OR
    #      (p1.ip_src == p2.ip_dst and p1.ip_dst == p2.ip_dst)

    def test_add_conv_ipv4(self):
        #setup
        id_session = 0 
        conv_type = 0
        print("\n#test_add_conv")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        ip1 = "133.219.243.23"
        ip2 = "192.168.30.33"
        names = mono_conv.get_table_name_and_id_key(conv_type)
        id_name = names["id_name"]
        
        #step1 test that packets are added to the same conversation if
        #(p1.ip_src == p2.ip_src and p1.ip_dst == p2.ip_dst)
        packet1  = mono_packet.create_ping_packet(ip_src=ip2, ip_dst=ip1)
        print (packet1.summary())
        conv1 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
        print("create conversation 1 ")
        print (conv1)
        conv2 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
        print("get conversation 2 ")
        print(conv2)
        self.assertEqual(conv1["id_conversation"], conv2[id_name], "conv id should be equal")
        self.assertGreaterEqual(conv1[id_name], 1)
        self.assertGreaterEqual(conv2[id_name], 1)
        # step2 test that packets are added to the same conversation if
        # (p1.ip_src == p2.ip_dst and p1.ip_dst == p2.ip_dst)
        print ("swap ip source and destination")
        src = packet1.getlayer(IP).src
        packet1.getlayer(IP).src = packet1.getlayer(IP).dst
        packet1.getlayer(IP).dst = src
        print (packet1.summary())
        print ("get conversation 3 ")
        conv3 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
        print(conv3)
        self.assertGreaterEqual(conv3[id_name], 1)
        self.assertEqual(conv1["id_conversation"], conv3[id_name])
        # step3 test that packets are NOT added to the same conversation if
        # (p1.ip_src == p2.ip_src and p1.ip_dst != p2.ip_dst)
        packet1.getlayer(IP).dst = "12.12.12.12"
        conv4 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
        self.assertGreaterEqual(conv4["id_conversation"], 1)
        self.assertEqual(conv4[id_name], conv3["id_conversation"] + 1)
        print("get conversation 4")
        print(conv4)
        print("Now removing conversations")
        mono_conv.remove_conversations(id_session, db, conv_type)
        db.close();

    #packets p1 and p2 are added to the same UDP/TCP conversations if and only if
    # (c1) p1.ip_src != p1.ip_dst p2.ip_src != p2.ip_dst
    # (c2) (p1.ip_src == p2.ip_src and p1.ip_dst == p2.ip_dst and p1.port_src == p2.port_src and p1.port_dst == p2.port_dst) 
    #             OR
    #      (p1.ip_src == p2.ip_dst and p1.ip_dst == p2.ip_src and p1.port_src == p2.port_dst and p1.port_dst == p2.port_src) 
    #tests api functions add_session and get_session

    def test_add_conv_tcp_udp(self):
        #setup
        id_session = 0 
        conv_type = 1
        print("\n#test_add_conv_tcp_udp")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        ip1 = "1.2.3.4"
        ip2 = "192.168.13.33"
        port1 = 1028
        port2 = 80
        port3 = 90
        for conv_type in range (1,2):
            names = mono_conv.get_table_name_and_id_key(conv_type)
            id_name = names["id_name"]
            #prepare packets
            #conv_type == 1   case udp
            #reference packet
            packet1 = mono_packet.create_udp_packet(ip_src= ip1, ip_dst=ip2, port_src=port1, port_dst=port2, ip_size=40)
            print(packet1.command())
            #inverted ips and ports
            packet2 = mono_packet.create_udp_packet(ip_src= ip2, ip_dst=ip1, port_src=port2, port_dst=port1, ip_size=40)
            #inverted ips and non inverted ports
            packet3 = mono_packet.create_udp_packet(ip_src= ip2, ip_dst=ip1, port_src=port1, port_dst=port2, ip_size=40)
            #inverted ips and differents ports
            packet4 = mono_packet.create_udp_packet(ip_src= ip2, ip_dst=ip1, port_src=port1, port_dst=port3, ip_size=50)
            #same as reference packet
            packet5 = mono_packet.create_udp_packet(ip_src= ip1, ip_dst=ip2, port_src=port1, port_dst=port2, ip_size=40)

            if conv_type == 2:#case tcp
                #reference packet
                packet1 = mono_packet.create_tcp_packet(ip_src= ip1, ip_dst=ip2, port_src=port1, port_dst=port2, ip_size=40)
                #inverted ips and ports
                packet2 = mono_packet.create_tcp_packet(ip_src= ip2, ip_dst=ip1, port_src=port2, port_dst=port1, ip_size=40)
                #inverted ips and non inverted ports
                packet3 = mono_packet.create_tcp_packet(ip_src= ip2, ip_dst=ip1, port_src=port1, port_dst=port2, ip_size=40)
                #inverted ips and differents ports
                packet4 = mono_packet.create_tcp_packet(ip_src= ip2, ip_dst=ip1, port_src=port1, port_dst=port3, ip_size=40)
                #same as reference packet
                packet5 = mono_packet.create_tcp_packet(ip_src= ip1, ip_dst=ip2, port_src=port1, port_dst=port2, ip_size=40)

            ## fresh start
            print("Fresh start: clear all conversations of the session")
            mono_conv.remove_conversations(id_session, db, conv_type)
            all_convs = mono_conv.get_conversations(id_session, db, conv_type)
            self.assertEqual(len(all_convs), 0)
        
            #create conversations from packets
            conv1 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
            conv2 = mono_conv.get_or_create_conv(packet2, db, conv_type, id_session)
            conv3 = mono_conv.get_or_create_conv(packet3, db, conv_type, id_session)
            conv4 = mono_conv.get_or_create_conv(packet4, db, conv_type, id_session)
            conv5 = mono_conv.get_or_create_conv(packet5, db, conv_type, id_session)
            print("create conversations")
            print(conv1); print(conv2); print(conv3); print(conv4); print(conv5); 
        
            #performing analysis fetched vs created
            self.assertGreaterEqual(conv1[id_name], 1)
            self.assertEqual(conv1[id_name], conv2[id_name], "conv1 and conv2 should be the same")
            self.assertEqual(conv2[id_name] + 1, conv3[id_name], "conv2 and conv3 should be !=")
            self.assertEqual(conv3[id_name] + 1, conv4[id_name], "conv3 and conv4 should be !=")
            self.assertEqual(conv5[id_name], conv1[id_name], "conv1 and conv5 should be the same")
        
            #packets 1,2 and 5 should belong to the same conversation
            self.assertEqual(conv1["from_a"], True, "packet1 goes from a to b")
            self.assertEqual(conv2["from_a"], False, "packet2 goes from b to a")
            self.assertEqual(conv5["from_a"], True, "packet5 goes from a to b")


            #adding packet to conversations
            #Maybe place this in another function
            id_packet = 0;
            mono_conv.add_packet_to_conversations(id_packet, packet1, db, id_session)
            mono_conv.add_packet_to_conversations(id_packet, packet2, db, id_session)
            mono_conv.add_packet_to_conversations(id_packet, packet3, db, id_session)
            mono_conv.add_packet_to_conversations(id_packet, packet4, db, id_session)
            mono_conv.add_packet_to_conversations(id_packet, packet5, db, id_session)
            #TODO perform some more analysis:
            #inspect bytes rel_start duration packets packets_a_b packets_b_a, bytes_a_b, bytes_b_a
            
            #retrieve all conversations
            convs = mono_conv.get_conversations(id_session, db, conv_type)
            self.assertEqual(len(convs), 3)
            print (convs)

            #2 ways to get a conversation 
            #either with mono_conv.get_or_create_conv (tested above)
            #or with mono_conv.get_or_create_conv (tested below)
            conv11 = mono_conv.get_conversation_from_id(conv1["id_conversation"], db, conv_type)
            conv22 = mono_conv.get_conversation_from_id(conv2["id_conversation"], db, conv_type)
            conv33 = mono_conv.get_conversation_from_id(conv3["id_conversation"], db, conv_type)
            conv44 = mono_conv.get_conversation_from_id(conv4["id_conversation"], db, conv_type)
            conv55 = mono_conv.get_conversation_from_id(conv5["id_conversation"], db, conv_type)

            #TODO perform some more analysis:
            #inspect bytes rel_start duration packets packets_a_b packets_b_a, bytes_a_b, bytes_b_a
            #conv1 tests
            self.assertEqual(conv11["packets"], 3)
            self.assertEqual(conv11["packets_a_b"], 2)
            self.assertEqual(conv11["packets_b_a"], 1)
            self.assertEqual(conv11["bytes"], 120)
            self.assertEqual(conv11["bytes_a_b"], 80)
            self.assertEqual(conv11["bytes_b_a"], 40)
            #conv2 tests
            self.assertEqual(conv22["id_conversation"], conv11["id_conversation"])
            #conv3 tests
            self.assertEqual(conv33["packets"], 1)
            self.assertEqual(conv33["packets_a_b"], 1)
            self.assertEqual(conv33["packets_b_a"], 0)
            self.assertEqual(conv33["bytes"], 40)
            self.assertEqual(conv33["bytes_a_b"], 40)
            self.assertEqual(conv33["bytes_b_a"], 0)
            #conv4 tests
            self.assertEqual(conv44["packets"], 1)
            self.assertEqual(conv44["packets_a_b"], 1)
            self.assertEqual(conv44["packets_b_a"], 0)
            self.assertEqual(conv44["bytes"], 50)
            self.assertEqual(conv44["bytes_a_b"], 50)
            self.assertEqual(conv44["bytes_b_a"], 0)
            #conv5 tests
            self.assertEqual(conv55["id_conversation"], conv11["id_conversation"])
            
        #clean
        mono_conv.remove_conversations(id_session, db, conv_type)
        db.close();
                
    def prepare_packets(self, conv_type):
        packet1 = mono_packet.create_ping_packet(ip_src="192.168.0.33", ip_dst="192.168.0.1")
        packet2 = mono_packet.create_ping_packet(ip_src="192.168.0.6", ip_dst="192.168.0.7")
        packet3 = mono_packet.create_ping_packet(ip_src="192.168.0.8", ip_dst="192.168.0.9")
        if (conv_type == 1): #udp
           packet1 = mono_packet.create_udp_packet(ip_src="192.168.0.33", ip_dst="192.168.0.1", port_src=1028, port_dst=80)
           packet2 = mono_packet.create_udp_packet(ip_src="192.168.0.33", ip_dst="192.168.0.1", port_src=1029, port_dst=80)
           packet3 = mono_packet.create_udp_packet(ip_src="192.168.0.8", ip_dst="192.168.0.9", port_src=1028, port_dst=80)
        if (conv_type == 1): #tcp
           packet1 = mono_packet.create_tcp_packet(ip_src="192.168.0.33", ip_dst="192.168.0.1", port_src=1028, port_dst=80)
           packet2 = mono_packet.create_tcp_packet(ip_src="192.168.0.33", ip_dst="192.168.0.1", port_src=1029, port_dst=80)
           packet3 = mono_packet.create_tcp_packet(ip_src="192.168.0.8", ip_dst="192.168.0.9", port_src=1028, port_dst=80)
        return (packet1, packet2, packet3)


    #test the functions remove_conversation and remove_conversations for 
    #all types of conversations (0:IP, 1:UDP, 2:TCP)
    def test_remove(self):
        print("\n#test_remove")
        id_session = 0;
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        conv_type = 0;
        for conv_type in range (0,2):
            names = mono_conv.get_table_name_and_id_key(conv_type)
            print("testing remove for table " + names["table_name"])
            ## preparing packets
            (packet1, packet2, packet3) = self.prepare_packets(conv_type)
            ## Fresh start: no conversation for the session
            mono_conv.remove_conversations(id_session, db, conv_type)
            print("create 3 different conversations with 3 different packets")
            conv1 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
            conv2 = mono_conv.get_or_create_conv(packet2, db, conv_type, id_session)
            conv3 = mono_conv.get_or_create_conv(packet3, db, conv_type, id_session)
            #Conversations should have differents ids
            self.assertEqual(conv1[names["id_name"]] + 1, conv2[names["id_name"]])
            self.assertEqual(conv2["id_conversation"] + 1, conv3["id_conversation"])
            #Get all conversations of current session
            convs = mono_conv.get_conversations(id_session, db, conv_type)
            print(convs)
            self.assertEqual(len(convs), 3)
            #supress individually one session and check if it worked
            mono_conv.remove_conversation(conv1[names["id_name"]], db, conv_type)
            convs = mono_conv.get_conversations(id_session, db, conv_type)
            self.assertEqual(len(convs), 2)
            #Remove all remaining conversations
            mono_conv.remove_conversations(id_session, db, conv_type)
            convs = mono_conv.get_conversations(id_session, db, conv_type)
            self.assertEqual(len(convs), 0)

    def test_select_conversation(self):
        print("\n#test select")
        id_session = 0;
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        for conv_type in range (0,2):
             ## preparing packets
            (packet1, packet2, packet3) = self.prepare_packets(conv_type)
            ## Fresh start: no conversation for the session
            mono_conv.remove_conversations(id_session, db, conv_type)
            conv1 = mono_conv.get_or_create_conv(packet1, db, conv_type, id_session)
            print("select the conversation")
            check = True
            mono_conv.select_conversation(conv1["id_conversation"], conv_type, check, db)
            self.assertEqual(mono_conv.is_conversation_selected(conv1["id_conversation"], conv_type, db), 1)
            check = False
            mono_conv.select_conversation(conv1["id_conversation"], conv_type, check, db)
            self.assertEqual(mono_conv.is_conversation_selected(conv1["id_conversation"], conv_type, db), 0)
            check = 1
            mono_conv.select_conversation(conv1["id_conversation"], conv_type, check, db)
            self.assertEqual(mono_conv.is_conversation_selected(conv1["id_conversation"], conv_type, db), 1)
            check = 0
            mono_conv.select_conversation(conv1["id_conversation"], conv_type, check, db)
            self.assertEqual(mono_conv.is_conversation_selected(conv1["id_conversation"], conv_type, db), 0)
            #clean : remove all conversations
            mono_conv.remove_conversations(id_session, db, conv_type)
            convs = mono_conv.get_conversations(id_session, db, conv_type)
            self.assertEqual(len(convs), 0)

            
    def test_add_packet(self):
        pass
    
def conversations_suite():
    suite = unittest.TestSuite()
    suite.addTest(ConversationsTestCase("test_add_conv_ipv4"))
    suite.addTest(ConversationsTestCase("test_add_conv_tcp_udp"))
    suite.addTest(ConversationsTestCase("test_remove"))
    suite.addTest(ConversationsTestCase("test_select_conversation"))
    return suite


if __name__ == '__main__':
    #unittest.main() #to run all tests at once
    db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db

    #show mysql warnings as exception
    warnings.filterwarnings('error', category= Warning)

    #configure and run tests
    suite = unittest.TestSuite()
#    suite.addTest(ConversationsTestCase("test_add_conv_ipv4"))
#    suite.addTest(ConversationsTestCase("test_add_conv_tcp_udp"))
#    suite.addTest(ConversationsTestCase("test_remove"))
    suite.addTest(ConversationsTestCase("test_select_conversation"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    #exception_catcher()

