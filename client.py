import socket
import time
import json
import threading
import math
from random import randint

# Classe usada para guardar informacoes dos 4 vizinhos do no
# TTL eh o time to live do no, que comeca com 20segundos, passando esse tempo sem nenhum ping, o no eh considerado excluido da rede
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

# Classe usada para guardar a lista de filmes (nao estamos usando ainda)
class Movie:
	ID = -1
	name = ""

# funcao para gerar uma porta aleatoria. Checa se porta gerada ja existe, caso sim, sorteia outra porta
def set_port():
	port = randint(1025,65535)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex(('127.0.0.1',port))
	if result == 0:
		set_port()
	else:
		return port

# Informacoes de localizacao do Server
IP_SERVER = "127.0.0.1"
PORT_SERVER = 8888

# Informacoes essencias do no principal
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

# Socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((MY_IP, MY_PORT))
def main():
	global self_ID
	global next_node
	global prev_node
	global PORT_root
	global maxid
	# Mensagem Hello
	MSG = ["hello", "1"]
	sock.sendto(json.dumps(MSG), (IP_SERVER, PORT_SERVER))

	# Recebe 3 coisas essenciais do servidor: ID, PORT do root e id_maximo possivel do DHT
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
	
	# verifica se eh root (root sempre eh id 0)
	if self_ID == 0:
		# root se coloca como vizinho
		root = True
		next_node.PORT = MY_PORT
		next_node.ID = self_ID
		prev_node.PORT = MY_PORT
		prev_node.ID = self_ID
		putInMem()
	else:
		# senao for root, devemos procurar nossos vizinhos (a partir do root) e avisa-los
		search_neighboors(PORT_root)
		warn_neighboors()
	
	print "VIZINHOS " + "NEXT: ", next_node.ID, "ANTERIOR: ", prev_node.ID
	
	# 5 threads que vao ficar rodando sempre
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

# Funcao que le input do cliente. INPUT TEM QUE SER "SEARCH: movie" OU "STORAGE: movie"
def SS_movie():
	MSG ="1"
	while MSG != "0":
		MSG = raw_input("Digite SEARCH: 'movie' ou STORAGE: 'movie': ")
		if(MSG != "0"):
			MSG = MSG + " " + MY_IP + " " + str(MY_PORT)
			sock.sendto(MSG, (MY_IP, PORT_root))

# Funcao que calcula o hash de um filme somando todos os caracteres e dividindo por maxid
def hash_function(name):
	soma = 0
	for c in name:
		soma += ord(c)
	return soma % maxid

# Checa se o no tem um filme
def has_movie(name):
	mov_id = hash_function(name)
	if(next_node.ID == 0 and self_ID != 0):
		ID_next = maxid
	else:
		ID_next = next_node.ID
	if abs(self_ID - mov_id) > abs(ID_next - mov_id) :
		return False
	else:
		return True
		

# Function to see if a movie is in hash
def haveInHash(name):
	for elem in hash_table:
		if elem[1] == name:
			print "ID: ", elem[0], "name: ", elem[1]
			return True
	return False

# Pega nomes dos filmes do arquivo "conf.txt" e os coloca no no principal. FUNCAO SOH EH EXECUTADA POR ROOT_NODE
def putInMem():
	global hash_table
	file1 = open("conf.txt")
	for movie in file1:
		movie = movie.strip('\n')
		mov_id = hash_function(movie)
		print mov_id, movie
		hash_table.append((mov_id, movie))
	hash_table.sort(key=lambda tup: tup[0])
	for movie in hash_table:
		print movie

# Pinga os vizinhos imediamente da frente e de tras do no. Pinga o vizinho da frente com informacoes do vizinho anterior e pinga o vizinho de tras com informacoes do no sucessor
def ping_next():
	global next_node
	global prev_node
	while True:
		MSG = "PREV2: " + str(prev_node.ID) + " " + str(prev_node.PORT)
		sock.sendto(MSG , (MY_IP, next_node.PORT))
		MSG = "NEXT2: " + str(next_node.ID) + " " + str(next_node.PORT)
		sock.sendto(MSG , (MY_IP, prev_node.PORT))
		time.sleep(5)

# Inicia o decrementador do vizinho sucessor. Caso zere, o no eh responsavel por dizer isso ao servidor e ajeita seu proximo no para o proximo do proximo
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

# Funcao semelhante a anterior, porem o foco eh o no antecessor. E neste caso, nao avisa ao servidor que o no saiu
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

# Funcao que diz ao no quem sao seus vizinhos. No manda uma mensagem "SEND_NEXT" ao root, root responde com seu proprio ID e a PORT do proximo da lista e assim vai, ate acharmos nosso sucessor imediato. Caso PORT_do_prox seja igual a PORT_root, fizemos um circulo sem achar ninguem maior, logo root eh nosso vizinho proximo
def search_neighboors(PORT):
	global next_node
	global prev_node
	global self_ID
	global PORT_root
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

# Funcao para avisar aos vizinhos que 'chegamos'
def warn_neighboors():
	global self_ID
	global next_node
	global prev_node
	global MY_IP
	sock.sendto("PREV: " + str(self_ID) , (MY_IP, next_node.PORT))
	sock.sendto("NEXT: " + str(self_ID) , (MY_IP, prev_node.PORT))

