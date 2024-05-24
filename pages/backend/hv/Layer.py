import pages.backend.InitPowerSupplies as Init
import pages.backend.hv.HVList as HVList

def pwOn(layer: int) -> str:
	cratesSlotsChannels = Init.channelMap.layer_to_cratesSlotsChannels(layer)
	reply = ""
	for entry in cratesSlotsChannels:
		crate = entry[0]
		slot = entry[1]
		chStart = entry[2]
		chStop = entry[2]
		reply += HVList.hvSupplyList[crate].pwOn_slotAndChannels(slot, chStart, chStop)
	return reply

def pwOff(layer: int) -> str:
	cratesSlotsChannels = Init.channelMap.layer_to_cratesSlotsChannels(layer)
	reply = ""
	for entry in cratesSlotsChannels:
		crate = entry[0]
		slot = entry[1]
		chStart = entry[2]
		chStop = entry[2]
		reply += HVList.hvSupplyList[crate].pwOff_slotAndChannels(slot, chStart, chStop)
	return reply

def setVoltage(layer: int, voltage) -> str:
	cratesSlotsChannels = Init.channelMap.layer_to_cratesSlotsChannels(layer)
	reply = ""
	for entry in cratesSlotsChannels:
		crate = entry[0]
		slot = entry[1]
		chStart = entry[2]
		chStop = entry[2]
		reply += HVList.hvSupplyList[crate].setVoltage_slotAndChannels(slot, chStart, chStop, voltage)
	return reply

def isHorizontal(layer: int) -> bool:
	return layer % 2 == 0