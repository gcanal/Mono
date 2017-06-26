#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 19 15:16:57 2017

@author: robert
"""

#ways to execute this test_file
#python -m mono.tests.test_file.py ( __name__ ='__main__' and package ='mono.tests')
#python tests/test_file.py ( __name__ ='__main__' and package = None)
#imported from another module ( __name__ ='mono.tests.test_conversations' and package ='mono.tests')
import os
if  __package__ != 'mono.test': #is None
    import sys
    from os import path
    sys.path.append( path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
import time
import logging

import sys
if sys.version_info > (3, 3):
    from pymysql import connect
    from pymysql import Warning
else:
    from MySQLdb import connect
    from MySQLdb import Warning

import warnings
from mono import mono_conversation as mono_conv
from mono import mono_config as mc
from mono import mono_mitm
from mono import mono_constant
from mono import mono_packet_conversation as mpc


class MitmTestCase(unittest.TestCase):

    #deprecated - We dont use this anymore
    def test_mitm_set_conversation_as_decrypted(self):
        #setup
        id_session = 0 
        conv_type = mono_constant.TCP_CONVERSATION_TYPE
        print("\n#test_add_mitm")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        s = {"ip_src": "133.219.243.23",  "ip_dst": "192.168.30.33", "port_src":3334, "port_dst":443, } #session summary
        #set conversation as decrypted (but the conversation does not already exist)
        conv = mono_mitm.set_conversation_as_decrypted(s, id_session, db)
        self.assertEqual(conv["already_exists"], 0)
        mono_conv.remove_conversation(conv["id_conversation_tcp"], db,conv_type )
        #create conversation 
        conv = mono_conv.get_or_create_conv_no_packet(s, 0, conv_type, id_session, db)
        #and mark the conversation as decrypted
        conv2 = mono_mitm.set_conversation_as_decrypted(s, id_session, db)
        self.assertEqual(conv2["already_exists"], 1)
        #"WERHJEHLK D  we are here johnny boy test l54 does not pass
        self.assertEqual(conv["id_conversation_tcp"], conv2["id_conversation_tcp"])
        #clear
        mono_conv.remove_conversation(conv["id_conversation_tcp"], db, conv_type)
        mono_conv.remove_conversation(conv2["id_conversation_tcp"], db, conv_type)

    def test_mitm_into_db(self,):
        #setup
        id_session = 0 
        print("\n#test_mitm_into_db")
        db = connect(mc.db_host, mc.db_user_name, mc.db_password, mc.db_db_name)#host, user, password, db
        s = {"ip_src": "133.219.243.23",  "ip_dst": "192.168.30.33", "port_src":3334, "port_dst":443, }  #session summary
        content = b"hola chiquitos"
        mitm1 = { "from_client": 1,
            "packet_length": len(content),
            "ip_src": s["ip_src"],
            "ip_dst": s["ip_dst"],
            "port_src": s["port_src"],
            "port_dst": s["port_dst"],
            "payload": content, 
            "selected": 0,
            "timestamp": int(time.time()),
            "sni": "sexydude.com"
          }
        #test the function mitm_into_db
        #it only modify PACKETS table (no CONVERSATION_* or PACKETS_CONVERSATIONS)
        (id_mitm, packet) = mono_mitm.mitm_into_db(mitm1, id_session, db)
        self.assertGreaterEqual(id_mitm, 1)
        mitm2 = mono_mitm.get_mitm_from_db(id_mitm, db)
        #print(mitm2)
        self.assertEqual(id_mitm, mitm2["id_packet"])
        #self.assertEqual(mitm1["packet_length"], mitm2["packet_length"]) cannot test packet length
        self.assertEqual(mitm1["ip_src"], mitm2["ip_src"])
        self.assertEqual(mitm1["ip_dst"], mitm2["ip_dst"])
        self.assertEqual(mitm1["port_src"], mitm2["port_src"])
        self.assertEqual(mitm1["port_dst"], mitm2["port_dst"])
        #self.assertEqual(mitm1["packet"], mitm2["packet"]) cannot compare payload content
        self.assertEqual(mitm1["selected"], mitm2["selected"])
        #self.assertEqual(mitm1["timestamp"], mitm2["timestamp"]) cannot compare timestamp
        self.assertEqual(mitm1["sni"], mitm2["domain"])
        
        #clear
        mono_mitm.remove_mitm_packet(id_mitm, db)

    def test_rule(self,):
        print("\n#test_rule")
        print("Delete the rule and make sure it does not exist")
        mono_mitm.delete_rule()
        self.assertEqual(mono_mitm.test_rule_exist(), False)
        print("add the rule ")
        mono_mitm.add_rule()
        self.assertEqual(mono_mitm.test_rule_exist(), True)
        print("delete rule ")
        mono_mitm.delete_rule()
        self.assertEqual(mono_mitm.test_rule_exist(), False)
        #add rule twice
        mono_mitm.add_rule()
        mono_mitm.add_rule()
        self.assertEqual(mono_mitm.test_rule_exist(), True)
        #delete all rules
        mono_mitm.delete_rule()
        self.assertEqual(mono_mitm.test_rule_exist(), False)
        #add the rule manually twice and delete it. Both lines should be deleted
        os.system("iptables -A PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")
        os.system("iptables -A PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")
        mono_mitm.delete_rule()
        self.assertEqual(mono_mitm.test_rule_exist(), False)

        

def mitm_suite():
    suite = unittest.TestSuite()
    suite.addTest(MitmTestCase("test_mitm_into_db"))
    suite.addTest(MitmTestCase("test_rule"))
    return suite


if __name__ == '__main__':
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(' %(levelname)-8s %(name)-12s %(message)s')#%(asctime)s
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    #unittest.main() #to run all tests at once
    db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db

    #show mysql warnings as exception
    warnings.filterwarnings('error', category= Warning)

    #configure and run tests
    suite = unittest.TestSuite()
    #suite.addTest(MitmTestCase("test_mitm_set_conversation_as_decrypted"))
    suite.addTest(MitmTestCase("test_mitm_into_db"))
    #suite.addTest(MitmTestCase("test_rule"))
    runner = unittest.TextTestRunner()
    runner.run(suite)












