import streamlit as st
import pages.backend.hv.HVList as HVList
import pages.backend.hv.Layer as Layer
import pages.backend.hv.HIMEConstants as HIMEConstants

def changeChannelVoltage(himeCh: int, voltage: float) -> None:
	if voltage != None:
		crateSlotAndChannel = HVList.channelMap.himeCh_to_crateSlotAndChannel(himeCh)
		crate = crateSlotAndChannel[0]
		slot = crateSlotAndChannel[1]
		channel = crateSlotAndChannel[2]
		HVList.hvSupplyList[crate].setVoltage_channel(slot, channel, voltage)

def pwOn_channel(himeCh: int) -> None:
	crateSlotAndChannel = HVList.channelMap.himeCh_to_crateSlotAndChannel(himeCh)
	crate = crateSlotAndChannel[0]
	slot = crateSlotAndChannel[1]
	channel = crateSlotAndChannel[2]
	HVList.hvSupplyList[crate].pwOn_channel(slot, channel)

def pwOff_channel(himeCh: int) -> None:
	crateSlotAndChannel = HVList.channelMap.himeCh_to_crateSlotAndChannel(himeCh)
	crate = crateSlotAndChannel[0]
	slot = crateSlotAndChannel[1]
	channel = crateSlotAndChannel[2]
	HVList.hvSupplyList[crate].pwOff_channel(slot, channel)

def show(himeCh: int, individualChannel_cols) -> None:
	if himeCh != None:

		channelDetails = HVList.channelMap.getChannelDetails(himeCh)

		if channelDetails != None:
			# -------- Row 0 --------
			# set target voltage
			if st.session_state.channel_voltage == None:
				individualChannel_cols[2].metric("Target :dart:", "--")
			else:
				individualChannel_cols[2].metric("Target :dart:", str(st.session_state.channel_voltage) + " V")
			# -------- Row 1 --------
			individualChannel_cols[0].button("Switch on", on_click=pwOn_channel, args=(himeCh,))
			individualChannel_cols[1].button("Switch off", on_click=pwOff_channel, args=(himeCh,))
			individualChannel_cols[2].button("Send now :satellite_antenna:", on_click=changeChannelVoltage, args=(himeCh,st.session_state.channel_voltage,), disabled=(st.session_state.channel_voltage == None))
			# -------- Row 2 --------
			# show FPGA, DAC chain and PaDiWa channel
			individualChannel_cols[0].metric("FPGA", str(channelDetails[0]))
			individualChannel_cols[1].metric("DAC chain", str(channelDetails[1]))
			individualChannel_cols[2].metric("PaDiWa channel", str(channelDetails[2]))
			layer = channelDetails[3]
			# -------- Row 3 --------
			# show layer, module ID and position
			individualChannel_cols[0].metric("Layer", str(layer))
			individualChannel_cols[1].metric("Module ID", str(channelDetails[4] + layer * HIMEConstants.N_MODULES_PER_LAYER))
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
			crateSlotAndChannel = HVList.channelMap.himeCh_to_crateSlotAndChannel(himeCh)
			individualChannel_cols[2].metric("Position", position)
			# -------- Row 4 --------
			# show HV crate, slot and channel
			individualChannel_cols[0].metric("HV crate", crateSlotAndChannel[0])
			individualChannel_cols[1].metric("HV slot", crateSlotAndChannel[1])
			individualChannel_cols[2].metric("HV channel", crateSlotAndChannel[2])
			hv = HVList.hvSupplyList[crateSlotAndChannel[0]]
			slot = crateSlotAndChannel[1]
			ch = crateSlotAndChannel[2]
			individualChannel_cols[0].metric("Voltage (V)", hv.measureVoltages(slot, ch)[0])
			individualChannel_cols[1].metric("Target (V)", hv.getTargetVoltages(slot, ch)[0])
			individualChannel_cols[2].metric("Current (\u03BCA)", hv.measureCurrents(slot, ch)[0])
			
		else:
			st.info("Not connected.", icon = "ℹ️")