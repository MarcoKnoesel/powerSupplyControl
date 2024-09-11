import streamlit as st
import pages.backend.hv.HVList as HVList

def submitPW(hv):
	password = st.session_state.pw_input_widget
	st.session_state.pw_input_widget = ""
	hv.login(password)


def show(login_col):
	
	# show login status of all HV supplies
	for hv in HVList.hvSupplyList:
		if hv.loggedIn:
			login_col.markdown("🟢  Logged in to " + hv.name)
		else:
			login_col.markdown("🔴  Not logged in to " + hv.name)
		
	# loop over all HV supplies and stop at the first one,
	# where you're not logged in yet
	for hv in HVList.hvSupplyList:
		# check if you are logged out of the current HV supply
		if hv.loggedIn == False:
			login_col.text_input("Enter password for " + hv.name, key = "pw_input_widget", type = "password", on_change=submitPW, args=(hv,))
			break