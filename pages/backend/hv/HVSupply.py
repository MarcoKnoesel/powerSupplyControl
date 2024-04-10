import pages.backend.hv.CWrapper as CWrapper
import pages.backend.Messages as Messages
import ctypes

class HVSupply:
	def __init__(self, name: str, user: str, ip: str) -> None:
		self.name = name
		self.user = user
		self.ip = ip
		self.pw = None
		self.cw = CWrapper.CWrapper()
		self.messages = Messages.Messages()

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
		if self.isError("logout", reply):
			return False
		return True
	
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
			errorMessage = "[" + source + "] "
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
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVGetCrateMap, removeLF = False)
		if self.isError("getMap", reply):
			return ""
		return reply
	
	def measureVoltages(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("VMon", slot, channelStart, channelStop)
		if self.isError("measureVoltages", reply):
			return [None,]
		return reply
	
	def measureCurrents(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("IMon", slot, channelStart, channelStop) 
		if self.isError("measureCurrents", reply):
			return [None,]
		return reply

	def getTargetVoltages(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("V0Set", slot, channelStart, channelStop) 
		if self.isError("getTargetVoltages", reply):
			return [None,]
		return reply
	
	def getRampSpeedUp(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("RUp", slot, channelStart, channelStop) 
		if self.isError("getRampSpeedUp", reply):
			return [None,]
		return reply
	
	def getRampSpeedDown(self, slot: int, channelStart: int, channelStop: int = -1):
		reply = self.cw.getChParam("RDWn", slot, channelStart, channelStop) 
		if self.isError("getRampSpeedDown", reply):
			return [None,]
		return reply
	
	# -------- Channel mapping --------

	# Map the combination of slot and channel number
	# on a global channel number running over all channels of HIME
	def slotAndCh_to_himeCh(self, slot: int, ch: int) -> int:
		if ch < 0 or ch >= 48 or slot < 0:
			return -1
		if slot < 9:
			return slot * 48 + ch
		if slot == 10:
			return 432 + ch
		if slot == 12:
			return 480 + ch
		if slot == 14:
			return 528 + ch
		return -1
	
	def layerToSlotsAndChannels(self, layer: int):
		defaultReturnVal = [[-1, -1, -1],[-1, -1, -1]]
		if layer < 1:
			return defaultReturnVal
		if layer > 2:
			return defaultReturnVal
		if layer == 1:
			slots = [2, 0]
			chStart = 0
			chStop = 24
		if layer == 2:
			slots = [4, 6]
			chStart = 0
			chStop = 24
		return [[slots[0], chStart, chStop],[slots[1], chStart, chStop]]
	
	def isHorizontal(self, layer: int) -> bool:
		return layer % 2 == 0
	
	def setVoltage_layer(self, layer: int, voltage: float) -> str:
		slotsAndChannels = self.layerToSlotsAndChannels(layer)
		return self.cw.setChParam_multiple("V0Set", slotsAndChannels, voltage, 0, 0)
	
	def setVoltage_channel(self, slot: int, channel: int, voltage: float) -> str:
		return self.cw.setChParam_single("V0Set", slot, channel, voltage, 0, 0)
	
	def pwOn_channel(self, slot: int, channel: int) -> str:
		return self.cw.setChParam_single("Pw", slot, channel, 0, 1, 1)
	
	def pwOff_channel(self, slot: int, channel: int) -> str:
		return self.cw.setChParam_single("Pw", slot, channel, 0, 0, 1)	
	
	def pwOn_layer(self, layer: int) -> str:
		slotsAndChannels = self.layerToSlotsAndChannels(layer)
		return self.cw.setChParam_multiple("Pw", slotsAndChannels, 0, 1, 1)
	
	def pwOff_layer(self, layer: int) -> str:
		slotsAndChannels = self.layerToSlotsAndChannels(layer)
		return self.cw.setChParam_multiple("Pw", slotsAndChannels, 0, 0, 1)

	def pwOff_crate(self) -> str:
		reply = ""
		for layer in [1,2]:
			reply += self.pwOff_layer(layer)
		return reply

	def pwOn_crate(self) -> str:
		reply = ""
		for layer in [1,2]:
			reply += self.pwOn_layer(layer)
		return reply
