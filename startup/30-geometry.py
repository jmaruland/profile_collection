import numpy as np

from ophyd import PseudoPositioner
from ophyd import PseudoSingle
from ophyd import EpicsSignal
from ophyd import Signal

import warnings

# from ophyd import EpicsMotor
from ophyd.pseudopos import pseudo_position_argument, real_position_argument
from ophyd import Component as Cpt
import bluesky.plans as bp
import bluesky.plan_stubs as bps

from ophyd.positioner import SoftPositioner


class EpicsMotorWithLimits(EpicsMotor):
    low_limit = Cpt(EpicsSignal, ".LLM")
    high_limit = Cpt(EpicsSignal, ".HLM")


too_small = 1.0e-10


class Geometry(PseudoPositioner):
    # angles
    alpha = Cpt(PseudoSingle, "", kind="hinted")
    beta = Cpt(PseudoSingle, "", kind="hinted")
    stth = Cpt(PseudoSingle, "", kind="hinted")
    # sth = Cpt(PseudoSingle, "", kind='hinted')

    # input motors
    th = Cpt(EpicsMotor, "{XtalDfl-Ax:Th}Mtr", doc="Θ 3-circle theta for mono")
    #
    phi = Cpt(EpicsMotor, "{XtalDfl-Ax:Phi}Mtr", doc="Φ-stage sets bragg angle")
    #    phi = Cpt(EpicsMotor, '{XtalDfl-Ax:M7}Mtr', labels=['geo'])
    chi = Cpt(EpicsMotor, "{XtalDfl-Ax:Chi}Mtr", doc="Χ, beam steering")
    tth = Cpt(EpicsMotor, "{XtalDfl-Ax:Tth}Mtr", doc="2Θ, spectrometer rotation")
    ih = Cpt(EpicsMotor, "{XtalDfl-Ax:IH}Mtr", doc="input height")
    ia = Cpt(EpicsMotorWithLimits, "{XtalDfl-Ax:IR}Mtr", doc="input rotation")
    phix = Cpt(EpicsMotor, "{XtalDfl-Ax:PhiX}Mtr")

    # Sample-detector motors
    sh = Cpt(EpicsMotor, "{Smpl-Ax:TblY}Mtr", doc="Sample vertical translation")
    astth = Cpt(EpicsMotor, "{Smpl-Ax:Tth}Mtr", doc="Sample-detector rotation")
    # asth = Cpt(EpicsMotor, "{Smpl-Ax:Th}Mtr", doc="Sample rotation")
    stblx = Cpt(EpicsMotor, "{Smpl-Ax:TblX}Mtr", doc="Sample Table X")

    oa = Cpt(EpicsMotor, "{Smpl-Ax:OR}Mtr", doc="β, output arm rotation")
    oh = Cpt(EpicsMotor, "{Smpl-Ax:OH}Mtr", doc="output arm vertical rotation")
    # gep,etru cps
    L1 = Cpt(
        EpicsSignal,
        "XF:12ID1:L_01",
        add_prefix=(),
        kind="config",
        doc="distance crystal to input arm elevator, mm",
    )
    
    L2 = Cpt(
        EpicsSignal,
        "XF:12ID1:L_02",
        add_prefix=(),
        kind="config",
        doc="distance crystal to sample center, mm",
    )

    L3 = Cpt(
        EpicsSignal,
        "XF:12ID1:L_03",
        add_prefix=(),
        kind="config",
        doc="distance sample to output elevator, mm",
    )

    L4 = Cpt(
        EpicsSignal,
        "XF:12ID1:L_04",
        add_prefix=(),
        kind="config",
        doc="table x offset, mm",
    )



    Eta = Cpt(
        EpicsSignal,
        "XF:12ID1:L_05",
        add_prefix=(),
        kind="config",
        doc="inc beam upward tilt from mirror (rad)",
    )


    SH_OFF = Cpt(
        EpicsSignal,
        "XF:12ID1:L_06",
        add_prefix=(),
        kind="config",
        doc="sample height offset, mm",
    )

    track_mode = Cpt(
        Signal, kind="config", doc="If the all the motors should track", value=1
    )

    def __init__(self, prefix, **kwargs):
        self.wlength = 0.77086  # x-ray wavelength, A
        self.s_qtau = 1.9236  # Ge 111 reciprocal lattice vector, 1/A
        #  self.s_Eta = 0.000  # inc beam upward tilt from mirror (rad)
        self.s_trck = 0  # whether to track sample tabletime
        super().__init__(prefix, **kwargs)
        self.phi.settle_time = 0.5
        self.ih.settle_time = 0.5

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        """Calculate a RealPosition from a given PseudoPosition
           based on the s_motors method

        Parameters
        ----------
        pseudo_pos : PseudoPosition
            The pseudo position input

        Returns
        -------
        real_position : RealPosition
            The real position output
        """
        # by convention in this function:
        #  - angles in degrees are not prefixed by underscores
        #  - angles in radians are prefixed by underscores
        track_mode = bool(self.track_mode.get())

        if pseudo_pos.alpha > 90:
            msg = f"Unobtainable position: alpha({a}) is greater than 90 degrees"
            raise ValueError(msg)

        # get pseudo positions in radians
        _alpha = np.deg2rad(pseudo_pos.alpha)
        _beta = np.deg2rad(pseudo_pos.beta)
        _stth = np.deg2rad(pseudo_pos.stth)

        cE = np.cos(self.Eta.get())
        sE = np.sin(self.Eta.get())
        _phix = self.phix.position

        # bragg is sin(theta_bragg)
        _lambda = self.wlength
        bragg = self.s_qtau * _lambda * 1.0 / (4.0 * np.pi)
        if np.fabs(bragg) > 1:
            msg = f"Unobtainable position: cannot find bragg angle, lambda ({_lambda}) too big"
            raise ValueError(msg)

        # calculate sin(phi)
        tmp = 2 * cE * bragg
        if np.fabs(tmp) < too_small:
            msg = (
                f"Unobtainable position: cannot find phi, denominator({tmp}) too small"
            )
            raise ValueError(msg)

        aphi = (2 * bragg * bragg - np.sin(_alpha) * sE - sE * sE) / tmp
        if np.fabs(aphi) > 1:
            msg = f"Unobtainable position: cannot find phi, lambda ({_lambda}) too big"
            raise ValueError(msg)

        _phi = np.arcsin(aphi)  # radians

        # calculate chi
        tmp = 2 * bragg * np.cos(_phi)
        if np.fabs(tmp) < too_small:
            msg = (
                f"Unobtainable position: cannot find chi, denominator({tmp}) too small"
            )
            raise ValueError(msg)

        # not an angle
        achi = (np.sin(_alpha) + sE) / tmp
        if np.fabs(achi) > 1:
            msg = f"Unobtainable position: cannot find chi, alpha({_alpha}) too big or phi({phi}) too small"
            raise ValueError(msg)

        _chi = np.arcsin(achi)  # as radians

        _th = 0

        tmp = cE - 2 * bragg * np.sin(_phi)
        if np.fabs(tmp) < too_small:
            msg = f"Unobtainable position: cannot find tth"
            raise ValueError(msg)

        # maybe use atan2(y, x), instead of atan(y/x) ?
        _tth = np.arctan(2 * bragg * np.cos(_phi) * np.cos(_chi) / tmp)
        # change this line (BEN)
        ih = -self.L1.get() * np.tan(_alpha)

        # 'th', 'phi', 'chi', 'tth', 'ih', and 'ir'

        sh = (
            -(self.L2.get() + self.L4.get()) * np.tan(_alpha) / np.cos(_tth)) + self.SH_OFF.get()
          # + correction

        stblx = self.L2.get() * np.tan(_tth)
        # todo check degree vs radian
        oh = sh + (self.L3.get() - self.L4.get()) * np.tan(_beta)

        # actually output theta
        _astth = _tth + _stth
        real_pos = self.real_position
        return self.RealPosition(
            th=np.rad2deg(_th),
            phi=np.rad2deg(_phi),
            chi=np.rad2deg(_chi),
            tth=np.rad2deg(_tth),
            ih=ih,
            ia=np.rad2deg(_alpha),
            oa=pseudo_pos.beta if track_mode else real_pos.oa,
            sh=sh if track_mode else real_pos.sh,
            stblx=stblx if track_mode else real_pos.stblx,
            astth=np.rad2deg(_astth) if track_mode else real_pos.astth,
            oh=oh if track_mode else real_pos.oh,
            phix=_phix,
        )

    @real_position_argument
    def inverse(self, real_pos):
        """Calculate a PseudoPosition from a given RealPosition

        Parameters
        ----------
        real_position : RealPosition
            The real position input

        Returns
        -------
        pseudo_pos : PseudoPosition
            The pseudo position output
        """

        bragg = self.s_qtau * self.wlength * 1.0 / (4.0 * np.pi)
        if np.fabs(bragg) > 1:
            msg = f"Unobtainable position: cannot find bragg angle, lambda ({_lambda}) too big"
            raise ValueError(msg)

        phi = real_pos.phi * (np.pi / 180.0)
        chi = real_pos.chi * (np.pi / 180.0)

        tmp = 2 * bragg * np.cos(phi) * np.sin(chi) - np.sin(self.Eta.get())
        if np.fabs(tmp) > 1:
            msg = f"Unobtainable position: cannot find alpha"
            raise ValueError(msg)

        _alpha = np.arcsin(tmp) * (180.0 / np.pi)

        stth = real_pos.astth - real_pos.tth

        # TODO compute beta from the other motors

        return self.PseudoPosition(alpha=_alpha, beta=real_pos.oa, stth=stth)

    def move_ab(self, val):
        warnings.warn("use `yield from bps.mv(goe, val)` instead")
        return (yield from bps.mv(self.alpha, val))

    def save_geo(self, L1):
        return (yield from bps.mv(self.L1, L1))


