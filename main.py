"""
@package docstring
File name : testAuto.py
Auteur : Adam Martineau
Date : 23/02/2018
Bref : The main function of the program is to automatically start when the Raspberry Pi start
		and take measures, the user can change the configuration of the program by using the
		argument "config" when lunching the scrip, a user interface will then show up.
Environnement : Rasbian Stretch 9.1
Compilateur : Python 2.7.13
Materiel : Rasberry Pi zero W
Revision : V1.2
"""


###################
###___IMPORTS___###
###################

import smbus
import time
import os
import sys
import configparser
from cls.control import Control


############################
###___SOURCE_DIRECTORY___###
############################

os.chdir("/home/pi/brazilproject")


######################################
###___CONFIG_FILE_INITIALIZATION___###
######################################

"""
Initialiation
of ConfigParser
"""
config_file = configparser.ConfigParser()

#if no config file is detected we create your own with default value
if not os.path.exists("cfg/config.ini"):

	#making a new confing.ini file
	file = open("cfg/config.ini", "a")
	
	#writing default value
	file.write("[ADDRESS]\n" +
			   "do = 97\n" +
			   "con = 100\n" +
			   "PH = 99\n" +
			   "temp = 102\n" +
			   "\n" +
			   "[PATH]\n" +
			   "usb = /media/usb0/data.csv\n" +
			   "local = data/data.csv\n" +
			   "error = err/errorlog.txt\n")
			   
	#closing file
	file.close()

#we read config.ini
config_file.read("cfg/config.ini")


######################
###___GLOBAL_VAR___###
######################

#making of a object to communicate on the I2C bus
bus = smbus.SMBus(1)
#classe with all the sub fonction inside
machine = Control(config_file, bus)	


###############################
###___FILE_INITIALIZATION___###
###############################

"""
Reading of the I2C address 
from the config file
"""
#all the address of the used EZO circuit, those can be changed in the user interface
addressTEMP = config_file.getint("ADDRESS", "TEMP")
addressCON = config_file.getint("ADDRESS", "CON")
addressPH = config_file.getint("ADDRESS", "PH")
addressDO = config_file.getint("ADDRESS", "DO")
#a usefull list containing all the address of the EZO chips
address = [addressTEMP, addressCON, addressPH, addressDO]


"""
Initialiation 
of errorlog.txt
"""
#if no error log file is detected we create your own
if not os.path.exists(config_file.get("PATH", "ERROR")):
	errorfile_ = open(config_file.get("PATH", "ERROR"), "a")
	errorfile_.close()

"""
Initialiation 
of local data file 
"""
#if no data file is detected we create a new one
if not os.path.exists(config_file.get("PATH", "LOCAL")):
	datafile_ = open(config_file.get("PATH", "LOCAL"), "a")
	datafile_.write("TIME; DATE; TEMP; CON; PH; DO; \n")
	datafile_.close()
	
"""
Initialiation 
of a usb data file 
"""
#if no data file is detected we create a new one
if machine.is_usb():
	if not os.path.exists(config_file.get("PATH", "USB")):
		datafile_ = open(config_file.get("PATH", "USB"), "a")
		datafile_.write("TIME; DATE; TEMP; CON; PH; DO; \n")
		datafile_.close()
else:
	errorFile = open(config_file.get("PATH", "error"), "a")
	errorFile.write("NO USB STRORAGE DETECTED" + " : " + time.strftime("%H:%M;%d/%m/%Y") + "\n")
	errorFile.close()

	
################
###___MAIN___###
################
"""
@Name : main()
@Brief : point of the start for the program
@Input arg : n/a
@Return : n/a
"""
def main(arg):

	#--- MAIN SWITCH CASE ---
	#if no argument is passed
	if arg.upper() == "":
		print("The program need a argument to start, please use the following arguments:")
		print("Auto : the standar programe, take measures and save them on a USB key")
		print("Config : change the I2C address of the EZO chips or the path were measures are saved")
		print("Test : takes 10 reading to be sur everything is working")

	#if the arg "auto" is used to start the scrip, we take measures
	elif arg.upper() == "AUTO":
		auto()

	#if the arg "config" is used to start the scrip, we lunch the user interface
	elif arg.upper() == "CONFIG":
		config()
		
	elif arg.upper() == "TEST":
		test()
		
	else :
		print("Wrong argument")
		

##########################
###___MAIN_FOUNCTION___###
##########################		

