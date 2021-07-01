import numpy as np
import pandas as pds
import os
import time

from ophyd import PseudoPositioner, PseudoSingle, EpicsMotor, EpicsSignal
import bluesky.preprocessors as bpp
from ophyd.pseudopos import pseudo_position_argument, real_position_argument

print(f'Loading {__file__}')
path = '/home/xf12id1/.ipython/profile_collection/startup/'
file_absorption = 'Mo_absorption.txt'

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

def attenuation_interpolation(path, filename, energy):
    """
    Interpolate the attenuation of a material at a given energy from the 1D curve obtained from CXRO files

    Parameters:
    -----------
    :param path: A string liking the path towards the saved txt data containing CXRO files
    :type path: string
    :param filename: A string with the filename under which the CXRO data is saved
    :type filename: string
    :param energy: the energy at which the absorption needs to be interpolated
    :type energy: float

    Returns
    -------
    att_ener: A float with the corresponding attenuation at a specific energy
    """

    array = np.loadtxt(os.path.join(path, filename))
    energy_cxro, attenuation_cxro = array[:, 0], array[:, 1]
    att_ener = np.interp(energy, energy_cxro, attenuation_cxro)
    return att_ener


def calc_attenuation(att_bar1, energy):
    """
    Calculate the attenuation value of all PPLS absorbers given it material and energy. This part mainly check if the
    absorbers materials is defined and the data available, and if the picked energy is suitable for the beamline

    Parameters:
    -----------
    :param material: A list containing all the attenuator materials
    :type att_mat: List of string
    :param energy: the energy at which the absorption needs to be interpolated
    :type energy: float

    Returns
    -------
    att_mat_value: A list of float which are the attenuation coefficient of each attenuators
    """
    if energy is None:
        raise attfuncs_Exception("error: No energy is input")
    elif energy > 24000 or energy < 5000:
        raise ValueError("error: energy entered is lower than 5keV or higher than 20keV")

    #load absorption of each material:
    for i, mat in enumerate(att_bar1['material']):
        if mat != 'Mo':
            raise ValueError("error: Foil material is not Mo and is not defined")
        else:
            att_ener_mo = attenuation_interpolation(path, file_absorption, energy)
            att_bar1['material_att_coef'][i] = att_ener_mo
            att_bar1['energy'][i] = energy

    return att_bar1


def calculate_att_comb(att_bar1, energy):
    """
    Calculate all the combination of attenuation at PPLS beamline

    Parameters:
    -----------
    :param att_thi: A list containing all the attenuator thicknesses
    :type att_thi: List of string
    :param att_mat: A list containing all the attenuator materials
    :type att_mat: List of string
    :param energy: the energy at which the absorption needs to be interpolated
    :type energy: float

    Returns
    -------
    T_coefs: A list of float which contains all the transmission coefficient of all the foils at a given energy
    """
    # Calculate the absorption coefficient of every foils
    att_bar1 = calc_attenuation(att_bar1, energy)
   
    # Define all the combination of foils
    t_coefs = np.zeros(np.shape(att_bar1['thickness']))

    # Calculate the absorption of every attenuators for a given energy and store them as a list
    for i, (att_mat_value, att_thi) in enumerate(zip(att_bar1['material_att_coef'], att_bar1['thickness'])):
        att_bar1['attenuator_aborp'][i] = np.exp(-1 * att_thi / att_mat_value)
    return att_bar1

def att_setup():
    """
    Defining the PLS attenuator system. Each attenuators is defined by a thickness, a material and a name

    Returns
    -------
    att_thi: A list containing all the attenuator thicknesses
    att_mat: A list containing all the attenuator materials
    att_name: A list containing all the attenuator names
    att_name: A list of float containing the position of the attenuator motor at the beamline
    """

    # att_thi = [0, 24.28, 49.89, 74.97, 100.4, 126.11, 151.61, 177.62]
    #att_thi = [0, 25.0, 50.72, 76.24, 100.76, 126.41, 152.45, 177.62]
    #june 26, 2021
    att_thi = [0, 24.69281, 50.299573, 75.855897, 100.892898, 127.098354, 153.204123, 179.600359]       

    

    att_mat = ['Mo', 'Mo', 'Mo', 'Mo', 'Mo', 'Mo', 'Mo', 'Mo']
    att_name = ['att0', 'att1', 'att2', 'att3', 'att4', 'att5', 'att6', 'att7']
    att_pos = [0.22, 1, 2, 3, 4, 5, 6, 7]

    ener = energy.energy.position
    ener = 9700
    # Create a dictionary of attenuators for bar1, it can only be use one att at a time
    att_bar1 = {'name':             ['att0', 'att1', 'att2', 'att3', 'att4', 'att5', 'att6', 'att7'],
                'material':         [  'Mo',   'Mo',   'Mo',   'Mo',   'Mo',   'Mo',   'Mo',   'Mo'],
                #  [   0.0,   25.0,  50.72,  76.24, 100.76, 126.41, 152.45, 177.62]
                'thickness':              [0,  26.35,   52.5, 77.923,103.062,130.2615, 154.1797, 181.824],
                'position':          [  0.22,    1.0,    2.0,    3.0,    4.0,    5.0,    6.0,    7.0],
                'energy':           [  ener,   ener,   ener,   ener,   ener,   ener,   ener,   ener],
                'material_att_coef':[   1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0],
                'attenuator_aborp': [   1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0,    1.0]
                }

    att_bar1 = calc_attenuation(att_bar1, ener)
    att_bar1 = calculate_att_comb(att_bar1,ener)

    '''
    Create a dictionary for the 2nd set of att that can be inserted in parallel
    att_bar2 = {'att0':{'name':'att0', material:'Mo', 'thickness':50.0, 'position':1, 'att_ener':1, 'att_mat_value':1},
                'att1':{'name':'att1', material:'Mo', 'thickness':50.0, 'position':1, 'att_ener':1, 'att_mat_value':1},
                'att2':{'name':'att2', material:'Mo', 'thickness':50.0, 'position':1, 'att_ener':1, 'att_mat_value':1},
                'att3':{'name':'att3', material:'Mo', 'thickness':50.0, 'position':1, 'att_ener':1, 'att_mat_value':1},
                }
    
    return att_bar1, att_bar2
    '''

    return att_bar1

