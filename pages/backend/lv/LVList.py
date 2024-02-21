from pages.backend.lv.LVSupply import *

lvSupplyList = []
lvSupplyNameList = []

def define_lv(name: str, mac: str, ip: str, minVoltage: float, maxVoltage: float) -> None:
	lv = LVSupply(name, mac, ip, minVoltage, maxVoltage)
	lvSupplyList.append(lv)
	lvSupplyNameList.append(lv.name)

def getLVID(name: str) -> int:
	for i in range(0, len(lvSupplyNameList)):
		if lvSupplyNameList[i] == name:
			return i
	return 0