# This script is compatible with the manson HCS-3102 power supply
# The script controls the voltage, current as well as the light pulse length and interval between light pulses

import serial, time 

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE)

x = 1 # first variable
y = 2 # second variable


def initialize():
	
	z = 1

	while z:                        
                                        
                                        
		ser.write("VOLT174\r")	# defines voltage
		time.sleep(0.5)
		response=ser.readline()
			
		if response == '':
			continue			
		break
	
	
					
	while z:
		ser.write("CURR017\r")	# defines current
		time.sleep(0.5)
		response=ser.readline()
		if response == '':
			continue			
		break


def illuminate():
	
	w = 1

	while w:

		ser.write("SOUT0\r")	# Send set voltage command. 
		time.sleep(0.5)
		response=ser.readline()
			
		if response == '':
			continue			
		break
	
	time.sleep(5)  #defines the light pulse length (in seconds)
					
	while w:
		ser.write("SOUT1\r")	# Send set voltage command. 
		time.sleep(0.5)
		response=ser.readline()
		if response == '':
			continue			
		break


	time.sleep(10)  # defines the interval between two light pulses (in seconds)
	


if ser.isOpen():

	try:
		ser.flushInput()
		ser.flushOutput()
		
		initialize()
		while x: 

			illuminate()
		
			
	
	except Exception, e1:
		print("Error communicating...: " + str(e1))
