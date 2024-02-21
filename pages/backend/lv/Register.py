import pandas as pd


def registerToDataframe(getRegister_func, nBits: int):

	bits = getRegister_func()

	df = pd.DataFrame(columns = ["Bit", "Value"])

	for i in range(0, nBits):
		bit = bits >> i & 1
		df.loc[i] = [i, bit]

	return df
