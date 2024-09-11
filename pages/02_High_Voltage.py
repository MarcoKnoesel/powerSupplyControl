import streamlit as st
from datetime import datetime
import pages.backend.InitPowerSupplies as Init
import pages.backend.hv.HVList as HVList
import pages.backend.hv.CrateMap as CrateMap
import pages.backend.InfluxDB as InfluxDB
import pages.backend.hv.HIMEConstants as HIMEConstants
import pages.backend.hv.FullDetector as FullDetector
import pages.backend.hv.Layer as Layer
import pages.backend.hv.SingleChannel as SingleChannel
import pages.backend.hv.LoginLoop as LoginLoop

# -------- Title of the page (displayed as tab name in the browser) --------

st.set_page_config("High-Voltage Control", page_icon = "svg/icon.svg")

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

# -------- Check if HV supplies have been defined --------
if len(HVList.hvSupplyList) == 0:
	st.warning("No HV supply found. You can define new HV supplies in `pages/backend/hv/HVDefinitions.py`.", icon = "⚠️")

else:
	# -------- Session-state variable definitions --------

	if "hvid" not in st.session_state:
		st.session_state.hvid = 0

	if "hv" not in st.session_state:
		st.session_state.hv = HVList.hvSupplyList[st.session_state.hvid]

	if "loggedIn" not in st.session_state:
		st.session_state.loggedIn = False

	if "layerStr" not in st.session_state:
		st.session_state.layerStr = "Layer 0"

	if "layer_voltage" not in st.session_state:
		st.session_state.layer_voltage = None

	if "channel_voltage" not in st.session_state:
		st.session_state.channel_voltage = -1

	if "session_state.hime_channel" not in st.session_state:
		st.session_state.hime_channel = None

	# -------- Pause threads writing to InfluxDB --------

	InfluxDB.pauseHVThread(st.session_state.hvid)

	# -------- Title --------

	st.title("Caen HV Control :joystick:")

	# -------- Check connection --------
	for hv in HVList.hvSupplyList:
		connectionResult = hv.checkConnection()
		# No connection
		if connectionResult == 0:
			hv.loggedIn = False
			hv.loginInfoText = "Currently not logged in. :lock:"
		# After 1 minute, the connection breaks down. 
		# Then, all commands result in error code 5 or 4098.
		if connectionResult == 1:
			hv.loggedIn = False
			# Try to log in again automatically.
			if hv.reconnect():
				hv.loginInfoText = "Logged in! :unlock:"
				hv.loggedIn = True
			else:
				hv.loginInfoText = "Timeout. Please log in again."
		# Connection works.
		if connectionResult == 2:
			hv.loggedIn = True
			hv.loginInfoText = "Logged in! :unlock:"

	# -------- Check whether you are logged in or not --------

	st.session_state.loggedIn = True

	for hv in HVList.hvSupplyList:
		if not hv.loggedIn:
			st.session_state.loggedIn = False
			break

	# -------- Log in/out; show logo --------

	top_col_1, top_col_2 = st.columns((6,2))
	top_col_2.image("svg/himeLogo.svg")

	# -------- Logged out --------

	if not st.session_state.loggedIn:

		login_cols = top_col_1.columns(2)
		LoginLoop.show(login_cols[0])
		
	# -------- Logged in --------

	else:

		# -------- Logout button --------
		def logOut() -> None:
			for hv in HVList.hvSupplyList:
				if hv.logout():
					hv.loggedIn = False
				else:
					st.error("Logout failed for " + hv.name, icon = "❗")

		top_col_1.button("Log out from all HV supplies", on_click = logOut)
		top_col_1.markdown("You are logged in to:")
		for hv in HVList.hvSupplyList:
			top_col_1.markdown("🟢  " + hv.name)

		st.button("Switch all channels off", on_click=FullDetector.switchAllChannelsOff)
		
		st.divider()

		# -------- Layers --------

		st.header("Set Voltage by Layer")

		Layer.show()

		st.divider()

		# -------- Full Detector --------

		st.header("Set Voltages from CSV file")

		FullDetector.show()

		#print(HVList.hvSupplyList[0].cw.getChParam("VMon", 0, 0, 8))
		#print(HVList.hvSupplyList[0].cw.getChParam("V0Set", 0, 0, 8))
		#print(HVList.hvSupplyList[0].cw.getChParam("Pw", 0, 0, 8))

		st.divider()

		# -------- Individual channel --------
		
		st.header("Individual Channel")
		st.markdown("The HIME channel is given by FPGA x 48 + DAC chain x 16 + PaDiWa channel.")

		individualChannel_cols = st.columns(3)
		
		st.session_state.hime_channel = individualChannel_cols[0].number_input("HIME channel", value = None, placeholder = "HIME-channel number", min_value=0, max_value = HIMEConstants.N_HIME_CHANNELS)
		st.session_state.channel_voltage = individualChannel_cols[1].number_input("Set target voltage (V) :level_slider:", value = None, placeholder = "Voltage (V)", min_value=0, max_value = 1550)
		
		SingleChannel.show(st.session_state.hime_channel, individualChannel_cols)

		# -------- System Map --------

		st.divider()

		st.header("System Map :world_map:")

		st.subheader(st.session_state.hv.name)
		selected_hv_name = st.selectbox("Choose an HV supply", HVList.hvSupplyNameList)

		# check if the selected HV is different from the current one 
		if selected_hv_name != st.session_state.hv.name:
			st.session_state.hv = HVList.getHV(selected_hv_name)
			st.rerun()

		st.dataframe(CrateMap.mapToDataframe(st.session_state.hv.getMap()), height = 620)

	# -------- Print error, warning and information messages --------
	for hv in HVList.hvSupplyList:
		if hv.messages.isUpdated:
			hv.messages.print()

	if HVList.channelMap.messages.isUpdated:
		HVList.channelMap.messages.print()

	# -------- Last updated --------

	st.divider()

	st.markdown("**Last updated:** " + datetime.now().strftime("%H:%M:%S"))

	# -------- Continue threads writing to InfluxDB --------

	InfluxDB.runAllThreads()
