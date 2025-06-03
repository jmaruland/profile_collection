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
    absorber1 = Cpt(EpicsMotor, "X}Mtr")

class Smaract1(Device):
   absorber1 = Cpt(EpicsMotor, "X}Mtr")

class Smaract2(Device):
   position1 = Cpt(EpicsMotor, "Y}Mtr")

class Smaract3(Device):
    y = Cpt(EpicsMotor, "BS}Mtr")

class BSTOP(Device):
    x = Cpt(EpicsMotor, "X}Mtr")
    y = Cpt(EpicsMotor, "Y}Mtr")

bstop =BSTOP("XF:12ID1-ES{BS-Ax:", name="Pilatus300 Beam Stop")
block = Smaract3("XF:12ID1-ES{Smpl-Ax:", name="Beam Stop")



S1 = SlitsWithTopBottomInbOutb("XF:12ID1-ES{Slt1-Ax:", name="S1")
S2 = SlitsWithGapAndCenter("XF:12ID1-ES{Slt2-Ax:", name="S2")
#S3 = Smaract1("XF:12ID1-ES{SM:1-Ax:", name="S3")
S3 = Smaract1("XF:12ID1-ES{Fltr:1-Ax:", name="S3")
S4 = Smaract1("XF:12ID1-ES{BPM:1-Ax:", name="S4")
S5 = Smaract2("XF:12ID1-ES{BPM:1-Ax:", name="S5")

S2.vg.user_readback.kind="normal"
S2.vc.user_readback.kind="normal"
S2.hg.user_readback.kind="normal"
S2.hc.user_readback.kind="normal"


class SLTH(Device):
    h = Cpt(EpicsMotor, 'Hpos}Mtr')
    hg = Cpt(EpicsMotor, 'Hgap}Mtr')

class SLTV(Device):
    v = Cpt(EpicsMotor, 'Vpos}Mtr')
    vg = Cpt(EpicsMotor, 'Vgap}Mtr')

# FOE mono beam slits
hfmslit = SLTH('XF:12IDA-OP:2{Slt:H-Ax:', name='hfmslit')
vfmslit = SLTV('XF:12IDA-OP:2{Slt:V-Ax:', name='vfmslit')

#SOLLER SLITS
class SOLLER(Device):
    tran = Cpt(EpicsMotor, 'lex16}Mtr')
    rot = Cpt(EpicsMotor, 'lex17}Mtr')

soller =  SOLLER('XF:12ID1-ES{Mdrive-Ax:', name='soller')



class SampleSlit(Device):
    x2 = Cpt(EpicsMotor, 'X2}Mtr')

sample_slit = SampleSlit("XF:12ID1-ES{Smpl-Slit:", name='sampl_slit')

slit_x2 = sample_slit.x2

# 2025-06-02, edge slit_x2 = 53.2




