import time
import streamlit as st

def tunableQuantity(name: str, unit: str, minValue: float, maxValue: float, getTarget_func, getMeasured_func, setTarget_func):
	
	st.header(name)

	# second column serves for horizontal spacing only -> leave empty
	voltageCol1, voltageCol2, voltageCol3, voltageCol4 = st.columns((2,1,2,2))

	targetVoltage = getTarget_func()
	newTargetVoltage = voltageCol1.number_input("Set target (" + unit + ") :level_slider:",\
		min_value = minValue, \
		max_value = maxValue, \
		value = targetVoltage)

	if float(newTargetVoltage) != targetVoltage:
		setTarget_func(newTargetVoltage)
		time.sleep(0.5)
		st.rerun()

	voltageCol3.metric("Target :dart:", str(getTarget_func()) + " " + unit)

	voltageCol4.metric("Measured :triangular_ruler:", str(getMeasured_func()) + " " + unit)