import os
import time
import RPi.GPIO as GPIO
import json
import numpy as np
from socket import *
import numpy as np
import math
from Tkinter import Tk, Message
import threading

##################################
####	  Global Variables	 #####
##################################
controller_id = 1
SPAT = 1
time_R = 10
time_G = 15
time_Y = 4

txt = '0.5'
color = 'red'
txt2 = 'No attack detected'
color2 = 'blue'

R = int(3961) # radius of earth in miles
m2feet = int(5280)

SPaT = {'R': time_R,
		'G': time_G,
		'Y': time_Y}

pins = {'pin_R' : 14,
		'pin_G' : 15,
		'pin_Y' : 18}
##################################
####	Broadcast Module #########
##################################
targetHost = '192.168.1.2'
targetPort = 8898
server_address = (targetHost, targetPort)

sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

sock.bind(server_address)
sock.listen(5)

print ('waiting for client...')

connection , addr = sock.accept()

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

def create_spat_data(c_phase,r_time):
	app_id = 4
	app_status = 1
	app_content = "Green : "
	
	if(c_phase == 'R'):
		app_content = "Red : "
		app_status = 1
	elif(c_phase == 'G'):
		app_content = "Green : "
		app_status = 0
	if(c_phase == 'Y'):
		app_content = "Yellow : "
		app_status = 2

	app_content+= str(r_time) + " s"
	
	data = {'type' : SPAT,
			'eventid'  : app_id,
			'content'  : app_content,
			'phase' : c_phase,
			'status' : app_status,
			'timestamp' : str(int(time.time() * 1000)),
			'rtime' : r_time}
	
	spat_data = json.dumps(data)

	return spat_data

def init_controller():
	global pins , state

	#GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	for key,value in pins.items():
		#print ('setting for ', key, ' value ' , value)
		GPIO.setup(value,GPIO.OUT)

	#state = 'R'
	
	print ('Controller Initialized')
	
		
def setSignal(c_state):
	global pins
	if(c_state=='R'):
		GPIO.output(pins['pin_R'],GPIO.HIGH)
		GPIO.output(pins['pin_Y'],GPIO.LOW)
		GPIO.output(pins['pin_G'],GPIO.LOW)
	elif(c_state=='G'):
		GPIO.output(pins['pin_R'],GPIO.LOW)
		GPIO.output(pins['pin_Y'],GPIO.LOW)
		GPIO.output(pins['pin_G'],GPIO.HIGH)
	elif(c_state=='Y'):
		GPIO.output(pins['pin_R'],GPIO.LOW)
		GPIO.output(pins['pin_Y'],GPIO.HIGH)
		GPIO.output(pins['pin_G'],GPIO.LOW)


def findDist(lon1,lat1,lon2,lat2):
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


def start_controller():
	global state, SPaT, txt, color, txt2, color2
	count = 0
	
	while (True):
		count = count+1
		for phase,timing in SPaT.items():
			print ('setting signal to ', phase)
			setSignal(phase)
			print(float(txt))
			if(float(txt)!=0.5):
				txt2 = 'Attack detected'
				color2 = 'orange'
				time.sleep(10)
			else:
				txt2 = 'No attack detected'
				color2 = 'blue'
			
			single_step = 0.5
			steps = np.arange(0,timing,single_step)
			for i in steps:
				s_time = time.time()
				if count>1 and phase=='G' and i==10:
					spat_data = create_spat_data(phase,timing-i+5)
				else:
					spat_data = create_spat_data(phase,timing-i)
				
				jdata = json.loads(spat_data)
				if 'eventid' in jdata:
					if int(jdata['eventid'])==4:
						txt = str(jdata['rtime'])
						ph = str(jdata['phase'])
						txt2 = 'No attack detected'
						color2 = 'blue'
						if ph=='R':
							color = 'red'
						elif ph=='Y':
							color = 'yellow'
						elif ph=='G':
							color = 'green'
						else:
							color = 'purple'
							
				connection.sendall(spat_data)
				e_time = time.time() 
				del_time = (e_time - s_time)
				time.sleep(single_step - del_time)
				
##############################
####		Main		######
##############################

def signal_thread():
	init_controller()
	start_controller()

##############################
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


	
