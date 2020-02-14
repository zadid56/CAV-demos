import os
import time
import RPi.GPIO as GPIO
import json
import numpy as np
from socket import *
import numpy as np
import math
##################################
####      Global Variables   #####
##################################
controller_id = 1
SPAT = 1
time_R = 10
time_G = 15
time_Y = 4

R = int(3961) # radius of earth in miles
m2feet = int(5280)

SPaT = {'R': time_R,
        'G': time_G,
        'Y': time_Y}

pins = {'pin_R' : 14,
        'pin_G' : 15,
        'pin_Y' : 18}
##################################
####    Broadcast Module #########
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

def create_spat_data(c_phage,r_time):
    app_id = 4
    app_status = 1
    app_content = "Green : "
    
    if(c_phage == 'R'):
        app_content = "Red : "
        app_status = 1
    elif(c_phage == 'G'):
        app_content = "Green : "
        app_status = 0
    if(c_phage == 'Y'):
        app_content = "Yellow : "
        app_status = 2

    app_content+= str(r_time) + " s"
    
    data = {'type' : SPAT,
            'eventid'  : app_id,
            'content'  : app_content,
            'phase' : c_phage,
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
    global state, SPaT
    
    s_long = -82.8392985
    s_lat = 34.675486
    
    count = 0
    values = np.zeros(shape=(10,6))
    while (True):
        for phase,timing in SPaT.items():
            print ('setting signal to ', phase)
            setSignal(phase)
            single_step = 0.5
            steps = np.arange(0,timing,single_step)
            i = 0
            numel = len(steps)
            dist_signal = 1000
            
            
            while(i<numel):
                file = open('data.txt','r')
                car_data = file.read()
                #print car_data
                file.close()
                bsm = []
                for t in car_data.replace(',',' ').replace('}',' ').split():
                    try:
                        bsm.append(float(t))
                    except ValueError:
                        pass
                
                if(len(bsm)==6):
                    values[count] = bsm
                    count = count+1
                    if(count==1):
                        #print values
                        ids = np.unique(values[:,0])
                        cv_data = np.zeros(shape=(len(ids),6))
                        for j in range(0,len(ids)):
                            ind = np.where(values[:,0] == ids[j])
                            cv_data[j,:] = np.mean(values[ind,:], axis=1)
                        

                        dist_signal = findDist(cv_data[0,3], cv_data[0,4], s_long, s_lat)
                        print dist_signal
                        
                        values = np.zeros(shape=(1,6))
                        count = 0
                    
                #print bsm
                s_time = time.time()
                if(dist_signal<100 and phase=='G' and timing-steps[i]<=2):
                    spat_data = create_spat_data(phase,2)
                    print('Extending Green Time')
                else:                   
                    spat_data = create_spat_data(phase,timing-steps[i])
                    i=i+1
                    #print(i)
                connection.sendall(spat_data)
                e_time = time.time() 
                del_time = (e_time - s_time)
                time.sleep(single_step - del_time)
                
##############################
####        Main        ######
##############################
def main():
    init_controller()
    start_controller()
##############################
if __name__ == "__main__":
    main()


