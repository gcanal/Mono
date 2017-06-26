import scapy
from scapy.all import IP, UDP,TCP, ICMP, Raw # for export/import_object
import socket
import importlib
import sys
import logging
if sys.version_info > (3, 3):
    from pymysql import cursors
else:
    from MySQLdb import cursors

from . import mono_tools 


proto_to_name = {num:name[8:] for name,num in vars(socket).items() if name.startswith("IPPROTO")}

def packet_summary(packet):
    ip_src = 'no ip'; ip_dst='no_ip'
    port_src = 0; port_dst =0;
    l4_proto_number = 0;l4_proto = "?";l5_proto = "?";
    packet_length = 1
    is_tcp = False ; is_udp = False;
    transport_string = "TCP"
    if packet.haslayer(IP):
        ip_src = packet.getlayer(IP).src
        ip_dst = packet.getlayer(IP).dst
        l4_proto_number = packet.getlayer(IP).proto
        l4_proto = proto_to_name[l4_proto_number] #surely always work
        packet_length = packet.getlayer(IP).len
    if packet.haslayer(TCP):
        port_src = packet[TCP].sport
        port_dst = packet[TCP].dport
        is_tcp = True
    if packet.haslayer(UDP):
        port_src = packet[UDP].sport
        port_dst = packet[UDP].dport
        transport_string = "UDP"
        is_udp = True;
    if (is_tcp or is_udp):
        try: 
            port_number = min(port_src, port_dst)
            l5_proto = socket.getservbyport(port_number,'udp' if is_udp else 'tcp')
        except Exception as e:
            l = logging.getLogger("mono_packet")
            l.warn("Could not retrieve proto name for port %s %s (maybe port is not registered or > 1024)"%(port_number,transport_string))
    return {"ip_src":ip_src, "ip_dst":ip_dst, "port_src":port_src, "port_dst":port_dst,
            "l4_proto_number":l4_proto_number, "l4_proto":l4_proto,
            "packet_length":packet_length, "l5_proto":l5_proto}


def packet_into_db(packet , id_session, db, domain = "", decrypted=0):
    l = logging.getLogger("mono_packet.callback")
    cursor = db.cursor()
    module_name = packet.__module__
    class_name = packet.__class__.__name__
    time = packet.time
    hexa_packet = bytes(packet)
    #print hexa_packet
    i = packet_summary (packet) #get packet infos
    l.debug("packet into db %15s/%6s -> %15s/%6s %s %s %s"%(i['ip_src'], i['port_src'], i['ip_dst'], i['port_dst'], i['l4_proto'], i['l5_proto'], domain) )
    sql = "INSERT INTO PACKETS (packet, time, class_name, module_name, id_session, \
           ip_src, ip_dst, port_src, port_dst, l4_proto_number, l4_proto, packet_length, l5_proto, domain, decrypted, constructor)\
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        #this query is safe and preserve float precision of time arrival. Oh yeah.
        cursor.execute(sql, (hexa_packet, format(time, '.10f'), class_name, module_name, id_session,
         i['ip_src'],  i['ip_dst'],  i['port_src'],  i['port_dst'],  i['l4_proto_number'],
         i['l4_proto'],  i['packet_length'],  i['l5_proto'], domain, decrypted, packet.command()))
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 
        #return -1;

def get_packet_from_id(id_packet, db):
    sql = "SELECT * FROM PACKETS WHERE id_packet= %s" 
    cursor = db.cursor(cursors.DictCursor)
    try:
        cursor.execute(sql, (int(id_packet),))
        result = cursor.fetchone()
        return result
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise


def get_scapy_packet_from_id(id_packet, db):
    #fetching results
    p = get_packet_from_id(id_packet, db)
    #building packet
    module_ = importlib.import_module(p["module_name"])
    class_ = getattr(module_, p["class_name"])
    packet = class_(p["packet"])
    packet.time = float(p["time"])
    return packet


def scapy_packet_from_db(id_packet, db):
    return get_scapy_packet_from_id(id_packet, db)

#Some helper function for testing
def create_ping_packet(ip_src="192.168.0.33", ip_dst="192.168.0.1"):
    packet = scapy.layers.inet.IP(src=ip_src, dst=ip_dst, ttl=20)/ICMP()
    new_packet = scapy.layers.inet.IP(bytes(packet)) # to populate all fields
    return new_packet

#ip_size is the optional size of the ip_payload. If it is superior to 8 (UPD header size),
#some padding will be added in the packet
def create_udp_packet(ip_dst="192.168.0.2",ip_src="192.168.13.33", port_src=1028, port_dst=80, ip_size = 8 ):
    packet = {};
    if ip_size > 8:
        packet = scapy.layers.inet.IP(dst=ip_dst, src=ip_src, ttl=20)/UDP(sport=port_src, dport=port_dst) / Raw(padding(ip_size - 8))
    else:
        packet = scapy.layers.inet.IP(dst=ip_dst, src=ip_src, ttl=20)/UDP(sport=port_src, dport=port_dst)
    new_packet = scapy.layers.inet.IP(bytes(packet)) # to populate all fields
    return new_packet

