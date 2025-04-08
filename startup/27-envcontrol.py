print(f'Loading {__file__}')

'''modified from SMI-SWAXS'''

from ophyd import EpicsSignal, Device, Component as Cpt


class output_lakeshore(Device):

    status = Cpt(EpicsSignal, "Val:Range-Sel")
    P = Cpt(EpicsSignal, "Gain:P-SP")
    I = Cpt(EpicsSignal, "Gain:I-SP")
    D = Cpt(EpicsSignal, "Gain:I-SP")
    temp_set_point = Cpt(EpicsSignal, "T-SP")

    def turn_on(self, range):
        if range in [1, 2, 3]:
            yield from bps.mv(self.status, range)
        else:
            print('The output range need be 1, 2, or 3!')

    def turn_off(self):
        yield from bps.mv(self.status, 0)

    def set_temp(self, temp):
        yield from bps.mv(self.temp_set_point, temp)

    def set_temp_celsius(self, temp):
        yield from self.set_temp(temp+273.15)


    ramp_sp = Cpt(EpicsSignal, "Val:Ramp-SP")
    ramp_status = Cpt(EpicsSignal, "Enbl:Ramp-Sel")

    def set_ramp(self, ramp):
        yield from bps.mv(self.ramp_sp, ramp)

    def ramp_on(self):
        yield from bps.mv(self.ramp_status, 1)
    def ramp_off(self):
        yield from bps.mv(self.ramp_status, 0)


class new_LakeShore(Device):
    """
    Lakeshore is the device reading the temperature from the heating stage for SAXS and GISAXS.
    This class define the PVs to read and write to control lakeshore
    :param Device: ophyd device
    """

    input_A = Cpt(EpicsSignal, "{Env:01-Chan:A}T-I")
    input_A_celsius = Cpt(EpicsSignal, "{Env:01-Chan:A}T:C-I")

    input_B = Cpt(EpicsSignal, "{Env:01-Chan:B}T-I")
    input_C = Cpt(EpicsSignal, "{Env:01-Chan:C}T-I")
    input_D = Cpt(EpicsSignal, "{Env:01-Chan:D}T-I")

    output1 = output_lakeshore("XF:12ID1-ES{Env:01-Out:1}", name="ls_outpu1")
    output2 = output_lakeshore("XF:12ID1-ES{Env:01-Out:2}", name="ls_outpu2")
    output3 = output_lakeshore("XF:12ID1-ES{Env:01-Out:3}", name="ls_outpu3")
    output4 = output_lakeshore("XF:12ID1-ES{Env:01-Out:4}", name="ls_outpu4")
    # xrange =


ls = new_LakeShore("XF:12ID1-ES", name="ls")
ls.input_A_celsius.kind='hinted'
# ls.ch1_read.kind = 'hinted'
# # ls.ch1_sp.kind = 'hinted'
# ls.ch2_read.kind = 'hinted'
# # ls.ch2_sp.kind = 'hinted'
# ls.ch3_read.kind = 'hinted'
