import pages.backend.hv.HVList as HVList
import pages.backend.hv.HIMEConstants as HIMEConstants
import pandas as pd

#TODO add the following information in channelMapping CSV: 
# - is the PMT left/bottom or right/top?
# - layer
# - module

def appendCircle(status: str) -> str:
	if status == "On":
		return status + " 🟢"
	return status + " 🔴"


def channelParametersToDataframe(layer: int):

	cratesSlotsAndChannels = HVList.channelMap.layer_to_cratesSlotsChannels(layer)

	# get voltages and currents from the HV supply
	voltages = []
	targetVoltages = []
	currents = []
	rampUp = []
	rampDown = []
	#statusList = []
	moduleIDs = []
	positions = []
	himeChannels = []

	for entry in cratesSlotsAndChannels:

		slot = entry[1]
		if slot == -1:
			continue
		crate = entry[0]
		hv = HVList.hvSupplyList[crate]
		chStart = entry[2]
		chStop = entry[3]
		voltages += hv.measureVoltages(slot, chStart, chStop)
		targetVoltages += hv.getTargetVoltages(slot, chStart, chStop)
		currents += hv.measureCurrents(slot, chStart, chStop)
		rampUp += hv.getRampSpeedUp(slot, chStart, chStop)
		rampDown += hv.getRampSpeedDown(slot, chStart, chStop)
		#statusList += hv.getStatus_slotAndChannels(slot, chStart, chStop)
		for channel in range(chStart, chStop):
			himeCh = HVList.channelMap.crateSlotAndChannel_to_himeCh(crate, slot, channel)
			himeChannels.append(himeCh)
			chDetails = HVList.channelMap.getChannelDetails(himeCh)
			layer = chDetails[3]
			moduleIDs.append(chDetails[4] + layer * HIMEConstants.N_MODULES_PER_LAYER)
			positions.append(chDetails[5])

	#print("voltages: " + str(len(voltages)))
	#print("targetVoltages: " + str(len(targetVoltages)))
	#print("currents: " + str(len(currents)))
	#print("rampUp: " + str(len(rampUp)))
	#print("rampDown: " + str(len(rampDown)))
	#print("moduleIDs: " + str(len(moduleIDs)))
	#print("positions: " + str(len(positions)))
	#print("himeChannels: " + str(len(himeChannels)))
	#print("statusList: " + str(len(statusList)))
	if len(voltages) == 0:
		df = pd.DataFrame(["----",])
		df.columns = ["Not available."]
		return [df,df]

	# combine the data to two arrays:
	# one for the PMTs on the bottom or right side, 
	# another one for the top or left side
	data = [[],[]]
	for i in range(0, len(voltages)):
		position = positions[i]
		data[position].append([moduleIDs[i], himeChannels[i], #appendCircle(statusList[i]), 
						 voltages[i], targetVoltages[i], currents[i], rampUp[i], rampDown[i]])

	# create dataframes
	# iterate over bottom/right and top/left
	dfList = []
	for pos in [0,1]:
		dfList.append(pd.DataFrame(data[pos]))
		dfList[pos].columns = ["Module ID", "Channel",# "Status", 
						 "Voltage (V) ⚡", "Target (V) 🎯", "Current (\u03BCA) 🌊", "Ramp up (V/s) 🛫", "Ramp down (V/s) 🛬"]

	return dfList
