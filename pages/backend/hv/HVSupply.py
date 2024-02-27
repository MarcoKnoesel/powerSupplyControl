import pages.backend.hv.CWrapper as CWrapper
import ctypes

class HVSupply:
	def __init__(self, name: str, ip: str) -> None:
		self.name = name
		self.ip = ip
		self.cw = CWrapper.CWrapper()
		self.pw = ""

	def login(self, password: str) -> str:
		self.pw = ctypes.create_string_buffer(password.encode("utf-8"))
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogin, self.pw)
		return reply
	
	def reconnect(self) -> str:
		# Before logging in again, HVSystemLogout() and forceInitCWrapper() need to be invoked.
		# Otherwise, the new login will not work.
		self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogout)
		self.cw.forceInitSystem()
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogin, self.pw)
		return reply

	def logout(self) -> str:
		self.pw = ""
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogout)
		return reply
	
	def checkConnection(self) -> int:
		#print("checkConnection")
		reply = self.getMap()
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

	def getMap(self) -> str:
		return self.cw.receiveString(self.cw.libHVWrapper.HVGetCrateMap, removeLF = False)
	
	def measureVoltages(self, slot: int, channelStart: int, channelStop: int = -1):
		return self.cw.getChParam("VMon", slot, channelStart, channelStop)
	
	def measureCurrents(self, slot: int, channelStart: int, channelStop: int = -1):
		return self.cw.getChParam("IMon", slot, channelStart, channelStop) 
