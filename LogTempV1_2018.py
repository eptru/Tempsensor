#Finished on 11/19/2018
import serial #py -m pip install pySerial
import csv
import time
from time import strftime, localtime
import sys
import os

usbport = 'COM3'		#Check and change if replugging the Arduino
sensorListFile='sensorList.dat'
filename=strftime("%Y%m", localtime())+'TemperatureLogFile.csv'
currentmonth = localtime().tm_mon

sensorList=[]
fieldnames = ['time1', 'time2']

def updateHeader():
	with open(filename,newline='') as f:
		r = csv.reader(f)
		data = [line for line in r]
	with open(filename,'w',newline='') as f:
		w = csv.writer(f)
		w.writerow(fieldnames+sensorList)
		w.writerows(data[1:])

ser = serial.Serial(usbport, 9600, timeout = 1)
if not ser.isOpen():
    ser.open()
print(usbport+' is open', ser.isOpen())
print ('Engine, start....rrrrrrrRRRRRRRRRRRRRR')

try:
	open(sensorListFile, 'r')
except:
	with open(sensorListFile, 'w+') as f:
		for s in sensorList:
			f.write(s + '\n')
		print ("file written")

with open(sensorListFile, 'r') as f:
	sensorList = [line.split(' ')[0].rstrip('\n') for line in f]
	print ("Sensor list loaded")

time.sleep(2) #strangely useful

try:
	open(filename, 'r')
	updateHeader()
except:
	with open(filename, 'w+', newline='') as f:
		w=csv.writer(f)
		w.writerow(fieldnames+sensorList)

with open(filename, 'a', newline='') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames+sensorList)
	while True:
		if (localtime().tm_mon!=currentmonth):
			os.execl(sys.executable, sys.executable, *sys.argv)
		print ('Recording: ',strftime("%Y-%m-%d %H:%M:%S", localtime()))
		dict = {'time1': str(time.time()), 'time2': strftime("%Y-%m-%d %H:%M:%S", localtime())}
		ser.write('test\n'.encode())
		for i in range(16):
			s=''
			s = ser.readline().strip(b'\n')
			if (s.isspace()) or (s==b'Start') or (s==b''):
				continue
			if (s==b'Stop'):
				break
			ID=s.split()[0].decode()
			value=s.split()[1].decode()
			if not ID in sensorList:
				sensorList.append(ID)
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames+sensorList)
				with open(sensorListFile, 'a') as f:
					#for s in sensorList:
					f.write(ID+'\n')
				updateHeader()
				print ("New sensor found and added")
			dict[ID] = value
			#print s
		writer.writerow(dict)	
		csvfile.flush()
		time.sleep(1)	#control gap time here unit: s
		
ser.close()