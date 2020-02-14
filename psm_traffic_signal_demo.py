#Collision Avoidance app
#contains udp socket part to receive messages from cars
# checks for cw condtions
# relvel<0, distance < 10 ft and speed_cur>5



import os
import socket
import sys
import json
import time
from gps import	 *
import math
import threading


filename = 'psm.txt'

def clear_file():
	with open(filename,'w') as f:
		return
def write_to_file(data):
   with open(filename,'a') as f:
	   f.write(data + '\n')

clear_file()


R = int(3961) # radius of earth in miles
m2feet = int(5280)

UDP_IP_DSRC = "192.168.234.255"
UDP_BCAST_PORT=8888
#UDP_BCAST_PORT_PED_WARNING = 7777
UDP_BCAST_PORT_PED_WARNING = 8888

UDP_MOB_IP="192.168.43.1"
UDP_MOB_PORT=9000
carID="3"
frontcar="2"
mps2mph=2.237
carid = 1

SPAT = 1
BSM	 = 0

gpsd = None #seting the global variable
pckcnt = 0
os.system('clear') #clear the terminal (optional)


def findDistance(lat1,lon1,lat2,lon2):
		rlat1 = math.radians(lat1)
		rlat2 = math.radians(lat2)
		rlon1 = math.radians(lon1)
		rlon2 = math.radians(lon2)
		dlon = rlon2-rlon1
		dlat = rlat2-rlat1
		#print dlon, dlat
		a = (math.sin(dlat/2))**2 + math.cos(rlat1) * math.cos(rlat2) * (math.sin(dlon/2))**2
		c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
		d = R * c * m2feet
		return d

class GpsPoller(threading.Thread):
  def __init__(self):
		threading.Thread.__init__(self)
		global gpsd #bring it in scope
		gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
		self.current_value = None
		self.running = True #setting the thread running to true

  def run(self):
		global gpsd
		while gpsp.running:
		  gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer



if __name__ == '__main__':
	gpsp = GpsPoller() # create the thread
		  #sockr,socks=udpSetup()
	sockr = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sockr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	sockr.bind(('',UDP_BCAST_PORT_PED_WARNING))

	socks = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

	sock_bcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock_bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

	#sock_bcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#sock_bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)


	try:
		gpsp.start() # start it up
					#print "started GPS"
		while True:
			message = "" #empty message
			pckcnt = pckcnt +1
			#time.sleep(0.1) #set to whatever

			data,addr = sockr.recvfrom(512)

			print(data)
			
			socks.sendto(data,(UDP_MOB_IP,UDP_MOB_PORT));
			time.sleep(0.1)
			#print 'sending hello'

			#print "received"

	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		socks.close()
		sockr.close()
		gpsp.running = False
		gpsp.join() # wait for the thread to finish what it's doing
		print "caught ctrl +  c \n"
		print "closing all \n"
	print "Done!!\n"
