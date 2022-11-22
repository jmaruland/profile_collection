# import sys
# import threading
# import argparse
import time
# import csv
# import os
# import numpy

from ophyd import Device, Signal, Component as Cpt


class KibronTrough(Device):
    '''
    To get target parameters from the kibron trough
    '''

    pressure = Cpt(Signal, kind = 'hinted')
    area = Cpt(Signal, kind = 'hinted')
    speed = Cpt(Signal, kind = 'normal')
    temperature1 = Cpt(Signal, kind = 'normal')
    temperature2 = Cpt(Signal, kind = 'normal')
    deviceStatus = Cpt(Signal, kind = 'normal')


    def __init__(self, device, sock, name = 'Kibron', read_attrs=None, *args, **kwargs):
        
        if read_attrs is None:
            read_attrs = ['pressure', 'area', 'speed', 'temperature1', 'temperature2']
        
        super().__init__(name = name, read_attrs=read_attrs, *args, **kwargs)
        self.name = name
        self.sock = sock
        self.device = device
        self.data = self.getData()
        self.update()
        # self.area.put(self.getArea())
        # self.pressure.put(self.getPressure())
        # self.speed.put(self.getSpeed())
        # self.temperature1.put(self.getTemperature1())
        # self.temperature2.put(self.getTemperature2())
        # self.deviceStatus.put(self.getDeviceStatus())

    def getData(self):
        try:
            vals = self.device.call("GetData")
            # Expecting the result to be of the form
            #   '<status-code> <value-1> <value-2> ... <value-n>
            # vals is list comprising staus code followed by list of values
            count = vals[0]
            if count >= 0:
                return vals
            else:
                print('Data polling error!')
        except:
            pass

    def update(self):
        latest_data = self.getData()
        self.area.put(latest_data[mtx.uTArea])
        self.pressure.put(latest_data[mtx.uTPressure])
        self.speed.put(latest_data[mtx.uTSpeed])
        self.temperature1.put(latest_data[mtx.uTTemperature1])
        self.temperature2.put(latest_data[mtx.uTTemperature2])
        self.deviceStatus.put(latest_data[mtx.uTDeviceStatus])

    def getArea(self):
        self.area.put(self.getData()[mtx.uTArea])
        return self.area.get()

    def getPressure(self):
        self.pressure.put(self.getData()[mtx.uTPressure])
        return self.pressure.get()

    def getSpeed(self):
        self.speed.put(self.getData()[mtx.uTSpeed])
        return self.speed.get()

    def getDeviceStatus(self):
        self.deviceStatus.put(self.getData()[mtx.uTDeviceStatus])
        return self.deviceStatus.get()

    def getTemperature1(self):
        self.temperature1.put(self.getData()[mtx.uTTemperature1])
        return self.temperature1.get()

    def getTemperature2(self):
        self.temperature2.put(self.getData()[mtx.uTTemperature2])
        return self.temperature2.get()

    def close(self):
        self.sock.close()


    def runPressureManual(self, target_pressure, max_area = 6000, target_speed = None):
        '''TO BE DONE'''

        if target_speed == None:
            max_speed = self.device.call("GetMaxBarrierSpeed")
            target_speed = max_speed/4


        try:
            print("Compressing barriers, gathering measurement data ...")

            # Tell the trough to produce measurement samples at 1 second intervals
            self.device.call("SetStoreInterval", 1.0)

            self.device.call("SetBarrierSpeed", target_speed)

            self.device.call("NewMeasureMode", mtx.MeManual)

            # Set time_offset in the measurement file when starting measurement
 
            self.device.call("StartMeasure")

            self.device.call("StepCompress")

            # Wait until area is three-quarters maximum
            print(f'Target pressure is {target_pressure}')
            _pressure = self.getPressure()
            print(f'Current pressure is {_pressure}')

            while _pressure-target_pressure < 0:
                time.sleep(1)
                _data = list(self.getData())
                _area = _data[mtx.uTArea]
                if _area < max_area * 0.25:
                    print('Area is less than 25%.')
                    break
                _pressure = _data[mtx.uTPressure]
                print('Pressure is: %.2f mN/m' %_pressure)

            self.device.call("StepStop")

            self.device.call("StopMeasure")

            print("... Done")


        except:
            pass

import importlib
mtx = importlib.import_module('85-mtx_client')


# # Communications with the trough
# import importlib
# mtx = importlib.import_module('85-mtx_client')
# # import mtx_client as mtx

# HOST, PORT = "10.66.91.26", 9897 ## HZ
# sock = mtx.connect(HOST, PORT)
# device = mtx.Trough(sock)
# kibron = KibronTrough(device, sock)

# ### Need to run kibron.close() to disconnect when it is done


