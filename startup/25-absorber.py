import numpy as np

from ophyd import PseudoPositioner
from ophyd import PseudoSingle
from ophyd import EpicsMotor
import bluesky.preprocessors as bpp


class AbsShutter(PseudoPositioner):
    # angles
    pos = Cpt(PseudoSingle, "", kind="hinted")

    # input motors
    mtr = Cpt(EpicsMotor, "", doc="The absorber slider")

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        """Calculate a RealPosition from a given PseudoPosition
           based on the s_motors method

        """
        return self.RealPosition(mtr=np.ceil(pseudo_pos.pos))

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
        return self.PseudoPosition(pos=int(np.round(real_pos.mtr)))

shutter = AbsShutter('XF:12ID1-ES{Slt1-Ax:X}Mtr', name='shutter')

import functools

@functools.wraps(bps.one_nd_step)
def shutter_flash_scan(*args, **kwargs):
    def cleanup_plan():
        yield from bps.mov(shutter, 4)

    def collect_plan(*args, **kwargs):
        yield from bps.mov(shutter, 0)
        yield from bps.one_nd_step(*args, **kwargs)
    
    yield from bpp.finalize_wrapper(
        collect_plan(*args, **kwargs),
        cleanup_plan()
    )
