from io import StringIO
import pandas as pd

def mapToDataframe(map: str):
	map = "Board type,Description,Number of channels,Serial number,Rel. (whatever that is)\n" + map
	with StringIO(map) as f:
		df = pd.read_csv(f, sep = ",")
		f.close()
	df = df.style.format({
		"Number of channels": lambda x : '{:.0f}'.format(x),
		"Serial number": lambda x : '{:.0f}'.format(x),
		"Rel. (whatever that is)": lambda x : '{:.2f}'.format(x)
	})
	df.index.names = ["Slot"]

	return df
