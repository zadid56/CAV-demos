import socket

UDP_IP_DSRC = "192.168.234.255"
UDP_BCAST_PORT=8888
bufsize = 8192 # Modify to suit your needs

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def broadcast(data):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(('192.168.1.2', 8898))
    my_socket.send(data)
    #print 'Data sent through eth'

def receiver():
    try:
        sockr = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sockr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sockr.bind(('',UDP_BCAST_PORT))
        print ('start service ...')

        while True :
            message  = sockr.recvfrom(bufsize)
            #print 'message:'+ str(message)
            if(message == ''):
                print ('pipe broken')
                sockr.close()
                return
            else :
                broadcast(str(message))
                                #pass
    #print ('message from :'+ str(address[0]) , message)
    except Exception as err:
        print 'exception in comm::receiver()'  , err

if __name__ == "__main__" :
    receiver()
