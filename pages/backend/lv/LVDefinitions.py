from pages.backend.lv.LVList import *

# ------------------------ Define your LV supplies here ------------------------
# Parameters: Name (str), MAC address (str), IP address (str), minimum voltage (float), maximum voltage (float)
def init():
	define_lv("Unused LV", "00:19:F9:10:4A:87", "192.168.30.165", 0., 2.)
	define_lv("TRB3sc LV", "00:19:F9:10:4A:71", "192.168.30.174", 0., 6.)
# ------------------------------------------------------------------------------
