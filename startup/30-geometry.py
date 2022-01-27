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


class UserError(Exception):
    ...


class EpicsMotorWithLimits(EpicsMotor):
    low_limit = Cpt(EpicsSignal, ".LLM")
    high_limit = Cpt(EpicsSignal, ".HLM")


too_small = 1.0e-10


class DetectorOffsets(Device):
    det_mode= Cpt(
        EpicsSignal,
        "XF:12ID1:DetMode",
        add_prefix=(),
        kind="config",
        )
    det_1= Cpt(
        EpicsSignal,
        "XF:12ID1:L_11",
        add_prefix=(),
        kind="config"
        )
    det_2= Cpt(
        EpicsSignal,
        "XF:12ID1:L_12",
        add_prefix=(),
        kind="config"
        )
    det_3= Cpt(
        EpicsSignal,
        "XF:12ID1:L_13",
        add_prefix=(),
        kind="config"
        )
    det_4= Cpt(
        EpicsSignal,
        "XF:12ID1:L_14",
        add_prefix=(),
        kind="config"
        )



    #mode = Cpt(EpicsSignal, "L_14", kind="config")
    #det1 = Cpt(EpicsSignal, "L_11", kind="config")
    #det2 = Cpt(EpicsSignal, "L_12", kind="config")
    #det3 = Cpt(EpicsSignal, "L_13", kind="config")
from ophyd.sim import SynAxis as _SynAxis



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
    stblx2 = Cpt(EpicsMotor, "{Smpl-Ax:X}Mtr", doc="Sample Table X2")
  #  chi2 = Cpt(EpicsMotor, "{Smpl-Ax:Chi}Mtr", doc="Sample chi")


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

    Energy = Cpt(
        EpicsSignal, "XF:12ID1:L_07", add_prefix=(), kind="config", doc="energy (kev)",
    )

    track_mode = Cpt(
        EpicsSignal,
        "XF:12ID1:TrackMode",
        add_prefix=(),
        kind="config",
        doc="track mode, mm",
    )

    L11 = Cpt(
        EpicsSignal,
        "XF:12ID1:L_11",
        add_prefix=(),
        kind="config",
        doc="L11 tth offset",
    )


    det_mode = Cpt(
        EpicsSignal,
        "XF:12ID1:DetMode",
        add_prefix=(),
        kind="config",
        doc="detector mode,",
    )


    detector_offsets = Cpt(
        DetectorOffsets,
        "XF:12ID1:",
        add_prefix=(),
        kind="config",
        doc="offsets from tth of each detector center",
    )

    def __init__(self, prefix, **kwargs):
        # self.wlength = 0.77086  # x-ray wavelength, A
        # self.wlength = 0.770088  # x-ray wavelength, A
        # self.wlength = 1.2834  # x-ray wavelength, A
        # WHY DOES THE FOLLOWING NOT WORK
        # print(self.Energy)
        # self.wlength = 12.39842/self.Energy
        self.s_qtau = 1.9236  # Ge 111 reciprocal lattice vector, 1/A
        #  self.s_Eta = 0.000  # inc beam upward tilt from mirror (rad)
        self.s_trck = 0  # whether to track sample tabletime
        super().__init__(prefix, **kwargs)
        # self.phi.settle_time = 0.5
        # self.ih.settle_time = 0.5

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
        _stblx2 = self.stblx2.position

        # bragg is sin(theta_bragg)
        # self.wlength = 12.39842 / self.Energy.get()
        self.wlength = 12.39842 / (0.001 * energy.energy.position)  #in A
        _lambda = self.wlength

        # COMMENT,  THIS MIGHT NOT UPDATE IN TIME
        # _lambda = 12.39842 / self.wlength.get()

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


        #SH_OFFSET IS TURNED OFF FOR NOW SINCE IT IS MULTIUPLIED BY ZERO.
        sh = (
            -(self.L2.get() + self.L4.get()) * np.tan(_alpha) / np.cos(_tth)
        ) + 0*self.SH_OFF.get()
        # + correction

        stblx = self.L2.get() * np.tan(_tth)
        # todo check degree vs radian
        oh = sh + (self.L3.get() - self.L4.get()) * np.tan(_beta)

        # actually output theta
        det_mode = int(self.detector_offsets.det_mode.get())

        det_dict = {
            1: 'det_1',
            2: 'det_2',
            3: 'det_3',
            4: 'det_4',
        }

        if det_mode not in det_dict:
            raise UserError(f'The "det_mode={det_mode}" you are trying to use '
                            f'is not supported. Use one of {list(det_dict.keys())} '
                            f'for the det_mode.')

        _tth_offset = np.deg2rad(getattr(self.detector_offsets, det_dict[det_mode]).get())

        _astth = _tth + _stth + _tth_offset

        #print("calcualted _astth=",np.rad2deg(_astth))
        #print("_tth=",np.rad2deg(_tth), "   _stth=",np.rad2deg(_stth), "tth_offset=",np.rad2deg(_tth_offset))
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
            stblx2=_stblx2,
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

        # self.wlength = 12.39842 / self.Energy.get()
        self.wlength = 12.39842 / (0.001 * energy.energy.position)

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
        # actually output theta
        det_mode = int(self.detector_offsets.det_mode.get())

        det_dict = {
            1: 'det_1',
            2: 'det_2',
            3: 'det_3',
            4: 'det_4',
        }

        if det_mode not in det_dict:
            raise UserError(f'The "det_mode={det_mode}" you are trying to use '
                            f'is not supported. Use one of {list(det_dict.keys())} '
                            f'for the det_mode.')

        _tth_offset = getattr(self.detector_offsets, det_dict[det_mode]).get()
        #print(f'{_tth_offset}')
        stth = real_pos.astth - real_pos.tth - _tth_offset


        # TODO compute beta from the other motors

        return self.PseudoPosition(alpha=_alpha, beta=real_pos.oa, stth=stth)

    def move_ab(self, val):
        warnings.warn("use `yield from bps.mv(goe, val)` instead")
        return (yield from bps.mv(self.alpha, val))

    def save_geo(self, L1):
        return (yield from bps.mv(self.L1, L1))

