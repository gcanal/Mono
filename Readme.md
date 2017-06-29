# Presentation
Mono is a VPN-based monitoring system, designed to (passively and actively) capture traffic from mobile device. It is composed of three elements: 
- an OpenVPN client installed on the mobile device (OpenVPN Connect/OpenVPN for Android)
- an OpenVPN server with a public IP address that can capture, decrypt (under certain conditions)
and store packets. It also runs a web server
- a web interface to examine in real-time the traffic of the VPN tunnel.
![Mono Architecture](https://github.com/gcanal/Mono/blob/master/imgs/use_case_3.png)


The code in this repository implements the monitoring server. It is coded in Python 3 with: 
- Flask + MySQL + Scapy3k + mitmproxy on the server side 
- Angular JS on the client side 


See the presentation video at: https://www.youtube.com/watch?v=pdM-xI4LYjI&feature=youtu.be

# Requirements

- A static IP server with root access
- An OpenVPN client installed on the device to monitor
- An OpenVPN server installed on your server

## Basic configuration of an OpenVPN server
Install OpenVPN and generate keys and certificates
```bash
apt install openvpn
cp -a /usr/share/easy-rsa /etc/openvpn/
cd /etc/openvpn/easy-rsa
source vars
./clean-all
./build-ca #generate certificate in keys cat.crt ca.key
./build-dh #generate diffie hellman keys #this is going to take a long time
./build-key-server srvcert #generate server certificates
```
Copy default configuration file 
```bash
gunzip -c /usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz > /etc/openvpn/server.conf
```
fill in  ca, cert and dh (diffie-hellman keys) fields
```bash
ca /etc/openvpn/easy-rsa/2.0/keys/ca.crt #Certificate of authority of the server -> Will authentify the client
cert /etc/openvpn/easy-rsa/2.0/keys/srvcert.crt # server's certificate
key  /etc/openvpn/easy-rsa/2.0/keys/srvcert.key # server's private key -> This file should be kept secret
dh /etc/openvpn/easy-rsa/2.0/keys/dh1024.pem # Diffie Hellamn parameters (used to encrypt the session, RSA keypair is used for authentication. 
```
Use a Push option to change the client's DNS server
```bash
push "dhcp-option DNS 213.186.33.99" 
```
Default port and protocol are: 
```bash
1194/udp
```
# Installation

## Configure the database
```bash
sudo service mysql start
mysql -u root -p 
Enter password: 
mysql> CREATE DATABASE mono;
mysql> Use mono
mysql> source mono.sql;
```
## Edit the settings
```bash
cd mono
cp mono_config_skeleton.py mono_config.py
vim mono_config.py
#Fill in the settings
```

## Install Python 3 dependencies



