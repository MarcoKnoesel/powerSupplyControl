import pages.backend.hv.CWrapper as CWrapper
import pages.backend.Messages as Messages
import ctypes


class HVSupply:
	def __init__(self, name: str, user: str, ip: str) -> None:
		self.name = name
		self.user = user
		self.ip = ip
		self.pw = None
		self.cw = CWrapper.CWrapper(ip)
		self.messages = Messages.Messages()
		self.N_SLOTS = 9
		self.N_CHANNELS_PER_SLOT = 24
		self.loggedIn = False
		self.loginInfoText = ""

	# -------- Login / Logout / Timeout --------
		
	def login(self, password: str) -> bool:
		self.pw = ctypes.create_string_buffer(password.encode("utf-8"))
		reply = self.cw.login(
			self.cw.libHVWrapper.HVSystemLogin, 
			ctypes.create_string_buffer(self.user.encode("utf-8")),
			self.pw,
			ctypes.create_string_buffer(self.ip.encode("utf-8"))
		)
		if reply == "!!4103":
			self.isError("login", "!!Wrong password.")
			return False
		if reply == "!!4100":
			self.isError("login", "!!Login failed. Is the IP address \"" + self.ip + "\" correct?")
			return False
		if self.isError("login", reply):
			return False
		return True
	
	def reconnect(self) -> bool:
		# Before logging in again, HVSystemLogout() and forceInitCWrapper() need to be invoked.
		# Otherwise, the new login will not work.
		self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogout)
		self.cw.forceInitSystem()
		reply = self.cw.login(self.cw.libHVWrapper.HVSystemLogin,
			ctypes.create_string_buffer(self.user.encode("utf-8")), 
			self.pw,
			ctypes.create_string_buffer(self.ip.encode("utf-8"))
		)
		if self.isError("reconnect", reply):
			return False
		return True

	def logout(self) -> bool:
		if self.checkConnection() == 1:
			self.reconnect()
		self.pw = None
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogout)
		self.isError("logout", reply)
	
	def checkConnection(self) -> int:
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVGetCrateMap, removeLF = False)
		# no connection; most probably due to timeout
		if reply == "!!5" or reply == "!!4098":
			return 1
		# device already open
		if reply == "!!24":
			return 2
		# no connection 
		if reply[0:2] == "!!":
			return 0
		# connection works
		return 2

	# -------- Error treatment --------
			
	def isError(self, source: str, message: str) -> bool:
		# Error messages start with "!!"
		if len(message) < 2:
			return False
		# Extract the error code, if present
		if message[0:2] == "!!":
			messageBody = message[2:]
			errorMessage = "[HVSupply." + source + "] "
			if(len(message) < 3):
				errorMessage = errorMessage + "Unknown error."
			else:
				# Check if message only consists of an error code
				try:
					int(messageBody)
					errorMessage = errorMessage + "Error code: " + messageBody
				except ValueError:
					errorMessage = errorMessage + messageBody
			self.messages.newError(errorMessage)
			return True
		return False
	
	# -------- Get data from the HV supply --------

	def getMap(self) -> str:
		if self.checkConnection() != 2:
			self.reconnect()
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVGetCrateMap, removeLF = False)
		if self.isError("getMap", reply):
			return ""
		return reply
	
	def measureVoltages(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("VMon", slot, channelStart, channelStop)
		if self.isError("measureVoltages", str(reply[0])):
			return [None,]
		return reply
	
	def measureCurrents(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("IMon", slot, channelStart, channelStop) 
		if self.isError("measureCurrents", str(reply[0])):
			return [None,]
		return reply

	def getTargetVoltages(self, slot: int, channelStart: int, channelStop: int = -1):
		# if channelStop == -1, it will be set to channelStart + 1, see CWrapper.py
		reply = self.cw.getChParam("V0Set", slot, channelStart, channelStop) 
		if self.isError("getTargetVoltages", str(reply[0])):
			return [None,]
		return reply
	
	def getRampSpeedUp(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("RUp", slot, channelStart, channelStop) 
		if self.isError("getRampSpeedUp", str(reply[0])):
			return [None,]
		return reply
	
	def getRampSpeedDown(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("RDWn", slot, channelStart, channelStop) 
		if self.isError("getRampSpeedDown", str(reply[0])):
			return [None,]
		return reply
	
	def setVoltage_slotAndChannels(self, slot: int, chStart: int, chStop: int, voltage: float) -> str:
		return self.cw.setChParam_multiple("V0Set", slot, chStart, chStop, voltage, 0, 0)
	
	def setVoltage_channel(self, slot: int, channel: int, voltage: float) -> str:
		return self.cw.setChParam_single("V0Set", slot, channel, voltage, 0, 0)

	def pwOn_slotAndChannels(self, slot: int, chStart: int, chStop: int) -> str:
		return self.cw.setChParam_multiple("Pw", slot, chStart, chStop, 0, 1, 1)

	def pwOff_slotAndChannels(self, slot: int, chStart: int, chStop: int) -> str:
		return self.cw.setChParam_multiple("Pw", slot, chStart, chStop, 0, 0, 1)
	
	def pwOn_channel(self, slot: int, channel: int) -> str:
		return self.cw.setChParam_single("Pw", slot, channel, 0, 1, 1)
	
	def pwOff_channel(self, slot: int, channel: int) -> str:
		return self.cw.setChParam_single("Pw", slot, channel, 0, 0, 1)
	
	def getStatus_slotAndChannels(self, slot: int, chStart: int, chStop: int):
		reply = self.cw.getChParamStr("Pw", slot, chStart, chStop, 1) 
		#print("reply is")
		#print(reply)
		#print("len(reply) is")
		#print(len(reply))
		if self.isError("getStatus_slotAndChannels", str(reply[0])):
			return [None,]
		return reply
		#statusList = []
		#for entry in reply:
		#	if entry == 0:
		#		statusList += ["Off",]
		#	else:
		#		statusList += ["On",]
		#return statusList