#Load a default attenuation set-up that will be recalculated if needed
att_bar1 = att_setup()

# ToDo: Check the T_target to constrain that it only consider T lower than a number
def best_att(T_target, att_bar1 = att_bar1):
    """
    Find the absorber combination that give the closest x-ray transmission from a taget value

    Parameters:
    -----------
    :param T_target: The target transmission value (has to be 1 or lower)
    :type T_target: float
    :param energy: the energy at which the absorption needs to be interpolated
    :type energy: float

    Returns
    -------
    best_att: A integer which contains the attenuator that best match the targeted transmission
    T[best_att]: A float which contains the corresponding best transmission value
    att2_name[best_att]: A string which contains the name of the matching attenuator
    att_pos[best_att]: A float which contains the physical position of the matching attenuator
    """
    # Check if energy move or not
    if energy.energy.position != int(att_bar1['energy'][0]) or att_bar1['attenuator_aborp'][2]==1:
        att_bar1 = att_setup()
    
    best_att = np.argmin(abs(np.asarray(att_bar1['attenuator_aborp'])-T_target))
    # print('The required attenuation is %s the best match is %s'%(T_target, T[best_att]))

    return best_att, att_bar1['attenuator_aborp'][best_att], att_bar1['name'][best_att], att_bar1['position'][best_att]


def put_default_absorbers(energy, default_attenuation=1e-07):
    """
    Put a default absorbers to protect the detector. With a default_attenuation factor of 1e-07,
    the full direct beam is attenuated enough to not damage the detector. This is used to set a default
    attenuator during a pre-count to define what is the necessary number of attenuators for a full image.

    Parameters:
    -----------
    :param energy: the energy at which the absorption needs to be interpolated
    :type energy: float
    :param default_attenuation: The default target transmission value (1e-07)
    :type default_attenuation: float

    Returnsput_default_absorbers
    -------
    default_factor: A float corresponding to the attenuation of the default attenuator
    """
    default_att, default_factor, default_name, default_position = best_att(default_attenuation)

    if energy < 9000 and energy > 10000:
        raise ValueError('error: the energy entered is not correct')

    yield from bps.mv(abs2, default_position)
    yield from bps.sleep(1)

    return default_factor


def calculate_and_set_absorbers(energy, i_max, att, precount_time=0.1):
    """
    Define the good attenuation needed based on the maximum counts recorded by the detector on an
    image taken with a known safe number of attenuator (default attenuations). The process of 'precount'
    is used to protect the detectors

    Parameters:
    -----------
    :param energy: the energy at which the absorption needs to be interpolated
    :type energy: float
    :param i_max: The maximum counts recorded by the detector during the pre-count
    :type i_max: float
    :param att: The attenuation used during the pre-count
    :type att: float
    :param precount_time: The pre-count exposure time
    :type precount_time: float

    Returns
    -------
    best_at: An integer which contains the attenuator that best match the targeted transmission
    att_factor: A float which contains the corresponding best transmission value
    att_name: A string which contains the name of the matching attenuator
    """
    # i_max_det is the maximum allowed pixel count (nominal value is 1e4)
    i_max_det = 5000  # 50000 if lambda, 500000 if pilatus

    # Theoretical maximum count to be seen by the detector
    max_theo_precount = i_max / (att * precount_time)

    # The required attenuation to not saturate the detector, i.e. keep i_max < max_theo
    att_needed = 1 / (max_theo_precount / i_max_det)

    # Calculate and move the absorber to the chosen one
    best_at, att_factor, att_name, att_pos = best_att(att_needed)
    yield from bps.mv(abs2, att_pos)

    return best_at, att_factor, att_name



