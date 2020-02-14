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

    count = 2000

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
        if(len(ids)==5):
            ids = np.delete(ids, [0])
        print(ids)
        cv_data = np.zeros(shape=(len(ids),6))
        dist_cv = np.zeros(shape=(len(ids),1))
        if(len(ids)==4):
            for i in range(0,len(ids)):
                ind = np.where(values[:,0] == ids[i])
                cv_data[i,:] = np.mean(values[ind,:], axis=1)
                dist_cv[i,0] = findDist(cv_data[i,3], cv_data[i,4], rsu_long, rsu_lat)
 
            #print(cv_data)
            mind = np.min(dist_cv)
            ind2 = np.argmin(dist_cv)
            minID = ids[ind2]
            if(minID == 1 or minID==3):
                phase = 'G,R,G,R'
                dist1 = dist_cv[0]
                dist2 = dist_cv[2]
            else: 
                phase = 'R,G,R,G'
                dist1 = dist_cv[1]
                dist2 = dist_cv[3]
		
            print(phase)
            vtl_data = create_vtl_data(phase)
            connection.sendall(vtl_data.encode('UTF-8'))
            producer.send(TOPIC,vtl_data.encode('UTF-8'))

            while(dist1>30 and dist2>30):
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
                if(len(ids)==5):
                    ids = np.delete(ids, [0])
                print(ids)
                cv_data = np.zeros(shape=(len(ids),6))
                dist_cv = np.zeros(shape=(len(ids),1))
                if(len(ids)==4):
                    for i in range(0,len(ids)):
                        ind = np.where(values[:,0] == ids[i])
                        cv_data[i,:] = np.mean(values[ind,:], axis=1)
                        dist_cv[i,0] = findDist(cv_data[i,3], cv_data[i,4], rsu_long, rsu_lat)

                    #print(cv_data)
                    if(phase == 'G,R,G,R'):
                        dist1 = dist_cv[0]
                        dist2 = dist_cv[2]
                    else:
                        dist1 = dist_cv[1]
                        dist2 = dist_cv[3]

                    print(phase)
                    if(np.isnan(dist1)):
                        dist1 = 1000
                    if(np.isnan(dist2)):
                        dist2 = 1000

                    vtl_data = create_vtl_data(phase)
                    connection.sendall(vtl_data.encode('UTF-8'))
                    producer.send(TOPIC,vtl_data.encode('UTF-8'))

                    print(dist1,dist2)

            if(phase=='G,R,G,R'):
                phase='R,G,R,G'
                print('phase changed')
                print(phase)
                while(1):
                    vtl_data = create_vtl_data(phase)
                    connection.sendall(vtl_data.encode('UTF-8'))
                    producer.send(TOPIC,vtl_data.encode('UTF-8'))
                print('phase changed')
            else:
                phase='G,R,G,R'
                print('phase changed')
                print(phase)
                while(1):
                    vtl_data = create_vtl_data(phase)
                    connection.sendall(vtl_data.encode('UTF-8'))
                    producer.send(TOPIC,vtl_data.encode('UTF-8'))

        else:
            break

        


#############################e
####        Main        ######
##############################
def main():
    start_controller()
##############################
if __name__ == "__main__":
    main()


