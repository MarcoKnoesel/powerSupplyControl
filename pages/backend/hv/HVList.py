import pages.backend.hv.HVSupply as HVSupply
import streamlit as st

hvSupplyList = []
hvSupplyNameList = []
hvConnectionErrors = []
hvCratesSlotsChannels = []
himeChannels = []
himeLayers = []

def define_hv(name: str, user: str, ip: str) -> None:
	if len(name) == 0 or name in hvSupplyNameList:
		errorMessage = "Please select unique and non-empty names for all your HV supplies. Otherwise, the corresponding HV definitions are ignored."
		if errorMessage not in hvConnectionErrors:
			hvConnectionErrors.append(errorMessage)
		return
	hv = HVSupply.HVSupply(name, user, ip)
	hvSupplyList.append(hv)
	hvSupplyNameList.append(hv.name)

def getHV(name: str):
	for i in range(0, len(hvSupplyNameList)):
		if hvSupplyNameList[i] == name:
			return hvSupplyList[i]
		
def showErrors() -> None:
	for errorMessage in hvConnectionErrors:
		st.error(errorMessage, icon = "❗")