class SynAxis(_SynAxis):
    def move(self, *args, wait=None, moved_cb=None, timeout=None, **kwargs):

        st = self.set(*args, **kwargs)
        import functools
        from ophyd.status import wait as status_wait
        if moved_cb is not None:
            st.add_callback(functools.partial(moved_cb, obj=self))
        if wait:
            status_wait(st)
        return st

class SynGeometry(Geometry):
    _real = ['th', 'phi', 'chi', 'tth', 'ih', 'ia', 'phix', 'sh', 'astth', 'stblx', 'stblx2', 'oa', 'oh']
    # input motors
    th = Cpt(SynAxis, doc="Θ 3-circle theta for mono", value=0.0)
    #
    phi = Cpt(SynAxis, doc="Φ-stage sets bragg angle", value=10.0)
    #    phi = Cpt(EpicsMotor, '{XtalDfl-Ax:M7}Mtr', labels=['geo'])
    chi = Cpt(SynAxis, doc="Χ, beam steering", value=0.0)
    tth = Cpt(SynAxis, doc="2Θ, spectrometer rotation", value=0.0)
    ih = Cpt(SynAxis, doc="input height", value=0.0)
    ia = Cpt(SynAxis, doc="input rotation", value=0.0)
    phix = Cpt(SynAxis, value=0.0)
    # Sample-detector motors
    sh = Cpt(SynAxis, doc="Sample vertical translation", value=0.0)
    astth = Cpt(SynAxis, doc="Sample-detector rotation", value=0.0)
    # asth = Cpt(EpicsMotor, "{Smpl-Ax:Th}Mtr", doc="Sample rotation")
    stblx = Cpt(SynAxis, doc="Sample Table X", value=200.0)
    stblx2 = Cpt(SynAxis, doc="Sample Table X2", value=0.0)
    #  chi2 = Cpt(EpicsMotor, "{Smpl-Ax:Chi}Mtr", doc="Sample chi")
    oa = Cpt(SynAxis, doc="β, output arm rotation", value=0.0)
    oh = Cpt(SynAxis, doc="output arm vertical rotation", value=0.0)

