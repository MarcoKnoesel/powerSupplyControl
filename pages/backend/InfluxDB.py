import threading
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import pages.backend.lv.LVSupply as LVSupply
import pages.backend.hv.HVSupply as HVSupply
import pages.backend.InfluxDBConfig as InfluxDBConfig
from datetime import datetime
import time
import os

lvThreads = []
hvThreads = []

def pauseLVThread(i: int) -> None:
	if InfluxDBConfig.writeTime >= 0:
		lvThreads[i].pause()

def pauseHVThread(i: int) -> None:
	if InfluxDBConfig.writeTime >= 0:
		hvThreads[i].pause()

def runAllThreads() -> None:
	if InfluxDBConfig.writeTime >= 0:
		for i in range(0, len(lvThreads)):
			lvThreads[i].run()
		for i in range(0, len(hvThreads)):
			hvThreads[i].run()

# By creating instances of this class, separate threads are started that allow to periodically write data to InfluxDB.
# In the main thread, streamlit keeps running the web page.
class InfluxDB:
	def __init__(self, lv: LVSupply = None, hv: HVSupply = None) -> None:
		self.pauseThread = False    # Setting this variable to True tells the subthread to stop as soon as possible. It is set by the main thread.
		self.influxDone = False     # This variable will be set to True after the subthread has stopped. This information is needed by the main thread.
		self.lv = lv
		self.hv = hv
		self.writeTime = InfluxDBConfig.writeTime
		if self.writeTime >= 0 and self.writeTime < 5:
			self.writeTime = 5
		self.startTime = time.time() - self.writeTime    # Initialize startTime to a value causing the first set of data to be submitted right now to InfluxDB
		# -- start InfluxDB client --
		self.bucket = InfluxDBConfig.bucket
		self.org = InfluxDBConfig.org
		self.token = os.getenv("INFLUX_TOKEN")
		self.url = InfluxDBConfig.url
		self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
		self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
		# -- create and start subthread --
		self.thread = threading.Thread(target = self.influxLoop)
		self.thread.start()

	# This can be invoked in the main thread
	# in order to stop the submission of data to InfluxDB
	def pause(self) -> None:
		self.pauseThread = True
		while not self.influxDone:
			time.sleep(0.1)

	# This can be invoked in the main thread
	# in order to restart the submission of data to InfluxDB
	def run(self) -> None:
		self.pauseThread = False

	# Submit data from the TDK Lambda low-voltage supply
	# Invoked in iterations of influxLoop()
	def lvToInflux(self) -> None:
		# check and handle timeout
		try:
			self.lv.getMAC()
		except:
			self.lv.reconnect()
		# measure voltage
		try:
			# If re-connecting has not yet finished, measureVoltage and measureCurrent
			# will result in ValueError exceptions.
			# If so, wait a short time until the connection is re-established.
			voltage = self.lv.measureVoltage()
			current = self.lv.measureCurrent()
			print("------------------------------------------")
			print("[InfluxDB.py] Submitting data to InfluxDB:")
			print("[InfluxDB.py] Time: " + datetime.now().strftime("%H:%M:%S"))
			print("[InfluxDB.py] Voltage: " + str(voltage) + " V")
			print("[InfluxDB.py] Current: " + str(current) + " A")
			print("------------------------------------------")
			point_voltage = influxdb_client.Point("lv").tag("name", self.lv.name).field("voltage", voltage)
			point_current = influxdb_client.Point("lv").tag("name", self.lv.name).field("current", current)
			self.write_api.write(self.bucket, self.org, point_voltage)
			self.write_api.write(self.bucket, self.org, point_current)
			self.startTime = time.time()
		except ValueError:
			# Wait a short time until the connection is re-established.
			time.sleep(0.1)

	# Submit data from the CAEN high-voltage supply
	# Invoked in iterations of influxLoop()
	def hvToInflux(self) -> None:
		# no connection
		if self.hv.checkConnection() == 0:
			return
		# timeout -> reconnect
		if self.hv.checkConnection() == 1:
			self.hv.reconnect()
			time.sleep(0.1)
		# connected
		if self.hv.checkConnection() == 2:
			# measure voltages of all channels in all slots of the HV supply
			for slot in list(range(0,9)) + [10, 12, 14]:
				voltages = self.hv.measureVoltages(slot, 0, 48)
				currents = self.hv.measureCurrents(slot, 0, 48)
				# iterate over all channels of the current slot
				for iCh in range(0, len(voltages)):
					# get the HIME channel number (ranges over all channels of HIME, not only the current slot)
					chStr = self.to4digit(self.hv.slotAndCh_to_himeCh(slot, iCh))
					# submit to InfluxDB
					point_voltage = influxdb_client.Point("hv").tag("name_channel", self.hv.name + "_" + chStr).field("voltage", voltages[iCh])
					point_current = influxdb_client.Point("hv").tag("name_channel", self.hv.name + "_" + chStr).field("current", currents[iCh])
					self.write_api.write(self.bucket, self.org, point_voltage)
					self.write_api.write(self.bucket, self.org, point_current)
			# reset time
			self.startTime = time.time()


	# This is invoked in the subthread
	def influxLoop(self) -> None:
		while True:
			if self.pauseThread:
				self.influxDone = True
			else:
				self.influxDone = False
				# Check if self.writeTime has passed since the last time something was written to InfluxDB
				if (time.time() - self.startTime) >= self.writeTime and self.lv != None:
					self.lvToInflux()
				if (time.time() - self.startTime) >= self.writeTime and self.hv != None:
					self.hvToInflux()
			# Wait, but allow interruption
			time.sleep(0.1)

	def to4digit(self, i: int) -> str:
		iStr = str(i)
		while len(iStr) < 4:
			iStr = "0" + iStr
		return iStr