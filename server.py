import socket
import time
from random import randint

UDP_IP = "127.0.0.1"
UDP_PORT = 8888

client_list = {}

sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
def main():
	sock.bind((UDP_IP, UDP_PORT))
	
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		print "received message:", data, "from: ", addr
		
		if(bool(client_list) == False):
			id_client = "0"
			port_root = addr[1]
			msg = "0 -1"
		else:
			id_client = str(randint(0,50));
			while(id_client in client_list.keys()):
				id_client = str(randint(0,50));
			msg = id_client + " " + str(port_root)
		client_list[id_client] = addr
		sock.sendto(msg, (addr))
		
		data, addr = sock.recvfrom(1024)
		print "received message:", data, "from: ", addr
    
if __name__ == "__main__":
	main()