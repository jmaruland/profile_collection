flow3 = EpicsSignal("XF:12ID1-ECAT:EL4104-00-AO3", name="flow3")
he_pid = EpicsSignal("XF:12ID1-ES{He-Flow}PID1.FBON", name = "feed back on/off")

def he_on():
    yield from mov(he_pid,1)
    yield from mov(flow3,2.7)

def he_off():
    yield from mov(he_pid,0)
    yield from mov(flow3,0)




