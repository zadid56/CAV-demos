
import threading  
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
from pandas.io.json import json_normalize
from geopy.distance import great_circle

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time

from tkinter import Tk, Message
#from SocketServer import ThreadingMixIn

txt = '0.5'
color = 'red'
txt2 = 'No attack detected'
color2 = 'blue'

##############################################################################################
TCP_IP = '192.168.2.16'
TCP_PORT = 9000
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
###############################################################################################

##################################
def vis_thread():
	global txt, color, txt2, color2
	def update():
		global txt, color, txt2, color2
		msg.config(text=txt, background=color)
		msg2.config(text=txt2, background=color2)
		root.after(250, update)

	root = Tk()
	root.geometry("900x600")

	msg = Message(root, text=txt, background=color)
	msg.config(font=('times', 200, 'italic bold'))
	msg.pack()

	msg2 = Message(root, text=txt2, background=color2)
	msg2.config(font=('times', 70, 'italic bold'))
	msg2.pack()

	root.after(250, update)

	root.mainloop()
##################################

def signal_thread():
	#tasks = [QueueWarning(), DOSAttack()]
	global txt, color, txt2, color2

	tcpsock.listen(4)
	print ("Waiting for incoming connections...at ", TCP_IP, ':' , TCP_PORT)
	(conn, (ip,port)) = tcpsock.accept()
	#print ("[+] New thread started for "+ip+":"+str(port))
	
	#data_frames = []
	
	prev_rtime = 20
	prev_phase = 'red'
	
	while True:
		try:
			data = conn.recv(2048)
			#if not data: break
			#print ("received data:", data)
			jdata = json.loads(data)
			if 'eventid' in jdata:
				if int(jdata['eventid'])==4:
					txt = str(jdata['rtime'])
					ph = str(jdata['phase'])
					if ph=='R':
						color = 'red'
					elif ph=='Y':
						color = 'yellow'
					elif ph=='G':
						color = 'green'
					else:
						color = 'purple'
						
					if prev_phase==color and prev_rtime<float(txt):
						txt2 = 'Attack detected'
						color2 = 'orange'
						
					prev_rtime = float(txt)
					prev_phase = color
			
			#####
			# rest of the things
			
				
		except Exception as err:
			continue

# start the program entry point	 
if __name__ == "__main__":
	t1 = threading.Thread(target=signal_thread, args=()) 
	t2 = threading.Thread(target=vis_thread, args=()) 
  
	# starting thread 1 
	t1.start() 
	# starting thread 2 
	t2.start() 
  
	# wait until thread 1 is completely executed 
	t1.join() 
	# wait until thread 2 is completely executed 
	t2.join() 
  
	# both threads completely executed 
	print("Done!")