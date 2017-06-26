#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:31:29 2017

@author: robert
"""
#ways to execute this test_file
#python -m mono.tests.test_file.py ( __name__ ='__main__' and package ='mono.tests')
#python tests/test_file.py ( __name__ ='__main__' and package = None)
#imported from another module ( __name__ ='mono.tests.test_sessions' and package ='mono.tests')
import sys 
if  __package__ != 'mono.test': #is None
    from os import path
    sys.path.append( path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
if sys.version_info > (3, 3):
    from pymysql import connect
    from pymysql import Warning
else:
    from MySQLdb import connect
    from MySQLdb import Warning

import warnings
from mono import mono_session
from mono import mono_config as mc

class SessionTestCase(unittest.TestCase):
    
    #tests api functions add_session and get_session
    def test_add_session(self):
        print("\n#test session")
        db = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)#host, user, password, db
        print("inserting to db")
        sess1 = {"name":"xxx", "iface":"wlan0"}
        id_session = mono_session.add_session(sess1, db)
        print("retrieving from db")
        sess2 = mono_session.get_session(id_session, db)
        print(sess2)
        
        self.assertEqual(sess1["name"],sess2['name'])
        self.assertEqual(sess1["iface"],sess2['iface'])
        self.assertEqual(id_session,sess2['id_session'])
        mono_session.remove_session(id_session, db)
        db.close()

def session_suite():
    suite = unittest.TestSuite()
    suite.addTest(SessionTestCase("test_add_session"))
    return suite

#run as: 
#python -m mono.tests.test_sessions
#or
#python test_sessions
if __name__ == '__main__':
    #show mysql warnings as exception
    warnings.filterwarnings('error', category=Warning)
    #configure and run test suite
    suite = unittest.TestSuite()
    suite.addTest(SessionTestCase("test_add_session"))  # add one unit test
    runner = unittest.TextTestRunner()
    runner.run(suite)