geo = Geometry("XF:12ID1-ES", name="geo")
[
    setattr(getattr(geo, k).user_readback, "kind", "hinted")
    for k in geo.real_position._fields
]

# this is how to add additional aliases
# ih = geo.ih


def cabt(*args, **kwargs):
    ret = geo.forward(*args, **kwargs)

    print(
        "footprint(mm)=",
        S2.vg.user_readback.value / ((args[0] + 0.001) * 3.14159 / 180),
    )
    print("qz=", (4 * np.pi / 0.77) * np.sin(args[0] * 3.14159 / 180))
    cur = geo.real_position
    print("| {:<6s} |{:>9s} |{:>9s} |".format("MOTOR", "TARGET", "CURRENT"))
    print("|" + "-" * 30 + "|")
    for k in ret._fields:
        print(f"| {k:<6s} |{getattr(ret, k):>9.03f} |{getattr(cur, k):>9.03f} |")
    print("|" + "-" * 30 + "|")


def mabt(*args, **kwargs):
    yield from bps.abs_set(geo, args, **kwargs, wait=True)


def my_over_night():
    for a in np.linspace(0, 5, 1000):
        yield from mabt(alpha=a)
        yield from bp.count(...)


# The PVs are: XF:12ID1:L_01  to XF:12ID1:L_20
# e.g., you can
# caget XF:12ID1:L_01 and caput XF:12ID1:L_01

# from epics import caput,caget
# caput(XF:12ID1:L_01,17)
# caget(XF:12ID1:L_01)

# BEN , change to read from EPIcs like we did earlier.
def param():
    print("En  :", 12.39847 / geo.wlength, "keV")
    print("L1  :", geo.L1.get(), "crystal to input arm elevator")
    print("L2  :", geo.L2.get(), "crystal to sample table")
    print("L3  :", geo.L3.get(), "sample to output arm elevator")
    print("L4  :", geo.L4.get(), "table x offset")
    print("SH_OFF :", geo.SH_OFF.get(), "sh offset")
    print("abs1:", int(S1.absorber1.user_readback.value+0.1))
    print("abs2:", int(S3.absorber1.user_readback.value+0.1))
    print("Eta :", geo.Eta.get(), "Upward angle of beam on chi circle")
    print("track:", geo.track_mode.value,":geo.track_mode.value = 0/1")
    print("shutter:", shutter.value,":%mov shutter 0/1")
 

def park():
    # this group will move simultanouslt
    yield from bps.mov(mtr1, 0, mtr2, 1, ...)
    # this group will move simultanouslt
    yield from bps.mov(mtr1, 0, mtr2, 1, ...)
    ...