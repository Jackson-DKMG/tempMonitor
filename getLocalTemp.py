from w1thermsensor import W1ThermSensor
#from time import sleep


#sum = 0
for i in W1ThermSensor.get_available_sensors():
	#sum = sum + i.get_temperature()
	temp = i.get_temperature()

print(round(temp, 2))

