from ophyd import (EpicsSignal, EpicsMotor, Device, Component as Cpt)


class XtalDflMotors(Device):
    z = Cpt(EpicsMotor, 'TblZ}Mtr')
    x = Cpt(EpicsMotor, 'TblX}Mtr')
    y = Cpt(EpicsMotor, 'TblY}Mtr')

    th = Cpt(EpicsMotor, 'Th}Mtr')
    tth = Cpt(EpicsMotor, 'Tth}Mtr')
    chi = Cpt(EpicsMotor, 'Chi}Mtr')
    phi = Cpt(EpicsMotor, 'Phi}Mtr')
    phiX = Cpt(EpicsMotor, 'PhiX}Mtr')

    h = Cpt(EpicsMotor, 'IH}Mtr')
    r = Cpt(EpicsMotor, 'IR}Mtr')    


class SmplMotors(Device):
    z = Cpt(EpicsMotor, 'TblZ}Mtr')
    x = Cpt(EpicsMotor, 'TblX}Mtr')
    y = Cpt(EpicsMotor, 'TblY}Mtr')

    th = Cpt(EpicsMotor, 'Th}Mtr')
    tth = Cpt(EpicsMotor, 'Tth}Mtr')
    chi = Cpt(EpicsMotor, 'Chi}Mtr')
    phi = Cpt(EpicsMotor, 'Phi}Mtr')
    phiX = Cpt(EpicsMotor, 'PhiX}Mtr')

    h = Cpt(EpicsMotor, 'OH}Mtr')
    r = Cpt(EpicsMotor, 'OR}Mtr')    

    
dfl = XtalDflMotors('SXF:12ID1-ES{XtalDfl-Ax:', name='dfl')
smpl = SmplMotors('SXF:12ID1-ES{Smpl-Ax:', name='smpl')
