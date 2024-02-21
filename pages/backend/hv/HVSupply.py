import pages.backend.hv.CWrapper as CWrapper
import ctypes

class HVSupply:
	def __init__(self, name: str, ip: str) -> None:
		self.name = name
		self.ip = ip
		self.cw = CWrapper.CWrapper()

	def login(self, password: str) -> str:
		password = ctypes.create_string_buffer(password.encode("utf-8"))
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogin, password)
		return reply

	def logout(self) -> str:
		reply = self.cw.receiveString(self.cw.libHVWrapper.HVSystemLogout)
		return reply
	
	def forceInitCWrapper(self) -> None:
		self.cw.forceInitSystem()

	def getMap(self) -> str:
		return self.cw.receiveString(self.cw.libHVWrapper.HVGetCrateMap, removeLF = False)
	
	def measureVoltages(self, slot: int, channelStart: int, channelStop: int = -1):
		return self.cw.getChParam("VMon", slot, channelStart, channelStop)
	
	def measureCurrents(self, slot: int, channelStart: int, channelStop: int = -1):
		return self.cw.getChParam("IMon", slot, channelStart, channelStop) 
