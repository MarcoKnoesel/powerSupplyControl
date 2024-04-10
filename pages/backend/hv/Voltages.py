import pandas as pd

NUMBER_OF_SLOTS = 8
NUMBER_OF_CHANNELS = 48
MAXIMUM_ALLOWED_VOLTAGE = 1550
readVoltagesFromCSV_errors = []
readVoltagesFromCSV_warnings = []



def isComment(line: str) -> bool:
	for i in range(0, len(line)):
		c = line[i]
		#  ignore whitespaces
		if c != " " and c != "\t" and c != "\n":
			# check the first non-whitespace character
			if c == "#":
				return True
			else:
				return False
	# for empty lines or lines with whitespaces only: return True
	return True



def findPosOfCharInString(char: str, string: str):
	# only allow searching for single characters
	if len(char) != 1:
		return None
	positions = []
	for i in range(0, len(string)):
		if string[i] == char:
			positions.append(i)
	# char not found
	if len(positions) == 0:
		return None
	# return all positions of char
	return positions



def readVoltagesFromCSV():

	readVoltagesFromCSV_errors.clear()
	readVoltagesFromCSV_warnings.clear()

	voltages = []
	try:
		csvFile = open("pages/backend/hv/voltages.csv", "r")
	except:
		readVoltagesFromCSV_errors.append("CSV file for voltages not found!")
		return voltages
	
	csvList = csvFile.readlines()

	for line in csvList:
		if isComment(line):
			continue
		commaPositions = findPosOfCharInString(",", line)
		if commaPositions == None:
			readVoltagesFromCSV_warnings.append("Comma not found in line \"" + line + "\"! Line is ignored.")
			continue
		try:
			slot = int(line[0:commaPositions[0]])
		except:
			readVoltagesFromCSV_warnings.append("Conversion to integer value failed for the slot number in line \"" + str(line) + "\"! Line is ignored.")
			continue
		if slot < 0 or slot >= NUMBER_OF_SLOTS:
			readVoltagesFromCSV_warnings.append("Invalid slot number in line \"" + str(line) + "\"! Line is ignored.")
			continue
		try:
			channel = int(line[commaPositions[0] + 1:commaPositions[1]])
		except:
			readVoltagesFromCSV_warnings.append("Conversion to integer value failed for the channel number in line \"" + str(line) + "\"! Line is ignored.")
			continue
		if channel < 0 or channel >= NUMBER_OF_CHANNELS:
			readVoltagesFromCSV_warnings.append("Invalid channel number in line \"" + str(line) + "\"! Line is ignored.")
			continue
		try:
			voltage = float(line[commaPositions[1] + 1:])
		except:
			readVoltagesFromCSV_warnings.append("Conversion to float value failed for the voltage in line \"" + str(line) + "\"! Line is ignored.")
			continue
		if voltage < 0 or voltage > MAXIMUM_ALLOWED_VOLTAGE:
			readVoltagesFromCSV_warnings.append("Invalid voltage value in line \"" + str(line) + "\"! Line is ignored.")
			continue
		voltages.append([slot, channel, voltage])

	return voltages



def getVoltageDataframe():
	# get voltages and currents from the HV supply
	voltages = readVoltagesFromCSV()

	# create and return dataframe
	df = pd.DataFrame(voltages)
	df.columns = ["Slot", "Channel", "Voltage (V) ⚡"]

	return df