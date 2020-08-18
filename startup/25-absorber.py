import numpy as np

from ophyd import PseudoPositioner
from ophyd import PseudoSingle
from ophyd import EpicsMotor
import bluesky.preprocessors as bpp
from ophyd.pseudopos import pseudo_position_argument, real_position_argument


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

#shutter = AbsShutter('XF:12ID1-ES{Slt1-Ax:X}Mtr', name='shutter')

import functools

@functools.wraps(bps.one_nd_step)
def shutter_flash_scan(*args, **kwargs):
    def cleanup_plan():
        yield from bps.mov(shutter, 0)
        yield from bps.sleep(.2)

    def collect_plan(detectors, step, pos_cache):
        motors = step.keys()
        yield from move_per_step(step, pos_cache)
        yield from bps.mov(shutter, 1)
        yield from bps.sleep(.2)
        yield from trigger_and_read(list(detectors) + list(motors))


    yield from bpp.finalize_wrapper(
        collect_plan(*args, **kwargs),
        cleanup_plan()
    )


shutter = EpicsSignal("XF:12ID1-ECAT:EL2124-00-DO1", name="shutter")







def att_setup():
    """
    defining physical configuration of PLS attenuator system
    Only consider attenuator2 for now
    returns:[att_thickness list], [att_material list]
    """
    #att1_thi =[220, 120, 1600, 800, 400, 200, 100, 50, 25, 0]
    #att1_mat =['Mo','Mo','Mo','Mo','Mo','Mo','Mo','Mo','Mo','Mo']   

    att2_thi =[0, 25, 50, 75, 100, 125, 150, 175]
    att2_mat =['Mo','Mo','Mo','Mo','Mo','Mo','Mo','Mo']

    return att2_thi, att2_mat

def attenuation_interpolation(path, file, energy):
    """
    Interpolate the attenuation of material from 1D curve obtained from cxro files
    input: path and file to look for and the energy at which interpolate
    returns: attenuation of Mo as integer
    """

    array = np.loadtxt(os.path.join(path, file))
    energy_cxro, attenuation_cxro = array[:, 0], array[:, 1]
    att_ener = np.interp(energy, energy_cxro, attenuation_cxro)
    return att_ener


def calc_attenuation(att_mat, energy):     
    """
    Interpolate the attenuation of material from 1D curve obtained from cxro
    input: path anf file to look for and the energy at which interpolate
    returns: attenuation of Mo as integer
    """
    if energy is None:
        raise attfuncs_Exception("error: No energy is input")
    elif energy > 24000 or energy < 5000:
        raise ValueError("error: energy entered is lower than 5keV or higher than 20keV")
    else:
        print('The energy is', energy, 'eV')

    #load absorption of each material:
    for mat in list(set(att_mat)):
        if mat != 'Mo':
            raise ValueError("error: Foil material is not Mo and is not defined")
        else:
            att_ener_mo = attenuation_interpolation(path, file_absorption, energy)

    att_mat_value = [] * len(att_mat)
    for mat in att_mat:
        if mat == 'Mo':
            att_mat_value += [att_ener_mo]
        else:
            raise ValueError("error: No other material than Mo aare defined so far")

    return att_mat_value


def calculate_att_comb(att2_thi, att2_mat, energy):
    """
    Calculate all the combination of attenuation 
    input: thickness and material of each attenuator and energy
    returns: all the combination of attenuation as an array
    """
    # att1_mat_value = calc_attenuation(att_mat1, energy)
    att2_mat_value = calc_attenuation(att2_mat, energy)
   
    # define all the combination of foils
    T_tot = np.zeros(np.shape(att2_thi))

    for i, (att2_mat_value, att2_thi) in enumerate(zip(att2_mat_value, att2_thi)):
        T_tot[i] = np.exp(-1*att2_thi/att2_mat_value )
    return T_tot


def best_att(T_target, energy):
    """
    Find the closest attenuation combination from a taget one but higher
    input: target attenuation, attenuator thickness and material
    returns: all the combination of attenuation as an array
    """
    att2_thi, att2_mat = att_setup()
    T = calculate_att_comb(att2_thi, att2_mat, energy)
    
    if T_target <= 0.99:
        valid_att = np.where(T >= T_target)[0]
    else:
        valid_att = np.where(T)

    best = np.argmin(abs(T[valid_att]-T_target))
    print('The required attenuation is %s the best match is %s'%(T_target, T[best]))

    return best, T[best]


def convert_best_att_to_pos(att_position, best_att_index):
    return att_position[best_att_index]


path = '/home/xf12id1/Downloads/' 
file_absorption = 'Mo_absorption.txt'
att_position = [0, 10, 20, 30]
