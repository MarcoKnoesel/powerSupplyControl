# -------- Initialize LVs --------
import sys
import pages.backend.lv.LVDefinitions as LVDef
import pages.backend.hv.HVDefinitions as HVDef
import pages.backend.InfluxDB as InfluxDB
import pages.backend.InfluxDBConfig as InfluxDBConfig
from pages.backend.lv.LVList import lvSupplyList

# Adding an entry to sys.argv is a hack to avoid that the TCP socket for the LV control
# and the C wrapper for the HV control are re-instanciated
# every time a new streamlit session is started. 
# (A new streamlit session is always started after (re-)loading the webpage!)
# We only want to start a TCP socket and to start the C wrapper 
# when the streamlit server is started!
def init():
	# Check if initialization was already done
	pow_sup_init = False
	for i in range(0, len(sys.argv)):
		if sys.argv[i] == "POWER_SUPPLY_INIT":
			pow_sup_init = True
	if not pow_sup_init:
		# Initialize LV and HV supplies
		LVDef.init()
		HVDef.init()
		# Start threads for writing data to InfluxDB
		if InfluxDBConfig.writeTime >= 0:
			for i in range(0, len(lvSupplyList)):
				InfluxDB.threads.append(InfluxDB.InfluxDB(lvSupplyList[i]))
		# Remember that initialization is done now
		sys.argv.append("POWER_SUPPLY_INIT")