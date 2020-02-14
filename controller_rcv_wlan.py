import socket

UDP_IP_DSRC = "192.168.2.255"
UDP_BCAST_PORT=8897
bufsize = 8192 # Modify to suit your needs

def receiver():
    try:
        sockr = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sockr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sockr.bind(('',UDP_BCAST_PORT))
        print ('start service ...')

        while True :
            message  = sockr.recvfrom(bufsize)
            print('message:'+ str(message))
    except Exception as err:
        print('exception in comm::receiver()', err)

if __name__ == "__main__" :
    receiver()
