import streamlit as st
from datetime import datetime
import pages.backend.InitPowerSupplies as Init
import pages.backend.hv.HVList as HVList
import pages.backend.hv.CrateMap as CrateMap
import pages.backend.hv.ChannelParameters as ChannelParameters
import pages.backend.InfluxDB as InfluxDB
import pages.backend.hv.Voltages as Voltages
import pages.backend.hv.Layer as Layer
import pages.backend.hv.HIMEConstants as HIMEConstants

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

	if "layer_voltage" not in st.session_state:
		st.session_state.layer_voltage = False

	if "targetVoltage" not in st.session_state:
		st.session_state.targetVoltage = -1

	if "session_state.hime_channel" not in st.session_state:
		st.session_state.hime_channel = None

	# -------- Pause threads writing to InfluxDB --------

	InfluxDB.pauseHVThread(st.session_state.hvid)

	# -------- Title --------

	st.title("Caen HV Control :joystick:")

	# -------- Check connection --------
	loggedInList = [False * len(HVList.hvSupplyList)]

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

		login_cols = []
		for i in range(0, len(HVList.hvSupplyList)):
			c0, c1 = top_col_1.columns(2)
			login_cols.append([c0, c1])
			hv = HVList.hvSupplyList[i]
			login_cols[i][1].info(hv.loginInfoText, icon = "ℹ️")
		
		def login(hv) -> None:
			if hv.login(st.session_state.password):
				hv.loggedIn = True
			st.session_state.password = ""
		
		for hv in HVList.hvSupplyList:
			login_cols[i][0].text_input("Enter password for " + str(hv.name), key = "password", type = "password", on_change = login, args=(hv,))
		
	# -------- Logged in --------

	else:

		# -------- Logout button --------
		def logOut() -> None:
			for hv in HVList.hvSupplyList:
				if hv.logout():
					hv.loggedIn = False

		top_col_1.button("Log out from all HV supplies", on_click = logOut)
		top_col_1.markdown("You are logged in to:")
		for hv in HVList.hvSupplyList:
			top_col_1.markdown(hv.name)
		
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

		layer_col1.button("Switch layer on :rocket:", on_click = Layer.pwOn, args = (currentLayer,))
		layer_col1.button("Switch layer off :zzz:", on_click = Layer.pwOff, args = (currentLayer,))

		def changeLayerVoltage() -> None:
			if st.session_state.layer_voltage != None:
				Layer.setVoltage(currentLayer, st.session_state.layer_voltage)
				st.session_state.layer_voltage = None

		st.session_state.layer_voltage = layer_col2.number_input("Set target voltage for this layer (V) :level_slider:", value = None, placeholder = "Voltage (V)", min_value=0, max_value = 1550)
		if st.session_state.layer_voltage == None:
			layer_col2.metric("Target :dart:", "--")
		else:
			layer_col2.metric("Target :dart:", str(st.session_state.layer_voltage) + " V")

		layer_col2.button("Send target voltage to layer " + str(currentLayer) + " :satellite_antenna:", on_click=changeLayerVoltage, disabled=(st.session_state.layer_voltage == None))

		st.subheader("Channel Parameters")

		st.markdown("Tip: Use `Shift + Mouse Wheel` to scroll left/right or choose \"Wide mode\" in the settings.")	  
		st.markdown("...and don't forget to press the `R` key to see the effect of your voltage settings! :eyes:")

		channelPar_col0, channelPar_col1 = st.columns(2)

		if Layer.isHorizontal(currentLayer):
			channelPar_col0.markdown("**" + st.session_state.layerStr + ": Left PMTs** :arrow_left:")
			channelPar_col1.markdown("**" + st.session_state.layerStr + ": Right PMTs** :arrow_right:")
		else:
			channelPar_col0.markdown("**" + st.session_state.layerStr + ": Top PMTs** :arrow_up:")
			channelPar_col1.markdown("**" + st.session_state.layerStr + ": Bottom PMTs** :arrow_down:")
		
		dfList = ChannelParameters.channelParametersToDataframe(currentLayer)
		for pos in [0,1]:
			[channelPar_col0, channelPar_col1][pos].dataframe(dfList[pos], hide_index = True, height = round(5.5 * (dfList[pos].size + 1)) )
		#df.index = df.index + chStart
		#df.index.names = ["Channel"]

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
#TODO specify filename of the CSV file on the webpage
		def setVoltagesFromCSV() -> None:
			voltagesFromCSV = Voltages.readVoltagesFromCSV()
			for i in range(0, len(voltagesFromCSV)):
					voltage = voltagesFromCSV[i][1]
					himeChannel = voltagesFromCSV[i][0]
					cratesSlotsAndChannels = HVList.hvCratesSlotsChannels[himeChannel]
					if voltage != None and cratesSlotsAndChannels[0] != -1:
						crate = cratesSlotsAndChannels[0]
						slot = cratesSlotsAndChannels[1]
						hvChannel = cratesSlotsAndChannels[2]
						HVList.hvSupplyList[crate].setVoltage_channel(slot, hvChannel, voltage)