IN_SIM_MODE = True # bool(sim_flag.get() > 0)

if IN_SIM_MODE:
    geo = SynGeometry("XF:12ID1-ES", name="geo")
    for atr in SynGeometry._real:
        mtr = getattr(geo, atr)
        mtr.set(mtr.get().readback)
        mtr.readback.kind = 'normal'
else:
    geo = Geometry("XF:12ID1-ES", name="geo")

    [   
        setattr(getattr(geo, k).user_readback, "kind", "hinted")
        for k in geo.real_position._fields
    ]


#geo = Geometry("XF:12ID1-ES", name="geo")
# Prefix the PV with "S" for simulations

# this is how to add additional aliases
# ih = geo.ih


def cabt(*args, **kwargs):
    ret = geo.forward(*args, **kwargs)
    print("wavelength", geo.wlength)
    print(
        "footprint(mm)=",
        S2.vg.user_readback.get() / ((args[0] + 0.001) * 3.14159 / 180),
    )
    print("fqz=", (4 * np.pi / geo.wlength.real) * np.sin(args[0] * 3.14159 / 180))

    cur = geo.real_position
    print("| {:<6s} |{:>9s} |{:>9s} |".format("MOTOR", "TARGET", "CURRENT"))
    print("|" + "-" * 30 + "|")
    for k in ret._fields:
        print(f"| {k:<6s} |{getattr(ret, k):>9.03f} |{getattr(cur, k):>9.03f} |")
    print("|" + "-" * 30 + "|")

def mabt(*args, **kwargs):
    # print(geo)
    yield from bps.abs_set(geo, args, **kwargs, wait=True)

def nabt(alpha_0,beta_0,stth_0):
    # print(geo)
    yield from bps.mv(geo.alpha, 0)
    yield from bps.mv(geo.beta,2*beta_0)
    yield from bps.mv(tilt.y,alpha_0)
    yield from bps.mv(geo.stth,stth_0)

def nab(alpha_0,beta_0):
    stth_corr = 0.003*pow(2*np.abs(alpha_0),1.72)
    print(stth_corr)
    if alpha_0 > 0:
        yield from nabt(alpha_0,beta_0,stth_corr)
    else:
        yield from nabt(alpha_0,beta_0,-1*stth_corr)




def my_over_night():
    for a in np.linspace(0, 5, 1000):
        yield from mabt(alpha=a)
        yield from bp.count(...)


# The PVs are: XF:12ID1:L_01  to XF:12ID1:L_20
# e.g., you can

# BEN , change to read from EPIcs like we did earlier.


def param():
    # print("En  :", 12.39842 / geo.wlength, "keV")
    print("L1  :", geo.L1.get(), "crystal to input arm elevator")
    print("L2  :", geo.L2.get(), "crystal to sample table")
    print("L3  :", geo.L3.get(), "sample to output arm elevator")
    print("L4  :", geo.L4.get(), "table x offset")
    print("SH_OFF :", geo.SH_OFF.get(), "sh offset")
    print("abs1:", int(S1.absorber1.user_readback.get() + 0.1))
    print("abs2:", int(S3.absorber1.user_readback.get() + 0.1))
    print("Eta :", geo.Eta.get(), "Upward angle of beam on chi circle")
    print("track_mode:", geo.track_mode.get(), ":geo.track_mode.get() = 0/1")
    print("detector_mode:", geo.detector_offsets.det_mode.get(), "detector_mode(1,2,3)")
    print("shutter:", shutter.get(), ":%mov shutter 0/1")
    # print("En  :", geo.Energy.get(), "keV")
    # print(" wavelength: ", 12.39842 / geo.Energy.get(), "Angstroms")

    print("En  :", 0.001 * energy.energy.position, "keV")
    print(" wavelength: ", 12.39842 / energy.energy.position, "Angstroms")

