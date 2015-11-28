import socket
import fcntl
import struct

class Node:
	ID = -1
	IP = ""
	def __init__(self, _ID, _IP):
		ID = _ID
		IP = _IP


IP_SERVER = "172.20.10.3"
UDP_PORT = 5005

self_ID = -1;
next_node = Node(-1, "0")
prev_node = Node(-1, "0")
IP_root = ""
root = False

def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	try:
		addr = socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])
	except IOError:
		addr = ""
	if addr=="":
		return False, addr
	return True,addr

up, MY_IP = get_ip_address('wlan0')
#MY_IP = "127.0.0.2"

print "UDP target IP:", IP_SERVER
print "UDP target port:", UDP_PORT

def main():
	global self_ID
	global IP_root
	# Mensagem Hello
	MSG = "HELLO"
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto(MSG, (IP_SERVER, UDP_PORT))

	# Recebe ID do servidor
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((MY_IP, UDP_PORT))
	data = sock.recv(1024)
	text = data.split()
	self_ID = int(text[0])
	IP_root = text[1]
	print "MEU ID: ", self_ID
	
	# Mensagem de ACK 
	MSG = "ACK"
	sock.sendto(MSG, (IP_SERVER, UDP_PORT))
	
	# verifica se eh root
	if IP_root == "0.0.0.0":
		root = True
		next_node.IP = MY_IP
		next_node.ID = self_ID
		prev_node.IP = MY_IP
		prev_node.ID = self_ID
	else:
		search_neighboors(IP_root)
		warn_neighboors()
	
	msg_rcv()
	
def search_neighboors(IP):
	global next_node
	global prev_node
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto("SEND_NEXT" , (IP, UDP_PORT))
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#sock.bind((MY_IP, PORTA))
	data, addr = sock.recvfrom(1024)
	text = data.split(' ')
	if int(text[0]) > self_ID:
		next_node.ID = int(text[0])
		next_node.IP = addr[0]
	else:
		prev_node.ID = int(text[0])
		prev_node.IP = addr[0]
		if(text[1] == IP_root):
			next_node.ID = int(text[0])
			next_node.IP = addr[0]
		else:
			search_neighboors(text[1])

def warn_neighboors():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto("NEXT: " + self_ID , (next_node.IP, UDP_PORT))
	sock.sendto("PREV: " + self_ID , (prev_node.IP, UDP_PORT))

def msg_rcv():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	#sock.bind((MY_IP, UDP_PORT))
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		text = data.split()
		if(text[0] == "SEND_NEXT"):
			msg = str(self_ID) + " " + next_node.IP
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto(msg , (addr[0], UDP_PORT))
		elif(text[0] == "PREV:"):
			next_node.IP = addr[0]
			next_node.ID = int(text[1])
		elif(text[0] == "NEXT:"):
			prev_node.IP = addr[0]
			prev_node.ID = int(text[1])

if __name__ == "__main__":
	main()
