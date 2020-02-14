#!/usr/bin/env python

# udp client for data sending and receiving

import socket
import time

UDP_IP = "192.168.2.255"
UDP_PORT=8888

def msg_bcast(UDP_IP,UDP_PORT): 
  """ 
  function to broadcast data 
  """
  sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # create udp socket
  sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)   ### for enabling broadcast
  msg_py = b'abcdefghijklmnopqrstuvwxyz'
  pckcnt = 0
  
  try:
    while(pckcnt<1000):
      sock.sendto(msg_py, (UDP_IP,UDP_PORT)) 
      pckcnt = pckcnt +1  
      time.sleep(0.0000001) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nKilling Thread...")
  print("Done.\nExiting.")
 
if __name__ == '__main__':
  msg_bcast(UDP_IP,UDP_PORT)
