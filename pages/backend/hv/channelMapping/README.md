# Channel mapping

In this directory, the mapping from HIME channels to HV channels is defined.

The HIME-channel number is given by

	(FPGA number) * 48 + (dac chain number) * 16 + (PaDiWa channel)

and the HV channels are uniquely defined by arrays of the form

	[HV crate number,  HV slot number,  HV channel]
