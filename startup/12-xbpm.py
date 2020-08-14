from ophyd import EpicsSignal, Device
from ophyd import Component as Cpt


class XBPM(Device):
    ch1 = Cpt(EpicsSignal, 'Current1:MeanValue_RBV')
    ch2 = Cpt(EpicsSignal, 'Current2:MeanValue_RBV')
    ch3 = Cpt(EpicsSignal, 'Current3:MeanValue_RBV')
    ch4 = Cpt(EpicsSignal, 'Current4:MeanValue_RBV')
    sumX = Cpt(EpicsSignal, 'SumX:MeanValue_RBV')
    sumY = Cpt(EpicsSignal, 'SumY:MeanValue_RBV')
    posX = Cpt(EpicsSignal, 'PosX:MeanValue_RBV')
    posY = Cpt(EpicsSignal, 'PosY:MeanValue_RBV')


xbpm1 = XBPM('XF:12IDA-BI:2{EM:BPM1}', name='xbpm1')
xbpm2 = XBPM('XF:12IDA-BI:2{EM:BPM2}', name='xbpm2')
xbpm3 = XBPM('XF:12IDB-BI:2{EM:BPM3}', name='xbpm3')
xbpm3.sumY.kind = 'hinted'
xbpm3.sumX.kind = 'hinted'
xbpm2.sumY.kind = 'hinted'
xbpm2.sumX.kind = 'hinted'

