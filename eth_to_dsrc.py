import socket


bufsize = 1024 # Modify to suit your needs
UDP_IP = "192.168.234.255"
UDP_PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def broadcast(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data, (UDP_IP, UDP_PORT))
    #print 'data sent through DSRC'

def receiver():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect(('192.168.1.2', 8898))
        print ('start service ...')

        while True :
            message  = my_socket.recv(8192)
            #print 'message:'+ str(message)
            if(message == ''):
                print ('pipe broken')
                my_socket.close()
                return
            else :
                broadcast(message)
        #print ('message from :'+ str(address[0]) , message)
    except Exception as err:
        print 'exception in comm::receiver()'  , err

if __name__ == "__main__" :
    receiver()
