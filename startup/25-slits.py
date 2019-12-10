from ophyd import Device, Component as Cpt


class SlitsWithGapAndCenter(Device):
    vg = Cpt(EpicsMotor, "Vg}Mtr")
    vc = Cpt(EpicsMotor, "Vc}Mtr")
    hg = Cpt(EpicsMotor, "Hg}Mtr")
    hc = Cpt(EpicsMotor, "Hc}Mtr")


class SlitsWithTopBottomInbOutb(Device):
    top = Cpt(EpicsMotor, "T}Mtr")
    bottom = Cpt(EpicsMotor, "B}Mtr")
    inb = Cpt(EpicsMotor, "I}Mtr")
    outb = Cpt(EpicsMotor, "O}Mtr")
    absorber1 = Cpt(EpicsMotor, "Absorber1}Mtr")


S1 = SlitsWithTopBottomInbOutb("XF:12ID1-ES{Slt1-Ax:", name="S1")
S2 = SlitsWithGapAndCenter("XF:12ID1-ES{Slt2-Ax:", name="S2")
