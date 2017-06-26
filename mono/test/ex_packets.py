#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 09:04:48 2017

@author: robert
"""
from scapy.all import IP, sendrecv, ICMP, utils, STP, TCP, UDP
from scapy.all import Ether, Dot3, Dot1Q, ARP, IPv6
from scapy.all import *
#for scapy http see https://github.com/invernizzi/scapy-http
import mono
import MySQLdb
import threading
import sys
import socket #for getservbyport 

try:
    # This import works from the project directory
    import scapy_http.http
except ImportError:
    # If you installed this package via pip, you just need to execute this
    from scapy.layers import http

#require scapy-http-1.8
proto_to_name = {num:name[8:] for name,num in vars(socket).items() if name.startswith("IPPROTO")}

def callback(packet):
    #retrieve packets info
    print "###### Packet received #######"
    ip_src = 'no ip'; ip_dst='no_ip' 
    port_src = 0; port_dst =0;
    l4_proto_number = 0;
    l4_proto = "?";
    packet_length = 1
    l5_proto = "?";
    is_tcp = False ; is_udp = False;

    if packet.haslayer(IP):
        ip_src = packet.getlayer(IP).src
        ip_dst = packet.getlayer(IP).dst
        l4_proto_number = packet.getlayer(IP).proto
        l4_proto = proto_to_name[l4_proto_number] #surely always work
        packet_length = packet.getlayer(IP).len
    #if packet.hasLayer(ICMP):
     #   l4_proto = 'ICMP'
    if packet.haslayer(TCP):
        port_src = packet[TCP].sport
        port_dst = packet[TCP].dport
        is_tcp = True
    if packet.haslayer(UDP):
        port_src = packet[UDP].sport
        port_dst = packet[UDP].dport
        is_udp = True;
    if (is_tcp or is_udp):
        try: 
            l5_proto = socket.getservbyport(min(port_src,port_dst),'udp' if is_udp else 'tcp')
        except Exception as e:
            print "Could not retrieve proto name (maybe port number > 1024)"
            print str(e)
    ### look for higher layer protocols
        #l4_proto = 'UDP'
#    if packet.haslayer('HTTP'):
#        l5_proto = '######################"HTTP'
#    if packet.haslayer(DNS):
#        l5_proto = 'DNS'

    print "ip_src=%s ip_dst=%s "% ( ip_src ,ip_dst)
    print "l4_proto=%s(%s) l5_proto=%s"%  (l4_proto,l4_proto_number, l5_proto)
    print "port_src=%s  port_dst=%s "%  (port_src, port_dst)
    print "packet_length=%s "%  packet_length


#print "ls (TCP)";
#ls(TCP)
#print "ls (UDP)";
#ls(UDP)

print "ls (DNS)";
ls(DNS)
print "start sniffing"
sendrecv.sniff(iface="wlan0", prn=callback, store=0, count=0) #filter="tcp"
