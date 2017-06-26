#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 21:44:18 2017

@author: robert
"""
import time
import sys
import subprocess
import logging
import threading
#import Queue
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors

from . import mono_tools
from . import mono_constant
from . import mono_conversation
from . import mono_packet_conversation as mpc
from . import mono_packet
from . import mono_param

#mitmproxy imports 
import os  # noqa
import signal  # noqa
from mitmproxy.tools import cmdline  # noqa
from mitmproxy import exceptions  # noqa
from mitmproxy import options  # noqa
from mitmproxy.proxy import config  # noqa
from mitmproxy.proxy import server  # noqa
from mitmproxy.utils import version_check  # noqa
from mitmproxy.utils import debug  # noqa

#idea: the same tcp conversation will appear twice in the packet_conversation table. 
#one coded with type = 2 (TCP) and the other decrypted with type MITM_CONVERSATION_TYPE
#id_pc: for test purposes only
def mitm_into_db(mitm, id_session, db):
    l =  logging.getLogger("mono_mitm.callback")
    m = mitm
    mitm_set_default_value(m) # set keys to default values
    #create packet 
    packet = mono_packet.create_tcp_packet(ip_dst=m["ip_dst"], ip_src=m["ip_src"], port_src=m["port_src"], port_dst=m["port_dst"], padding=m["payload"])
    #place packet in db
    if (not m["sni"]):
        m["sni"] = "?"
    id_packet = mono_packet.packet_into_db(packet, id_session, db, domain = m["sni"], decrypted=1)
    l.debug("MITM callback (session %s) %15s/%6s -> %15s/%6s %s"%(str(id_session), m['ip_src'], m['port_src'], m['ip_dst'], m['port_dst'], m["sni"] ) )
    l.debug(m["payload"])
    return (id_packet, packet)


def get_mitm_from_db(id_packet_tcp_mitm, db):
    return mono_packet.get_packet_from_id(id_packet_tcp_mitm, db)

#Deprecated (legacy)
def remove_mitm_packet(id_packet_tcp_mitm, db):
    mono_packet.delete_packet_from_db(id_packet_tcp_mitm, db)

def mitm_set_default_value(m):
    if (not "from_client" in m):
        m["from_client"] = 1
    if (not "packet_length" in m):
        m[" "] = 0
    if (not "ip_src" in m):
        m["ip_src"] = "0.0.0.0"
    if (not "ip_dst" in m):
        m["ip_dst"] = "0.0.0.0"
    if (not "port_src" in m):
        m["port_src"] = "0"
    if (not "port_dst" in m):
        m["port_dst"] = "0"
    if (not "payload" in m):
        m["payload"] = b"1 2 3 test"
    if (not "selected" in m):
        m["selected"] = 0
    if (not "timestamp" in m):
        m["timestamp"] = int(time.time()) #seconds since epoch
    if (not "sni" in m):
        m["sni"] = "robert.com"

#s is the conversation summary and is like:
# s={"ip_src":ip_client, "ip_dst":ip_server, "port_src":port_client, "port_dst":port_server
#DEPRECATED
def set_conversation_as_decrypted(s, id_session, db):
        conv_type = mono_constant.TCP_CONVERSATION_TYPE
        conv = mono_conversation.get_or_create_conv_no_packet(s, 0, conv_type, id_session, db)
        conv["decrypted"] = 1
        #TODO get rid of this cheap trick (NO generic update. Es una mierda)
        ar = conv["already_exists"]
        id = conv["id_conversation"]
        mono_conversation.update_conv(conv, conv_type, db)
        conv["already_exists"] = ar
        conv["id_conversation"] = id
        conv["id_conversation_tcp"] = id
        return conv

class MitmException(Exception):
    pass


#global variable 
mitm_master = None
mitm_thread = None

def start_mitm_thread():
    l = logging.getLogger("mono_mitm")
    l.info("starting mitm thread")
    global mitm_thread
    mitm_thread = threading.Thread(target=start_mitm)
    mitm_thread.start()

def process_options(options):
    #debug.register_info_dumpers()
    pconf = config.ProxyConfig(options)
    if options.no_server:
        return server.DummyServer(pconf)
    else:
        try:
            return server.ProxyServer(pconf)
        except exceptions.ServerException as v:
            print(str(v))
            sys.exit(1)

#starts the mitm proxy with the following command
#mitmdump -T --tcp ".*"  --ssl-version-client all --ssl-version-server all  --insecure -s mitm.py -p 8182 --cadir certs
def start_mitm():
    global mitm_master
    l = logging.getLogger("mono_mitm")
    if sys.version_info < (3, 5):
        l.critical("MITM NEEDS PYTHON > 3.5 TO START")
        print("MITM NEEDS PYTHON > 3.5 TO START")
        return 
    l.info("start mitm proxy")
    #iptables thingy
    add_rule()
    #delete rule if it already exist
    os.system("iptables -D PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")
    #add rule 
    os.system("iptables -A PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")
    from mitmproxy.tools import dump
    version_check.check_pyopenssl_version();

    #args = parser.parse_args(args) This might cause a problem
    #dump_options.load_paths(args.conf)
    #dump_options.merge(cmdline.get_common_options(args))
    
    dump_options = options.Options()
    dump_options.merge(
        dict(
            flow_detail           = 1,
            web_port              = 8081,
            cadir                 = '~/.mitmproxy', 
            listen_port           = 8182, 
            mode                  = 'transparent',
            no_server             = False, 
            rawtcp                = False, 
            scripts               = ['mitm.py'],
            ssl_insecure          = True, 
            ssl_version_client    = 'all', 
            ssl_version_server    = 'all',
            tcp_hosts             = ['.*'],
        )
    )
    server = process_options(dump_options)
    mitm_master = dump.DumpMaster(dump_options, server)
    l.info("start_mitm --> run master")
    mitm_master.run()

def is_mitm_active():
    global mitm_master
    return (mitm_master is not None)

def stop_mitm(): 
    #TODO make this param
    delete_rule()
    global mitm_master
    global mitm_thread
    if (mitm_master is not None):
        mitm_master.shutdown()
    logging.getLogger("mono_mitm").info("stop MITM: mitm_master=None")
    mitm_master = None
    if (mitm_thread is not None):
        pass
        #mitm_thread.join()

# iptables -S -t nat | grep "-s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182"
#iptables -S -t nat | fgrep  -i '8182' | wc -l
def test_rule_exist():
    command = "iptables -S -t nat | fgrep  -i '8182' | wc -l"
    res = subprocess.check_output(command, shell=True, executable='/bin/bash')
    n = int(res)
    return n > 0

#delete the itables rule  : -A PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182
#and make sure that all duplicate lines are deleted
def delete_rule(log=True):
    if log:
        l = logging.getLogger("mono_mitm")
        l.info("DELETE iptables rule -D PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")
    while (test_rule_exist()):
        os.system("iptables -D PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")

#Insert the iptables rule -A PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182
#And make sure it is inserted once
def add_rule():
    l = logging.getLogger("mono_mitm")
    l.info("ADD iptables rule -A PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")
    delete_rule(log=False)
    os.system("iptables -A PREROUTING -t nat -s 10.8.0.0/24 -p tcp -j REDIRECT --to-ports 8182")


