import streamlit as st
from datetime import datetime
import pages.backend.InitPowerSupplies as Init
import pages.backend.padiwa.PaDiWaList as PaDiWaList
import subprocess

# -------- Title of the page (displayed as tab name in the browser) --------

st.set_page_config("PaDiWa Temperature", page_icon = "svg/icon.svg")

# -------- Initialize Power Supplies --------
# In each Python file that defines a new webpage, 
# `Init.init()` needs to be done at first
# in order start a new TCP socket for the LV supply
# and a C wrapper for the HV supply.
Init.init()

def temperatureStringToArray(reply: str):
	entries = []
	entryStart = 0
	for i in range(0, len(reply)):
		if reply[i] == "\t":
			entry = reply[entryStart:i]
			entryStart = i + 1
			entries.append(entry)
		else:
			if i == len(reply) - 1:
				entry = reply[entryStart:]
				entries.append(entry)
	return entries

st.title("PaDiWa Temperature :thermometer:")

for addrAndChains in PaDiWaList.padiwaList:

	address = str(addrAndChains[0])

	st.subheader("FPGA " + address)

	cols = st.columns(4)

	for c in addrAndChains[1]:

		chain = str(c)

		# start the perl script that reads the PaDiWa temperature
		p = subprocess.Popen(["perl", "/home/hime/trbsoft/daqtools/padiwa.pl", str(address), chain, "temp"], stdout = subprocess.PIPE)

		# the reply has the form 
		#    [FPGA address]\t[DAC chain]\t[temperature in degree Celsius]\n
		reply = p.stdout.read().decode()

		# remove \n at the end of the reply
		if reply[-1] == "\n":
			reply = reply[:-1]

		# store all tab-separated entries in an array
		entries = temperatureStringToArray(reply)

		cols[0].metric("Chain " + chain, entries[2] + " °C")

# -------- Last updated --------

st.divider()

st.markdown("**Last updated:** " + datetime.now().strftime("%H:%M:%S"))