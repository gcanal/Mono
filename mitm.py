# #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 21:15:46 2017

@author: robert
"""
#WORKS with MITM proxy version 2.0.2 by Aldo cortesi
#and PYTHON >3.5
from mono  import mono_param 
from mono import mono_conversation
from mono import mono_constant
from mono import mono_mitm
import mono.mono_config as mc



import logging
import os
from mitmproxy.utils import strutils
import sys
from pymysql import connect
if sys.version_info < (3, 5):
     print("# mitmproxy only supports Python 3.5 and above! #")

#sys.path.append('../mono_web/')
#import argparse
#import random
#from mitmproxy import io, http
#from mono import mono_packet as mp
#from scapy.all import IP, UDP,TCP, ICMP, Raw # for export/import_object
#import scapy 
#import socket
#import importlib
#import inspect

#How to use this command


#mitmdump -T --tcp ".*"  --ssl-version-client all --ssl-version-server all  --insecure -s mitm.py -p 8182 --cadir certs
#mitmdump -T --ssl-version-client all --ssl-version-server all  --insecure  --cadir certs -p 8182

#mitmdump -T --ssl-version-client all --ssl-version-server all  --insecure  -p 8182 --cert=certs/mitmproxy-ca-cert.pem tried but does not work

#--insecure does not veryfy  upstream server SSL/TLS certificates
#--raw-tcp Explicitly enable/disable experimental raw tcp support.  Disabled by default.  Default value will change in a future version.

#to use custom certificate http://docs.mitmproxy.org/en/stable/certinstall.html#using-a-custom-certificate

print("Gid=" + str(os.getegid()))
print(sys.version)




current_id_session = 0
recording = 0
decrypting = 0
db = connect(mc.db_host, mc.db_user_name, mc.db_password, mc.db_db_name)#host, user, password, db
ip_server = "0.0.0.0"
ip_client = "0.0.0.0"
port_server = 0
port_client = 0
id_conver = -1
#callback function called everytime a tcp packet is received
def tcp_message(flow):
    l1 = logging.getLogger("mitm")
    l = logging.getLogger("mono_mitm.callback")
    global current_id_session, recording, decrypting, db
    global ip_server, ip_client, port_server, port_client
    global id_conver
    number = len(flow.messages)
    lm = flow.messages[-1] #last_message
    #if this is the first message of the flow , we update our values
    if (number == 1):
        l.debug("Number ONE : first message of the flow")
        mono_param.set_decrypting(1, db)
        #reset vars
        current_id_session = mono_param.get_id_session(db)
        id_conver = -1
        ip_server = flow.server_conn.address.host #supposedly unresolved ip 
        ip_client = flow.client_conn.address.host
        port_server = flow.server_conn.address.port
        port_client = flow.client_conn.address.port
        #flow.server_conn.ip_address.host is the resolved ip 

    if (current_id_session > 0):
        #mitm summary
        m= { "from_client": lm.from_client,
            "packet_length": len(lm.content),
            "ip_src": ip_client if lm.from_client else ip_server,
            "ip_dst": ip_server if lm.from_client else ip_client,
            "port_src": port_client if lm.from_client else port_server,
            "port_dst": port_server if lm.from_client else port_client,
            "payload": lm.content, 
            "selected": 0,
            "timestamp":lm.timestamp,
            "sni": flow.server_conn.sni
                }
        #create mitm and add it to db
        (id_packet, packet) = mono_mitm.mitm_into_db(m, current_id_session, db)
        #add packet to mitm conversation
        conv = mono_conversation.add_packet_to_conversations(id_packet, packet, db, current_id_session, id_conv = -1, mitm = True)
        l.info("adding packet %s to current_session %s "%(id_packet, current_id_session))
        l.debug(str(packet))
        id_conver = conv["id_conversation"]


"""
    print(strutils.bytes_to_escaped_str(flow.messages[-1].content).encode('UTF-8'))
    
    size = len(flow.messages[-1].content)
    conn1 = flow.server_conn
    conn2 = flow. client_conn
    server_dns = flow.server_conn.address # ip or dns
    
    sni = flow.server_conn.sni
    
    ts = flow.messages[-1].timestamp
    from_cli = flow.messages[-1].from_client
    sys.version
    #with open("test.txt", "ab") as bindump:
        #bindump.write(bin("\n packet %s \n"%n)
        #bindump.write(flow.messages[-1].content)
    with open("test.txt", "a") as f: 
        #bindump.write(bin("\n packet %s \n"%n)
        f.write("\n Start OF PACKET \n ")
        f.write(" size=%d "%(size))
        f.write(" N=%d  "%(number))
        f.write(" timestamp=%f \n "%(ts))
        
        f.write(" server_dns=%s  "%(server_dns))
        f.write(" sni=%s "%(sni))
        f.write(" server_ip=%s  "%(server_ip))
        #f.write(" cli_ip.__module__=%s  "%(cli_ip.__module__)) 
        #f.write(" cli_ip.__class__.__name__=%s  "%(cli_ip.__class__.__name__)) 
        #f.write(" cli_addr=%s  "%(cli_ip.address))
        #f.write("inspect.getfile(cli_ip)=%s  "%(inspect.getfile(cli_ip.__class__)))
        f.write(" cli_ip=%s  cli_port=%s\n "%(cli_ip.host, cli_ip.port))


        f.write(" conn1=%s  \n"%(conn1))
        f.write(" conn2=%s  \n"%(conn2))
        f.write(" from_cli=%d  \n"%(from_cli))
        f.write(strutils.bytes_to_escaped_str(flow.messages[-1].content))
        f.write("\n END OF PACKET \n")
