from pages.backend.hv.HVList import define_hv

# ------------------------ Define your HV supplies here ------------------------
# Parameters: Name (str), user (str), IP address (str)
def init():
	define_hv("HIME_HV_01", "hime", "192.168.30.129")
# ------------------------------------------------------------------------------
	