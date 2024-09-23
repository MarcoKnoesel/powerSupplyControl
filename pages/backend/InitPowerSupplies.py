# -------- Initialize LVs --------
import sys
import time
import pages.backend.lv.LVDefinitions as LVDef
import pages.backend.hv.HVDefinitions as HVDef
import pages.backend.padiwa.PaDiWaDefinitions as PaDiWaDef
import pages.backend.InfluxDB as InfluxDB
import pages.backend.InfluxDBConfig as InfluxDBConfig
import pages.backend.lv.LVList as LVList
import pages.backend.hv.HVList as HVList
import pages.backend.hv.ChannelMap as ChannelMap

# Adding an entry to sys.argv is a hack to avoid that the TCP socket for the LV control
# and the C wrapper for the HV control are re-instanciated
# every time a new streamlit session is started. 
# (A new streamlit session is always started after (re-)loading the webpage!)
# We only want to start a TCP socket and to start the C wrapper 
# when the streamlit server is started!
def init():
	# Display error messages if the connection to any of the 
	# LV power supplies could not be set up.
	LVList.showErrors()
	HVList.showErrors()
	# Check if initialization was already done
	for i in range(0, len(sys.argv)):
		if sys.argv[i] == "POWER_SUPPLY_INIT":
			return
	print("\ninitialize\n")
	# Remember that initialization is done now
	sys.argv.append("POWER_SUPPLY_INIT")
	time.sleep(4)
	# Initialize LV and HV supplies
	LVDef.init()
	HVDef.init()
	PaDiWaDef.init()
	# Create channel map
	HVList.channelMap = ChannelMap.ChannelMap("pages/backend/hv/channelMapping/2024-09-06_de.csv")
	# Start threads for writing data to InfluxDB
	if InfluxDBConfig.writeTime >= 0:
		for i in range(0, len(LVList.lvSupplyList)):
			InfluxDB.lvThreads.append(InfluxDB.InfluxDB(lv = LVList.lvSupplyList[i]))
		for i in range(0, len(HVList.hvSupplyList)):
			InfluxDB.hvThreads.append(InfluxDB.InfluxDB(hv = HVList.hvSupplyList[i], hvid = i))
		InfluxDB.padiwaThreads.append(InfluxDB.InfluxDB())