"""
@Name : auto()
@Brief : fonction called for the automatic part of the programe
		 take mesurs on all 4 probes and save the data 
@Input arg : n/a
@Return : n/a
"""
def auto():
	#variables to save data for later compensation
	Temperature = 0.00
	WaterSal = 0.00
	
	#we wait for the Raspberry Pi to boot
	time.sleep(10)
	
	#adding a space between all readings
	machine.writeData("\n")
	
	#we save the time and dita in our data file
	machine.writeData(time.strftime("%H:%M;%d/%m/%Y;"))
	
	#we do the "for" loop for all the sensors in the "address" list
	for i in range(0, 4):
		adr = address[i]

		#waking up the EZO from sleep
		machine.Sleep(False, adr)
		
		#we need to take 16 reading after the wake up to be sure the reading are accurate
		for i in range(16):
			machine.write(adr, "r", 0.9)
		
		"""
		Temprature and salinity compensation
		"""
		if adr == config_file.getint("ADDRESS", "CON"):
			machine.write(adr, "T," + str(Temperature), 0.3)
		elif adr == config_file.getint("ADDRESS", "PH"):
			machine.write(adr, "T," + str(Temperature), 0.3)
		elif adr == config_file.getint("ADDRESS", "DO"):
			machine.write(adr, "T," + str(Temperature), 0.3)
			machine.write(adr, "S," + str(WaterSal), 0.3)
		
		"""
		we send the char "R" to read once the 
		sensor to take a reading
		"""
		machine.write(adr, "r", 0.9)

		#we read back the answer from the EZO circuit
		buffer = machine.read(adr)
		
		#the EZO circuit is put back to sleep
		machine.Sleep(True, adr)
		
		#we save the reading in the usb key
		machine.writeData(str(buffer) + ";")
		
		"""
		Saving temprature and salinity
		for compensation later 
		"""
		if adr == config_file.getint("ADDRESS", "TEMP"):
			_Temperature = buffer
		elif adr == config_file.getint("ADDRESS", "CON"):
			_DivolvedOxy = buffer
	
	#os.system("sudo shutdown now")


"""
@Name : config()
@Brief : 
@Input arg : n/a
@Return : n/a
"""
def config():

	#we print the menu
	print("\033[1;32;40m")
	print("")
	printMenu()
	
	#Main loop
	while True:
		menuInput = input("Choose a option (1~7): ")
		print("")
		
		#Main switch case
		
		#(1) Change the registered I2C address of the EZO chip
		if menuInput == "1":
			machine.changeAdd()
			printMenu()
		
		#(2) Change file path, were data is saved
		elif menuInput == "2":
			machine.changePath()
			printMenu()
		
		#(3) Change the date of the Raspberry pi
		elif menuInput == "3":
			machine.changeDate()
			printMenu()
		
		#(4) Probe calibration
		elif menuInput == "4":
			print("")
			machine.calibration()
			printMenu()
		
		#(5) Send custum command to the EZO circuit
		elif menuInput == "5":
			manual()
			print("")
			printMenu()
		
		#(6) Read the config file
		elif menuInput == "6":#calls the function that show to the user all the config
			machine.readconfig()
			print("")
		
		#(7) Quit and save
		elif menuInput == "7" or menuInput.upper() == "Q":#quiting the menu
			break
		
		#else the input do not conform with our options
		else :
			print("")
			print("\033[1;37;41m" + "Wrong input" + "\033[1;32;40m")
			printMenu()	
			

"""
@Name : man_input()
@Brief : fonction called to send costum commends to the sensor
@Input arg : n/a
@Return : n/a
"""
def manual():	

	#we adjust the color of the text
	print("\033[1;32;40m")

	print("")
	print("Warning!!! When comming out of sleep, the EZO chip")
	print("need 16 dummy readings to be be accurate again\n\r")
	print("\033[1;37;41m" + "All reading are RAW !!! \n\r" + "\033[1;32;40m")
	
	#we wake up all the sensor from sleep
	for adr in address:
		machine.Sleep(False, adr)

	"""
	Main loop
	"""
	while True:
		wrongInput = False
		print("Use the commend Quit to exit\n\r")
		print("Select a EZO chip")
		
		#the user chose witch sensor he want to talk to
		buffer_input = input("DO, PH, CON, TEMP: ")

		#if the user inputs the command "quit" we exit the main loop
		if buffer_input.upper() == "QUIT":
			break
		
		"""
		we go look in the config file for the address of theselected 
		sensor if it fails, the input from the user was wrong, we raise 
		the "wrongInput" flag and we start all over again
		"""
		try:
			controlAdr = config_file.getint("ADDRESS", buffer_input.upper())
		except Exception as e:
			print("\033[1;37;41m" + "Wrong input" + "\033[1;32;40m")
			wrongInput = True
		
		#Loop where we send all the commands given by the user
		while wrongInput == False:
			
			#the user send his command
			send = input("Commend: ")
			
			#if the user inputs "quit", we break out this loop and go back to the main one
			if send.upper() == "QUIT":
				break
			
			machine.write(controlAdr, send, 0.9)
			
			#read the answer from the sensor
			try:
				inflow = []
				inflow = bus.read_i2c_block_data(controlAdr, 0)
			except Exception as e:
				print("Can't communicate at the selected address")

			#we convert a list of int to a string
			output = ""
			inflow[0] = 0
			for i in inflow:
				i &= 0x7F
				output = output + chr(i)
			
			print("output : " + output)
			
	#all the sensors are put back to sleep
	for adr in address:
		machine.Sleep(True, adr)

