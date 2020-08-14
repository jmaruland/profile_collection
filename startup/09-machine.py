print(f'Loading {__file__}')

from ophyd import (PVPositioner, EpicsSignal, EpicsSignalRO, EpicsMotor,
                   Device, Signal, PseudoPositioner, PseudoSingle)
from ophyd.utils.epics_pvs import set_and_wait
from ophyd.ophydobj import StatusBase, MoveStatus
from ophyd.status import DeviceStatus
from ophyd import Component as Cpt
from ophyd import Component
from scipy.interpolate import InterpolatedUnivariateSpline
from epics import (caput, caget)


class Ring(Device):
    current = EpicsSignalRO('SR:C03-BI{DCCT:1}I:Real-I', name='ring_current')
    lifetime = EpicsSignalRO('SR:OPS-BI{DCCT:1}Lifetime-I', name='ring_lifetime')
    energy = EpicsSignalRO('SR{}Energy_SRBend', name='ring_energy')
    mode = EpicsSignal('SR-OPS{}Mode-Sts', name='ring_ops', string=True)
    filltarget = EpicsSignalRO('SR-HLA{}FillPattern:DesireImA', name='ring_filltarget')

ring = Ring(name = 'ring')

#ring_ops = EpicsSignal('SR-OPS{}Mode-Sts', name='ring_ops', string=True)
mstr_shutter_enable = EpicsSignalRO('SR-EPS{PLC:1}Sts:MstrSh-Sts', name='mstr_shutter_enable')
ivu_permit = EpicsSignalRO('XF:12ID-CT{}Prmt:Remote-Sel', name='ivu_permit')
smi_shutter_enable = EpicsSignalRO('SR:C12-EPS{PLC:1}Sts:ID_BE_Enbl-Sts', name='smi_shutter_enable')



class EpicsSignalOverridePrecRO(EpicsSignalRO):
    def __init__(self, *args, precision=4, **kwargs):
        self._precision = precision
        super().__init__(*args, **kwargs)

    @property
    def precision(self):
        return self._precision


class EpicsSignalOverridePrec(EpicsSignal):
    def __init__(self, *args, precision=4, **kwargs):
        self._precision = precision
        super().__init__(*args, **kwargs)

    @property
    def precision(self):
        return self._precision


# TODO: clean up the obsolete classes after the new IVU device class
# is tested enough
class UndulatorGap(PVPositioner):
    # positioner signals
    setpoint = Cpt(EpicsSignalOverridePrec, '-Ax:Gap}-Mtr-SP')
    readback = Cpt(EpicsSignalOverridePrecRO, '-Ax:Gap}-Mtr.RBV')
    stop_signal = Cpt(EpicsSignal, '-Ax:Gap}-Mtr.STOP')
    actuate = Cpt(EpicsSignal, '-Ax:Gap}-Mtr-Go')
    actuate_value = 1
    done = Cpt(EpicsSignalRO, '-Ax:Gap}-Mtr.MOVN')
    done_value = 0

    permit = Cpt(EpicsSignalRO, 'XF:12ID-CT{}Prmt:Remote-Sel',
                 name='permit',
                 add_prefix=())

    def set(self, new_position, **kwargs):
        if np.abs(self.position - new_position) < .2:
             return DeviceStatus(self, done=True, success=True)
        return super().set(new_position, **kwargs)

    def move(self, new_position, moved_cb=None, **kwargs):
        print(np.abs(self.position - new_position),  .2, self.position, new_position)
        if np.abs(self.position - new_position) < .2:
            if moved_cb is not None:
                moved_cb(obj=self)
            return DeviceStatus(self, done=True, success=True)
        return super().move(new_position, moved_cb=moved_cb, **kwargs)

    def stop(self, *, success=False):
        if self.permit.get():
            super().stop(success=success)


class IVUBrakeCpt(Component):
    def maybe_add_prefix(self, instance, kw, suffix):
        if kw not in self.add_prefix:
            return suffix

        prefix = ''.join(instance.prefix.partition('IVU:1')[:2]) + '}'
        return prefix + suffix


class InsertionDevice(EpicsMotor):
    brake = IVUBrakeCpt(EpicsSignal,
                        write_pv='BrakesDisengaged-SP',
                        read_pv='BrakesDisengaged-Sts',
                        add_prefix=('read_pv', 'write_pv', 'suffix'))

    def move(self, *args, **kwargs):
        set_and_wait(self.brake, 1)
        return super().move(*args, **kwargs)

