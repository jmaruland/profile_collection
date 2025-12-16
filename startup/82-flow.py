flow1 = EpicsSignal("XF:12ID1-ECAT:EL4104-00-AO1", name="he_flow1")
flow2 = EpicsSignal("XF:12ID1-ECAT:EL4104-00-AO2", name="he_flow2")
flow3 = EpicsSignal("XF:12ID1-ECAT:EL4104-00-AO3", name="he_flow3")
#he_pid = EpicsSignal("XF:12ID1-ES{He-Flow}PID1.FBON", name = "feed back on/off")
#oxygen_percent = EpicsSignal("XF:12ID1:O2", name = "oxygen_percent")
o2_per = EpicsSignal("XF:12ID1:O2", name = "o2_per")
he_pid = EpicsSignal("XF:12ID1-ES{He-Flow}PID1.FBON", name = "he_pid")
# he_pid_setpoint = EpicsSignal("XF:12ID1-ES{He-Flow}PID1.VAL", name = "he_pid_setpoint")

chiller = EpicsSignal("XF:12ID1-ES{Chiller}T-SP", name="chiller")



def he_on(constant_rate = 2.6):
    yield from mov(he_pid,1)
    yield from mov(flow3,5)
    yield from mov(flow2,constant_rate)

def he_off():
    yield from mov(he_pid,0)
    yield from mov(flow3,0)
    yield from mov(flow2,0)

#sets the dry helium valve opening (5 is the max)
def dry_he_on(value):
    yield from mov(flow2,value)

def dry_he_off(value):
    yield from mov(flow2,0.0)







    




def record (time,number):
    for i in range(number):
        record_file = open('/home/xf12id1/.ipython/profile_collection/startup/record','a')
        e = str(datetime.datetime.now())
        yield from bps.sleep(time)
        record_file.write(e[0:19])
        record_file.write(" {:6.3f} {:6.3f} \n".format(o2_per.get(),flow3.get()))
        print(e,o2_per.get(),flow3.get())
        record_file.close()





