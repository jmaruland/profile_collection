from ophyd import EpicsSignal, EpicsMotor, Device, Component as Cpt


class XtalDflMotors(Device):
    z = Cpt(EpicsMotor, "TblZ}Mtr")
    x = Cpt(EpicsMotor, "TblX}Mtr")
    y = Cpt(EpicsMotor, "TblY}Mtr")

    th = Cpt(EpicsMotor, "Th}Mtr")
    tth = Cpt(EpicsMotor, "Tth}Mtr")
    chi = Cpt(EpicsMotor, "Chi}Mtr")
    #   phi = Cpt(EpicsMotor, 'Phi}Mtr')
    phi = Cpt(EpicsMotor, "M7}Mtr")
    phiX = Cpt(EpicsMotor, "PhiX}Mtr")

    h = Cpt(EpicsMotor, "IH}Mtr")
    r = Cpt(EpicsMotor, "IR}Mtr")


class SmplMotors(Device):
    z = Cpt(EpicsMotor, "TblZ}Mtr")
    x = Cpt(EpicsMotor, "TblX}Mtr")
    y = Cpt(EpicsMotor, "TblY}Mtr")

    th = Cpt(EpicsMotor, "Th}Mtr")
    tth = Cpt(EpicsMotor, "Tth}Mtr")
    chi = Cpt(EpicsMotor, "Chi}Mtr")
    phi = Cpt(EpicsMotor, "Phi}Mtr")
    phiX = Cpt(EpicsMotor, "PhiX}Mtr")

    h = Cpt(EpicsMotor, "OH}Mtr")
    r = Cpt(EpicsMotor, "OR}Mtr")


# what is the p for in ip??
ip = XtalDflMotors("XF:12ID1-ES{XtalDfl-Ax:", name="ip")
op = SmplMotors("XF:12ID1-ES{Smpl-Ax:", name="op")
