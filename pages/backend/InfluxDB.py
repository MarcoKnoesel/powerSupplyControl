import threading
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import pages.backend.lv.LVSupply as LVSupply
import pages.backend.InfluxDBConfig as InfluxDBConfig
from datetime import datetime
import time
import os

threads = []

def pauseThread(i: int) -> None:
	if InfluxDBConfig.writeTime >= 0:
		threads[i].pause()

def runAllThreads() -> None:
	if InfluxDBConfig.writeTime >= 0:
		for i in range(0, len(threads)):
			threads[i].run()

# By creating instances of this class, separate threads are started that allow to periodically write data to InfluxDB.
# In the main thread, streamlit keeps running the web page.
class InfluxDB:
	def __init__(self, lv: LVSupply) -> None:
		self.pauseThread = False    # Setting this variable to True tells the subthread to stop as soon as possible. It is set by the main thread.
		self.influxDone = False     # This variable will be set to True after the subthread has stopped. This information is needed by the main thread.
		self.lv = lv
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
		self.thread = threading.Thread(target = self.influx)
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

	# This is invoked in the subthread
	def influx(self) -> None:
		while True:
			if self.pauseThread:
				self.influxDone = True
				time.sleep(0.1)
			else:
				self.influxDone = False
				# Check if self.writeTime has passed since the last time something was written to InfluxDB
				if (time.time() - self.startTime) >= self.writeTime:
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
				else:
					# Wait, but allow interruption
					time.sleep(0.1)