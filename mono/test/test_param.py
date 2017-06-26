#ways to execute this test_file
#python -m mono.tests.test_file.py ( __name__ ='__main__' and package ='mono.tests')
#python tests/test_file.py ( __name__ ='__main__' and package = None)
#imported from another module ( __name__ ='mono.tests.test_conversations' and package ='mono.tests')
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

from mono import mono_param
from mono import mono_config as mc

class ParamTestCase(unittest.TestCase):

    def test_set_get(self):
        #setup
        print ("\n#test_set_get")
        db = connect(mc.db_host, mc.db_user_name, mc.db_password, mc.db_db_name)#host, user, password, db
        mono_param.set_recording(0, db)
        self.assertEqual(mono_param.get_recording(db), 0)
        mono_param.set_recording(1, db)
        self.assertEqual(mono_param.get_recording(db), 1)
        mono_param.set_decrypting(0, db)
        self.assertEqual(mono_param.get_decrypting(db), 0)
        mono_param.set_decrypting(1, db)
        self.assertEqual(mono_param.get_decrypting(db), 1)
        mono_param.set_id_session(0, db)
        self.assertEqual(mono_param.get_id_session(db), 0)
        mono_param.set_id_session(33, db)
        self.assertEqual(mono_param.get_id_session(db), 33)
        #print "packet1_time: %s packet_time2 %s"%(format(packet.time, '.10f'), format(packet2.time, '.10f') )
        db.close();

def param_suite():
    suite = unittest.TestSuite()
    suite.addTest(ParamTestCase("test_set_get"))
    return suite

if __name__ == '__main__':

    #show mysql warnings as exception
    warnings.filterwarnings('error', category=Warning)

    #configure and run tests
    suite = unittest.TestSuite()
    suite.addTest(ParamTestCase("test_set_get"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    #exception_catcher()
