#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:31:29 2017

@author: robert
"""
import unittest

import warnings

import sys
if sys.version_info > (3, 3):
    from pymysql import Warning
else:
    from MySQLdb import Warning

#main test file 

if __package__ != 'mono.test':
    import sys
    from os import path
    sys.path.append( path.dirname(path.dirname(path.dirname( path.abspath(__file__)))))

from mono import mono_session
from mono.test import test_packet
from mono.test import test_conversation
from mono.test import test_session
from mono.test import test_packet_conversation
from mono.test import test_param
from mono.test import test_mitm

class IfacesTestCase(unittest.TestCase):
    """Tests for mono_session.get_ifaces"""
    def test_ifaces(self):
        print("\n")
        print("#test ifaces (check if eth0 is in list of ifaces)")
        ifaces = mono_session.get_ifaces()
        print(ifaces)
        self.assertIn("eth0", ifaces, msg="Coucou")

def ifaces_suite():
    suite = unittest.TestSuite()
    suite.addTest(IfacesTestCase("test_ifaces"))
    return suite


def run_all_tests():
    #unittest.main() #to run all tests at once
    suite = unittest.TestSuite()
    suite.addTest(ifaces_suite()) 
    suite.addTest(test_session.session_suite())
    suite.addTest(test_packet.packet_suite())
    suite.addTest(test_conversation.conversations_suite())
    suite.addTest(test_packet_conversation.packet_conversation_suite())
    suite.addTest(test_param.param_suite())
    suite.addTest(test_mitm.mitm_suite())
    runner = unittest.TextTestRunner()
    runner.run(suite)

def exception_raiser():
    raise RuntimeError('this is the error message')
    
def plain_function():
    print("I am calling the exception raiser")
    exception_raiser()

def exception_catcher():
    try:
        plain_function()
    except Exception as e:
        print("exception_caught in exception_catcher")
        print (str(e))
        raise

if __name__ == '__main__':
    #unittest.main() #to run all tests at once

    #show mysql warnings as exception
    warnings.filterwarnings('error', category=Warning)
    
    #run all tests
    run_all_tests()

#    suite = unittest.TestSuite()
#    runner = unittest.TextTestRunner()
#    runner.run(suite)

    #blabla

    #exception_catcher()

