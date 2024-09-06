import streamlit as st
import pages.backend.hv.HVList as HVList
import pages.backend.hv.ChannelParameters as ChannelParameters



def pwOn(layer: int) -> str:
	for hv in HVList.hvSupplyList:
		if hv.checkConnection() != 2:
			hv.reconnect()
	cratesSlotsChannels = HVList.channelMap.layer_to_cratesSlotsChannels(layer)
	reply = ""
	for entry in cratesSlotsChannels:
		crate = entry[0]
		slot = entry[1]
		chStart = entry[2]
		chStop = entry[3]
		reply += HVList.hvSupplyList[crate].pwOn_slotAndChannels(slot, chStart, chStop)
	return reply



def pwOff(layer: int) -> str:
	for hv in HVList.hvSupplyList:
		if hv.checkConnection() != 2:
			hv.reconnect()
	cratesSlotsChannels = HVList.channelMap.layer_to_cratesSlotsChannels(layer)
	reply = ""
	for entry in cratesSlotsChannels:
		crate = entry[0]
		slot = entry[1]
		chStart = entry[2]
		chStop = entry[3]
		reply += HVList.hvSupplyList[crate].pwOff_slotAndChannels(slot, chStart, chStop)
	return reply



def setVoltage(layer: int, voltage) -> str:
	cratesSlotsChannels = HVList.channelMap.layer_to_cratesSlotsChannels(layer)
	reply = ""
	for entry in cratesSlotsChannels:
		crate = entry[0]
		slot = entry[1]
		chStart = entry[2]
		chStop = entry[3]
		reply += HVList.hvSupplyList[crate].setVoltage_slotAndChannels(slot, chStart, chStop, voltage)
	return reply



def isHorizontal(layer: int) -> bool:
	return layer % 2 == 0



def changeLayerVoltage(currentLayer: int) -> None:
	if st.session_state.layer_voltage != None:
		setVoltage(currentLayer, st.session_state.layer_voltage)



def show() -> None:
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

	layer_col1.button("Switch layer on :rocket:", on_click = pwOn, args = (currentLayer,))
	layer_col1.button("Switch layer off :zzz:", on_click = pwOff, args = (currentLayer,))

	st.session_state.layer_voltage = layer_col2.number_input("Set target voltage for this layer (V) :level_slider:", value = None, placeholder = "Voltage (V)", min_value=0, max_value = 1550)
	if st.session_state.layer_voltage == None:
		layer_col2.metric("Target :dart:", "--")
	else:
		layer_col2.metric("Target :dart:", str(st.session_state.layer_voltage) + " V")

	layer_col2.button("Send target voltage to layer " + str(currentLayer) + " :satellite_antenna:", on_click=changeLayerVoltage, args=(currentLayer,), disabled=(st.session_state.layer_voltage == None))

	st.subheader("Channel Parameters")

	st.markdown("Tip: Use `Shift + Mouse Wheel` to scroll left/right or choose \"Wide mode\" in the settings.")	  
	st.markdown("...and don't forget to press the `R` key to see the effect of your voltage settings! :eyes:")

	channelPar_col0, channelPar_col1 = st.columns(2)

	if isHorizontal(currentLayer):
		channelPar_col0.markdown("**" + st.session_state.layerStr + ": Left PMTs** :arrow_left:")
		channelPar_col1.markdown("**" + st.session_state.layerStr + ": Right PMTs** :arrow_right:")
	else:
		channelPar_col0.markdown("**" + st.session_state.layerStr + ": Top PMTs** :arrow_up:")
		channelPar_col1.markdown("**" + st.session_state.layerStr + ": Bottom PMTs** :arrow_down:")
	
	dfList = ChannelParameters.channelParametersToDataframe(currentLayer)
	for pos in [0,1]:
		[channelPar_col0, channelPar_col1][pos].dataframe(dfList[pos], hide_index = True, height = round(5.5 * (dfList[pos].size + 1)) )