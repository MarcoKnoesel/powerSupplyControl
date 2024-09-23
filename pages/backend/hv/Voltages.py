import pandas as pd
import pages.backend.hv.CSVHelper as csvh
import pages.backend.hv.HVList as HVList

readVoltagesFromCSV_errors = []
readVoltagesFromCSV_warnings = []
N_HIME_CHANNELS = 192



def readVoltagesFromCSV():

	readVoltagesFromCSV_errors.clear()
	readVoltagesFromCSV_warnings.clear()

	voltages = []
	try:
		csvFile = open("pages/backend/hv/voltages/2024-09-06_de.csv", "r")
	except:
		readVoltagesFromCSV_errors.append("CSV file for voltages not found!")
		return voltages
	
	csvList = csvFile.readlines()
	csvFile.close()

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

	seenChannels = []
	for entry in voltages:
		ch = entry[0]
		if ch in seenChannels:
			readVoltagesFromCSV_warnings.append("Channel " + str(ch) + " appears more than one time in the CSV file defining voltages!")
			continue
		if ch >= len(HVList.hvCratesSlotsChannels):
			readVoltagesFromCSV_warnings.append("Channel " + str(ch) + " listed in the CSV file doesn't exist!")
			continue
		else:
			if HVList.hvCratesSlotsChannels[ch] == [-1, -1, -1]:
				readVoltagesFromCSV_warnings.append("Channel " + str(ch) + " listed in the CSV file doesn't exist!")
				continue
		seenChannels.append(ch)

	# create and return dataframe
	df = pd.DataFrame(voltages)
	df.columns = ["HIME channel", "Voltage (V) ⚡"]

	return df
