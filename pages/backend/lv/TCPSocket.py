import socket

class TCPSocket:
	def __init__(self, mac: str, ip: str, port: int, lineEnding: str) -> None:
		self.ip = ip
		self.port = port
		self.lineEnding = lineEnding
		self.mac = mac
		self.textEncoding = "utf-8"

	def open(self) -> None:
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect((self.ip, self.port)) 

	def receiveString(self, command: str) -> str:
		command = command + self.lineEnding
		self.client_socket.sendall(bytes(command, self.textEncoding))
		reply = self.client_socket.recv(1024)
		decodedReply = reply.decode(self.textEncoding)
		if len(decodedReply) == 0:
			return ""
		if decodedReply[-1] == self.lineEnding:
			decodedReply = decodedReply[:-1]
		return decodedReply
	
	def send(self, command: str) -> None:
		command = command + self.lineEnding
		self.client_socket.sendall(bytes(command, self.textEncoding))

	def close(self) -> None:
		self.client_socket.close()
		