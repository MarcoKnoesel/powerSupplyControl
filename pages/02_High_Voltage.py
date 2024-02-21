import streamlit as st
import pandas as pd
from datetime import datetime
import pages.backend.hv.HVSupply as HVSupply
import pages.backend.InitPowerSupplies as Init
import pages.backend.hv.HVList as HVList
import pages.backend.hv.CrateMap as CrateMap

# -------- Title of the page (displayed as tab name in the browser) --------

st.set_page_config("High-Voltage Control")

# -------- Initialize Power Supplies --------
# In each Python file that defines a new webpage, 
# `Init.init()` needs to be done at first
# in order start a new TCP socket for the LV supply
# and a C wrapper for the HV supply.
Init.init()

# -------- Session-state and function definitions --------

if "hv" not in st.session_state:
	st.session_state.hv = HVList.hvSupplyList[0]

def checkConnection() -> int:
	#print("checkConnection")
	reply = st.session_state.hv.getMap()
	# no connection; most probably due to timeout
	if reply == "!!5" or reply == "!!4098":
		return 1
	# device already open
	if reply == "!!24":
		return 2
	# no connection 
	if reply[0:2] == "!!":
		return 0
	# connection works
	return 2

# initialization for each new session
if "password" not in st.session_state:
	st.session_state.password = ""

if "loggedIn" not in st.session_state:
	st.session_state.loggedIn = False

if "layer" not in st.session_state:
	st.session_state.layer = "Layer 0"

if "showTimeoutInfo" not in st.session_state:
	st.session_state.showTimeoutInfo = False

def isError(source: str, message: str) -> bool:
	#print("isError")
	# Timeout -> simply rerun the script, so checkConnection()
	# can take care of that
	if message == "!!5" or message == "!!4098":
		st.rerun()
	# Error messages start with "!!"
	if len(message) < 2:
		return False
	# Extract the error code, if present
	if message[0:2] == "!!":
		errorMessage = "[" + source + "]"
		if(len(message) < 3):
			errorMessage = errorMessage + "Unknown error"
		else:
			errorMessage = errorMessage + message[2:]
		st.error(errorMessage, icon = "❗")
		return True
	return False

def logIn() -> None:
	if not len(st.session_state.password): 
		return
	#print("logIn")
	reply = st.session_state.hv.login(st.session_state.password)
	st.session_state.password = ""
	if reply == "!!4103":
		st.error("Wrong password.", icon = "❗")
		return
	if not isError("logIn", reply):
		st.session_state.loggedIn = True
		st.rerun()
	
def logOut() -> None:
	#print("logOut")
	st.session_state.hv.logout()
	st.session_state.loggedIn = False

def getMap():
	#print("getMap")
	reply = st.session_state.hv.getMap()
	if isError("getMap", reply):
		return ""
	return reply

def channelParametersToDataframe(hv: HVSupply.HVSupply, slot: int, channelStart: int, channelStop: int = -1):
	# get voltages and currents from the HV supply
	voltages = hv.measureVoltages(slot, channelStart, channelStop)
	currents = hv.measureCurrents(slot, channelStart, channelStop)

	if isError("channelParametersToDataframe", str(voltages[0])):
		return pd.DataFrame()
	if isError("channelParametersToDataframe", str(currents[0])):
		return pd.DataFrame()

	# combine data to a single two-dimensional array
	data = []
	for i in range(0, len(voltages)):
		if i < len(currents):
			current = currents[i]
		else:
			current = None
		data.append([i + channelStart, slot, voltages[i], current])

	# create and return dataframe
	df = pd.DataFrame(data)
	df.columns = ["Channel", "Slot", "Voltage (V) ⚡", "Current (A) 🌊"]
	df.index = df.index + channelStart
	df.index.names = ["Channel"]

	return df

def layerStrToInt(layerStr: str) -> int:
	return int(layerStr[6:])

def layerToSlotAndChannels(layer: int):
	return [[layer, 0, 24], [layer, 24, 48]]

# -------- Check connection --------

connectionResult = checkConnection()
# No connection
if connectionResult == 0:
	st.session_state.loggedIn = False
	loginInfoText = "Currently not logged in. :lock:"
# After 1 minute, the connection breaks down. 
# Then, all commands result in error code 5 or 4098.
# Before logging in again, logOut() and hv.forceInitCWrapper are required.
# Otherwise, logIn() will not work.
if connectionResult == 1:
	logOut()
	st.session_state.hv.forceInitCWrapper()
	loginInfoText = "Timeout. Please log in again."
# Connection works.
if connectionResult == 2:
	st.session_state.loggedIn = True
	loginInfoText = "Logged in! :unlock:"

# # # # # # # # # # # # #
#                       #
#   Page starts here    #
#                       #
# # # # # # # # # # # # #

# -------- Title --------

st.title("Caen HV Control :joystick:")


# -------- Device selection --------

st.header(st.session_state.hv.name)

selected_hv_name = st.selectbox("Choose an HV supply", HVList.hvSupplyNameList)

# check if the selected HV is different from the current one 
if selected_hv_name != st.session_state.hv.name:
	st.session_state.hv = HVList.getHV(selected_hv_name)
	st.rerun()

# -------- Logged out --------

if not st.session_state.loggedIn:
	login_col_1, login_col_2 = st.columns((3,7))
	login_col_1.text_input("Enter password for the HV supply", key = "password", type = "password", on_change = logIn())
	login_col_2.info(loginInfoText, icon = "ℹ️")
	if st.session_state.showTimeoutInfo:
		st.info("Server not reachable, most probably due to timeout. Please log in again.", icon = "ℹ️")
		st.session_state.showTimeoutInfo = False

# -------- Logged in --------

else:
	logout_col_1, logout_col_2 = st.columns((3,7))
	logout_col_1.button("Log out", on_click = logOut)
	logout_col_2.info(loginInfoText, icon = "ℹ️")
	
	st.divider()

	st.header("Measured Voltages and Currents :triangular_ruler:")

	st.session_state.layer = st.selectbox("Choose a layer :roll_of_paper:", 
		(
			"Layer 0", 
			"Layer 1", 
			"Layer 2", 
			"Layer 3"
		)
	)

	col1, col2 = st.columns(2)

	layer = layerStrToInt(st.session_state.layer)
	if layer % 2 == 0:
		col1.subheader(st.session_state.layer + ": Left PMTs :arrow_left:")
		col2.subheader(st.session_state.layer + ": Right PMTs :arrow_right:")
	else:
		col1.subheader(st.session_state.layer + ": Bottom PMTs :arrow_down:")
		col2.subheader(st.session_state.layer + ": Top PMTs :arrow_up:")

	slotAndChs = layerToSlotAndChannels(layer)
	col1.dataframe(channelParametersToDataframe(st.session_state.hv, slotAndChs[0][0], slotAndChs[0][1], slotAndChs[0][2]), hide_index = True, height = 900)
	col2.dataframe(channelParametersToDataframe(st.session_state.hv, slotAndChs[1][0], slotAndChs[1][1], slotAndChs[1][2]), hide_index = True, height = 900)

	st.divider()

	st.header("System Map :world_map:")

	st.dataframe(CrateMap.mapToDataframe(getMap()), height = 620)

# -------- Last updated --------

st.divider()

st.markdown("**Last updated:** " + datetime.now().strftime("%H:%M:%S"))