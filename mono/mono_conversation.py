#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:57:42 2017

@author: robert
"""
import scapy

from scapy.all import IP, UDP,TCP 
import logging 
from . import mono_tools
from . import mono_packet
from . import mono_constant as mc
from mono import mono_packet_conversation as mono_pc

import sys
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors

convs_start = -1; #global var - start time 

last_A = ""; #A point of last packet (in its own conversation)

last_B = ""; #B point of last packet (in its own conversation)

#To be called on first packet arrival to store reference time 
def start_conversations(packet):
    global convs_start
    if(convs_start < 0):
        logging.getLogger("mono_conversation").info("starting conversations at time %f"%(packet.time,))
        convs_start = packet.time

#stop conversations on session shut down
def stop_conversations():
    global convs_start
    convs_start = -1


#creates the conversation line in the table CONVERSATION_IPV4/UDP/TCP/MITM  according 
#to the packet type (if necessary)
#updates the apropriate conversation line in the table CONVERSATION_IPV4/UDP/TCP/MITM
#creates the aproriate line in the PACKETS_CONVERSATIONS table
def add_packet_to_conversations(id_packet, packet, db, id_session, id_conv = -1, mitm = False):
    l = logging.getLogger("mono_conversation")
    global convs_start
    if packet.haslayer(IP):
        #start conversations if needed (only first packet)
        start_conversations(packet)
        conv = None
        if (mitm):
            if (packet.haslayer(TCP)):
                if id_conv >= 1: 
                    conv = get_conversation_from_id(id_conv, db, mc.MITM_CONVERSATION_TYPE)
                else:
                    conv = get_or_create_conv(packet, db, mc.MITM_CONVERSATION_TYPE, id_session)
                    l.debug("creating conv")
                    l.debug(conv)
                add_packet_to_conversation_dic(conv, packet, db)
                mono_pc.add_packetconversation(id_session, id_packet, conv["id_conversation"], mc.MITM_CONVERSATION_TYPE, db)
                update_conv(conv, mc.MITM_CONVERSATION_TYPE, db)

        else:
            #add packet to ipv4 conv
            conv = get_or_create_conv(packet, db, mc.IPV4_CONVERSATION_TYPE, id_session)
            
            #step 1 : Add packet to conversation 
            #  --> update conv fields with new packet
            #  --> add new link between packet and conv tables in PACKETS_CONVERSATIONS table
            # !!!! Careful, always call add_packetconversation *BEFORE* update_conv !!!!
            add_packet_to_conversation_dic(conv, packet, db)
            mono_pc.add_packetconversation(id_session, id_packet, conv["id_conversation"], mc.IPV4_CONVERSATION_TYPE, db)
            
            #step2: update MySQL database
            update_conv(conv, 0, db)
            #Now conv dictionnary no has  longer an "id_conversation" attribute
            
            if packet.haslayer(UDP):
                conv = get_or_create_conv(packet, db, mc.UDP_CONVERSATION_TYPE, id_session)
                add_packet_to_conversation_dic(conv, packet, db)
                mono_pc.add_packetconversation(id_session, id_packet, conv["id_conversation"], mc.UDP_CONVERSATION_TYPE, db)
                update_conv(conv, mc.UDP_CONVERSATION_TYPE, db)
                
            if (packet.haslayer(TCP)):
                conv = get_or_create_conv(packet, db, mc.TCP_CONVERSATION_TYPE, id_session)
                add_packet_to_conversation_dic(conv, packet, db)
                mono_pc.add_packetconversation(id_session, id_packet, conv["id_conversation"], mc.TCP_CONVERSATION_TYPE, db)
                update_conv(conv, mc.TCP_CONVERSATION_TYPE, db)
        return conv


#same action is performed for any conversation (UDP, TCP,IP)
#Update fields {packets, bytes, duration, ...} of conversations
#Wireshark count bytes at Eth layer, Mono at IP layer
#packet.getlayer(IP).len returns the ip packet size (including header)
#we substract the ihl*4 (Internet Header Length) = header size (in bytes)
#to get the ip_packet payload size
def add_packet_to_conversation_dic(conv, packet, db):
    ip_packet = packet.getlayer(IP)
    if (conv['from_a']):
        conv['packets_a_b'] += 1
        conv['bytes_a_b'] += ip_packet.len - ip_packet.ihl * 4
    else:
        conv['packets_b_a'] += 1
        conv['bytes_b_a'] +=  ip_packet.len - ip_packet.ihl * 4
    conv["bytes"] +=  ip_packet.len - ip_packet.ihl * 4
    conv["packets"] += 1
    #duration = p.time -first_packet.time
    #first_packet.time = rel_start + convs_start
    conv["duration"] = float(packet.time - conv['rel_start'] - convs_start)


#conv_type = 0 for IPV4, 1 for UDP, 2 for TCP
#updates the conversation in the db
def update_conv(conv, conv_type, db):
    names = get_table_name_and_id_key(conv_type)
    id_name = names["id_name"]
    table_name = names["table_name"]
    id_value = int(conv["id_conversation"])#use generic id
    #the following keys might be in the conv dictionnary, but are not a valid
    #column name in the datatabse. So we mark them as forbidden keys
    f = ("id_conversation", id_name, "from_a", "already_exists")
    mono_tools.generic_update(table_name, conv, db, id_name, id_value, forbidden_keys = f)



#auxiliary function 
#s is the packet_summary 
#conv_type = 0 for IPV4, 1 for UDP, 2 for TCP
#s must have the following fields: s["ip_src"] s["ip_dst"] 
#and optionally s["port_src"] s["port_dst"]
def get_or_create_conv_no_packet(s, rel_start, conv_type, id_session, db):
    l = logging.getLogger("mono_conversation")
    if (s["ip_src"] == s["ip_dst"]):
        l.error("impossible to add packet with same ip_src and ip_dst to a conversation")
        return {}
    names = get_table_name_and_id_key(conv_type)
    id_key = names["id_name"];
    table_name = names["table_name"];
    tcp_or_udp = (conv_type > 0)
    cursor = db.cursor(cursors.DictCursor)
    already_exists = 0
    #default conversation
    cv = {"from_a":1, "id_session":id_session, "ip_a":s["ip_src"],"ip_b":s["ip_dst"], "bytes":0, 
          "rel_start":rel_start,
          "duration":0, "packets":0, "packets_a_b":0, "packets_b_a":0, "bytes_a_b":0, "bytes_b_a":0} 
    cv[id_key] = -1
    cv["id_conversation"] = -1
    if (tcp_or_udp):
        cv.update({"port_a":s["port_src"], "port_b":s["port_dst"]})
    try:
        #1 check if conv already exist cursor.row_count 
        sql = "SELECT *, IF(ip_a=%s AND ip_b=%s, True, False) as from_a  from " ##### Test this line
        sql += table_name 
        sql += " WHERE  id_session=%s AND ((ip_a=%s AND ip_b=%s ) "
        params = (s["ip_src"], s["ip_dst"], id_session, s["ip_src"], s["ip_dst"])
        if (tcp_or_udp):
            sql = sql[:-2]
            sql += " AND port_a = %s AND port_b = %s) "
            params += ( s["port_src"], s["port_dst"])
        sql += " OR (ip_a=%s AND ip_b=%s )) "
        params += (s["ip_dst"], s["ip_src"])
        if (tcp_or_udp):
            sql = sql[:-3]
            sql += " AND port_a = %s AND port_b = %s)) "
            params += (s["port_dst"], s["port_src"])
        # where clause should look like
        #" WHERE  id_session=%s AND ((ip_a=%s AND ip_b=%s) OR (ip_a=%s AND ip_b=%s)) "
        #try:
        cursor.execute(sql, params) #safe sql querry
#        except Exception as e:
#            print(params)
#            raise
        if (cursor.rowcount > 0):
            cv = cursor.fetchone()
            already_exists = 1
            db.commit()
        #2 If conversation does not exist, we create a new one
        else:
            sql = "INSERT INTO "
            sql += table_name
            sql += " (id_session, ip_a, ip_b, bytes, rel_start, duration, packets, packets_a_b, packets_b_a, bytes_a_b, bytes_b_a) "
            if (tcp_or_udp):
                sql = sql[:-2]
                sql += ", port_a, port_b) "
            sql += " VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            if (tcp_or_udp):
                sql = sql[:-2]
                sql += ", %s, %s) "
            params = (id_session, cv["ip_a"], cv["ip_b"], cv["bytes"], cv["rel_start"], cv["duration"],
                      cv["packets"], cv["packets_a_b"], cv["packets_b_a"], cv["bytes_a_b"], cv["bytes_b_a"] )
            if (tcp_or_udp):
                params += (cv["port_a"], cv["port_b"])
            cursor.execute(sql, params) #safe sql querry
            db.commit()

            cv[id_key] = cursor.lastrowid 
        cv["id_conversation"] = cv[id_key]
        cv["already_exists"] = already_exists
        return cv
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        
#packet= a scapy packet
#conv_type = 0 for IPV4, 1 for UDP, 2 for TCP
#convention : point A is the ip_src of the 1st packet captured of the conversation
def get_or_create_conv(packet, db, conv_type, id_session):
    global convs_start
    s = mono_packet.packet_summary(packet)
    return get_or_create_conv_no_packet(s, float(packet.time - convs_start), conv_type, id_session, db)
        

#conv_type: (conversation type) 0 for ipv4, 1 for UDP, 2 for TCP
def get_conversation_from_id(id_conversation, db, conv_type):
    cursor = db.cursor(cursors.DictCursor)
    #get table_name and id_key from conversation type
    names = get_table_name_and_id_key(conv_type)
    sql = "SELECT *  from " + names["table_name"] + " WHERE " + names["id_name"] + " = %s"
    try:
        cursor.execute(sql, (id_conversation,))
        db.commit()
        conv = cursor.fetchone()
        conv["id_conversation"] = conv[names["id_name"]]
        return conv
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)

def remove_conversation(id_conversation, db, conv_type):
    l = logging.getLogger("mono_conversation")
    l.debug("removing conversation %d"%(id_conversation,))
    names = get_table_name_and_id_key(conv_type) 
    #names var does not come from user input so, the query is safe
    cursor = db.cursor()
    try:
        sql = "DELETE FROM " + names["table_name"] + " WHERE " + names["id_name"] + " = %s"
        cursor.execute(sql, (int(id_conversation),))
        db.commit()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)

def remove_conversations(id_session, db, conv_type):
    l = logging.getLogger("mono_conversation")
    l.debug("removing ALL conversation from session %d"%(id_session,))
    names = get_table_name_and_id_key(conv_type)
    cursor = db.cursor()
    try:
        sql = "DELETE FROM " + names["table_name"] + " WHERE id_session = %s"
        cursor.execute(sql, (id_session, ))
        db.commit()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)

def get_conversations(id_session, db, conv_type):
    names = get_table_name_and_id_key(conv_type)
    cursor = db.cursor(cursors.DictCursor)
    try:
        sql = "SELECT * FROM " + names["table_name"] + " WHERE id_session = %s"
        cursor.execute(sql, (id_session, ))
        db.commit()
        return cursor.fetchall()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)

def get_conversations_ipv4(id_session, db):
    return get_conversations(id_session, db, mc.IPV4_CONVERSATION_TYPE)

def get_conversations_udp(id_session, db):
    return get_conversations(id_session, db, mc.UDP_CONVERSATION_TYPE)

def get_conversations_tcp(id_session, db):
    return get_conversations(id_session, db, mc.TCP_CONVERSATION_TYPE)

def get_conversations_mitm(id_session, db):
    return get_conversations(id_session, db, mc.MITM_CONVERSATION_TYPE)


#returns an dictionnary containint the table name and id_key
#according to the given conversation type
def get_table_name_and_id_key(conv_type):
    table_name = 'CONVERSATIONS_IPV4'
    id_name = "id_conversation_ipv4"
    if conv_type == mc.UDP_CONVERSATION_TYPE:
        table_name = 'CONVERSATIONS_UDP'
        id_name = "id_conversation_udp"
    if conv_type == mc.TCP_CONVERSATION_TYPE:
        table_name = 'CONVERSATIONS_TCP'
        id_name = "id_conversation_tcp"
    if conv_type == mc.MITM_CONVERSATION_TYPE:
        table_name = 'CONVERSATIONS_MITM'
        id_name = "id_conversation_mitm"
    return {"table_name":table_name, "id_name":id_name}

#works to select and unselect a conversation
#the conversation type is 0:IPV4  1:UDP 2:TCP
#check is True to select and False to Unselect
def select_conversation(id_conversation, conv_type, check, db):
    names = get_table_name_and_id_key(conv_type)
    try:
        sql = "UPDATE " + names["table_name"] + " SET selected = %s  WHERE " + names["id_name"] + " = %s"
        params = (check, id_conversation) 
        cursor = db.cursor()
        cursor.execute(sql, params) #safe sql querry
        db.commit()
        return 0;
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        return -1;

def set_selected_all_conversation_of_type(id_session, conv_type, check, db):
    names = get_table_name_and_id_key(conv_type)
    try:
        sql = "UPDATE " + names["table_name"] + " SET selected = %s  WHERE id_session = %s"
        params = (check, id_session) 
        cursor = db.cursor()
        cursor.execute(sql, params) #safe sql querry
        db.commit()
        return 0;
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        return -1;

def is_conversation_selected(id_conversation, conv_type, db):
    names = get_table_name_and_id_key(conv_type)
    try:
        sql = "SELECT * FROM " + names["table_name"] + " WHERE " + names["id_name"] + " = %s"
        dataCursor = db.cursor(cursors.DictCursor)
        dataCursor.execute(sql, (id_conversation,))
        result = dataCursor.fetchone()
        if result:
            return result["selected"]
    except Exception as e :
        mono_tools.handle_db_exception(e, db, dataCursor)

#Never used
#Never tested
#def conversations_to_pcap(id_session, conv_type, fileName, db):
#    convs = get_conversations(id_session, db, conv_type)
#    #Get a list of selected conversations in session of the given conv_type
#    id_convs = []
#    names = get_table_name_and_id_key(conv_type)
#    for conv in convs: 
#        if (conv["selected"]):
#            id_convs.append(conv[names["id_name"]])
#
#    #BAD method.
#    #TODO improve this:for instance with a table packets_conversations
#    # Get all packets in session
#    packets = mono_packet.get_packets_summary(100000000, id_session, 1, db)
#    #test if each packet belongs to a selected conversation
#    for p in packets:
#        binary_packet = mono_packet.scapy_packet_from_db(p["id_packet"], db)
#        conv = get_or_create_conv(binary_packet, db, conv_type, id_session)
#        if ( conv["id_conversation"] in id_convs):
#            scapy.utils.wrpcap(fileName, binary_packet, append=True)

#Never used
#Never tested
#Write all the selected packet of a conversation to pcap
def conversation_to_pcap(id_sess, conv_type, id_conversation, fileName, db):
    packets = mono_packet.get_packets_summary(100000000, id_sess, 1, db)
    #test if each packet belongs to a selected conversation
    for p in packets:
        if (p["selected"]):
            binary_packet = mono_packet.scapy_packet_from_db(p["id_packet"], db)
            conv = get_or_create_conv(binary_packet, db, conv_type, id_sess)
            if ( conv["id_conversation"] == id_conversation):
                scapy.utils.wrpcap(fileName, binary_packet, append=True)

#write all packets of all the conversation of the given type.
#if avoid_dupplicates is True, then packets having select = True, won't be written to the file.
#packet_id_list is a list of id of packets already written to the pcap file, that the function will not duplicate 
#(if avoid_duplicate if True).
#We do this, because a packet might belong to many conversations at the same time
def conversations_to_pcap(id_session, conv_type, fileName, db, avoid_duplicates = True, packet_id_list = (),):
    l = logging.getLogger("mono_conversation")
    l.debug("conversations_to_pcap")
    #get all the packets of the selected conversation of the given type in the given session
    names = get_table_name_and_id_key(conv_type)#id_name and table_name
    sql = "SELECT pc.id_packet as id_packet, p.selected as selected FROM PACKETS_CONVERSATIONS pc\
    INNER JOIN PACKETS p ON pc.id_packet = p.id_packet\
    INNER JOIN " + names["table_name"]+ " c ON c." + names["id_name"] + " = pc.id_conversation \
    WHERE pc.id_session = %s AND pc.conversation_type=%s AND c.selected = 1"
    if avoid_duplicates:
        sql += " AND p.selected=0"
    id_list = []
    try:
        cursor = db.cursor(cursors.DictCursor)
        cursor.execute(sql,(id_session, conv_type))
        results = cursor.fetchall()
        l.debug("fetching results")
        for r in results:
            l.debug("evaluating packet %s"%(r["id_packet"]))
            l.debug(r)
            if avoid_duplicates and r["id_packet"] in packet_id_list:
                continue
            else:
                id_list.append(r["id_packet"])
                l.debug("inserting packet %s in .pcap"%(r["id_packet"],))
                packet = mono_packet.scapy_packet_from_db(r["id_packet"], db)
                scapy.utils.wrpcap(fileName, packet, append=True)  #appends packet to output file
                l.debug("add packet %s to file "%(r["id_packet"]))
        if hasattr(cursor, '_last_executed'):
            l.error(cursor._last_executed)
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
    return id_list
