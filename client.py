import socket
import time
import json
import threading
import math
from random import randint

class Node:
	ID = -1
	PORT = -1
	TTL = 20
	def __init__(self, _ID, _PORT):
		self.ID = _ID
		self.PORT = _PORT
		self.TTL = 20
		
	
	def resetTTL(self):
		self.TTL = 20

class Movie:
	ID = -1
	name = ""

sair = 0
def set_port():
	port = randint(1025,65535)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex(('127.0.0.1',port))
	if result == 0:
		set_port()
	else:
		return port

IP_SERVER = "127.0.0.1"
PORT_SERVER = 8888

maxid = -1
self_ID = -1;
next_node = Node(-1, "0")
prev_node = Node(-1, "0")
next_next_node = Node(-1, "0")
prev_prev_node = Node(-1, "0")
PORT_root = -1
root = False
hash_table = []

MY_IP = "localhost"
MY_PORT = set_port()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((MY_IP, MY_PORT))
def main():
	global self_ID
	global next_node
	global prev_node
	global PORT_root
	global sair
	global maxid
	# Mensagem Hello
	MSG = ["hello", "1"]
	sock.sendto(json.dumps(MSG), (IP_SERVER, PORT_SERVER))

	# Recebe ID do servidor
	
	data = sock.recv(1024)
	data = json.loads(data)
	print data[0]
	self_ID = int(data[0])
	aux = data[1]["Rport"]
	PORT_root = int(aux)
	maxid = int(data[2])
	print "maxid: ", maxid
	
	# Mensagem de ACK 
	MSG = ["ack"]
	sock.sendto(json.dumps(MSG), (IP_SERVER, PORT_SERVER))
	
	# verifica se eh root
	if self_ID == 0:
		root = True
		next_node.PORT = MY_PORT
		next_node.ID = self_ID
		prev_node.PORT = MY_PORT
		prev_node.ID = self_ID
		putInMem()
	else:
		search_neighboors(PORT_root)
		warn_neighboors()
	
	print "VIZINHOS " + "NEXT: ", next_node.ID, "ANTERIOR: ", prev_node.ID
	
	thr1 = threading.Thread(target = ping_next)
	thr3 = threading.Thread(target = msg_rcv)
	thr4 = threading.Thread(target = decrementaTTL_next)
	thr5 = threading.Thread(target = decrementaTTL_prev)
	thr6 = threading.Thread(target = SS_movie)
	thr1.setDaemon(True)
	thr3.setDaemon(True)
	thr4.setDaemon(True)
	thr5.setDaemon(True)
	thr6.setDaemon(True)
	thr1.start()
	thr3.start()
	thr4.start()
	thr5.start()
	thr6.start()
	
	
	# Encerra o programa caso Ctrl+D (EOF) seja inserido
	try:
		while (input()):
			pass
	except EOFError:
		sock.close()
		return
	
def SS_movie():
	while True:
		MSG = raw_input("Digite SEARCH: 'movie' ou STORAGE: 'movie': ")
		MSG = MSG + " " + MY_IP + " " + str(MY_PORT)
		sock.sendto(MSG, (MY_IP, PORT_root))

def hash_function(name):
	soma = 0
	for c in name:
		soma += ord(c)
	return soma % maxid

def has_movie(name, origem_IP, origem_PORT):
	mov_id = hash_function(name)
	if(next_node.ID == 0 and self_ID != 0):
		ID_next = maxid
	else:
		ID_next = next_node.ID
	if abs(self_ID - mov_id) > abs(ID_next - mov_id) :
		return False
	else:
		return True
		

#Function to see if a movie is in hash
def haveInHash(name):
	print '**************************************************************'
	print 'ID list'
	for elem in hash_table:
		print "aa " + elem[1] + " " + name
		if elem[1] == name:
			print "ID: ", elem[0]
			return True
	return False

def putInMem():
	global hash_table
	file1 = open("conf.txt")
	for movie in file1:
		movie = movie.strip('\n')
		mov_id = hash_function(movie)
		print mov_id, movie
		hash_table.append((mov_id, movie))

