N_LAYERS = 4
N_FPGAS = 4
N_DACCHAINS = 3
N_PADIWA_CHANNELS = 16
N_HIME_CHANNELS = 192
	
def isHorizontal(self, layer: int) -> bool:
	return layer % 2 == 0