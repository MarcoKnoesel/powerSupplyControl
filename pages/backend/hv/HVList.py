import pages.backend.hv.HVSupply as HVSupply

hvSupplyList = []
hvSupplyNameList = []

def define_hv(name: str, ip: str) -> None:
	hv = HVSupply.HVSupply(name, ip)
	hvSupplyList.append(hv)
	hvSupplyNameList.append(hv.name)

def getHV(name: str):
	for i in range(0, len(hvSupplyNameList)):
		if hvSupplyNameList[i] == name:
			return hvSupplyList[i]