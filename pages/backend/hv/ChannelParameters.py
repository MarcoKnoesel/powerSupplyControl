import pages.backend.hv.HVSupply as HVSupply
import pandas as pd

def channelParametersToDataframe(hv: HVSupply, slot: int, channelStart: int, channelStop: int = -1):

	if slot == -1:
		df = pd.DataFrame(["----",])
		df.columns = ["Not available."]
		return df

	# get voltages and currents from the HV supply
	voltages = hv.measureVoltages(slot, channelStart, channelStop)
	targetVoltages = hv.getTargetVoltages(slot, channelStart, channelStop)
	currents = hv.measureCurrents(slot, channelStart, channelStop)
	rampUp = hv.getRampSpeedUp(slot, channelStart, channelStop)
	rampDown = hv.getRampSpeedDown(slot, channelStart, channelStop)

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
		data.append([slot, i + channelStart, voltages[i], tgtVolt, current, rUp, rDown])

	# create and return dataframe
	df = pd.DataFrame(data)
	df.columns = ["Slot", "Channel", "Voltage (V) ⚡", "Target (V) 🎯", "Current (\u03BCA) 🌊", "Ramp up (V/s) 🛫", "Ramp down (V/s) 🛬"]
	df.index = df.index + channelStart
	df.index.names = ["Channel"]

	return df