all_area_dets = [lambda_det, quadem]
@bpp.stage_decorator(all_area_dets)

def define_all_att_thickness():
    ratios = np.zeros((8,))
    base_md = {'plan_name': 'calibration_att'}
    # yield from bps.mv(S2.vg, 0.05)
    # yield from bps.mv(S2.vc, 0)
    # yield from bps.mv(S2.hg, 0.3)
    # yield from bps.mv(S2.hc, -0.1)

    yield from bps.open_run(md=base_md)

    #From 0 to 6 because the last ratio should be 0 
    th_angle = [0.1, 0.2, 0.25, 0.35, 0.6, 1.2, 2]
    for nu, th_angles in zip(range(0, 7, 1)[::-1], th_angle):
        ratio = yield from define_att_thickness(attenuator1=nu+1, attenuator2=nu, th_angle=th_angles)
        ratios[nu] = 1
        ratios *= ratio
        print('ratio between %s and %s'%(nu+1, nu), ratios[nu])
    yield from bps.close_run()

    att_ener = attenuation_interpolation(path=path, filename=file_absorption, energy=energy.energy.position)
    att_thickness_new = att_ener * np.log(ratios)

    current_att_thickness = attenuator_thickness_load()
    print('The new calculated attenuators thickness are to %s um while the current were %s um'%(att_thickness_new, current_att_thickness))
    response = input('Do you want to use the new thicknesses? (y/[n]) ')

    if response is 'y' or response is 'Y':
        print('The new attenuators thickness are to %s um'%att_thickness_new)
        #Need to implement the new thickness
        attenuator_thickness_save(att_thickness_new)

    else:
        print('The current attenuators thicknesses were kept at %s um'%current_att_thickness)


def attenuator_thickness_load():
    '''
    Load the previous attenuator thickness
    '''
    OPLS_CONFIG_FILENAME = os.path.join(get_ipython().profile_dir.location,
                                       'OPLS_attenuator_thickness.csv')
    # collect the current positions of motors
    smi_config = pds.read_csv(OPLS_CONFIG_FILENAME, index_col=0)

    att_thickness = np.zeros((8,))

    att_thickness[0] = smi_config.att0.values[-1]
    att_thickness[1] = smi_config.att1.values[-1]
    att_thickness[2] = smi_config.att2.values[-1]
    att_thickness[3] = smi_config.att3.values[-1]
    att_thickness[4] = smi_config.att4.values[-1]
    att_thickness[5] = smi_config.att5.values[-1]
    att_thickness[6] = smi_config.att6.values[-1]
    att_thickness[7] = smi_config.att7.values[-1]

    return att_thickness

def attenuator_thickness_save(attenuators_thickness):
    '''
    Save the new attenuators thckness
    '''

    SMI_CONFIG_FILENAME = os.path.join(get_ipython().profile_dir.location,
                                       'OPLS_attenuator_thickness.csv')

    # collect the current positions of motors
    current_config = {
        'att0': attenuators_thickness[0],
        'att1': attenuators_thickness[1],
        'att2': attenuators_thickness[2],
        'att3': attenuators_thickness[3],
        'att4': attenuators_thickness[4],
        'att5': attenuators_thickness[5],
        'att6': attenuators_thickness[6],
        'att7': attenuators_thickness[7],
        'time': time.ctime()
    }

    current_config_DF = pds.DataFrame(data=current_config, index=[1])

    # load the previous config file
    smi_config = pds.read_csv(SMI_CONFIG_FILENAME, index_col=0)
    smi_config_update = smi_config.append(current_config_DF, ignore_index=True)

    # save to file
    smi_config_update.to_csv(SMI_CONFIG_FILENAME)
    global current_att_thickness
    current_att_thickness = attenuator_thickness_load()
    print(current_att_thickness)


def define_att_thickness(attenuator1, attenuator2, th_angle):
    detector='lambda_det'

    yield from mabt(th_angle, th_angle, 0)
    yield from bps.mv(abs2, attenuator1)
    yield from bps.sleep(10)
    yield from det_exposure_time(5, 5)

    yield from bps.mv(shutter, 1)
    ret = yield from bps.trigger_and_read(area_dets, name='precount')    
    yield from bps.mv(shutter, 0)

    i_max1 = ret['%s_stats4_total'%detector]['value']

    yield from bps.mv(abs2, attenuator2)
    yield from bps.sleep(10)
    yield from det_exposure_time(5, 5)

    yield from bps.mv(shutter, 1)
    ret = yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.mv(shutter, 0)
    i_max2 = ret['%s_stats4_total'%detector]['value']

    ratio = i_max2 / i_max1
    return ratio

current_att_thickness = attenuator_thickness_load()

