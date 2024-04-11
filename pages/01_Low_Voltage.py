import streamlit as st
import time
from datetime import datetime
import pages.backend.InitPowerSupplies as Init
import pages.backend.lv.LVList as LVList
import pages.backend.lv.TunableQuantity as tq
import pages.backend.lv.Register as Register
import pages.backend.InfluxDB as InfluxDB

# -------- Title of the page (displayed as tab name in the browser) --------

st.set_page_config("Low-Voltage Control", page_icon = "svg/icon.svg")

# -------- Initialize Power Supplies --------
# In each Python file that defines a new webpage, 
# `Init.init()` needs to be done at first
# in order start a new TCP socket for the LV supply
# and a C wrapper for the HV supply.
Init.init()

# -------- Hack to remove the +/- stepper buttons in st.number_input() --------
#
# -> Please replace this with a nicer solution (most likely: parameter in st.number_input() ),
# once it is implemented... 
#
# See GitHub issue: https://github.com/streamlit/streamlit/issues/894#issuecomment-1433112038

st.markdown("""
<style>
    button.step-up {display: none;}
    button.step-down {display: none;}
    div[data-baseweb] {border-radius: 4px;}
</style>""",
unsafe_allow_html=True)

# -------- Check if LV supplies have been defined --------

if len(LVList.lvSupplyList) == 0:
	st.warning("No LV supply found. You can define new LV supplies in `pages/backend/lv/LVDefinitions.py`.", icon = "⚠️")

else:
	# -------- Session-state variable definitions --------

	if "lvid" not in st.session_state:
		st.session_state.lvid = 0

	if "lv" not in st.session_state:
		st.session_state.lv = LVList.lvSupplyList[st.session_state.lvid]

	if "showDetails" not in st.session_state:
		st.session_state.showDetails = False

	# -------- Pause threads writing to InfluxDB --------

	InfluxDB.pauseLVThread(st.session_state.lvid)

	# -------- Title --------

	st.title("TDK Lambda LV Control :joystick:")

	# -------- Device selection --------

	st.header(st.session_state.lv.name)
	col_lvSelection_1, col_lvSelection_2, col_lvSelection_3 = st.columns((2,4,2))
	selected_lv_name = col_lvSelection_1.selectbox("Choose an LV supply", LVList.lvSupplyNameList)
	col_lvSelection_3.image("svg/himeLogo.svg")

	# check if the selected LV is different from the current one 
	if selected_lv_name != st.session_state.lv.name:
		st.session_state.lvid = LVList.getLVID(selected_lv_name)
		st.session_state.lv = LVList.lvSupplyList[st.session_state.lvid]
		st.rerun()

	# -------- Handle timeout --------
		
	try:
		st.session_state.lv.getMAC()
	except:
		st.session_state.lv.reconnect()
		st.info("The TCP connection was re-established automatically. \
			Most probably, it broke down due to the timeout of the LV supply.", icon = "ℹ️")

	# -------- Warnings --------

	detectedMac = st.session_state.lv.getMAC()
	# Right after timeout, the detectedMac is empty sometimes.
	# If so, wait a little and rerun().
	if detectedMac == "":
		time.sleep(0.1)
		st.rerun()
	if detectedMac != st.session_state.lv.manuallyEnteredMAC:
		st.warning("The detected MAC (\"" + detectedMac + "\") \
			is different from the manually entered one (\"" + st.session_state.lv.manuallyEnteredMAC + "\")! \
			You are probably talking to a different LV than you think! \
			Please check carefully and correct LVDefinitions.py afterwards.", icon = "⚠️")
		
	if st.session_state.lv.isInConstantCurrentMode():
		st.warning("This LV supply is in constant-current mode:\
			It will increase its output voltage until the target current is reached!", icon = "⚠️")

	# -------- Power output --------
		
	st.divider()

	st.header("Power Output :electric_plug:")

	col1, col2, col3, col4 = st.columns((2,1,2,2))

	lvIsOn = st.session_state.lv.isOn()

	togglePos = col1.toggle(":orange[Send]", value = lvIsOn)

	if togglePos == False and lvIsOn:
		st.session_state.lv.switchOff()
		time.sleep(0.5)
		st.rerun()

	if togglePos == True and not lvIsOn:
		st.session_state.lv.switchOn()
		time.sleep(0.5)
		st.rerun()

	if lvIsOn:
		col3.markdown(":green[**Status: ON**] :rocket:")
	else:
		col3.markdown(":red[**Status: OFF**] :zzz:")

	# -------- Voltage --------

	st.divider()

	tq.tunableQuantity("Voltage :zap:", "V", st.session_state.lv.minVoltage, st.session_state.lv.maxVoltage, st.session_state.lv.getTargetVoltage, st.session_state.lv.measureVoltage, st.session_state.lv.setTargetVoltage)

	# -------- Current --------

	st.divider()

	tq.tunableQuantity("Current :ocean:", "A", 0., 2., st.session_state.lv.getTargetCurrent, st.session_state.lv.measureCurrent, st.session_state.lv.setTargetCurrent)

	# -------- Details --------

	st.divider()

	st.header("Details :microscope:")

	def switchDetails(show: bool) -> None:
		st.session_state.showDetails = show

	if st.session_state.showDetails:
		st.button("Hide details", on_click=switchDetails, args=(False,))
	else:
		st.button("Show details", on_click=switchDetails, args=(True,))

	if st.session_state.showDetails:
		# -------- Network --------

		st.subheader("Network :globe_with_meridians:")

		networkTable = [
			["Hostname", str(st.session_state.lv.hostname)],
			["IP address", str(st.session_state.lv.ip)], 
			["MAC address", str(st.session_state.lv.mac)]]

		st.table(networkTable)

		# -------- Status --------

		st.divider()

		st.subheader("Status :gear:")
		
		st.markdown("**Mode of operation:** " + st.session_state.lv.getOperationModeDescription())

		registerNames = [
			"Questionable-condition register",
			"Standard-event status register",
			"Operational-condition register"
		]

		nBits = [16, 8, 16]

		registerFunctions = [
			st.session_state.lv.getQuestionableConditionRegister,
			st.session_state.lv.getStandardEventStatusRegister,
			st.session_state.lv.getOperationalConditionRegister
		]

		columnsStatus = st.columns(len(registerNames))

		for i in range(0, len(registerNames)):
			columnsStatus[i].markdown("**" + registerNames[i] + "**")
			columnsStatus[i].dataframe(
				Register.registerToDataframe(registerFunctions[i], nBits[i]),
				hide_index = True
			)

	# -------- Print error messages sent by the LV supply --------

	if st.session_state.lv.messages.isUpdated:
		st.session_state.lv.messages.print()

	# -------- Last updated --------

	st.markdown("**Last updated:** " + datetime.now().strftime("%H:%M:%S"))

	# -------- Continue threads writing to InfluxDB --------

	InfluxDB.runAllThreads()