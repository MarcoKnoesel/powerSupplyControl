import streamlit as st
import pages.backend.InfluxDB as InfluxDB
import pages.backend.InfluxDBConfig as InfluxDBConfig
import pages.backend.InitPowerSupplies as Init
import pages.backend.hv.HVList as HVList
import os 

# -------- Title of the page (displayed as tab name in the browser) --------

st.set_page_config("Power-Supply Control", page_icon = "svg/icon.svg")

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

# -------- Session-state variable definitions --------

if "changeWriteTimeBool" not in st.session_state:
	st.session_state.changeWriteTimeBool = False

if "showReadmeAndLicense" not in st.session_state:
	st.session_state.showReadmeAndLicense = False

# -------- Title and introduction --------
	
st.title("Power-Supply Control :joystick:")

col1, col2 = st.columns((6,2))

col1.markdown(
'''
Welcome to Power-Supply Control.

Choose LV or HV from the side menu.

Press the `R` key to refresh the page.
'''
)

col2.image("svg/himeLogo.svg")

# -------- InfluxDB --------
if InfluxDBConfig.writeTime >= 0:
	
	st.divider()

	st.header("InfluxDB :chart_with_upwards_trend:")

	influxdb_col1, influxdb_col2 = st.columns(2)


	# -------- Number input to change the time interval of data submission to InfluxDB --------
	if len(InfluxDB.lvThreads) > 0 or len(InfluxDB.hvThreads) > 0:
		def changeWriteTime():
			st.session_state.changeWriteTimeBool = True

		writeTime = influxdb_col1.number_input("Time interval for data submission", value=None, placeholder="Time in seconds", min_value=5, on_change=changeWriteTime)

		if st.session_state.changeWriteTimeBool:
			if writeTime != None:
				for thread in InfluxDB.lvThreads:
					thread.writeTime = writeTime
				for thread in InfluxDB.hvThreads:
					thread.writeTime = writeTime
			st.session_state.changeWriteTimeBool = False

	# -------- Display the time interval of data submission to InfluxDB --------
	if len(InfluxDB.lvThreads) > 0:
		influxdb_col2.metric("Current value", str(InfluxDB.lvThreads[0].writeTime) + " s")
	else:
		if len(InfluxDB.hvThreads) > 0:
			influxdb_col2.metric("Current value", str(InfluxDB.hvThreads[0].writeTime) + " s")
		else:
			st.warning("No power supplies found. You can define LV and HV supplies in `pages/backend/lv/LVDefinitions.py` and `pages/backend/hv/HVDefinitions.py`, respectively.", icon = "⚠️")
	
	# -------- Display a warning message if HV supplies have been defined, but the connection was not set up --------
	disconnectedHVNames = ""
	for i in range(0,len(HVList.hvSupplyList)):
		if HVList.hvSupplyList[i].checkConnection() == 0 :
			disconnectedHVNames += HVList.hvSupplyList[i].name
	if len(disconnectedHVNames) > 0:
		st.warning("The following HV supply/supplies was/were defined, but no connection was set up: " + disconnectedHVNames + ". Did you enter the password?", icon = "⚠️")

# -------- Links --------

st.divider()

st.header("External links :link:")

linkDescriptions = [
	"Caen HV wrapper",
	"Caen SY4527",
	"DABC Online Server",
	"DAQ Control",
	"HIME ELOG",
	"IKP webmail",
	"InfluxDB",
	"InfluxDB documentation",
	"TDK Lambda manual"
]

links = [
	"https://www.caen.it/products/caen-hv-wrapper-library/",
	"https://www.caen.it/products/sy4527/",
	"http://hime01:8091",
	"http://hime01:1234",
	"https://neptun.ikp.physik.tu-darmstadt.de/elog/HIME/",
	"https://lwapsr.ikp.physik.tu-darmstadt.de/cgi-bin/login.pl",
	"http://hime01:8086/",
	"https://docs.influxdata.com/influxdb/v2/",
	"https://product.tdk.com/system/files/dam/doc/product/power/switching-power/prg-power/instruction_manual/genesystm-lan-interface-manual-1u.pdf"
]

for i in range(0, len(links)):
	col1, col2 = st.columns((2,6))
	col1.markdown("**" + linkDescriptions[i] + "**")
	col2.markdown(links[i])

# -------- License --------

st.divider()

st.header("Readme :newspaper: and License :scales:")


def switchDetails(show: bool) -> None:
	st.session_state.showReadmeAndLicense = show

if st.session_state.showReadmeAndLicense:
	st.button("Hide", on_click=switchDetails, args=(False,))
else:
	st.button("Show", on_click=switchDetails, args=(True,))

if st.session_state.showReadmeAndLicense:
	path = os.path.dirname(os.path.realpath(__file__))
	try:
		with open(path + "/README.md") as f:
			readme = f.read()
			f.close()
		st.divider()
		st.header("Readme :newspaper:")
		st.markdown(readme)
	except FileNotFoundError:
		st.error("README.md not found!", icon = "❗")
	try:
		with open(path + "/COPYING") as f:
			license = f.read()
			f.close()
		st.divider()
		st.header("License Text :scales:")
		st.text(license)
	except FileNotFoundError:
		st.error("File COPYING not found!", icon = "❗")