"""



#    for message in flow.messages:
#        print("\n"+str(i))
#        print(message)
#        i +=1
#    print(flow.messages[-1])
#    print(flow.messages[-1].content)
#    a = strutils.bytes_to_escaped_str(flow.messages[-1].content)
#    print(a)
    #packet = scapy.layers.l2.Ether(flow.messages[-1].content)
    #print(packet.command())
#    with open("test.txt", "ab") as bindump:
#        bindump.write(flow)


#    if (number == 1):
#        mono_param.set_decrypting(1, db)
#        l.debug("Number ONE : first message of the flow")
#        current_id_session = mono_param.get_id_session(db)
##        When this callback is called, we place the mitm packets in the db
##        recording = mono_param.get_recording(db) deprecated
##        decrypting = mono_param.get_decrypting(db) deprecated
#
#        #ips
#        #ip_server_dns = flow.server_conn.address.host
#        #flow.server_conn.ip_address.host is the resolved ip 
#        ip_server = flow.server_conn.address.host #resolved ip 
#        ip_client = flow.client_conn.address.host
#        #ports
#        port_server = flow.server_conn.address.port
#        port_client = flow.client_conn.address.port
#
#        #get tcp conversation and mark as decrypted
#        #create conversation summary
#        s={"ip_src":ip_client, "ip_dst":ip_server, "port_src":port_client, "port_dst":port_server}
#        #EVOL only have get_conversation instead of get or create
#        if (current_id_session > 0): #and recording and decrypting 
#            #conv = mono_mitm.set_conversation_as_decrypted(s, current_id_session, db)
#            l.debug("looking for the conversation")
#            l.debug(conv)
#            id_conv = conv["id_conversation"]
#        
#        #step 1 get_or create conv the packet belongs to (type MITM)
#        
#        #step 2 add packet_to_conversation_dic
#        if number > 1
#        #step 3 get_conversation_from_id()a
#        add_packet_to_conversation_dic
#        #update_conv
#
#    if (current_id_session > 0 and id_conv > 0 ):
#        #gather information
#        #create a new mitm entry 
#        lm = flow.messages[-1] #last_message
#        print("mitm received message")
#
#        m= { "from_client": lm.from_client,
#            "packet_length": len(lm.content),
#            "ip_src": ip_client if lm.from_client else ip_server,
#            "ip_dst": ip_server if lm.from_client else ip_client,
#            "port_src": port_client if lm.from_client else port_server,
#            "port_dst": port_server if lm.from_client else port_client,
#            "payload": lm.content, 
#            "selected": 0,
#            "timestamp":lm.timestamp,
#            "sni": flow.server_conn.sni
#                }
#
#        mono_mitm.mitm_into_db(m, current_id_session, id_conv, db)
