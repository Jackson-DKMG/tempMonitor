from flask import Flask, render_template, jsonify
from datetime import datetime
from time import sleep, mktime
from threading import Thread
from subprocess import STDOUT, check_output #, PIPE
from json import dumps, loads
#from requests import get
import logging
from shutil import copyfile
from nest import apiConnect

import variables
import nest_data

from socket import socket, AF_INET, SOCK_DGRAM

#get the local IP address
def getIP():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    return IP

##autoreboot    #no longer necessary
#import ctypes
#import struct
#from os import system
#libc = ctypes.CDLL('libc.so.6')
#buf = ctypes.create_string_buffer(4096)
##

logging.basicConfig(filename='/home/pi/tempMonitor/graph.log', filemode='w', format='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S :', level=logging.DEBUG)

try:
    with open('/home/pi/tempMonitor/data') as f:
       for line in f:
         data = loads(line)

    data1 = data[0]
    data2 = data[1]
    data3 = data[2]
    data4 = data[3]
    data5 = data[4]
    data6 = data[5]

except Exception as e:
    logging.error("Couldn't load data, loading the backup: " + str(e))
    copyfile('/home/pi/tempMonitor/data', '/home/pi/tempMonitor/data_corrupted')
    try:
        with open('/home/pi/tempMonitor/dataBackup') as f:
            for line in f:
                data = loads(line)

        data1 = data[0]
        data2 = data[1]
        data3 = data[2]
        data4 = data[3]
        data5 = data[4]
        data6 = data[5]

    except Exception as e:
        logging.error("Couldn't load the backup either. Starting with no history: " + str(e))
        data = []
        pass

def query(dict_name,ip):

        try:
           res = str(check_output(["ssh", "pi@{0}".format(ip), "python3 getTemp.py"], stderr=STDOUT, timeout=5))[2:-3]
           result = float(res)
        except Exception as e:
           logging.warning(ip + ": " + str(e))
           try:
               result = dict_name[-1]["temp"] #if any error, just reuse the previous value
           except Exception as e1:
               logging.warning(ip + ": " + str(e1))
               result = 0

        return result

def removeOldEntries(dataset):

        temp_dict = []
        for i in dataset:
            if i['date'] < int(mktime   (datetime.now().timetuple())) - 172800:
                temp_dict.append(i)
        for i in temp_dict:
                dataset.remove(i)

app = Flask(__name__)