#TODO set voltages for individual channels and show mapping from crate,slot,hvChannel to fpga,dacChain,padiwaChannel

		col_setVoltage_2.button("Send voltages now", on_click = setVoltagesFromCSV)

		st.divider()

		# -------- Individual channel --------
		
		st.header("Individual Channel")

		st.markdown("The HIME channel is given by FPGA x 48 + DAC chain x 16 + PaDiWa channel.")
#TODO status, voltage setting
		individualChannel_cols = [st.columns(3), st.columns(3), st.columns(3), st.columns(3), st.columns(3)]
		st.session_state.hime_channel = individualChannel_cols[0][0].number_input("HIME channel :level_slider:", value = None, placeholder = "HIME-channel number", min_value=0, max_value = HIMEConstants.N_HIME_CHANNELS)
		if st.session_state.hime_channel != None:
			channelDetails = HVList.channelMap.getChannelDetails(st.session_state.hime_channel)
			if channelDetails != None:
				individualChannel_cols[1][0].metric("FPGA", str(channelDetails[0]))
				individualChannel_cols[1][1].metric("DAC chain", str(channelDetails[1]))
				individualChannel_cols[1][2].metric("PaDiWa channel", str(channelDetails[2]))
				layer = channelDetails[3]
				individualChannel_cols[2][0].metric("Layer", str(layer))
				individualChannel_cols[2][1].metric("Module ID", str(channelDetails[4] + layer * HIMEConstants.N_MODULES_PER_LAYER))
				if Layer.isHorizontal(layer):
					if channelDetails[5] == 0:
						position = "Right"
					else:
						position = "Left"
				else:
					if channelDetails[5] == 0:
						position = "Bottom"
					else:
						position = "Top"
				crateSlotAndChannel = HVList.channelMap.himeCh_to_crateSlotAndChannel(st.session_state.hime_channel)
				individualChannel_cols[2][2].metric("Position", position)
				individualChannel_cols[3][0].metric("HV crate", crateSlotAndChannel[0])
				individualChannel_cols[3][1].metric("HV slot", crateSlotAndChannel[1])
				individualChannel_cols[3][2].metric("HV channel", crateSlotAndChannel[2])
				hv = HVList.hvSupplyList[crateSlotAndChannel[0]]
				slot = crateSlotAndChannel[1]
				ch = crateSlotAndChannel[2]
				individualChannel_cols[3][0].metric("Voltage (V)", hv.measureVoltages(slot, ch)[0])
				individualChannel_cols[3][1].metric("Target (V)", hv.getTargetVoltages(slot, ch)[0])
				individualChannel_cols[3][2].metric("Current (\u03BCA)", hv.measureCurrents(slot, ch)[0])
			else:
				st.info("Not connected.", icon = "ℹ️")

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

	# -------- Print error messages sent by the HV supply --------

	if st.session_state.hv.messages.isUpdated:
		st.session_state.hv.messages.print()

	# -------- Last updated --------

	st.divider()

	st.markdown("**Last updated:** " + datetime.now().strftime("%H:%M:%S"))

	# -------- Continue threads writing to InfluxDB --------

	InfluxDB.runAllThreads()
