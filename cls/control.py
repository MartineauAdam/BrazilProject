import os
import time
import subprocess
import io

"""@package docstring
File name : control.py
Auteur : Adam Martineau
Date : 22/05/2018
Bref : The main class used by the main.py program, contain all function to 
	   read/right in the i2c and in local files. Also containe a butch of 
	   usefull fonction made for our use.
Environnement : Rasbian Stretch 9.1
Compilateur : Python 2.7.13
Materiel : Rasberry Pi zero W
Revision : V1.2
"""

class Control(object):
	
	def __init__(self, config_file, bus):
		"""
		@Name : __init__()
		@Brief : the class constructor
		@Input arg : n/a
		@Return : n/a
		"""
		
		self.config_file = config_file
		self.bus = bus
		
	def write(self, address, string, delay):
		"""
		@Name : write()
		@Brief : write any int to the EZO circuit
		@Input arg : (int) address : the address of the EZO circuit we want to write to
					 (string) string : the string we want to send trough I2C
		@Return : n/a
		"""
		
		r = True
		
		try:
			#we send the commend over I2C
			buffer = []
			
			for i in range(len(string)):
				if i != 0:
					buffer.append(ord(string[i]))

			self.bus.write_i2c_block_data(address, ord(string[0]), buffer)
			
			time.sleep(delay)#we wait for the sensor to compute our command
			
		except Exception as e:
			r = False
			
			errorFile = open(self.config_file.get("PATH", "error"), "a")
			errorFile.write(str(e) + " : " + time.strftime("%H:%M;%d/%m/%Y") + "\n")
			errorFile.close()
			
		return r
	
	def read(self, adr):
		"""
		@Name : read()
		@Brief : read any EZO circuit
		@Input arg : (int) address : the address of the EZO circuit
		@Return : the answer from the EZO circuit
		"""
		
		buffer = []
		output = ""
		
		try :
			buffer = self.bus.read_i2c_block_data(adr ,0)
		except Exception as e:
			errorFile = open(self.config_file.get("PATH", "ERROR"), "a")
			errorFile.write(str(e) + " : " + time.strftime("%H:%M;%d/%m/%Y") + "\n")
			errorFile.close()
		
		#we convert a list of int to a string
		buffer[0] = 0 #we don't read the first char
		
		for i in buffer:
			i &= 0x7F
			output += chr(i)

		output = output.replace("\x00", "")#we earase empty character
		
		return output
		
	def is_number(self, n):
		"""
		@Name : is_number()
		@Brief : return "true" if the string "n" is purely made out of integer, else return "false"
		@Input arg : n : the string that need verification 
		@Return : true or false
		"""
	
		try:
			#we try to cast the "number" into the integer form
			int(n)

		#if it crashes then it's not a number
		except ValueError:
			return False

		return True
	
	def readconfig(self):
		"""
		@Name : readconfig()
		@Brief : read and print all the config 
		@Input arg : n/a
		@Return : n/a
		"""
		
		print("EZO circuit address I2C address :")
		print("	   PH : " + self.config_file.get("ADDRESS", "PH"))
		print("	   DO : " + self.config_file.get("ADDRESS", "DO"))
		print("	   CON : " + self.config_file.get("ADDRESS", "CON"))
		print("	   Temp : " + self.config_file.get("ADDRESS", "TEMP"))
		print("")
		print("Data location :")
		print("	   USB : " + self.config_file.get("PATH", "USB"))
		print("	   LOCAL : " + self.config_file.get("PATH", "LOCAL"))
		print("	   ERROR LOG : " + self.config_file.get("PATH", "ERROR"))	

	def writeData(self, data):
		"""
		@Name : save()
		@Brief : right date to the usb key, if no usb key is detected, we save the date locally
		@Input arg : (string) data : the data we want to save to the usb key
		@Return : n/a
		"""
	
		send = data.replace("\x00", "")
		
		if (self.is_usb()):
			try:
				usb = open(self.config_file.get("PATH", "usb"), "a")
				usb.write(data)
				usb.close()
			except Expetion as e:
				errorFile = open(self.config_file.get("PATH", "error"), "a")
				errorFile.write(str(e) + " : " + time.strftime("%H:%M;%d/%m/%Y") + "\n")
				errorFile.close()
		else:
			try:
				localFile = open(self.config_file.get("PATH", "local"), "a")
				localFile.write(data)
				localFile.close()
			except Expetion as e:
				errorFile = open(self.config_file.get("PATH", "error"), "a")
				errorFile.write(str(e) + " : " + time.strftime("%H:%M;%d/%m/%Y") + "\n")
				errorFile.close()
	
	def changeDate(self):
		"""
		@Name : changeDate()
		@Brief : print a menu and take the user input to change Rasbian system date and time
		@Input arg : n/a
		@Return : n/a
		"""
	
		print("All input must be numerical")
		print("")

		#the user input the date
		year = input("Year : ")
		month = input("Month : ")
		day = input("Day : ")
		
		print("")
		
		#and the time
		hour = input("Hour : ")
		min = input("Minute : ")
		sec = input("Second : ")
		
		print("")
		
		os.system("sudo date -s '" + year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec + "'")
		
		print("")
		
		subprocess.Popen(['bash', '-c', '. /home/pi/wittyPi/utilities.sh; system_to_rtc'])
		
		print("")
		
		time.sleep(3)
		
		os.system("sudo rm wittyPi.log")
		
		print("")

	def changeAdd(self):
		"""
		@Name : changeAdd()
		@Brief : print a menu and take the user input to change a selected address
		@Input arg : n/a
		@Return : n/a
		"""
	
		quit = False

		while quit != True:
			addressType = input("Select sensor :\n\r    (1) Dissolved oxygen\n\r    (2) PH\n\r    (3) Conductivity\n\r    (4) Temperature\n\r\n\rSensor : ")

			newAdd = input("\n\rNew address : ")
			print("")
			
			if addressType == "1" and self.is_number(newAdd) == True:
				self.config_file.set("ADDRESS", "DO", newAdd)
				quit = True

			elif addressType == "2" and self.is_number(newAdd) == True:
				self.config_file.set("ADDRESS", "PH", newAdd)
				quit = True

			elif addressType == "3" and self.is_number(newAdd) == True:
				self.config_file.set("ADDRESS", "CON", newAdd)
				quit = True

			elif addressType == "4" and self.is_number(newAdd) == True:
				self.config_file.set("ADDRESS", "TEMP", newAdd)
				quit = True

			else:
				print("\033[1;37;41m" + "Wrong input" + "\033[1;32;40m")


		with open("./cfg/config.ini", "w") as file:
			self.config_file.write(file)

	def changePath(self):
		"""
		@Name : changePath()
		@Brief : print a menu and take the user input to change a selected path, where data is stored 
		@Input arg : n/a
		@Return : n/a
		"""
	
		quit = False

		while quit != True:

			pathType = input("Select a path to change :\n\r    (1) USB Key\n\r    (2) Local data file\n\r    (3) Local error file\n\r\n\rPath :")

			newpath = input("Use the format : /media/pi/Transcend/Data/data.csv \n\r Has to point to a .csv, except for the error log \n\r New path :")

			if pathType.upper() == "1":
				#usbPath = newpath
				self.config_file.set("PATH", "usb", newpath)
				quit = True

			elif pathType.upper() == "2":
				#localPath = newpath
				self.config_file.set("PATH", "local", newpath)
				quit = True

			elif pathType.upper() == "3":
				#errorFilePath = newpath
				self.config_file.set("PATH", "error", newpath)
				quit = True

			else:
				print("\033[1;37;41m" + "Wrong input" + "\033[1;32;40m")

		with open("./cfg/config.ini", "w") as file:
			self.config_file.write(file)

	def Sleep(self, state, adr):
		"""
		@Name : Sleep()
		@Brief : Put a EZO chip to sleep or wake it up from sleep.
		@Input arg : (bollean) state : True or False, define if we put the chip to sleep (True) or wake it up (False)
					 (string) adr : address of the chip we want to control
		@Return : n/a
		"""
		
		#we decide what will be send to the sensor
		if state == True:
			send = "SLEEP"
		elif state == False:
			send = "WAKEUP"

		Buffer = []

		#we send our string
		for i in range(len(send)):
			if i > 0:
				Buffer.append(ord(send[i]))
		try:
			self.bus.write_i2c_block_data(int(adr), ord(send[0]), Buffer)
		except Exception as e:
			errorFile = open(self.config_file.get("PATH", "ERROR"), "a")
			errorFile.write(str(e) + " : " + time.strftime("%H:%M,%d/%m/%Y") + "\n")
			errorFile.close()

		time.sleep(0.9)
	
	def calibration(self):
		"""
		@Name : calibration()
		@Brief : print a menu and take the user input to calibrate the EZO circuit
		@Input arg : n/a
		@Return : n/a
		"""
		
		while True:
			#under menu 
			print("Welcome to the calibration menu \n\r")
			print("\033[1;37;41m" + "When calibrating the probe, watch out")
			print("for cross contamination of liquids\n\r" + "\033[1;32;40m")
			print("*Select a probe to caliber*")

			#the user chose witch sensor he want to talk to
			buffer_input = input("DO, PH, CON, TEMP, enter the \"q\" command to exit:")
			
			#sensor selection
			if buffer_input.upper() == "DO":
				self.cal_do()
			elif buffer_input.upper() == "PH":
				self.cal_ph()
			elif buffer_input.upper() == "CON":
				self.cal_con()	
			elif buffer_input.upper() == "TEMP":
				self.cal_temp()
			elif buffer_input.upper() == "Q":
				break
			else:
				print("\033[1;37;41m" + "Wrong input" + "\033[1;32;40m")
	
	def cal_temp(self):
		"""
		@Name : cal_temp()
		@Brief : calibration of the temperature sensor
		@Input arg : n/a
		@Return : n/a
		"""
	
		while True:
			print("Selecte between :\n\r(1)Calibration\n\r(2)Clear calibration data\n\r")
			buffer = input("Select a calibration option(1~2), enter the \"q\" command to exit:")
			
			if buffer == "q":
				break
			
			#one point calibration 
			elif buffer == "1":
				temp = input("Enter the calibration temperature :")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "TEMP"), "Cal," + temp, 0.9)
			
			#clear calibration data
			elif buffer == "2":
				self.cal_clear("TEMP")
	
	def cal_con(self):
		"""
		@Name : cal_con()
		@Brief : calibration of the electrical conductivity sensor
		@Input arg : n/a
		@Return : n/a
		"""	
	
		while True:
			print("")
			print("A dry calibration " + "\033[1;37;41m" + "WILL" + "\033[1;32;40m" + " be done in the calibration step when doing any other calibration\n\r")
			print("Selecte between :\n\r(1)One point calibration\n\r(2)Two points calibration\n\r(3)Clear calibration data\n\r")
			buffer = input("Select a calibration (1~4), enter the \"q\" command to exit:")
			print("")
			
			if buffer == "q":
				break
			
			#one point calibration 
			elif buffer == "1":
				print("First will need to do a dry calibration")
				print("Make sur the probe is " + "\033[1;37;41m" + "DRY" + "\033[1;32;40m")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "CON"), "Cal,dry", 1.3)
				
				print("Now for the calibration")
				print("Enter the one point calibration value,\n\rexpressed in any E.C. value in microsiemens\n\r")
				#taking user input
				cal_value = input("Value: ")
				print("Insert the probe in the calibration liquide\n\r")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "CON"), "Cal,one," + cal_value, 1.3)
			
			#one point calibration 
			elif buffer == "2":
				print("First will need to do a dry calibration")
				print("\033[1;37;41m" + "Make sur the probe is DRY" + "\033[1;32;40m")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "CON"), "Cal,dry", 1.3)
				
				print("Now for the calibration")
				print("Enter the low point calibration value,\n\rexpressed in any E.C. value in microsiemens\n\r")
				#taking user input
				cal_value = input("Low value: ")
				print("Insert the probe in the calibration liquide")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "CON"), "Cal,low," + cal_value, 1.3)
				
				print("Enter the high point calibration value,\n\rexpressed in any E.C. value in microsiemens\n\r")
				#taking user input
				cal_value = input("High value: ")
				print("Insert the probe in the calibration liquide")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "CON"), "Cal,high," + cal_value, 1.3)
				
			elif buffer == "3":
				self.cal_clear("CON")
	
	def cal_ph(self):
		"""
		@Name : cal_ph()
		@Brief : calibration of the ph sensor
		@Input arg : n/a
		@Return : n/a
		"""
		
		while True:
			print("")
			print("A MIDPOINT calibration MUST be done before any other calibration\n\r")
			print("Selecte between :\n\r(1)Midpoint calibration\n\r(2)Lowpoint calibration\n\r(3)Highpoint calibration\n\r(4)Clear calibration data\n\r")
			buffer = input("Select a calibration (1~4), enter the \"q\" command to exit:")
			print("")
			
			if buffer == "q":
				break
			
			#midpoint calibration
			elif buffer == "1":
				print("Enter the midpoint calibration value,\n\rexpressed in ph, should be 7.XX")
				#taking user input
				cal_value = input("Midpoint value: ")
				print("Insert the probe in the calibration liquide\n\r")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "PH"), "Cal,mid," + cal_value, 1.6)
			
			#lowpoint calibration
			elif buffer == "2":
				print("Enter the lowpoint calibration value,\n\rexpressed in ph (1~14)")
				#taking user input
				cal_value = input("Lowpoint value: ")
				print("Insert the probe in the calibration liquide\n\r")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "PH"), "Cal,low," + cal_value, 1.6)
			
			#hight point
			elif buffer == "3":
				print("Enter the highpoint calibration value,\n\rexpressed in ph (1~14)")
				#taking user input
				cal_value = input("Highpoint value: ")
				print("Insert the probe in the calibration liquide")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "PH"), "Cal,high," + cal_value, 1.6)
			
			#clear calibration data 
			elif buffer == "4":
				self.cal_clear("PH")
				
	def cal_do(self):
		"""
		@Name : cal_do()
		@Brief : calibration of the dissolved oxygen sensor 
		@Input arg : n/a
		@Return : n/a
		"""
	
		while True:
			print("")
			print("A dry calibration can be done for the calibration, the 0 dissolved oxygen is optional\n\r")
			print("Selecte between :\n\r(1)Dry calibration\n\r(2)0 dissolved oxygen\n\r(3)Clear calibration data\n\r")
			buffer = input("Select a calibration (1~3), enter the \"q\" command to exit:")
			print("")
			
			if buffer == "q":
				break
				
			elif buffer == "1":
				print("Let the probe in the air")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "DO"), "Cal", 1.3)
			
			elif buffer == "2":
				print("Insert the probe in the 0 dissolved oxygen calibration liquide")
				#waiting for user
				input("Press enter when ready to calibrate")
				print("")
				#writing the calibration to the sensor 
				self.write(self.config_file.getint("ADDRESS", "DO"), "Cal,0", 1.3)
			
			elif buffer == "3":
				self.cal_clear("DO")
	
	def cal_clear(self, probe):
		"""
		@Name : cal_clear()
		@Brief : print a menu and take the user input to change a selected path, where data is stored 
		@Input arg : n/a
		@Return : n/a
		"""
	
		#writing the calibration to the sensor 
		self.write(self.config_file.getint("ADDRESS", probe), "Cal,clear", 0.3)
		print("")
		print("The clear is done")
		time.sleep(1)
		
	def is_usb(self):
		"""
		@Name : is_usb()
		@Brief : print a menu and take the user input to change a selected path, where data is stored 
		@Input arg : n/a
		@Return : n/a
		"""
		
		r = False
		
		#we start a process to detect all mounted partition
		proc = subprocess.Popen(["lsblk"], stdout=subprocess.PIPE)
		
		#we look for a partition mount in the usb file
		for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
			if line.find("/media/usb") != -1:
				r = True
				break
		
		return r