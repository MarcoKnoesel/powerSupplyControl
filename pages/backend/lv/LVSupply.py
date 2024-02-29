from pages.backend.lv.TCPSocket import *
import pages.backend.Messages as Messages

# class representing an LV supply
class LVSupply:

	def __init__(self, name: str, mac: str, ip: str, minVoltage: float, maxVoltage: float) -> None:
		self.tcpSocket = TCPSocket(mac, ip, 8003, chr(10)) # TCP port 8003, LF in ASCII code
		self.tcpSocket.open()
		self.name = name
		self.manuallyEnteredMAC = mac
		self.minVoltage = minVoltage
		self.maxVoltage = maxVoltage
		self.messages = Messages.Messages()
		self.hostname = self.getHostname()
		self.ip = self.getIP()
		self.mac = self.getMAC()

	# -------- Always after sending a command: Ask for errors (recommendation from TDK Lambda manual) --------

	def errorQuery(self) -> None:
		errorMessage = self.tcpSocket.receiveString("SYST:ERR?")
		if len(errorMessage) and errorMessage != "0,\"No error\"":
			self.messages.newError(errorMessage)

	def receiveString(self, command: str) -> str:
		try:
			reply = self.tcpSocket.receiveString(command)
		except BrokenPipeError:
			self.reconnect()
			reply = self.tcpSocket.receiveString(command)
		self.errorQuery()
		return reply
	
	def receiveFloat(self, command: str) -> float:
		reply = float(self.receiveString(command))
		return reply

	def receiveInt(self, command: str) -> int:
		reply = int(self.receiveString(command))
		return reply
	
	def send(self, command: str) -> None:
		self.tcpSocket.send(command)
		self.errorQuery()

	def reconnect(self) -> None:
		self.tcpSocket.close()
		self.tcpSocket.open()
		self.errorQuery()

	# *** Don't access the TCP socket directly below here ***
	#
	# -> Instead, use the methods above to send commands and receive messages!
	# -> This will invoke errorQuery() every time and thereby avoid to send to many commands at the same time
		
	# -------- off / on --------
	def getStatus(self):
		return self.receiveString("OUTP:STAT?")
	
	def isOn(self) -> bool:
		return self.getStatus() == "ON"

	def switchStatus(self) -> None:
		if self.isOn():
			self.switchOff()
		else:
			self.switchOn()

	def switchOn(self) -> None:
		self.setStatus(True)

	def switchOff(self) -> None:
		self.setStatus(False)

	def setStatus(self, on: bool) -> None:
		command = "OUTP:STAT OFF"
		if on:
			command = "OUTP:STAT ON"
		self.send(command)

	# -------- voltage --------
	def measureVoltage(self) -> float:
		return self.receiveFloat("MEAS:VOLT?")
	
	def getTargetVoltage(self) -> float:
		return self.receiveFloat("VOLT?")
	
	def setTargetVoltage(self, targetVoltage: float) -> None:
		self.send("VOLT " + str(targetVoltage))

	# -------- current --------
	def measureCurrent(self) -> float:
		return self.receiveFloat("MEAS:CURR?")
	
	def getTargetCurrent(self) -> float:
		return self.receiveFloat("CURR?")
	
	def setTargetCurrent(self, targetCurrent: float) -> None:
		self.send("CURR " + str(targetCurrent))

	# -------- network --------
	def getHostname(self) -> str:
		return self.receiveString("SYST:COMM:LAN:HOST?")
	
	def getIP(self) -> str:
		return self.receiveString("SYST:COMM:LAN:IP?")
	
	def getMAC(self) -> str:
		return self.receiveString("SYST:COMM:LAN:MAC?")
	
	# -------- status --------
	def isInConstantVoltageMode(self) -> bool:
		return self.getOperationalConditionRegister() & 1 == 1

	def isInConstantCurrentMode(self) -> bool:
		return (self.getOperationalConditionRegister() >> 1) & 1 == 1
	
	def getOperationMode(self) -> str:
		return self.receiveString("SYST:SET?")
	
	def getOperationModeDescription(self) -> str:
		mode = self.getOperationMode()
		if mode == "LOC":
			return "Local mode"
		if mode == "REM":
			return "Remote mode"
		if mode == "LLO":
			return "Local-lockout mode"
		return "[No valid answer!]"
	
	# -------- registers --------
	
	def getQuestionableConditionRegister(self) -> int:
		return self.receiveInt("STAT:QUES:COND?")
	
	def getStandardEventStatusRegister(self) -> int:
		return self.receiveInt("*ESR?")
	
	def getOperationalConditionRegister(self) -> int:
		return self.receiveInt("STAT:OPER:COND?")