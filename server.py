import socket
import time
from random import randint

UDP_IP = "127.0.0.2"
UDP_PORT = 5005

client_list = []

sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
def main():
	sock.bind((UDP_IP, UDP_PORT))
	
	data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
	print "received message:", data, "from: ", addr
	
	#ip = "192.168.1." +  str(randint(2,255))
	id_client = str(randint(0,50));
	time.sleep(2)
	sock.sendto(id_client, ("127.0.0.1", UDP_PORT))
	
	data, addr = sock.recvfrom(1024)
	print "received message:", data, "from: ", addr
    
if __name__ == "__main__":
	main()