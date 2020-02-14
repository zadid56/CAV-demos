#!/usr/bin/env python

import socket

TCP_IP = '192.168.1.2'
TCP_PORT = 8899
BUFFER_SIZE = 8192  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

while (1):
    conn, addr = s.accept()
    #print 'Connection address:', addr
    car_data = conn.recv(BUFFER_SIZE)
    if not car_data: break
    #print "received data:", car_data
    values=[]
    for t in car_data.replace(',',' ').replace('}',' ').split():
        try:
            values.append(float(t))
        except ValueError:
            pass
    
    if(len(values)==6):
        file = open('data.txt','w')
        file.write(car_data)
        file.close()