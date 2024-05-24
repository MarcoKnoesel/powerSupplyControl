import pages.backend.hv.HVList as HVList
import pandas as pd

def channelParametersToDataframe(layer: int):

	cratesSlotsAndChannels = HVList.channelMap.layer_to_cratesSlotsChannels(layer)

	# get voltages and currents from the HV supply
	voltages = []
	targetVoltages = []
	currents = []
	rampUp = []
	rampDown = []
	for entry in cratesSlotsAndChannels:
		slot = entry[1]
		if slot == -1:
			continue
		hv = HVList.hvSupplyList[entry[0]]
		chStart = entry[2]
		chStop = entry[3]
		voltages = voltages + hv.measureVoltages(slot, chStart, chStop)
		targetVoltages = targetVoltages + hv.getTargetVoltages(slot, chStart, chStop)
		currents = currents + hv.measureCurrents(slot, chStart, chStop)
		rampUp = rampUp + hv.getRampSpeedUp(slot, chStart, chStop)
		rampDown = rampDown + hv.getRampSpeedDown(slot, chStart, chStop)

	if len(voltages) == 0:
		df = pd.DataFrame(["----",])
		df.columns = ["Not available."]
		return df

	# combine data to a signle two-dimensional array
	data = []
	for i in range(0, len(voltages)):
		if i < len(targetVoltages):
			tgtVolt = targetVoltages[i]
		else:
			tgtVolt = None
		if i < len(currents):
			current = currents[i]
		else:
			current = None
		if i < len(rampUp):
			rUp = rampUp[i]
		else:
			rUp = None
		if i < len(rampDown):
			rDown = rampDown[i]
		else:
			rDown = None
		data.append([slot, i + chStart, voltages[i], tgtVolt, current, rUp, rDown])

	# create and return dataframe
	df = pd.DataFrame(data)
	df.columns = ["Slot", "Channel", "Voltage (V) ⚡", "Target (V) 🎯", "Current (\u03BCA) 🌊", "Ramp up (V/s) 🛫", "Ramp down (V/s) 🛬"]
	df.index = df.index + chStart
	df.index.names = ["Channel"]

	return df
