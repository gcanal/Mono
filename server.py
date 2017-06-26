from flask import Flask, send_file, send_from_directory, jsonify
from flask import request, make_response, Response

app = Flask(__name__, static_url_path='/static')

from mono import mono_session
import mono.mono_config as mc
import mono.mono_packet as mono_packet
import mono.mono_datatable as md
import mono.mono_conversation as m_conv
import mono.mono_param as m_param
import mono.mono_constant as m_constant
from mono import mono_mitm

import logging
import signal
import sys
if sys.version_info > (3, 3):
    from pymysql import connect
else:
    from MySQLdb import connect

import json 

#from scapy.all import utils, TCP
#from scapy.all import IP,sendrecv, ICMP,  STP, Ether, Dot3, Dot1Q, ARP, IPv6, 

#context.use_privatekey_file('/etc/ssl/private/ssl-cert-snakeoil.key')
#context.use_certificate_file('/etc/ssl/certs/ssl-cert-snakeoil.pem')

#this db connector should be kept active while the program is running
always_on_db = connect(mc.db_host, mc.db_user_name, mc.db_password, mc.db_db_name)#host, user, password, db


#print("now showing results")
#print(m_param.get_decrypting(always_on_db))
#print(m_param.get_recording(always_on_db))
#print(m_param.get_id_session(always_on_db))
#import sys
#sys.exit(0)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/html/<path:path>')
def send_html(path):
    return send_from_directory('html', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/app.js")
def appjs():
    return send_file("app.js")

@app.route("/awebservice", methods=['GET','POST'])
def awebservice():
    l = logging.getLogger("server")
    try:
        method = request.json['method']
        params = request.json['params']
        #print (request)
        db2 = connect(mc.db_host, mc.db_user_name, mc.db_password, mc.db_db_name)
        if (method == 'get_sessions'):
            l.info('get_sessions')
            return jsonify(sessions=mono_session.get_sessions(db2))
        elif (method == 'get_ifaces'):
            l.info('get ifaces')
            return jsonify(ifaces=mono_session.get_ifaces())
        elif (method == 'get_session'):
            l.info('get_session')
        elif (method == 'add_session'):
            l.info('add_session')
            mono_session.add_session(params['session'], db2)
            return jsonify(message="ok")
        elif (method == 'update_session'):
            l.info('update session')
            l.info(params["session"])
            sess = params["session"]
            mono_session.update_session(sess, db2)
            return jsonify(session=mono_session.get_session(sess["id_session"],db2))
        elif (method == 'start_session'):
            l.info('start_session')
            id_sess = params["id_session"]
            #launch session if possible
            res = mono_session.run_session(id_sess, always_on_db)
            return jsonify(success=res)
        elif (method == 'stop_session'):
            l.info('stop_session set run order to false')
            mono_session.stop_session(db2)
            l.info('stop_mitm as well')
            mono_mitm.stop_mitm()
            return jsonify(success=True)
        elif (method == 'is_session_active'):
            l.info('is_session_active')
            id_sess = params["id_session"]
            curr_sess = mono_session.get_current_session_id()
            res = (id_sess == curr_sess)
            l.info("is_session_active " + str(id_sess)+"  (current session is " + str(curr_sess) + ") "+ str(res))
            return jsonify(result=res)
        
        elif (method == 'is_any_session_active'):
            res = mono_session.is_session_active()
            res2 = mono_mitm.is_mitm_active()
            l.info('is_any_session_active ? session_active=' + str(res) + " mitm_active=" + str(res2) + " \
            (id_active_session = " + str(mono_session.get_current_session_id()) + ")")
            return jsonify(session_active=res, mitm_active=res2)

        elif (method == 'remove_session'):
            id_sess = params['id_session'];
            l.info('remove_session ' +str(id_sess))
            mono_session.remove_session(id_sess, db2)
            return jsonify(message="ok")
        elif (method == 'get_packets_summary'):
            l.info('get_packets_summary')
            id_sess = params['id_session']
            id_first = params['id_first']
            max_packets = 10 #TODO as global var in db
            return jsonify(packets=mono_session.get_packets_summary(max_packets, id_sess, id_first, db2))
        #mitm
        elif (method == 'start_mitm'):
            l.info('start_mitm')
            mono_mitm.stop_mitm()
            if (mono_session.is_session_active()):
                mono_mitm.start_mitm_thread()
                return jsonify(mitm_active=1)
            else:
                return jsonify(mitm_active=0)
        elif (method == 'stop_mitm'):
            l.info('stop_mitm')
            mono_mitm.stop_mitm()
            return jsonify(mitm_active=0)
        elif (method == 'datatatables_packets'):
            l.info('datatatables_packets')
            table = {"name":"PACKETS", "as": "", "join":[]}
            index_column = "id_packet"
            datatable = md.MonoDatatables(request, index_column, table, db2)
            #add filters
            id_session = params['id_session']
            datatable.add_filter("id_session", id_session, True)
            datatable.add_filter("decrypted", 0, True) #only show undecrypted packets
            if ("select_all" in params and params['select_all']):
                datatable.update_rows({"table_name":"PACKETS", "col_name":"selected", "col_value":1, "id_key":"id_packet"})
            datatable.run_queries()
            results = datatable.output_result()
            # return the results as a string for the datatable
            return json.dumps(results)
        elif (method == 'datatatables_mitm_packets'):
            l.info('datatatables_mitm_packets')
            table = {"name":"PACKETS", "as": "", "join":[]}
            index_column = "id_packet"
            datatable = md.MonoDatatables(request, index_column, table, db2)
            #add filters
            id_session = params['id_session']
            datatable.add_filter("id_session", id_session, True)
            datatable.add_filter("decrypted", 1, True) #only show decrypted packets
            if ("select_all" in params and params['select_all']):
                datatable.update_rows({"table_name":"PACKETS", "col_name":"selected", "col_value":1, "id_key":"id_packet"})
            datatable.run_queries()
            results = datatable.output_result()
            # return the results as a string for the datatable
            return json.dumps(results)
        
        elif (method == 'datatatables_ipv4_conversation'):
            l.info('datatatables_ipv4_conversation')
            table = {"name":"CONVERSATIONS_IPV4", "as": "", "join":[]}
            index_column = "id_conversation_ipv4"
            datatable = md.MonoDatatables(request, index_column, table, db2)
             #add filters
            id_session = params['id_session'];
            datatable.add_filter("id_session", id_session, True)
            if ("select_all" in params and params['select_all']):
                datatable.update_rows({"table_name":"CONVERSATIONS_IPV4", "col_name":"selected", "col_value":1, "id_key":"id_conversation_ipv4"}) # id_conversation_ipv4 must be in the list of the requested columns names sent by the client 
            datatable.run_queries()
            results = datatable.output_result()
            # return the results as a string for the datatable
            return json.dumps(results)
        
        elif (method == 'datatatables_tcp_conversation'):
            l.info('datatatables_tcp_conversation')
            table = {"name":"CONVERSATIONS_TCP", "as": "", "join":[]}
            index_column = "id_conversation_tcp"
            datatable = md.MonoDatatables(request, index_column, table, db2)
             #add filters
            id_session = params['id_session'];
            datatable.add_filter("id_session", id_session, True)
            if ("select_all" in params and params['select_all']):
                datatable.update_rows({"table_name":"CONVERSATIONS_TCP", "col_name":"selected", "col_value":1, "id_key":"id_conversation_tcp"})
            datatable.run_queries()
            results = datatable.output_result()
            # return the results as a string for the datatable
            return json.dumps(results)
        elif (method == 'datatatables_udp_conversation'):
            l.info('datatatables_udp_conversation')
            table = {"name":"CONVERSATIONS_UDP", "as": "", "join":[]}
            index_column = "id_conversation_udp"
            datatable = md.MonoDatatables(request, index_column, table, db2)
             #add filters
            id_session = params['id_session'];
            datatable.add_filter("id_session", id_session, True)
            if ("select_all" in params and params['select_all']):
                datatable.update_rows({"table_name":"CONVERSATIONS_UDP", "col_name":"selected", "col_value":1, "id_key":"id_conversation_udp"})
            datatable.run_queries()
            results = datatable.output_result()
            # return the results as a string for the datatable
            return json.dumps(results)
        elif (method == 'datatatables_mitm_conversation'):
            l.info('datatatables_mitm_conversation')
            table = {"name":"CONVERSATIONS_MITM", "as": "", "join":[]}
            index_column = "id_conversation_mitm"
            datatable = md.MonoDatatables(request, index_column, table, db2)
             #add filters
            id_session = params['id_session'];
            datatable.add_filter("id_session", id_session, True)
            if ("select_all" in params and params['select_all']):
                datatable.update_rows({"table_name":"CONVERSATIONS_MITM", "col_name":"selected", "col_value":1, "id_key":"id_conversation_mitm"})
            datatable.run_queries()
            results = datatable.output_result()
            # return the results as a string for the datatable
            return json.dumps(results)

        elif (method == 'datatatables_applis_conversation'):
            l.info('datatatables_applis_conversation')
            return json.dumps(success = "nothing here dear" )

        elif (method == 'datatatables_sublist' or method == 'datatatables_sublist_mitm'):
            if (method == 'datatatables_sublist'):
                l.info('datatatables_sublist')
            else:
                l.info('datatatables_sublist_mitm')
            index_column = "id_pc" #don't prefix index column 
            on = "p.id_packet = pc.id_packet"
            #here addFilter 
            table = {"name":"PACKETS_CONVERSATIONS", "as": "pc", "join":[{"name":"PACKETS", "as":"p", "on":on}]}
            datatable = md.MonoDatatables(request, index_column, table, db2)
            id_conv = params['id_conversation'];
            datatable.add_filter("pc.id_conversation", id_conv, True)

            conversation_type = params['conversation_type'];
            datatable.add_filter("pc.conversation_type", conversation_type, True)
            if ("select_all" in params and params['select_all']):
                datatable.update_rows({"table_name":"PACKETS", "col_name":"selected", "col_value":1, "id_key":"id_packet"})
            datatable.run_queries()
            results = datatable.output_result()
            # return the results as a string for the datatable
            return json.dumps(results)

        
        elif (method == 'select_packet'):
            l.info('select_packet')
            id_packet = params['id_packet']
            check = params['check'];
            mono_packet.select_packet(id_packet, check, db2);
            return jsonify(checked=mono_packet.is_packet_selected(id_packet, db2))
        elif (method == 'select_conversation'):
            l.info('select_conversation')
            id_conversation = params['id_conversation']
            conv_type = params['conversation_type']
            check = params['check'];
            m_conv.select_conversation(id_conversation, conv_type, check, db2);
            return jsonify(checked=m_conv.is_conversation_selected(id_conversation, conv_type, db2))
        elif (method == 'unselect_all'):
            l.info('unselect_all')
            id_session = params['id_session']
            mono_session.unselect_all(id_session, db2) 
            return jsonify(success=1)

         #Deprecated to select all packets, we use the mono_datatable api
        elif (method == 'select_all_packets_in_session'):
            l.info('select_all_packets_in_session')
            id_session = params['id_session']
            check = params['check'];
            mono_packet.set_selected_all_packets_in_session(id_session, check, db2)
            are_checked = mono_packet.are_packets_selected_in_session(id_session, db2);
            return jsonify(checked=are_checked)
        
        elif (method == 'get_packet_details'):
            l.info('get_packet_details')
            id_packet = params['id_packet']
            details = mono_packet.get_packet_details(id_packet, db2)
            return jsonify(packet_details=details)
        else:
            l.error("Method %s unknown"%method)
            l.error(params)
        #return jsonify(companies=companies)
        db2.close()
    except Exception as e:
        print(str(e))
        raise 
        return jsonify(status='ERROR', message=str(e))

@app.route('/download', methods=['POST', 'GET'])
def download():
    l = logging.getLogger("server")
    id_sess = int(request.args.get('id_session'))
    #conversation_type = int(request.args.get('conversation_type'))
    #id_conversation = int(request.args.get('id_conversation'))
    l.info("now creating pcap for session %s"%id_sess)
    fileName = 'pcap.pcap' #TODO as global variable 
    #EMPTY FILE
    try:
        l.debug("EMPTY FILE")
        open(fileName, 'w').close()
    except Exception as e:
        logging.error("In dowload method, could not empty file")
        logging.error(str(e))
    #WRITE FILE
    try:
        l.debug("WRITE FILE")
        db2 = connect(mc.db_host,mc.db_user_name, mc.db_password,mc.db_db_name)
        mono_session.session_to_pcap(id_sess, fileName, db2)
        db2.close();
    except Exception as e:
        l.error("In dowload method, could not write file")
        l.error(str(e))
        raise
    try:
#        pcap = "";
#        with open("robert.pcap") as fp:
#        pcap = fp.read()
#        return Response(pcap,
#        mimetype="application/vnd.tcpdump.pcap",
#        headers={"Content-disposition":
#                 "attachment; filename="+fileName})
        return send_file(fileName, attachment_filename='session'+str(id_sess)+'.pcap', as_attachment=True)
    except Exception as e:
        l.error(str(e))
        raise

#TODO find a nicer to call this function only once
exit_fn_called = False
#reset all params when exiting
def exit_function(signum, frame):
    global exit_fn_called
    if exit_fn_called :
        return
    exit_fn_called = True
    l = logging.getLogger("server")
    signame = "SIGTERM"
    if signum == signal.SIGINT: 
        signame = "SIGINT"
    if signum == signal.SIGQUIT: 
        signame = "SIGQUIT"
    l.info("%s CAUGHT"%(signame,))
    m_param.set_decrypting(0, always_on_db)
    m_param.set_recording(0, always_on_db)
    m_param.set_id_session(0, always_on_db)
    mono_mitm.stop_mitm()
    always_on_db.close()
    sys.exit(0)#TODO find a better way to quit
    #https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used
    #See here where sigterm handler is called multiple times
    #https://stackoverflow.com/questions/17705062/sigterm-handler-called-multiple-times
    #maybe catch the SystemExit Exception and let it propagate

#def shutdown_server():
#    func = request.environ.get('werkzeug.server.shutdown')
#    if func is None:
#        raise RuntimeError('Not running with the Werkzeug Server')
#    func()

#if the file is called as a standalone script, we run the server
if __name__ == "__main__":
    #logging setup
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(' %(levelname)-8s %(name)-12s %(message)s')#%(asctime)s
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #global logging level
    logger.setLevel(logging.DEBUG)
    #datatable log level (noisy when set to debug)
    logging.getLogger("mono_datatable").setLevel(logging.WARNING)
    #callbacks log levels (very noisy when set to debug)
    logging.getLogger("mono_packet.callback").setLevel(logging.WARNING)
    logging.getLogger("mono_session.callback").setLevel(logging.WARNING)
    logging.getLogger("mono_mitm.callback").setLevel(logging.INFO)
    #speficic log levels
#    logging.getLogger("mono_param").setLevel(logging.INFO)
#    logging.getLogger("mono_packet").setLevel(logging.INFO)
#    logging.getLogger("mono_mitm").setLevel(logging.INFO)
#    logging.getLogger("mono_tools").setLevel(logging.INFO)
#    logging.getLogger("mono_conversation").setLevel(logging.INFO)
#    logging.getLogger("mono_packet_conversation").setLevel(logging.INFO)
#    logging.getLogger("mono_session").setLevel(logging.INFO)
    #logging level for dependencies
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("watchdog").setLevel(logging.ERROR)
    context = None
    #default settings
    m_param.set_decrypting(0, always_on_db)
    m_param.set_recording(0, always_on_db)
    m_param.set_id_session(0, always_on_db)
    signal.signal(signal.SIGTERM, exit_function )
    signal.signal(signal.SIGINT, exit_function )
    signal.signal(signal.SIGQUIT, exit_function )
    if mc.use_tls:
        context = (mc.certificate, mc.key)

    app.run(host='0.0.0.0', port=mc.server_port, debug = mc.flask_debug, ssl_context=context)
    ### TODO try catch SIGTERM + close always on db connector 
#@application.route('/')
#def showMachineList():
#    return render_template('index.html')