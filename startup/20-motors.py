from ophyd import EpicsSignal, EpicsMotor, Device, Component as Cpt


class Table1(Device):
    z = Cpt(EpicsMotor, "TblZ}Mtr")
    x = Cpt(EpicsMotor, "TblX}Mtr")
    y = Cpt(EpicsMotor, "TblY}Mtr")
    


tab1 = Table1("XF:12ID1-ES{XtalDfl-Ax:", name="tab1")


class Tilt(Device):
    x = Cpt(EpicsMotor, "X}Mtr")
    y = Cpt(EpicsMotor, "Y}Mtr")

    
tilt = Tilt("XF:12ID1-ES{Smpl-Ax:Tilt", name="tilt")
#Name:        XF:12ID1-ES{Smpl-Ax:TiltY}Mtr.DESC

class DET_SAXS(Device):
    x = Cpt(EpicsMotor, "X}Mtr")
    y = Cpt(EpicsMotor, "Y}Mtr")
    
detsaxs = DET_SAXS("XF:12ID1-ES{DetSAXS-Ax:", name="det_saxs")

class FLIGHT_PATH_SAXS(Device):
    y1 = Cpt(EpicsMotor, "Y1}Mtr")
    y2 = Cpt(EpicsMotor, "Y2}Mtr")

fp_saxs =  FLIGHT_PATH_SAXS("XF:12ID1-ES{SAXS-Ax:", name ="flight_path_saxs")

