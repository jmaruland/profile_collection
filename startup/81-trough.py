
#for reading in the A/D and making isotherm plots

#AD1 = EpicsSignal("XF:12ID1:TrufA1", name="analog/digital 1")
#AD2 = EpicsSignal("XF:12ID1:TrufA2", name="analog/digital 2")
#AD3 = EpicsSignal("XF:12ID1-ECAT:EL3164-00-AI3", name="analog/digital 3")
#AD4 = EpicsSignal("XF:12ID1-ECAT:EL3164-00-AI4", name="analog/digital 4")
AD1 = EpicsSignal("XF:12ID1:TrufA1", name="AD1")
AD2 = EpicsSignal("XF:12ID1:TrufA2", name="AD2")

import matplotlib.pyplot as plt 
import json
import time


def isotherm(wait_time=1, clear='no',color='b--',file='tmp',read='no', barrier_speed=50, trough_width=59, area_max=14573):
    '''
    Perform isotherm using Kibron trough with moving barrier
    The pressure is read by AD1

    '''
    area_scale = barrier_speed/60*trough_width
    directory ='/nsls2/xf12id1/data/kibron/'
    
    # if clear == 'yes':
    #     plt.close()
    #     plt.figure()
    #     plt.axis([1,2.5,-1,5])
    #     plt.xlabel('area')
    #     plt.ylabel('pressure')
    pressure=[]
    pressure2=[]
    area=[]
    run_time=[]
    time_start = time.time()
    # plt.figure()
    # plt.xlabel('Area (mm^2)')
    # plt.ylabel('Pressure (mN/m)')
    # plt.show()
    for n in range(1000):
        # print("1")
        if read != 'no':
            filename=directory+file
            g=open(filename,'r+')
            # g=open('/nsls2/xf12id1/data/kibron','r+')
            [run_time3,pressure3]=json.load(g)
            plt.figure()
            plt.plot(area_max-area_scale*run_time3,pressure3*10,color)
            # plt.xlabel('Time (s)')
            plt.xlabel('Area (mm^2)')
            plt.ylabel('Pressure (mN/m)')
            plt.show()
            break
        k=open('/nsls2/xf12id1/data/kibron/run','r+')
        stop=json.load(k)

        # print(stop)
        print('Running...')
        if stop ==0:
            # plt.plot(area,pressure,color)
            pressure_t=AD1.get()
            pressure_t2=AD2.get()
            time_t=time.time()-time_start
            area_t=area_max-area_scale*time_t
            print('Run time %.1fs: Pressure = %.2f mN/m, Pressure2 = %.2f mN/m'%(time_t,pressure_t*10, pressure_t2*10))
            pressure.append(pressure_t)
            pressure2.append(pressure_t2)
            area.append(area_t)
            run_time.append(time_t)
            time.sleep(wait_time)
            # plt.plot(time_t,pressure_t,'ob')
            # plt.show()
            # plt.plot(area,pressure,color)
            # plt.show()
            # plt.pause(0.0001)
        #    yield from bps.mov(shutter,1)
 #           yield from bp.count([pilatus100k]) # gid
        #    yield from bps.mov(shutter,0)
         #   yield from bps.sleep(wait_time)
        else:
            print('Stopped!')
            # plt.plot(area,pressure,color)
            # plt.show()
            # plt.pause(0.0001)
            plt.figure()
            # plt.plot(run_time,pressure)
            # plt.xlabel('Time (s)')
            plt.plot(area,pressure)
            plt.xlabel('Area (mm^2)')
            plt.ylabel('Pressure (mN/m)')
            plt.show()

            filename= directory+file
            f=open(filename,'w')
            json.dump([run_time, area, pressure,pressure2],f)
            break



