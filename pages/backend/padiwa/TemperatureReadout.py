import subprocess
import pages.backend.padiwa.PaDiWaList as PaDiWaList



def temperatureStringToArray(reply: str):
	entries = []
	entryStart = 0
	for i in range(0, len(reply)):
		if reply[i] == "\t":
			entry = reply[entryStart:i]
			entryStart = i + 1
			entries.append(entry)
		else:
			if i == len(reply) - 1:
				entry = reply[entryStart:]
				entries.append(entry)
	return entries



def getTemperatureString(address: str, chain: str) -> str:

	reply = ""

	# start the perl script that reads the PaDiWa temperature
	with subprocess.Popen(["perl", "/home/hime/trbsoft/daqtools/padiwa.pl", address, chain, "temp"], stdout = subprocess.PIPE) as p:
		
		# the reply has the form 
		#    [FPGA address]\t[DAC chain]\t[temperature in degree Celsius]\n
		reply = p.stdout.read().decode()

		# request the return code, so that p can be garbage collected
		p.wait()

		# kill the subprocess
		p.kill()

	if len(reply) == 0:
		return "0"
	
	# remove \n at the end of the reply
	if reply[-1] == "\n":
		reply = reply[:-1]

	# store all tab-separated entries in an array
	entries = temperatureStringToArray(reply)

	# return temperature
	return entries[2]

def getTemperature(address: str, chain: str) -> float:
	return float(getTemperatureString(address, chain))