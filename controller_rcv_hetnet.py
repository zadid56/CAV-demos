#!/usr/bin/env python

import socket
import os

TCP_IP = '192.168.1.2'
TCP_PORT = 8899
BUFFER_SIZE = 8192	# Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

ho_flag = 0

while (1):
	conn, addr = s.accept()
	#print 'Connection address:', addr
	data = conn.recv(BUFFER_SIZE)
	if not data: break
	print "received data:", data
	values=[]
	for t in data.replace(',',' ').replace('}',' ').split():
		try:
			values.append(float(t))
		except ValueError:
			pass
	
	if(values[3]==1 and ho_flag==0):
		os.system("sudo pkill -f controller_send.py")
		os.system("python controller_send_wlan.py")
		ho_flag = 1