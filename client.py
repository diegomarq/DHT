import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

self_ID = 0;

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
def main():
	MSG = "HELLO"
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto(MSG, ("127.0.0.2", UDP_PORT))
	
	data = sock.recv(1024)
	self_ID = int(data)
	print "MEU ID: " + self_ID
	
	MSG = "ACK"
	sock.sendto(MSG, ("127.0.0.2", UDP_PORT))
	
	

if __name__ == "__main__":
	main()