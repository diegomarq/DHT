import socket
import time
import json
from random import randint

class Node:
	ID = -1
	PORT = -1
	def __init__(self, _ID, _PORT):
		ID = _ID
		PORT = _PORT

def set_port():
	port = randint(1025,65535)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex(('127.0.0.1',80))
	if result == 0:
		return port
	else:
		set_port()

IP_SERVER = "127.0.0.1"
PORT_SERVER = 8888

self_ID = -1;
next_node = Node(-1, "0")
prev_node = Node(-1, "0")
PORT_root = -1
root = False

MY_IP = "localhost"
MY_PORT = set_port()
#MY_IP = "127.0.0.2"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((MY_IP, MY_PORT))
def main():
	global self_ID
	global PORT_root
	# Mensagem Hello
	MSG = "hello"
	sock.sendto(json.dumps(MSG), (IP_SERVER, PORT_SERVER))

	# Recebe ID do servidor
	#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	data = sock.recv(1024)
	data = json.loads(data)
	print data[0]
	self_ID = int(data[0])
	aux = data[1]["Rport"]
	PORT_root = int(aux)
	print "MEU ID: ", self_ID, PORT_root
	
	# Mensagem de ACK 
	MSG = "ack"
	sock.sendto(json.dumps(MSG), (IP_SERVER, PORT_SERVER))
	
	# verifica se eh root
	if self_ID == 0:
		root = True
		next_node.PORT = MY_PORT
		next_node.ID = self_ID
		prev_node.PORT = MY_PORT
		prev_node.ID = self_ID
	else:
		search_neighboors(PORT_root)
		warn_neighboors()
	
	print "VIZINHOS " + "NEXT: ", next_node.ID, "ANTERIOR: ", prev_node.ID
	msg_rcv()
	
def search_neighboors(PORT):
	global next_node
	global prev_node
	#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto("SEND_NEXT" , (MY_IP, PORT))
	
	#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#sock.bind((MY_IP, PORTA))
	data, addr = sock.recvfrom(1024)
	text = data.split(' ')
	if int(text[0]) > self_ID:
		next_node.ID = int(text[0])
		next_node.PORT = addr[1]
	else:
		prev_node.ID = int(text[0])
		prev_node.PORT = addr[1]
		if(int(text[1]) == PORT_root):
			next_node.ID = 0
			next_node.PORT = addr[1]
		else:
			search_neighboors(int(text[1]))

def warn_neighboors():
	#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto("NEXT: " + str(self_ID) , (MY_IP, next_node.PORT))
	sock.sendto("PREV: " + str(self_ID) , (MY_IP, prev_node.PORT))

def msg_rcv():
	#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	#sock.bind((MY_IP, UDP_PORT))
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		text = data.split()
		if(text[0] == "SEND_NEXT"):
			print "YAA ", next_node.PORT
			msg = str(self_ID) + " " + str(next_node.PORT)
			#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto(msg , (MY_IP, addr[1]))
		elif(text[0] == "PREV:"):
			next_node.PORT = addr[1]
			next_node.ID = int(text[1])
		elif(text[0] == "NEXT:"):
			prev_node.PORT = addr[1]
			prev_node.ID = int(text[1])

if __name__ == "__main__":
	main()
