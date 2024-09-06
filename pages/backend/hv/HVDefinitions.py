from pages.backend.hv.HVList import define_hv

# ------------------------ Define your HV supplies here ------------------------
# Parameters: Name (str), user (str), IP address (str)
def init():
	define_hv("HIME_HV_02", "admin", "10.32.17.119")
	define_hv("HIME_HV_01", "admin", "10.32.17.118")
# ------------------------------------------------------------------------------
	
