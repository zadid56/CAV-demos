import json
import numpy as np
from socket import *
import math
import time
from kafka import KafkaProducer

R = int(3961) # radius of earth in miles
m2feet = int(5280)

producer = KafkaProducer(bootstrap_servers='18.234.19.54:9092')
TOPIC = 'vtldata'

targetHost = '192.168.2.1'
targetPort = 8898
server_address = (targetHost, targetPort)

sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

sock.bind(server_address)
sock.listen(5)

print ('waiting for client...')

connection , addr = sock.accept()

##################################

def create_vtl_data(phase):
    app_id = 20
    data = {'eventid'  : app_id,
            'content'  : phase,
            'timestamp' : str(int(time.time() * 1000))}

    vtl_data = json.dumps(data)

    return vtl_data



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

    global producer, TOPIC
    rsu_long = -82.826830
    rsu_lat = 34.668305

    count = 3000
    done_id = np.zeros(shape=(4,1))
    done_count = 0

    while (True):
        print('Calculating Phase')
        values = np.zeros(shape=(count,6))
        for i in range(0,count):
            file = open('data.txt','r')
            car_data = file.read()
            file.close()
            bsm = []
            for t in car_data.replace(',',' ').replace('}',' ').split():
                try:
                    bsm.append(float(t))
                except ValueError:
                    pass

            if(len(bsm)==6):
                values[i] = bsm


        ids = np.unique(values[:,0])
        ids = np.sort(ids)

        print(ids)

        ids = np.delete(ids, np.where(ids == done_id[0]))
        ids = np.delete(ids, np.where(ids == done_id[1]))
        ids = np.delete(ids, np.where(ids == done_id[2]))
        ids = np.delete(ids, np.where(ids == done_id[3]))
        print(ids)

        cv_data = np.zeros(shape=(len(ids),6))
        dist_cv = np.zeros(shape=(len(ids),1))
        if(len(ids)>0):
            for i in range(0,len(ids)):
                ind = np.where(values[:,0] == ids[i])
                cv_data[i,:] = np.mean(values[ind,:], axis=1)
                dist_cv[i,0] = findDist(cv_data[i,3], cv_data[i,4], rsu_long, rsu_lat)

                if(np.isnan(dist_cv[i,0])):
                    dist_cv[i,0] = int(1000) 

            print(dist_cv)
            mind = np.min(dist_cv)
            ind2 = np.argmin(dist_cv)
            minID = ids[ind2]
            if(minID == 1 or minID==3):
                phase = 'G,R,G,R'
                dist1 = mind
            elif(minID == 2 or minID==4): 
                phase = 'R,G,R,G'
                dist1 = mind
            else:
                phase = 'G,R,G,R'

		
            print(phase)
            vtl_data = create_vtl_data(phase)
            connection.sendall(vtl_data.encode('UTF-8'))
            producer.send(TOPIC,vtl_data.encode('UTF-8'))

            while(1):
                values = np.zeros(shape=(count,6))
                for i in range(0,count):
                    file = open('data.txt','r')
                    car_data = file.read()
                    file.close()
                    bsm = []
                    for t in car_data.replace(',',' ').replace('}',' ').split():
                        try:
                            bsm.append(float(t))
                        except ValueError:
                            pass

                    if(len(bsm)==6):
                        values[i] = bsm

                print(minID)
                cv_data = np.zeros(shape=(1,6))
                ind = np.where(values[:,0] == minID)
                cv_data[0,:] = np.mean(values[ind,:], axis=1)
                dist1 = findDist(cv_data[0,3], cv_data[0,4], rsu_long, rsu_lat)

                print(phase)
                if(np.isnan(dist1)):
                    dist1 = int(1000)

                vtl_data = create_vtl_data(phase)
                connection.sendall(vtl_data.encode('UTF-8'))
                producer.send(TOPIC,vtl_data.encode('UTF-8'))

                print(dist1)

                if(dist1<25):
                    print('phase change')
                    if(done_count<4):
                        done_id[done_count,0] = minID
                        print(done_id)
                        done_count = done_count+1
                    break



#############################e
####        Main        ######
##############################
def main():
    start_controller()
##############################
if __name__ == "__main__":
    main()


