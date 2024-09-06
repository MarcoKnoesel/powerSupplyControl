import streamlit as st
import pages.backend.hv.HVList as HVList
import pages.backend.hv.Voltages as Voltages
import pages.backend.hv.CSVHelper as csvh

def setVoltagesFromCSV() -> None:
	voltagesFromCSV = Voltages.readVoltagesFromCSV()
	for i in range(0, len(voltagesFromCSV)):
			voltage = voltagesFromCSV[i][1]
			himeChannel = voltagesFromCSV[i][0]
			cratesSlotsAndChannels = HVList.hvCratesSlotsChannels[himeChannel]
			if voltage != None and cratesSlotsAndChannels[0] != -1:
				crate = cratesSlotsAndChannels[0]
				slot = cratesSlotsAndChannels[1]
				hvChannel = cratesSlotsAndChannels[2]
				HVList.hvSupplyList[crate].setVoltage_channel(slot, hvChannel, voltage)

def show() -> None:
	st.markdown(
		"On the left side, you can see the voltage values you defined in the csv file \
		`pages/backend/hv/voltages.csv`. \
		On the right side, you can send these voltages by clicking the corresponding button."
	)

	col_setVoltage_1, col_setVoltage_2 = st.columns(2)

	col_setVoltage_1.subheader("Imported from CSV file :clipboard:")

	col_setVoltage_1.dataframe(Voltages.getVoltageDataframe(), hide_index = True)

	for errorMessage in Voltages.readVoltagesFromCSV_errors:
		col_setVoltage_1.error(errorMessage, icon = "❗")
	
	for warningMessage in Voltages.readVoltagesFromCSV_warnings:
		col_setVoltage_1.warning(warningMessage, icon = "⚠️")

	col_setVoltage_2.subheader("Send voltages :satellite_antenna:")
#TODO specify filename of the CSV file on the webpage

	col_setVoltage_2.button("Send voltages now", on_click = setVoltagesFromCSV)



def switchAllChannelsOff() -> None:

	for hv in HVList.hvSupplyList:
		map = hv.getMap()

		# lines of the channel map
		lines = []
		# positions of the new-line character \n
		newLinePositions = csvh.findPosOfCharInString("\n", map)

		# Read the crate map as a list of lines, 
		# each one representing an HV slot.
		# Each line contains information on the board type, the serial number, etc.
		# and in particular -- what we need here -- the number of channels
		for i in range(0, len(newLinePositions)):
			lines.append(csvh.getEntry(map, newLinePositions, i))
		# Extract the number of channels for each slot.
		# The channel map is oredered,
		# so the slot number is equal to the line number
		for i in range(0, len(lines)):
			line = lines[i]
			if line[0] == "-":
				continue
			commaPositions = csvh.findPosOfCharInString(",", line)
			nCh = csvh.getEntry(line, commaPositions, 2)
			print(hv.name)
			hv.pwOff_slotAndChannels(i, 0, int(nCh))
