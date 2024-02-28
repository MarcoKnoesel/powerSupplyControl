from pages.backend.lv.LVSupply import *
import streamlit as st

lvSupplyList = []
lvSupplyNameList = []
lvConnectionErrors = []

def define_lv(name: str, mac: str, ip: str, minVoltage: float, maxVoltage: float) -> None:
	if len(name) == 0 or name in lvSupplyNameList:
		errorMessage = "Please select unique and non-empty names for all your LV supplies. Otherwise, the corresponding LV definitions are ignored."
		if errorMessage not in lvConnectionErrors:
			lvConnectionErrors.append(errorMessage)
		return
	try:
		lv = LVSupply(name, mac, ip, minVoltage, maxVoltage)
		lvSupplyList.append(lv)
		lvSupplyNameList.append(lv.name)
	except OSError:
		errorMessage = "Could not connect to LV supply \"" + name + "\" "
		errorMessage += "with IP address \"" + ip + "\"!"
		lvConnectionErrors.append(errorMessage)

def getLVID(name: str) -> int:
	for i in range(0, len(lvSupplyNameList)):
		if lvSupplyNameList[i] == name:
			return i
	return 0

def showErrors() -> None:
	for errorMessage in lvConnectionErrors:
		st.error(errorMessage, icon = "❗")