#ip_size is the optional size of the ip_payload. If it is superior to 20 (TCP header size),
#some padding will be added in the packet
def create_tcp_packet(ip_dst="192.168.0.2", ip_src="192.168.13.33", port_src=7865, port_dst=8080, ip_size = 20, padding=None):
    packet = {}
    if padding:
         packet = scapy.layers.inet.IP(dst=ip_dst, src=ip_src, ttl=20)/TCP(sport=port_src, dport=port_dst) / Raw(padding)
    elif ip_size > 20:
        packet = scapy.layers.inet.IP(dst=ip_dst, src=ip_src, ttl=20)/TCP(sport=port_src, dport=port_dst) / Raw(padding(ip_size - 20))
    else:
        packet = scapy.layers.inet.IP(dst=ip_dst, src=ip_src, ttl=20)/TCP(sport=port_src, dport=port_dst)
    new_packet = scapy.layers.inet.IP(bytes(packet)) # to populate all fields
    return new_packet

def padding(n_bytes):
    return bytes(bytearray(n_bytes))
#    if n_bytes < 0:
#        n_bytes = 0;
#    a_string = ""
#    for i in range(0, n_bytes):
#        a_string += "x"
#    return bytes(a_string, "utf8")

def select_packet(id_packet, check, db):
    try:
        sql = "UPDATE PACKETS SET selected = %s  WHERE id_packet = %s"
        params = (check, id_packet) 
        cursor = db.cursor()
        cursor.execute(sql, params) #safe sql querry
        db.commit()
        return 0;
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 
        return -1;

def is_packet_selected(id_packet, db):
    try:
        sql = "SELECT * FROM PACKETS WHERE id_packet = %s"
        dataCursor = db.cursor(cursors.DictCursor)
        dataCursor.execute(sql, (id_packet,))
        result = dataCursor.fetchone()
        if result == None:
            l = logging.getLogger("mono_packet")
            l.error("Error Fetching packet with id %d returned None" %id_packet)
            return None
        else:
            #fetching results
            return result["selected"]
    except Exception as e:
        mono_tools.handle_db_exception(e, db, dataCursor)
        raise 

def delete_packet_from_db(id_packet, db):
    l = logging.getLogger("mono_packet")
    l.info("delete packet id_packet=%s"%(id_packet,))
    try:
        sql = "DELETE FROM PACKETS WHERE id_packet = %s"
        cursor = db.cursor()
        cursor.execute(sql, (id_packet,))
        db.commit()
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 

#return true if all packets are selected in the given session
def are_packets_selected_in_session(id_session, db):
    try:
        sql = "SELECT COUNT(*) FROM PACKETS WHERE selected = 0 AND id_session = %s"
        cursor = db.cursor()
        cursor.execute(sql, (id_session,))
        #we return true if the number of unselected packets is 0
        return (cursor.fetchone()[0] == 0)
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 
        
def set_selected_all_packets_in_session(id_session, check, db):
    try:
        sql = "UPDATE PACKETS SET selected = %s  WHERE id_session = %s"
        params = (check, id_session) 
        cursor = db.cursor()
        cursor.execute(sql, params) #safe sql querry
        db.commit()
        return 0;
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 
        return -1;


#tested But see if the L persists at client side 
#in the expression {'id_session': 45L, 'class_name': ....}
def get_packets_summary(max_packets, id_session, id_first, db):
    try:
        cursor = db.cursor()
        sql = "SELECT * FROM PACKETS WHERE id_session = %s AND id_packet >= %s LIMIT %s"
        cursor.execute(sql,(id_session, id_first, max_packets))
        packets =  mono_tools.select_to_objects(cursor)
        for p in packets:
            del p['packet'];
        return packets
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 

def get_packet_details(id_packet, db):
    packet = get_scapy_packet_from_id(id_packet, db)
    return  packet.command()


#ON peut pas laisser ça comme ça.
#TODO nice sql query
#def packets_to_pcap(id_session, fileName, db):
#    packets = get_packets_summary(100000000, id_session, 1, db)
#    l = logging.getLogger("mono_session")
#    l.info("session_to_pcap")
#    id_packets = []
#    for p in packets:
#        if (p['selected']):
#            id_packets.append(p["id_packet"])
#            packet = scapy_packet_from_db(p["id_packet"], db)
#            scapy.utils.wrpcap(fileName, packet, append=True)  #appends packet to output file
#    return id_packets

#save all selected packets in session to .pcap
#returns the list of id saved to .pcap
def packets_to_pcap(id_session, fileName, db):
    id_packets = []
    try:
        cursor = db.cursor(cursors.DictCursor)
        sql = "SELECT id_packet FROM PACKETS WHERE id_session = %s AND selected = 1"
        cursor.execute(sql,(id_session,))
        packets = cursor.fetchall()
        for p in packets:
            id_packets.append(p["id_packet"])
            packet = scapy_packet_from_db(p["id_packet"], db)
            scapy.utils.wrpcap(fileName, packet, append=True)  #appends packet to output file
        return id_packets
    except Exception as e:
        mono_tools.handle_db_exception(e, db, cursor)
        raise 

