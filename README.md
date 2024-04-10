# Power-Supply Control

Power-Supply Control serves to remotely control low-voltage (LV) and high-voltage (HV) power supplies for the HIME neutron detector. It uses the streamlit package for Python, which provides a convincing solution to run your own webserver and to build small webpages. This allows to control your power supplies platform independently from everywhere around the world, using a web browser. Furthermore, for monitoring and documentation purposes, Power-Supply Control can automatically submit measured values of e.g. currents or voltages to InfluxDB.



## Table of Contents
- [Power-Supply Control](#power-supply-control)
	- [Table of Contents](#table-of-contents)
	- [Installation](#installation)
		- [Caen HV Wrapper Library](#caen-hv-wrapper-library)
		- [Create Python Environment (recommended)](#create-python-environment-recommended)
		- [Install Python Packages](#install-python-packages)
		- [Install InfluxDB Open Source](#install-influxdb-open-source)
	- [Setup](#setup)
		- [InfluxDB](#influxdb)
		- [Adding or Removing LV and HV Supplies](#adding-or-removing-lv-and-hv-supplies)
	- [Start and Stop the Program](#start-and-stop-the-program)
	- [Access the Web Page from Outside of Your Workplace](#access-the-web-page-from-outside-of-your-workplace)
	- [Details](#details)
	- [License](#license)



## Installation



### Caen HV Wrapper Library 
Add the location of the Caen HV wrapper library (see [Details](#details)) to your `LD_LIBRARY_PATH`. I.e., for instance in your `~/.bashrc`, `~/.zshrc` or similar, add the line

	export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:[absolute_path_to]/powerSupplyControl/pages/backend/hv/CAENHVWrapper-6.3/bin/x86_64

Then, go to the directory

	pages/backend/hv/CAENHVWrapper-6.3/himeHV 

and type

	[shell] make 

inside. This will create the shared library

	pages/backend/hv/CAENHVWrapper-6.3/himeHV/libHVWrapper.so



### Create Python Environment (recommended)
It is recommended to use a separate Python environment for Power-Supply Control. To do so, you need to 

	[shell] apt-get install python3.8-venv

and then execute the command 

	[shell] python3 -m venv .venv

which will create a new environment in the directory `.venv`. (The location of `.venv` can be chosen arbitrarily, but in the following, it assumed to be in the home directory.) 
To start using the environment, type

	[shell] source ~/.venv/bin/activate

and to leave the environment, type

	[shell] deactivate

Make sure to install all Python packages for Power-Supply control inside this environment. In order to check which Python and pip installations you are currently using, execute

	[shell] which python
	[shell] which pip



### Install Python Packages
Power-Supply Control is written for (and was tested with) Python3. As usual, you can install the required python packages using `pip3`. For instance, install streamlit with

	pip3 install streamlit

and the InfluxDB client with 

	pip install influxdb-client



### Install InfluxDB Open Source
See https://www.influxdata.com/products/influxdb/.



## Setup



### InfluxDB
In order to give Power-Supply Control access to your InfluxDB, you need to define an environment variable in your shell that contains the InfluxDB token.
Open a `tmux` session (or `screen` or similar) and type

	[shell] export INFLUX_TOKEN='[your_token]'

The URL of the InfluxDB server as well as the organization and the bucket you want to submit the data to can be defined in 

	pages/backend/InfluxDBConfig.py

Besides, you can choose a time interval for the automatic data submission to InfluxDB. You can set a negative value to disable the data submission completely.



### Adding or Removing LV and HV Supplies
If you want to add or remove LV HV supplies from Power-Supply Control, or change their IP addresses, you can do so in the files

	pages/backend/lv/LVDefinitions.py

and

	pages/backend/hv/HVDefinitions.py

Inside these files, you can choose an arbitrary name for your devices. (In particular, the names don't need to be identical with the host names of the devices.) Note that your choice defines the name tag of the data submitted to InfluxDB. For the data from the HV supply, an underscore followed by the channel number will be appended to the name tag.



## Start and Stop the Program
Executing

	[shell] ./start.sh

will activate the Python environment (see [Create Python environment (recommended)](#create-python-environment-recommended)) and start the program.

In the URL line of your favorite web browser, type

	[machine_for_powerSupplyControl]:8501

where `[machine_for_powerSupplyControl]` is the hostname of the PC that runs Power-Supply Control, for instance

	hime02:8501

If that doesn't work, the IP address or the port of the server might have changed. If so, you can find the correct IP address and port printed to your tmux session behind `Network URL`.

You can stop Power-Supply Control by typing `Ctrl+C` twice. Currently, it will end with a `RuntimeError` exception, which is a consequence of using multithreading in combination with streamlit.
Currently, I am not aware of a solution that leads to a more graceful ending of the program, so you need to ignore the message until this issue is solved.



## Access the Web Page from Outside of Your Workplace
One of the main advantages of Power-Supply Control is that you can use an arbitrary web browser on any machine to access your devices. However, if you want to open the web page while you're not at your work place, you have to get access to the local network of your workplace at first. This might be possible by opening a dynamic ssh tunnel (depending on the IT-security policy of your workplace). To do so, type

	[shell] ssh -D [free_port] [user]@[serverAtWorkplace]

where `[free_port]` is an unoccupied port on your PC and `[user]` is the username you use to login to the server `[serverAtWorkplace]` which is part of the local network of your workplace. Then, go to the proxy settings of your web browser and select the following:
- Choose "Manual proxy configuration"
- Choose "SOCKS v5"
- Choose "Proxy DNS when using SOCKS v5"
- For "SOCKS Host", enter `localhost`
- As "Port", enter `[free_port]`

The, in the URL line of your web browser, type

	[machine_for_powerSupplyControl]:8501

where `[machine_for_powerSupplyControl]` is the same as in [Start and Stop the Program](#start-and-stop-the-program), but can be different from `[serverAtWorkplace]` in general.



## Details
For the communication with the TDK Lambda LV supply, a TCP socket is used. All information on how that is done can be found in the TDK Lambda manual. Please also note the settings that can be done in the web interface of the power supply itself. (Type the IP of the device in your web browser.)

The communication with the Caen HV supply also works via TCP, but all the functionality is inside a pre-compiled library that can be downloaded from the Caen webpage. For this library, there exists an "HV wrapper" written in C code, which I modified to make it compatible with the streamlit server. The C code is compiled by typing 

	[shell] make 

in the directory

	pages/backend/hv/CAENHVWrapper-6.3/himeHV

As there is no Python version of the HV wrapper from Caen, another wrapper (written in Python) is required to make it compatible with streamlit. (So, in summary, you need to use a C wrapper in Python, which wraps the HV wrapper written in C, which controls the pre-compiled library, which communicates with your device via TCP.)

If a command fails, an error code is sent. A list of all error codes can be found in the file `pages/backend/hv/CAENHVWrapper-6.3/include/CAENHVWrapper.h`.
	
The original version of the C code can be found in 

	pages/backend/hv/CAENHVWrapper-6.3/HVWrapperDemo

It can still be compiled with `make` and started with `./HVWrappdemo`. This will lead to an interactive terminal interface, which allows communicating with the HV supply for testing purposes.

There are external links on the home page of Power-Supply control leading to the manuals of the TDK Lambda LV supply, the Caen HV supply and the C library for the Caen HV wrapper.



## License
Power-Supply Control serves to remotely control the low-voltage (LV) and high-voltage (HV) power supplies for the HIME neutron detector.

Copyright (C) 2024 Marco Knösel (marco.knoesel@t-online.de)

Power-Supply Control is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Power-Supply Control makes use of the CAEN HV Wrapper, version 6.3, developed by C.A.E.N. S.p.A, is licensed under the "License Agreement for CAEN Software or Firmware", see 

	pages/backend/hv/CAENHVWrapper-6.3/CAEN_License_Agreement.txt
	
The CAEN HV Wrapper is located in
	
	pages/backend/hv/CAENHVWrapper-6.3

The contents of

	pages/backend/hv/pages/backend/hv/CAENHVWrapper-6.3/himeHV

were copied from the CAEN HV Wrapper and modified. All modifications which are not covered by the copyright of C.A.E.N. S.p.A and the "License Agreement for CAEN Software or Firmware" underlie the copyright and the license of Power-Supply Control.