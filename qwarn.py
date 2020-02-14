# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 15:48:29 2017

@author: mahfi
"""

import threading, logging 
import multiprocessing 
import socket
import sys
import time
import pandas as pd
import numpy as np
import json
# SKLEARN imports
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
# Kafka Imports
from kafka import KafkaProducer
from kafka.client import KafkaClient
from kafka.producer import SimpleProducer
from kafka import KafkaConsumer
from pandas.io.json import json_normalize
from geopy.distance import great_circle


#kafka =  KafkaClient('130.127.198.22:9092')
#producer = SimpleProducer(kafka)

count = 0 
Q_WARN_AVAIL = False
Q_LANE_ID = 0
Q_SPEED = 0 
Q_V_THR = 20
Q_D_THR = 150 
##############################################################################################
 
import socket
import time
from threading import Thread
from SocketServer import ThreadingMixIn

Q_STATUS = 0  # if queue status is 0 then there is no queue #if 1 then there is queue ahead.

class ClientThread(Thread):
    def __init__(self,conn,ip,port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn=conn
        print "[+] New thread started for "+ip+":"+str(port)
 
 
    def run(self):
        while True:
            #data = conn.recv(2048)
            #if not data: break
            #print "received data:", data
            time.sleep(1)            
            self.conn.send(str(Q_STATUS) + '\n')  # echo
 
TCP_IP = '130.127.198.22'
TCP_PORT = 8014
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
 

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
threads = []

###############################################################################################

class QueueWarning(threading.Thread):
    deamon = True
    producer = None
    warn_count = 0 
    Q_laneId = 0 
    Q_carId = 0  
    Q_speed = 0
    def InitProducer(self):
        self.producer = KafkaProducer(bootstrap_servers='130.127.198.22:9092')
        print('Producer Initialized!')
    def InitConsumer(self):
        self.consumer = KafkaConsumer('TextLinesTopic', bootstrap_servers=['130.127.198.22:9092'])
        print('Consumer Initialized!')
    
    def SendWarning(self):
        if(self.producer!=None):            
            data = "{\"eventid\":"+ str('100') +",\"laneid\":" + str(self.Q_laneId) + ",\"timestamp\":\"" + str(int(time.time()*1000)) + "\",\"msg\":"+ str('Queue at lane ' + str(self.Q_laneId) + ' with speed ' + str(self.Q_speed))  +"}"
            self.producer.send("TextLinesTopic",data)
            #warn_count = warn_count  + 1 
    def Q_Warn_DOT(self,df):
        global Q_STATUS
        groups = df.groupby(['carid'])
        v = np.array([])
        cid = np.array([])
        clat = np.array([])
        clong = np.array([])
        cdist = np.array([])
        dist = np.array([])
        print(df)
        for carId,group in groups:
            self.Q_speed = group['speed'].mean()*2.23694
            v = np.append(v,self.Q_speed)
            self.Q_carId  = carId
            cid = np.append(cid,self.Q_carId)
            self.Q_lat = group['latitude'].mean()
            clat = np.append(clat,self.Q_lat)
            self.Q_long = group['longitude'].mean()
            clong = np.append(clong,self.Q_long)
        
        n = v.size
        if(n<2):
            Q_STATUS = 0
            print('Number of cars ahead less than 2, Queue warning not applicable')
        else:
            for i in range(0, n):
                for j in range(0,n):
                    if(i!=j):
                        temp1 = (clat[i],clong[i])
                        temp2 = (clat[j],clong[j])
                        cdist = np.append(cdist,great_circle(temp1, temp2).meters)
                dist = np.append(dist,np.amin(cdist))
            print(dist)
            for i in range(0,n):
                if(v[i] <= Q_V_THR and dist[i] <= Q_D_THR and cid[i] != 4.0): 
                    #self.SendWarning()
                    Q_STATUS = 1 
                    print('Queue Ahead. Car: ' + str(cid[i]) + ' is in Queue')
                else:
                    Q_STATUS = 0
                
    def Q_Warn_DBSCAN(self,df):
        groups = df.groupby(['carid']).mean()
        X_ = np.array(groups.as_matrix())
        X = StandardScaler().fit_transform(X_)
        db = DBSCAN(eps=1, min_samples=1).fit(X)
        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        print('Estimated number of clusters: %d' % n_clusters_)
        unique_labels = set(labels)
        y_pred = db.labels_.astype(np.int)
        unique_ypred , counts = np.unique(y_pred,return_counts=True)
        print ('Number of vehicles in clusters : ' , counts)
    
    def run(self):
        #self.InitProducer()
        self.InitConsumer()        
        consumer = KafkaConsumer('TextLinesTopic', bootstrap_servers=['130.127.198.22:9092'])
        time_now = time.time()
        time_prev = time_now
        timeout = 1 
        df = pd.DataFrame([])
        while True: 
            print ('Here While')
            try:
                for message in consumer:
                        # print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                        #                                       message.offset, message.key,
                        #                                      message.value))
                        #print(message.value)  
                        ldata = json.loads(message.value)
                        #ldata = json.loads(message.value)
                        pdf = pd.DataFrame(ldata,index=[0])
                        #print (pdf)
                        
                        frames = [df,pdf]
                        df = pd.concat(frames)                    
                        #pdf = pd.DataFrame(ldata,index=[0])
                        #df.append(pdf)                    
                        #print df
                        #data_list.append(json.loads(message.value))
                        #connection.sendall(message.value + str('\n'))
   
                    
                        time_now = time.time()
                        if(time_now>= time_prev+ timeout):
                            print ('-------------------------------------')
                            #result_df = df
                            self.Q_Warn_DOT(df)
                            #self.Q_Warn_DBSCAN(df)                            
                            df = pd.DataFrame([])                    
                            time_prev = time_now
            except Exception as e:
                print ('Connection problem : ' + str(e))
            
def main():
    tasks = [QueueWarning()]
    for t in tasks:
        t.start()
    
    #while True:
    #    time.sleep(100)
    
    while True:
        tcpsock.listen(4)
        print "Waiting for incoming connections..."
        (conn, (ip,port)) = tcpsock.accept()
        newthread = ClientThread(conn,ip,port)
        newthread.start()
        threads.append(newthread)
     
    for t in threads:
        t.join()
    
if __name__ == '__main__':
    main()
    
    
