import streamlit as st
from datetime import datetime
import pages.backend.InitPowerSupplies as Init
import pages.backend.padiwa.PaDiWaList as PaDiWaList
import pages.backend.padiwa.TemperatureReadout as TemperatureReadout
import pages.backend.InfluxDB as InfluxDB

# -------- Title of the page (displayed as tab name in the browser) --------

st.set_page_config("PaDiWa Temperature", page_icon = "svg/icon.svg")

# -------- Initialize Power Supplies --------
# In each Python file that defines a new webpage, 
# `Init.init()` needs to be done at first
# in order start a new TCP socket for the LV supply
# and a C wrapper for the HV supply.
Init.init()


# -------- Pause threads writing to InfluxDB --------

InfluxDB.pausePaDiWaThread()

# -------- Beginning of the PaDiWa-temperature page --------

st.title("PaDiWa Temperature :thermometer:")

if len(PaDiWaList.padiwaList) == 0:
	st.warning("No PaDiWa board found. You can define new PaDiWas in `pages/backend/padiwa/PaDiWaDefinitions.py`.", icon = "⚠️")

for addrAndChains in PaDiWaList.padiwaList:

	address = str(addrAndChains[0])

	st.subheader("FPGA " + address)

	cols = st.columns(4)

	for c in addrAndChains[1]:

		chain = str(c)

		temperature = TemperatureReadout.getTemperatureString(address, chain)

		cols[0].metric("DAC chain " + chain, temperature + " °C")

# -------- Last updated --------

st.divider()

st.markdown("**Last updated:** " + datetime.now().strftime("%H:%M:%S"))

# -------- Continue threads writing to InfluxDB --------

InfluxDB.runAllThreads()