"""
@Name : test()
@Brief : fonction called for the testing, takes 10 readings
@Input arg : n/a
@Return : n/a
"""
def test():
	for x in range(0, 20):
		#adding a space between all readings
		machine.writeData("\n")
		
		#we save the time and dita in our data file
		machine.writeData(time.strftime("%H:%M;%d/%m/%Y;"))
		
		#we do the "for" loop for all the sensors in the "address" list
		for i in range(0, 4):
			adr = address[i]
			
			#waking up the EZO from sleep
			machine.Sleep(False, adr)
			
			#we need to take 16 reading after the wake up to be sure the reading are accurate
			for i in range(16):
				machine.write(adr, "r", 0.9)
			
			"""
			Temprature and salinity compensation
			"""
			if adr == config_file.getint("ADDRESS", "CON"):
				machine.write(adr, "T," + _Temperature, 0.3)
			elif adr == config_file.getint("ADDRESS", "PH"):
				machine.write(adr, "T," + _Temperature, 0.3)
			elif adr == config_file.getint("ADDRESS", "DO"):
				machine.write(adr, "T," + _Temperature, 0.3)
				machine.write(adr, "S," + _DivolvedOxy, 0.3)
			
			"""
			we send the char "R" to read once the 
			sensor to take a reading
			"""
			machine.write(adr, "r", 0.9)

			#we read back the answer from the EZO circuit
			buffer = machine.read(adr)
			
			#the EZO circuit is put back to sleep
			machine.Sleep(True, adr)
			
			#we save the reading in the usb key
			machine.writeData(str(buffer) + ";")
			
			"""
			Saving temprature and salinity
			for compensation later 
			"""
			if adr == config_file.getint("ADDRESS", "TEMP"):
				_Temperature = buffer
			elif adr == config_file.getint("ADDRESS", "CON"):
				_DivolvedOxy = buffer
		
		
"""
@Name : printMenu()
@Brief : Print our configuration menu.
@Input arg : n/a
@Return : n/a
"""
def printMenu():

	print("        IIIIIII  .d2222b.   .cCCCCc.						")
	print("          III   d22P  222b cCCP  CCCc					")
	print("          III          222 CCC    CCC					")
	print("          III        .d22P CCC							")
	print("          III    .o22222'  CCC							")
	print("          III   2222'      CCC    CCC					")
	print("          III   222'       CCCc  cCCC					")
	print("        IIIIIII 222222222   'CCCCCP'						")
	print("                          __ _							")
	print("                         / _(_)							")
	print("          ___ ___  _ __ | |_ _  __ _						")
	print("         / __/ _ \| '_ \|  _| |/ _` |					")
	print("        | (_| (_) | | | | | | | (_| |					")
	print("         \___\___/|_| |_|_| |_|\__, |					")
	print("                                __/ |					")
	print("                               |___/						")
	print("															")
	print("   Welcome to the I2C configuration menu 				")
	print("     QUIT THE PROGRAM TO APPLY CHANGE     				")
	print("															")
	print("Chose a option :											")
	print("(1) Change the registered I2C address of the EZO chip	")
	print("(2) Change file path, were data is saved					")
	print("(3) Change the date of the Raspberry pi					")
	print("(4) Probe calibration									")
	print("(5) Send custum command to the EZO circuit				")
	print("(6) Read the config file									")
	print("(7) Quit and save										")
	print("															")

	
	
#Entry point of the program, calls out main()
if __name__ == '__main__':

	if len(sys.argv) > 1:
		main(str(sys.argv[1]))
	else:
		main("")
