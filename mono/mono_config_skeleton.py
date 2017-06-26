#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#Rename mono_config_skeleton.py to mono_config.py
#Database parameters

db_host = "localhost"
db_user_name = "mono"
db_password = "Pasword"
db_db_name = "mono"


#Web server parameters

server_port = 5000
flask_debug = True
use_tls = True
key = '/etc/ssl/private/ssl-cert-snakeoil.key'
certificate = '/etc/ssl/certs/ssl-cert-snakeoil.pem'