class getTemp(Thread):

    def __init__(self):
        super().__init__()
        self.sdm = None #the Nest resource object
        self.data = []
        self.temp1 = 0
        self.temp2 = 0
        self.temp3 = 0
        self.temp4 = 0
        self.temp5 = 0
        self.temp6 = 0

    def run(self): #subroutine to check the temperature every 2 minutes

        while True:

          ###### BEGIN LOCAL TEMP ######
            try:
               #temp2 = Popen(["ssh", "pi@192.168.3.48", "python3 getLocalTemp.py"], stdout=PIPE).communicate()[0]
               #res = Popen(["python3", "/home/pi/tempMonitor/getLocalTemp.py"], stdout=PIPE).communicate()[0]
               res = str(check_output(["python3", "/home/pi/tempMonitor/getLocalTemp.py"], stderr=STDOUT, timeout=5))[2:-3]
               self.temp2 = float(res)
               logging.info("Pi 3 = " + str(self.temp2))
            except Exception as e:
               logging.warning("Pi 3: " + str(e))
               #temp2 = 0
               try:
                   self.temp2 = data2[-1]["temp"]
               except Exception as e1:
                   logging.warning("Pi 3: " + str(e1))
                   self.temp2 = 0
          ##### END LOCAL TEMP #####

          ##### PI ZEROS START ####
            self.temp1 = query(data1, "192.168.3.40")
            self.temp3 = query(data3, "192.168.3.41")
            self.temp5 = query(data5, "192.168.3.43")
            self.temp6 = query(data6, "192.168.3.42")
           ##### PI ZEROS END ####

           ##### EXTERNAL TEMP: request every 10 minutes instead of 2 ####
          #exterior sensor is connected to the .43 RPI, but the script has a different name so can't use the "query" function.
            variables.extTempDelay = variables.extTempDelay + 1
            if variables.extTempDelay > 4:
               try:
                    res = str(check_output(["ssh", "pi@192.168.3.43", "python3 getExternalTemp.py"], stderr=STDOUT, timeout=5))[2:-3]
                    self.temp4 = float(res)
                    logging.info("External = " + str(self.temp4))
               except Exception as e:
                    logging.warning("External :" + str(e))
                    try:
                        self.temp4 = data4[-1]["temp"]
                    except Exception as e1:
                        logging.warning("External :" + str(e1))
                        self.temp4 = 0
            ##### END EXTERNAL TEMP ####

            #### ROOM 3 : MANUAL HEATING START AT NIGHT ####
            try:
                if datetime.now().hour > 21 or datetime.now().hour < 4:
                  #print(datetime.now().hour)
                    if 0 < float(self.temp3) < 17.5 and variables.heat_on == 0 :
                        if not self.sdm:
                            self.sdm = apiConnect().connect()
                            request = {"command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat","params": {"heatCelsius": 20.0}}
                            self.sdm.enterprises().devices().executeCommand(name=nest_data.name,body=request).execute()

                            variables.heat_on = 1
                            logging.critical("Temperature in room 3 is {0} ; heating activated".format(self.temp3))

                    elif float(self.temp3) > 0 and float(self.temp3) > 18 and variables.heat_on == 1:
                        #print("off")
                        if not self.sdm:
                            self.sdm = apiConnect().connect()
                            request = {"command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", "params": {"heatCelsius": 18.0}}
                            self.sdm.enterprises().devices().executeCommand(name="enterprises/de7329e7-b23e-4e23-a13b-633b67c4a7fe/devices/"
                                   "AVPHwEu9X3X5t7NOybVFebPTxkfbHPbyMRTpoK4H-iXFcGQnsL8LRHIn-udhyKQ6IUtLhGBkRnirYVzgq-Y1PtZN8xp0tg",body=request).execute()
                        heat_on = 0
                        logging.critical("Temperature in room 3 is {0} ; heating deactivated".format(self.temp3))

                elif variables.heat_on == 1:
                         variables.heat_on = 0

            except Exception as e:
                  logging.warning(str(e))
                  pass
            #### END ROOM 3 ####

            for i,j in ([self.temp1,data1], [self.temp2, data2],[self.temp3,data3],[self.temp4,data4],
                        [self.temp5,data5], [self.temp6,data6]):
                try:
                    checkpoint = {'temp': i, 'date': int(mktime(datetime.now().timetuple()))}
                    j.append(checkpoint)
                    removeOldEntries(j)
                    self.data.append(j)
                except Exception as e:
                    logging.warning(str(e))
                    pass

            #try:
            #   if float(self.temp1) < 85:  #sometimes the garage sensor sends a crazy high reading. Ignore if so.
            #       checkpoint = {'temp': self.temp1, 'date': int(mktime(datetime.now().timetuple()))}
            #       #print(checkpoint)
            #       data1.append(checkpoint)
            #       removeOldEntries(data1)
            #except:
            #       pass

            try:
                with open('/home/pi/tempMonitor/data', 'w') as file:
                    file.write(dumps(self.data))
                    variables.saveData = variables.saveData + 1

            except Exception as e:
                logging.error("Couldn't write data to file: " + str(e))
                pass

            if variables.saveData > 4:         #make a backup of the data file every 10 minutes.
                   variables.saveData = 0
                   try:
                       copyfile('/home/pi/tempMonitor/data', '/home/pi/tempMonitor/dataBackup')
                   except Exception as e:
                       logging.error("Couldn't make the backup: " + str(e))
                       pass

            self.data = []

 ##REBOOT AT NIGHT     #disabled, not needed anymore. Also, seems like it wasn't working anymore, too.
            #libc.sysinfo(buf)
            #if datetime.now().hour == 0 and 2 <= datetime.now().minute <= 5 and round(struct.unpack_from('@l', buf.raw)[0]/3600) > 12:
            #        system('sudo reboot')


            sleep(120)

getTemp = getTemp()
getTemp.daemon = True

@app.route('/', methods=['GET'])
def graph():
   return render_template('graph.html')

@app.route('/_getTemp1', methods=['GET'])
def response():
    return jsonify(data1)

@app.route('/_getTemp2', methods=['GET'])
def response2():
    return jsonify(data2)

@app.route('/_getTemp3', methods=['GET'])
def response3():
    return jsonify(data3)

@app.route('/_getTemp4', methods=['GET'])
def response4():
    return jsonify(data4)

@app.route('/_getTemp5', methods=['GET'])
def response5():
    return jsonify(data5)

@app.route('/_getTemp6', methods=['GET'])
def response6():
    return jsonify(data6)


if __name__ == '__main__':
    IP = getIP()
    getTemp.start()
    app.run(host=IP, port=5005, debug=True)
