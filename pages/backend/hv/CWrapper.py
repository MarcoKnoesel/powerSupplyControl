import ctypes as ct

class CWrapper:
	def __init__(self) -> None:
		ct.cdll.LoadLibrary("libHVWrapper.so")
		self.libHVWrapper = ct.CDLL("libHVWrapper.so")

		self.libHVWrapper.initSystem.argtypes = [ct.c_int]
		self.libHVWrapper.initSystem.restype = ct.c_void_p 
		#print("[Py] Try to initialize system.")
		self.libHVWrapper.initSystem(0)

	def forceInitSystem(self) -> None:
		self.libHVWrapper.initSystem(1)

	# convert a single line of comma-separated values to an array of float values
	def csvLineToFloatArr(self, csvstr: str):
		# remove all whitespaces: newline, space, tab, ...
		csvstr = "".join(csvstr.split())

		positions = [0]
		for i in range(0, len(csvstr)):
			if csvstr[i] == ",":
				positions.append(i)
		positions.append(len(csvstr))

		data = []
		for i in range(0, len(positions) - 1):
			pos0 = positions[i] + 1
			pos1 = positions[i+1]
			if pos1 - pos0 < 1:
				data.append(None)
			else:
				try:
					data.append(float(csvstr[pos0:pos1]))
				# A value error will be raised when HVWrapper.c sends an error message,
				# for instance due to timeout.
				except ValueError:
					data.append(csvstr[pos0:pos1])

		return data

	# get an array of voltages or currents for a range of channels
	def getChParam(self, parameterName: str, slot: int, channelStart: int, channelStop: int  = -1):
		function = self.libHVWrapper.HVGetChParam
		function.argtypes = [ct.c_ushort, ct.c_ushort, ct.c_ushort, ct.c_char_p]
		# c_char_p would lead to automatic conversion to python byte_string,
		# which we don't want, so we can still apply free() on the pointer.
		# Therefore, restype = c_void:
		function.restype = ct.c_void_p 
		ptr = function(slot, channelStart, channelStop, parameterName.encode("utf-8"))
		bytes = ct.cast(ptr, ct.c_char_p).value
		self.free(ptr)
		reply = bytes.decode("utf-8")
		return self.csvLineToFloatArr(reply)

	# send a command and get the reply of the HV supply
	def receiveString(self, function, parameterStr: str = None, removeLF: bool = True) -> str:
		if parameterStr != None:
			function.argtypes = [ct.c_char_p]
		else:
			function.argtypes=[]
		# c_char_p would lead to automatic conversion to python byte_string,
		# which we don't want, so we can still apply free() on the pointer.
		# Therefore, restype = c_void:
		function.restype = ct.c_void_p 
		if parameterStr == None:
			ptr = function()
		else:
			ptr = function(parameterStr)
		bytes = ct.cast(ptr, ct.c_char_p).value
		self.free(ptr)
		reply = bytes.decode("utf-8")
		if removeLF:
			reply = reply.replace("\n", "")
		return reply
	
		# send a command and get the reply of the HV supply
	def login(self, function, user, pw, ip) -> str:
		function.argtypes = [ct.c_char_p, ct.c_char_p, ct.c_char_p]
		# c_char_p would lead to automatic conversion to python byte_string,
		# which we don't want, so we can still apply free() on the pointer.
		# Therefore, restype = c_void:
		function.restype = ct.c_void_p 
		ptr = function(user, pw, ip)
		bytes = ct.cast(ptr, ct.c_char_p).value
		self.free(ptr)
		reply = bytes.decode("utf-8")
		reply = reply.replace("\n", "")
		return reply

	# free memory of the C wrapper
	def free(self, ptr) -> None:
		self.libHVWrapper.freeMe.argtypes = [ct.c_void_p]
		self.libHVWrapper.freeMe.restype = None
		self.libHVWrapper.freeMe(ptr)
