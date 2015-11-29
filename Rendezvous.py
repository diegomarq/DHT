#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import random
import json
import socket


class Rendezvous:
	"""A rendezvous for all client who wants to conect to the DHT.
	This class give ID for clients who join to the DHT.
	Theses ids are chosen randomly from the range(0,k), where k is given from a configuration file (cf).
	The cf supply also one of two modes for take the ks. k is a power of 2 or k is some number 0,1,2,...
	"""
	def __init__(self):
		with open("conf.json") as conf_file:
			conf_data = json.load(conf_file) #Lê o arquivo de configuração

			#Obtem informações específicas do conf_file
			idformat = conf_data["idformat"]
			idrange = conf_data["idrange"]
	
			self.idProcessing(idformat, idrange)
			#Como é a primeira vez que o servidor foi "ligado" setamos a variável root para false	
			self.root = False 
			
			#Cria a lista com a topologia
			self.topology =[]
##
# @brief embaralha a lista de ids disponíveis
#
# @return o primeiro elemento da lista embaralhada. Se a lista estiver vazia retorna -1
	def getRandomId(self):
		if not self.availableIDs:
			print "Todos os ids estão em uso"
			return -1

		random.shuffle(self.availableIDs)
		return self.availableIDs[0]

##
# @brief seta a variável de objeto availableIDs com a lista de ids disponíveis
#
# @param idformat o formato dos ids diponíveis; potência de 2 ou não
# @param idrange o limite superior para um id; é o k da especificação
#
# @return 
	def idProcessing(self, idformat, idrange):
		#A quantidade de ids precisa ser no mínimo 1
		if idrange < 1:
			idrange = 1
			
		self.maxid = idrange

		#Teste
		#print idformat, idrange

		#Trata as duas formas de gerar id:
		#Progressão aritimética de razão 1 ou potências de 2
		if idformat == 0:	
			#PA de razão 1
			self.availableIDs = list( range(1, self.maxid) )
		elif idformat == 1:
			#Potência de 2
			i = 1
			self.availableIDs = []
			while i <= self.maxid:
				self.availableIDs.append(i)
				i = i << 1
		else:
			print "idformat {}, não é um valor válido. Reveja o arquivo de configuração"\
			.format(idformat)
			sys.exit()
			
	def start_server(self, port):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind( ("", port) )
		print "waiting on port:", port
		while 1:
			serial_data, addr = s.recvfrom(1024)
			#Deseriazação
			data = json.loads(serial_data)	
			#Teste
			print data	
			if data.strip() == 'hello':
				id = self.send_id(s, addr)

				#Teste
				print "Recebi hello"

				#Espera por uma confirmação
				#Bloqueia enquanto não receber o ack
				#O retorno já está deserializado
				data, addr = self.wait_ack(s)
								
				#Teste
				print "Recebi ack?"
				print data

				if data.strip() == 'ack':
					if id != -1:
						self.remove_id(id)			
						#Atualiza topologia
						self.updateTopology(id)	
						#Teste
						print self.topology
			
			#Teste
			#s.sendto("..", addr)	
##
# @brief envia o id para o nó que requisitou
#
# @param server 
# @param addr
# @param root true ou false; indica se já existe um root ou não
#
# @return retorna o id enviado para o nó que requisitou
	def send_id(self, server, addr):
		if not self.root:
			id = 0
			self.root = True 
			self.rootIP, self.rootPort = addr
		else:
			id =  self.getRandomId() 		
		
		#Testa se a lista está vazia
		if  id == -1:
			return id
		
		#Data serializer
		data = ( id, {"IDroot":0, "Rip":self.rootIP, "Rport":self.rootPort})
		serial_data = json.dumps(data)
		
		#server.sendto(str(id), addr)
		server.sendto(serial_data, addr)

		print "Message: {} \n".format(serial_data)

		return id
	
##
# @brief 
#
# @param server
#
# @return 
	def wait_ack(self, server):
		while 1:
			serial_data, addr = server.recvfrom(1024)
			data = json.loads(serial_data)

			if data.strip() == 'ack':
				return data, addr	

	def remove_id(self, id):
		#Teste
		#print id
		#print "ids disponíveis", self.availableIDs
		try:
			self.availableIDs.remove( id )
		except:
			pass
		#Teste
		#print "ids disponíveis", self.availableIDs

	def updateTopology(self,id, remove = False):
		if remove:
			try:
				self.topology.remove( id )	
				#O ID tem que voltar para a lista de IDs disponíveis
				self.availableIDs.append( id )
			except:
				pass
		else:
			self.topology.append( id )

		self.topology.sort()

#Instanciação da classe
rendezvous = Rendezvous()
rendezvous.start_server(8888)
#Teste
#print rendezvous.getRandomId()

	
