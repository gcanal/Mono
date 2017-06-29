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

-A static IP server with root access
-An OpenVPN client installed on the device to monitor
-An OpenVPN server installed on your server

#Installation

## Configure the database
```bash
sudo service mysql start
mysql -u root -p 
Enter password: 
mysql> CREATE DATABASE mono;
mysql> Use mono
mysql> source mono.sql;
```

## Configure the OpenVPN tunnel


