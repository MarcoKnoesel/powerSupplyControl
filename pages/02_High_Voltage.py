import streamlit as st
from datetime import datetime
import pages.backend.InitPowerSupplies as Init
import pages.backend.hv.HVList as HVList
import pages.backend.hv.CrateMap as CrateMap
import pages.backend.hv.ChannelParameters as ChannelParameters
import pages.backend.InfluxDB as InfluxDB
import pages.backend.hv.Voltages as Voltages

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

	if "password" not in st.session_state:
		st.session_state.password = ""

	if "loggedIn" not in st.session_state:
		st.session_state.loggedIn = False

	if "layerStr" not in st.session_state:
		st.session_state.layerStr = "Layer 0"

	if "showTimeoutInfo" not in st.session_state:
		st.session_state.showTimeoutInfo = False

	if "layer_voltage" not in st.session_state:
		st.session_state.layer_voltage = False

	if "targetVoltage" not in st.session_state:
		st.session_state.targetVoltage = -1

	# -------- Pause threads writing to InfluxDB --------

	InfluxDB.pauseHVThread(st.session_state.hvid)

	# -------- Title --------

	st.title("Caen HV Control :joystick:")

	# -------- Check connection --------

	connectionResult = st.session_state.hv.checkConnection()
	# No connection
	if connectionResult == 0:
		st.session_state.loggedIn = False
		loginInfoText = "Currently not logged in. :lock:"
	# After 1 minute, the connection breaks down. 
	# Then, all commands result in error code 5 or 4098.
	if connectionResult == 1:
		st.session_state.loggedIn = False
		# Try to log in again automatically.
		if st.session_state.hv.reconnect():
			loginInfoText = "Logged in! :unlock:"
			st.session_state.loggedIn = True
		else:
			loginInfoText = "Timeout. Please log in again."
	# Connection works.
	if connectionResult == 2:
		st.session_state.loggedIn = True
		loginInfoText = "Logged in! :unlock:"

	# -------- Device selection --------

	st.header(st.session_state.hv.name)

	top_col_1, top_col_2 = st.columns((6,2))
	top_col_2.image("svg/himeLogo.svg")

	selected_hv_name = top_col_1.selectbox("Choose an HV supply", HVList.hvSupplyNameList)

	# check if the selected HV is different from the current one 
	if selected_hv_name != st.session_state.hv.name:
		st.session_state.hv = HVList.getHV(selected_hv_name)
		st.rerun()

	# -------- Show whether you are logged in or not --------
	login_col_1, login_col_2 = top_col_1.columns(2)
	login_col_2.info(loginInfoText, icon = "ℹ️")

	# -------- Logged out --------

	if not st.session_state.loggedIn:
		
		def login() -> None:
			if st.session_state.hv.login(st.session_state.password):
				st.session_state.loggedIn = True
			st.session_state.password = ""
		
		login_col_1.text_input("Enter password for the HV supply", key = "password", type = "password", on_change = login)
		
		if st.session_state.showTimeoutInfo:
			st.info("Server not reachable, most probably due to timeout. Please log in again.", icon = "ℹ️")
			st.session_state.showTimeoutInfo = False

	# -------- Logged in --------

	else:

		# -------- Logout button --------
		def logOut() -> None:
			if st.session_state.hv.logout():
				st.session_state.loggedIn = False

		login_col_1.button("Logout", on_click = logOut)

		st.header("Switch the Complete HV Supply On/Off")
		switch_on_col, switch_off_col = st.columns(2)
		switch_on_col.button("Switch on all channels :rocket:", on_click = st.session_state.hv.pwOn_crate)
		switch_off_col.button("Switch off all channels :zzz:", on_click = st.session_state.hv.pwOff_crate)
		
		st.divider()

		# -------- Layers --------

		st.header("Set Voltage by Layer")

		layer_col1, layer_col2 = st.columns(2)

		layer_col1.selectbox("Choose a layer :roll_of_paper:", key="layerStr", 
			options = (
				"Layer 0", 
				"Layer 1", 
				"Layer 2", 
				"Layer 3"
			)
		)

		currentLayer = int(st.session_state.layerStr[6:])

		layer_col1.button("Switch layer on :rocket:", on_click = st.session_state.hv.pwOn_layer, args = (currentLayer,))
		layer_col1.button("Switch layer off :zzz:", on_click = st.session_state.hv.pwOff_layer, args = (currentLayer,))

		def changeLayerVoltage() -> None:
			if st.session_state.layer_voltage != None:
				st.session_state.hv.setVoltage_layer(currentLayer, st.session_state.layer_voltage)
				st.session_state.layer_voltage = None

		st.session_state.layer_voltage = layer_col2.number_input("Set target voltage for this layer (V) :level_slider:", value = None, placeholder = "Voltage (V)", min_value=0, max_value = 1550)
		if st.session_state.layer_voltage == None:
			layer_col2.metric("Target :dart:", "--")
		else:
			layer_col2.metric("Target :dart:", str(st.session_state.layer_voltage) + " V")

		layer_col2.button("Send target voltage to layer " + str(currentLayer) + " :satellite_antenna:", on_click=changeLayerVoltage, disabled=(st.session_state.layer_voltage == None))

		st.markdown("... and don't forget to press the `R` key to see the effect of your changes! :eyes:")

		col1, col2 = st.columns(2)

		if st.session_state.hv.isHorizontal(currentLayer):
			col1.subheader(st.session_state.layerStr + ": Left PMTs :arrow_left:")
			col2.subheader(st.session_state.layerStr + ": Right PMTs :arrow_right:")
		else:
			col1.subheader(st.session_state.layerStr + ": Top PMTs :arrow_up:")
			col2.subheader(st.session_state.layerStr + ": Bottom PMTs :arrow_down:")

		slotAndChs = st.session_state.hv.layerToSlotsAndChannels(currentLayer)
		df1 = ChannelParameters.channelParametersToDataframe(st.session_state.hv, slotAndChs[0][0], slotAndChs[0][1], slotAndChs[0][2])
		df2 = ChannelParameters.channelParametersToDataframe(st.session_state.hv, slotAndChs[1][0], slotAndChs[1][1], slotAndChs[1][2])
		col1.dataframe(df1, hide_index = True, height = round(5.5 * (df1.size + 1)) )
		col2.dataframe(df2, hide_index = True, height = round(5.5 * (df2.size + 1)) )

		st.markdown("Tip: Use `Shift + Mouse Wheel` to scroll left/right or choose \"Wide mode\" in the settings.")
		
		st.divider()

		# -------- Full Detector --------

		st.header("Set Voltages from CSV file")

		st.markdown(
			"On the left side, you can see the voltage values you defined in the csv file \
			`pages/backend/hv/voltages.csv`. \
			On the right side, you can send these voltages by clicking the corresponding button."
		)

		col_setVoltage_1, col_setVoltage_2 = st.columns(2)

		col_setVoltage_1.subheader("Imported from CSV file :clipboard:")

		col_setVoltage_1.dataframe(Voltages.getVoltageDataframe(), hide_index = True)

		for errorMessage in Voltages.readVoltagesFromCSV_errors:
			col_setVoltage_1.error(errorMessage, icon = "❗")
		
		for warningMessage in Voltages.readVoltagesFromCSV_warnings:
			col_setVoltage_1.warning(warningMessage, icon = "⚠️")

		col_setVoltage_2.subheader("Send voltages :satellite_antenna:")

		def setVoltagesFromCSV() -> None:
			voltagesFromCSV = Voltages.readVoltagesFromCSV()
			for i in range(0, len(voltagesFromCSV)):
					voltage = voltagesFromCSV[i][2]
					if voltage != None:
						st.session_state.hv.setVoltage_channel(voltagesFromCSV[i][0], voltagesFromCSV[i][1], voltage)


		col_setVoltage_2.button("Send voltages now", on_click = setVoltagesFromCSV)

		# -------- System Map --------

		st.divider()

		st.header("System Map :world_map:")

		st.dataframe(CrateMap.mapToDataframe(st.session_state.hv.getMap()), height = 620)

	# -------- Print error messages sent by the HV supply --------

	if st.session_state.hv.messages.isUpdated:
		st.session_state.hv.messages.print()

	# -------- Last updated --------

	st.divider()

	st.markdown("**Last updated:** " + datetime.now().strftime("%H:%M:%S"))

	# -------- Continue threads writing to InfluxDB --------

	InfluxDB.runAllThreads()