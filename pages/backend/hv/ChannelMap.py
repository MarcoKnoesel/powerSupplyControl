import pages.backend.hv.CSVHelper as csvh
import pages.backend.hv.HVList as HVList
import pages.backend.Messages as Messages
import numpy as np
import pages.backend.hv.HIMEConstants as HIMEConstants

#TODO
# warning messages when -1 is returned

class ChannelMap:

	# This constructor reads a CSV file defining the mapping from the channel numbers given by
	#   (FPGA number) * 48 + (dac chain number) * 16 + (PaDiWa channel)
	# (-> this is called "HIME channel" in the following)
	# to HV channels, i.e. combinations of the crate number, the slot number of an HV module
	# and the number of a channel of that module.
	def __init__(self, path: str):
		self.messages = Messages.Messages()

		# map the HIME-channel number on an array of the form
		# [HV crate, HV slot, HV channel]
		HVList.hvCratesSlotsChannels = [[-1, -1, -1] for i in range(0, HIMEConstants.N_HIME_CHANNELS)]
		# map a combination of HV crate, HV slot, HV channel
		# on HIME channel
		HVList.himeChannels = [
			[
				[ 
					-1 for i in range(0, HVList.hvSupplyList[k].N_CHANNELS_PER_SLOT) 
				] 
				for j in range(0, HVList.hvSupplyList[k].N_SLOTS)
			] 
			for k in range(0, len(HVList.hvSupplyList)) 
		]
		# map HIME layers on a list of
		# [HV crate, HV Slot, HV chStart, HV chStop] arrays
		HVList.himeLayers = [[] for k in range(0, HIMEConstants.N_LAYERS)]
		# hime channel -> FPGA, DAC chain, PaDiWa channel, Layer, module number of that layer 
		# *** module ID != module number ***
		# The module ID runs over all modules of HIME and is different
		# from the module number of a specific layer!
		HVList.channelDetails = [None for i in range(0, HIMEConstants.N_HIME_CHANNELS)]
		
		try:
			csvFile = open(path, "r")
		except:
			self.errors.append("CSV file for channel mapping not found!")
			return
		
		csvList = csvFile.readlines()
		csvFile.close()

		for line in csvList:
			if csvh.isComment(line):
				continue
			commaPositions = csvh.findPosOfCharInString(",", line)
			if commaPositions == None:
				self.messages.newWarning("[ChannelMap] Comma not found in line \"" + line + "\"! Line is ignored.")
				continue
			entryCounter = 0
			# -------- HV crate --------
			try:
				crate = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to integer value failed for the crate number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if crate < 0 or crate >= len(HVList.hvSupplyList):
				self.messages.newWarning("[ChannelMap] Invalid crate number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- HV slot --------
			try:
				slot = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to integer value failed for the slot number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if slot < 0 or slot >= HVList.hvSupplyList[crate].N_SLOTS:
				self.messages.newWarning("[ChannelMap] Invalid slot number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- HV channel --------
			try:
				channel = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to integer value failed for the channel number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if channel < 0 or channel >= HVList.hvSupplyList[crate].N_CHANNELS_PER_SLOT:
				self.messages.newWarning("[ChannelMap] Invalid channel number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- FPGA --------
			try:
				fpga = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to int value failed for the FPGA number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if fpga < 0 or fpga >= HIMEConstants.N_FPGAS:
				self.messages.newWarning("[ChannelMap] Invalid FPGA number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- DAC chain --------
			try:
				dacChain = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to int value failed for the DAC-chain number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if dacChain < 0 or dacChain >= HIMEConstants.N_DACCHAINS:
				self.messages.newWarning("[ChannelMap] Invalid DAC-chain number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- PaDiWa channel (0 - 16) --------
			try:
				padiwaChannel = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to int value failed for the HIME channel in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if padiwaChannel < 0 or padiwaChannel >= HIMEConstants.N_PADIWA_CHANNELS:
				self.messages.newWarning("[ChannelMap] Invalid HIME channel in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- HIME layer --------
			try:
				himeLayer = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to int value failed for the HIME layer in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if himeLayer < 0 or himeLayer >= HIMEConstants.N_LAYERS:
				self.messages.newWarning("[ChannelMap] Invalid HIME layer in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- HIME module number in this layer --------
			try:
				moduleNumber = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to int value failed for the HIME-module number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			if moduleNumber < 0 or moduleNumber >= HIMEConstants.N_MODULES_PER_LAYER:
				self.messages.newWarning("[ChannelMap] Invalid HIME-module number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			entryCounter += 1
			# -------- Position: 0 -> right/down or 1 -> left/up --------
			try:
				position = int(csvh.getEntry(line, commaPositions, entryCounter))
			except:
				self.messages.newWarning("[ChannelMap] Conversion to int value failed for the HIME-module number in line \"" + str(line) + "\"! Line is ignored.")
				continue
			
			himeCh = fpga * 48 + dacChain * 16 + padiwaChannel

			HVList.channelDetails[himeCh] = [fpga, dacChain, padiwaChannel, himeLayer, moduleNumber, position]

			if HVList.himeChannels[crate][slot][channel] != -1:
				self.messages.newWarning("[ChannelMap] Line \"" + line + "\" is ignored because this channel has been initialized before!")
				continue

			HVList.hvCratesSlotsChannels[himeCh] = [crate, slot, channel]
			HVList.himeChannels[crate][slot][channel] = himeCh

		for layer in range(0, HIMEConstants.N_LAYERS):
			self.createMapping_layerToHVChannels(layer)

		# print channel mapping

#		for i in range(0, len(HVList.hvCratesSlotsChannels)):
#			entry = HVList.hvCratesSlotsChannels[i]
#			print(str(i)+ ": ----> crate " + str(entry[0]) + "    slot " + str(entry[1]) + "    HV channel " + str(entry[2]))

#		for crate in range(0, len(HVList.himeChannels)):
#			for slot in range(0, len(HVList.himeChannels[crate])):
#				for channel in range(0, len(HVList.himeChannels[crate][slot])):
#					print("crate " + str(crate) + "    slot " + str(slot) + "    HV channel " + str(channel) + ": ---->   himeChannel " + str(HVList.himeChannels[crate][slot][channel]))

#		for layer in range(0, HIMEConstants.N_LAYERS):
#			print("*** Layer " + str(layer) + " ***")
#			for entry in HVList.himeLayers[layer]:
#				print(entry)				



	# This function creates for each layer of the HIME detector
	# a list of arrays, where each one has the following structure:
	# [number of the hv crate,    number of the HV slot,    chStart,    chStop]
	#
	# This allows to manipulate multiple channels (all channels from chStart to chStop - 1)
	# of the same slot at the same time efficiently
	# using the functions "const char* HVGetChParam(...)" and "const char* HVSetChParam(...)"
	# defined in the C file "pages/backend/hv/CAENHVWrapper-6.3/himeHV/HVWrapper.c".
	#
	# For each slot, this function needs to find **HV channel numbers with a difference of 1**
	# that are connected to the same layer; that's why it's a little complicated...
	def createMapping_layerToHVChannels(self, layer: int):
		# create a temporary empty array
		# -> first index is for the number of the HV crate
		# -> second index is for the slot 
		# For each slot, the HV channels are listed that are connected to the same hime layer,
		# but not yet in the right order.
		unsortedChannels = [
			[
				[] for j in range(0, HVList.hvSupplyList[i].N_SLOTS)
			] for i in range(0, len(HVList.hvSupplyList))
		]
		
		
		himeChannelsOfCurrentLayer = range(layer * 48, (layer + 1) * 48)

		for himeCh in himeChannelsOfCurrentLayer:
			iHV = HVList.hvCratesSlotsChannels[himeCh][0]
			slot = HVList.hvCratesSlotsChannels[himeCh][1]
			ch = HVList.hvCratesSlotsChannels[himeCh][2]
			if iHV == -1 or slot == -1 or ch == -1:
				continue
			unsortedChannels[iHV][slot].append(ch)
		
		for iHV in range(0, len(unsortedChannels)):

			for slot in range(0, len(unsortedChannels[iHV])):
			
				if len(unsortedChannels[iHV][slot]) == 0:
					continue

				sortedChannels = np.sort(np.array(unsortedChannels[iHV][slot]))
				
				# after sorting, find sequences of HV channels in a specific HV slot,
				# which are connected to the same HIME layer
				chStart = sortedChannels[0]
				chStop = chStart + 1
				# all channels from chStart (inclusively) to chStop (exclusively)
				# are connected to the current HIME layer
				HVList.himeLayers[layer].append([iHV, slot, chStart, chStop])

				for i in range(1, len(sortedChannels)):

					chCurrent = sortedChannels[i]
				
					# check if the difference of two HV-channel numbers is 1;
					# i.e. if chCurrent is equal to chStop
					if chCurrent == HVList.himeLayers[layer][-1][-1]:
						# update chStop of the current slot
						HVList.himeLayers[layer][-1][-1] += 1
					else:
						# start filling a new slot
						HVList.himeLayers[layer].append([iHV, slot, chCurrent, chCurrent + 1])


	# clear warning and error messages
	def clearMessages(self) -> None:
		self.warnings.clear()
		self.errors.clear()

	#
	# HV crate, HV slot, HV channel ---> HIME channel
	#
	# Map the combination of HV crate, slot and channel number
	# on a global channel number running over all channels of HIME
	def crateSlotCh_to_himeCh(self, crate: int, slot: int, ch: int) -> int:
		try:
			return HVList.himeChannels[crate][slot][ch]
		except:
			self.messages.newWarning("[ChannelMap] No HIME channel found for crate " + str(crate) + ", slot " + str(slot) + " and channel " + str(ch) + "!")
		return -1

	#
	# HIME layer ---> HV crate, HV slot, HV channel
	#
	# Pass a layer number of HIME as a parameter
	# -> get a list of arrays of the following form:
	#   [HV crate,   HV slot,   chStart,   chStop]
	#
	# This allows to manipulate all channels from chStart to chStop - 1
	# (for each HV crate and HV slot the layer is connected to)
	def layer_to_cratesSlotsChannels(self, layer: int):
		try:
			# this can cause an IndexError
			hvChannels = HVList.himeLayers[layer]
			# even if there's no index error, there might be layers which have no HV channels assigned
			# (depends on the content of the CSV file)
			# -> raise an exception
			if hvChannels[0][0] == -1:
				raise Exception()
			return hvChannels
		except:
			self.messages.newWarning("[ChannelMap] No HV channels found for layer " + str(layer) + "!")
		return [[-1, -1, -1, -1]]

	# 
	# HIME channel ---> HV crate, HV slot, HV channel
	#
	# Pass a HIME channel as parameter, which is given by
	#   (FPGA number) * 48 + (dac chain number) * 16 + (PaDiWa channel)
	# -> get an array of the following form:
	#   [HV crate,   HV slot,   chStart,   chStop]
	#
	# This allows to manipulate all channels from chStart to chStop - 1
	# (for each HV crate and HV slot the layer is connected to)
	def himeCh_to_crateSlotAndChannel(self, himeCh: int):
		return HVList.hvCratesSlotsChannels[himeCh]
	
	def getChannelDetails(self, himeCh: int):
		return HVList.channelDetails[himeCh]
	
	def crateSlotAndChannel_to_himeCh(self, crate: int, slot: int, channel: int) -> int:
		return HVList.himeChannels[crate][slot][channel]
	#TODO fill himeChannelsOfCurrentLayer automatically