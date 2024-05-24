import pandas as pd
import pages.backend.hv.CSVHelper as csvh

readVoltagesFromCSV_errors = []
readVoltagesFromCSV_warnings = []
N_HIME_CHANNELS = 192



def readVoltagesFromCSV():

	readVoltagesFromCSV_errors.clear()
	readVoltagesFromCSV_warnings.clear()

	voltages = []
	try:
		csvFile = open("pages/backend/hv/voltages/2024-05-24.csv", "r")
	except:
		readVoltagesFromCSV_errors.append("CSV file for voltages not found!")
		return voltages
	
	csvList = csvFile.readlines()

	for line in csvList:
		if csvh.isComment(line):
			continue
		commaPositions = csvh.findPosOfCharInString(",", line)
		if commaPositions == None:
			readVoltagesFromCSV_warnings.append("Comma not found in line \"" + line + "\"! Line is ignored.")
			continue
		entryCounter = 0
		try:
			himeChannel = int(csvh.getEntry(line, commaPositions, entryCounter))
		except:
			readVoltagesFromCSV_warnings.append("Conversion to integer value failed for the HIME-channel number in line \"" + str(line) + "\"! Line is ignored.")
			continue
		if himeChannel < 0 or himeChannel >= N_HIME_CHANNELS:
			readVoltagesFromCSV_warnings.append("Invalid HIME-channel number in line \"" + str(line) + "\"! Line is ignored.")
			continue
		entryCounter += 1
		try:
			voltage = float(csvh.getEntry(line, commaPositions, entryCounter))
		except:
			readVoltagesFromCSV_warnings.append("Conversion to float value failed for the voltage in line \"" + str(line) + "\"! Line is ignored.")
			continue
		if voltage < 0:
			readVoltagesFromCSV_warnings.append("Invalid voltage value in line \"" + str(line) + "\"! Line is ignored.")
			continue
		voltages.append([himeChannel, voltage])

	return voltages



def getVoltageDataframe():
	# get voltages and currents from the HV supply
	voltages = readVoltagesFromCSV()

	# create and return dataframe
	df = pd.DataFrame(voltages)
	df.columns = ["HIME channel", "Voltage (V) ⚡"]

	return df