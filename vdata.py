# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import time 

from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='130.127.198.22:9092')


import socket
import sys

# Create a TCP/IP socket
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
#server_address = ('130.127.198.22', 55555)
#print >>sys.stderr, 'starting up on %s port %s' % server_address
#sock.bind(server_address)

full_data = 0
def ReadDataFromFile(file_name):
    global full_data
    df = pd.read_csv(file_name)
    full_data = df
    X = np.array(df)
    return X

def LoadPartialData(time):
    global full_data
    ldata = full_data[full_data['time']>= time]
    pdata = ldata[ldata['time']<(time+0.1)]
    return pdata

def main():
    ReadDataFromFile('vehicleGeoData.csv')
    #print(X)
    end_time = 200  
    steps = 0.0
    count = 0 
    #global sock
    #sock.listen(1)
    #connection, client_address = sock.accept()
      
    while(steps <= end_time):    
        #print ( 'step  : ', steps , 'time : ' , int(time.time()*1000))
        pd = LoadPartialData(steps)        
        for index,row in pd.iterrows():
            data = "{\"carid\":"+ str(row['id']) +",\"seq\":" + str(count) + ",\"timestamp\":\"" + str(int(time.time()*1000)) + "\",\"longitude\":"+ str(row['x'])+",\"latitude\":"+ str(row['y'])+",\"speed\":" + str(row['speed']) + "}"
            if row['id'] < 5:
		print (data)           
            #print (row['time'] , row['id'] , row['x'] , row['y'])
            #print ('time : ' , int(time.time()*1000))
            #connection.sendall(data)
            if row['id'] < 5:
	    	producer.send('TextLinesTopic',data)
	time.sleep(0.1)
	count = count + 1 
	steps = steps + 0.1 
main()