def ping_next():
	global next_node
	global prev_node
	while True:
		MSG = "PREV2: " + str(prev_node.ID) + " " + str(prev_node.PORT)
		sock.sendto(MSG , (MY_IP, next_node.PORT))
		MSG = "NEXT2: " + str(next_node.ID) + " " + str(next_node.PORT)
		sock.sendto(MSG , (MY_IP, prev_node.PORT))
		time.sleep(5)

def decrementaTTL_next():
	global next_node
	while(next_node.TTL > 0):
		time.sleep(1)
		next_node.TTL -= 1
	MSG = ["saiu",str(next_node.ID)]
	next_node.ID = next_next_node.ID
	next_node.PORT = next_next_node.PORT
	next_node.TTL=20
	sock.sendto(json.dumps(MSG), (IP_SERVER, PORT_SERVER))
	print "VIZINHOS " + "NEXT: ", next_node.ID, "ANTERIOR: ", prev_node.ID
	decrementaTTL_next()
	

def decrementaTTL_prev():
	global prev_node
	while(prev_node.TTL > 0):
		time.sleep(1)
		prev_node.TTL -= 1
	prev_node.ID = prev_prev_node.ID
	prev_node.PORT = prev_prev_node.PORT
	prev_node.TTL=20
	print "VIZINHOS " + "NEXT: ", next_node.ID, "ANTERIOR: ", prev_node.ID
	decrementaTTL_prev()

def search_neighboors(PORT):
	global next_node
	global prev_node
	global self_ID
	global PORT_root
	#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto("SEND_NEXT" , (MY_IP, PORT))
	
	data, addr = sock.recvfrom(1024)
	text = data.split(' ')
	text[0].strip()
	if int(text[0]) > self_ID:
		next_node.ID = int(text[0])
		next_node.PORT = addr[1]
	else:
		prev_node.ID = int(text[0])
		prev_node.PORT = addr[1]
		text[1].strip()
		if(int(text[1]) == PORT_root):
			next_node.ID = 0
			next_node.PORT = PORT_root
		else:
			search_neighboors(int(text[1]))

def warn_neighboors():
	global self_ID
	global next_node
	global prev_node
	global MY_IP
	sock.sendto("PREV: " + str(self_ID) , (MY_IP, next_node.PORT))
	sock.sendto("NEXT: " + str(self_ID) , (MY_IP, prev_node.PORT))

def msg_rcv():
	global next_node
	global prev_node
	global next_next_node
	global prev_prev_node
	
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		text = data.split(' ')
		if(text[0] == "SEND_NEXT"):
			msg = str(self_ID) + " " + str(next_node.PORT)
			sock.sendto(msg , (MY_IP, addr[1]))
		elif(text[0] == "NEXT:"):
			next_node.PORT = addr[1]
			next_node.ID = int(text[1])
		elif(text[0] == "PREV:"):
			prev_node.PORT = addr[1]
			prev_node.ID = int(text[1])
		elif(text[0] == "PREV2:"):
			#print "PING PREV2: "
			prev_node.resetTTL()
			prev_prev_node.ID = int(text[1])
			prev_prev_node.PORT = int(text[2])
		elif(text[0] == "NEXT2:"):
			#print "PING NEXT2: "
			next_node.resetTTL()
			next_next_node.ID = int(text[1])
			next_next_node.PORT = int(text[2])
		elif(text[0] == "SEARCH:"):
			if has_movie(text[1], text[2], int(text[3])) == True:
				if haveInHash(text[1]) == True:
					MSG = "END: 1"
				else:
					MSG = "END: 0"
				sock.sendto(MSG, (text[2], int(text[3])))
			else:
				MSG = "SEARCH: " + text[1] + " " + text[2] + " " + text[3]
				sock.sendto(MSG, (MY_IP, next_node.PORT))
				
		elif(text[0] == "STORAGE:"):
			soma = 1
		elif(text[0] == "END:"):
			if(text[1] == "1"):
				print "Beleza, filme existe, vou baixar"
			else:
				print "Putz, filme nao existe, vou procurar no Google"

if __name__ == "__main__":
	main()
