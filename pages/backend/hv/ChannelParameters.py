import pages.backend.hv.HVSupply as HVSupply
import pandas as pd

def channelParametersToDataframe(hv: HVSupply, slot: int, channelStart: int, channelStop: int = -1):

	# get voltages and currents from the HV supply
	voltages = hv.measureVoltages(slot, channelStart, channelStop)
	currents = hv.measureCurrents(slot, channelStart, channelStop)

	# combine data to a signle two-dimensional array
	data = []
	for i in range(0, len(voltages)):
		if i < len(currents):
			current = currents[i]
		else:
			current = None
		data.append([slot, i + channelStart, voltages[i], current])

	# create and return dataframe
	df = pd.DataFrame(data)
	df.columns = ["Slot", "Channel", "Voltage (V) ⚡", "Current (A) 🌊"]
	df.index = df.index + channelStart
	df.index.names = ["Channel"]

	return df