# Funcao usada para redistribuicao dos nomes dos filmes
def send_list_next(PORT, ind):
	global hash_table
	
	lista = []
	for i in hash_table:
		if i[0] >= ind:
			if i[0] > next_node.ID:
				break
			lista.append(i)
			#hash_table.remove(i)
	#lista = [(d, q) for d, q in hash_table if d >= ind and d <= next_node.ID]
	
	print "LISTA DO OUTRO"
	print lista
	print "\nLISTA MINHA"
	print hash_table
	MSG = "LIST: " + json.dumps(lista)
	sock.sendto(MSG , (MY_IP, PORT))

# Funcao usada para redistribuicao dos nomes dos filmes (unica diferenca da anterior sao os dois 'ifs')
def send_list_prev(PORT, ind):
	global hash_table
	
	lista = []
	for i in hash_table:
		if i[0] >= prev_node.ID:
			if i[0] > ind:
				break
			lista.append(i)
			#hash_table.remove(i)
	#lista = [(d, q) for d, q in hash_table if d >= ind and d <= next_node.ID]
	
	print "LISTA DO OUTRO2"
	print lista
	print "\nLISTA MINHA2"
	print hash_table
	MSG = "LIST: " + json.dumps(lista)
	sock.sendto(MSG , (MY_IP, PORT))

# Funcao que trata as mensagens recebidas pelo no. Podemos receber mensagens de 10 tipos
def msg_rcv():
	global next_node
	global prev_node
	global next_next_node
	global prev_prev_node
	global hash_table
	
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		text = data.split(' ')
		# manda proprio ID e PORT_NEXT para quem solicitou a informacao
		if(text[0] == "SEND_NEXT"):
			msg = str(self_ID) + " " + str(next_node.PORT)
			sock.sendto(msg , (MY_IP, addr[1]))
		# no sucessor esta me avisando que ele eh meu novo sucessor, ocorre redistribuicao
		elif(text[0] == "NEXT:"):
			next_node.PORT = addr[1]
			next_node.ID = int(text[1])
			ind = (next_node.ID + self_ID)/2 + 1
			send_list_next(next_node.PORT, ind)
		# no antecessor esta me avisando que ele eh meu novo antecessor, ocorre redistribuicao
		elif(text[0] == "PREV:"):
			prev_node.PORT = addr[1]
			prev_node.ID = int(text[1])
			ID_calc = self_ID
			if(self_ID == 0):
				ID_calc = maxid
			ind = (prev_node.ID + ID_calc)/2
			send_list_prev(prev_node.PORT, ind)
		# no antecessor esta me avisando quem eh o antecessor dele
		elif(text[0] == "PREV2:"):
			#print "PING PREV2: "
			prev_node.resetTTL()
			prev_prev_node.ID = int(text[1])
			prev_prev_node.PORT = int(text[2])
		# no sucessor esta me avisando quem eh o sucessor dele
		elif(text[0] == "NEXT2:"):
			#print "PING NEXT2: "
			next_node.resetTTL()
			next_next_node.ID = int(text[1])
			next_next_node.PORT = int(text[2])
		# Alguem quer saber se filme em text[1] existe no meu no.
		elif(text[0] == "SEARCH:"):
			if has_movie(text[1]) == True:
				if haveInHash(text[1]) == True:
					MSG = "END: " + str(self_ID)
				else:
					MSG = "END: -1"
				sock.sendto(MSG, (text[2], int(text[3])))
			else:
				MSG = "SEARCH: " + text[1] + " " + text[2] + " " + text[3]
				sock.sendto(MSG, (MY_IP, next_node.PORT))
		# Alguem quer guarda um filme no DHT
		elif(text[0] == "STORAGE:"):
			if has_movie(text[1]) == True:
				if text[1] in hash_table:
					MSG = "END2: -1"
				else:
					hash_table.append((hash_function(text[1]), text[1]))
					MSG = "END2: " + str(self_ID)
				sock.sendto(MSG, (text[2], int(text[3])))
			else:
				MSG = "STORAGE: " + text[1] + " " + text[2] + " " + text[3]
				sock.sendto(MSG, (MY_IP, next_node.PORT))
		# Alguem respondeu a minha busca por algum filme
		elif(text[0] == "END:"):
			if(text[1] != "-1"):
				print "Beleza, filme existe, vou baixar em " + text[1]
			else:
				print "Putz, filme nao existe, vou procurar no Google"
		# Alguem respondeu ao meu pedido de insercao de filme
		elif(text[0] == "END2:"):
			if(text[1] != "-1"):
				print "Filme inserido em " + text[1]
			else:
				print "Filme ja existestente no DHT"
		# Alguem esta me mandando uma lista para eu aplicar a redistribuicao
		elif(text[0] == "LIST:"):
			del text[0]
			text = ' '.join(text)
			lista = []
			lista = json.loads(text)
			for x in lista:
				if x in hash_table:
					continue
				hash_table.append(x)
				
			for movie in hash_table:
				print "id: " + str(movie[0]) + "filme: " + movie[1]
		
if __name__ == "__main__":
	main()
