#Notes from Ben on how to set sh zero from the direct beam
#%mov abs2 5 : moves the attenuator to 5
#RE(shopen()): opens the shutter
#RE(mabt(0,0,0)): goes to the direct beam
#open the fast shutter by the screen or by the command 
#%mov shutter 1
#manual click the start on the lambda_detector, set to 1 sec collect time 
#by the screen you can use RE(bp.count([lambda_det])
#if there is no beam then lower the sh(sample height steps of about 0.1mm) and count again
#if there is beam then raise the sample height (steps of about 0.1 mm) and count again
#when it is close enough
#RE(set_sh(0)) 
# set title below for ccny_1
# run cntrl S to save the file
# from blue sky you need to reread the macro
# %run -i .ipython/profile_collection/startup/users/97-ccny-2.py
# RE(ccny_1())

#if the direct beam is not in the middle of the center box (up down) this means that astth is off.
#mov astth by hand using the screen, counting at each time till it is in the middle of the box
#RE(set_astth(22.566))

def ccny_1():
    proposal_id("2022_2","309891_tu")

    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow

    sample_x2 = 0
    # sample_name = "SF_5x_300uL_16.7"
    # sample_name = "SF_wait_15_compress_8p5_300uL_5x_early2"
    # sample_name = "SF_12p2_StartingP_wait15_300uL_5x_PlatCheck__Current28p2"
    sample_name = "CTAB_19C+h50uL_1e-3_c16"

    yield from one_xrr(sample_name,sample_x2)

    # yield from bps.mv(geo.stblx2,sample_x2-2)  #move the  Sample Table X2 to xpos
    # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    # yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    # yield from gid_scan_tth(sample_name)
    # detector=lambda_det
    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(abs2,5)
    yield from he_off()# stops the He flow
    yield from shclose()


def ccny_multi():
    proposal_id("2022_2","309891_tu")

    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow

    sample_x2 = -60 # the position of the sample
    sample_name = "water_small_kibron"
    sample_x2_offset = -3.5 # trough move to back, the measured spot moves to the front
    wait_time = 5 # in min
    run_cycle = 5  # the total number of runs

    for ii in range(run_cycle):
        
        sample_x2_updated = sample_x2 + sample_x2_offset*ii
        yield from one_xrr(sample_name+f'_run{ii+1}',sample_x2_updated)
        yield from print(f'Start incubating for {wait_time} min.')
        yield from bps.sleep(wait_time*60)

    # detector=lambda_det
    yield from det_exposure_time_new(lambda_det, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(abs2,5)
    yield from he_off()# stops the He flow
    yield from shclose()



def one_xrr(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(block.y,xpos)  #move the  block to xpos
    yield from bps.mv(shutter,1) # open shutter
    yield from check_ih()  #Align the spectrometer  height
   # yield from check_tth() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
    yield from xr_scan1(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)


def one_xrf(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)
    yield from shopen()
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(shutter,1) # open shutter
    yield from check_ih()  #Align the spectrometer  height
   # yield from check_tth() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
    yield from bps.mv(abs3,4)
    yield from xrf_scan1(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)

        
def sample_height_set_coarse(value=0,detector=lambda_det):
    geo.sh.user_readback.kind = 'hinted'
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
    yield from mabt(0.05,0.05,0)
    tmp1=geo.sh.position
    print('Start the height scan before GID')
    Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]
    yield from det_exposure_time_new(detector, 1,1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-1,1,13,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)


def sample_height_set_fine_o(value=0,detector=lambda_det):
    geo.sh.user_readback.kind = 'hinted'
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
    yield from mabt(0.05,0.05,0)
    tmp1=geo.sh.position
    print('Start the height scan before GID')
    Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]
    yield from det_exposure_time_new(detector, 1,1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.15,0.15,13,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)

def xr_scan1(name):


    #9.7kev Qz to 0.65, more overlap
    alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  0.65, 0.95,  1.9, 2.9]
    alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.1, 3.8]
    number_points_list = [    8,   8,     8,    9,    9,   23,   13,  10]
    auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   0]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,   5]
    precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1, 0.1]
    wait_time_list=      [    5,   5,     5,     5,    5,    5,   5,   5]
    x2_offset_start_list=[    0,   0,     0,     0,    0,    0, -0.5, -1.5]
    x2_offset_stop_list= [    0,   0,     0,     0,    0,  -0.5, -1.5, -2.5]
    block_offset_list=   [    0,   0,     0,     0,    0,   0,    0,   0]


    # #9.7kev Qz to 0.65
    # alpha_start_list =   [ 0.04, 0.16, 0.24, 0.40,  0.7,  1.0,  2.0, 3.0]
    # alpha_stop_list =    [ 0.16, 0.24, 0.40, 0.70,  1.0,  2.0,  3.0, 3.8]
    # number_points_list = [    7,   6,     5,    7,    6,   21,   11,   9]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,   5]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1, 0.1]
    # wait_time_list=      [    7,   7,     7,     7,    7,   7,    7,   7]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,    0, 0.1]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0,    0, 0.9]



    #     #9.7kev Qz to 0.65, sleep to 12s
    # alpha_start_list =   [ 0.04, 0.16, 0.24, 0.40,  0.7,  1.0,  2.0, 3.0]
    # alpha_stop_list =    [ 0.16, 0.24, 0.40, 0.70,  1.0,  2.0,  3.0, 3.8]
    # number_points_list = [    7,   6,     5,    7,    6,   21,   11,   9]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,   5]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1, 0.1]
    # wait_time_list=      [   12,  12,    12,    12,   12,  12,   12,  12]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,    0, 0.1]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0,    0, 0.9]


    # #9.7kev Qz to 0.65, remove a few point in the low q
    # alpha_start_list =   [ 0.10, 0.16, 0.24, 0.40,  0.7,  1.0,  2.0, 3.0]
    # alpha_stop_list =    [ 0.16, 0.24, 0.40, 0.70,  1.0,  2.0,  3.0, 3.8]
    # number_points_list = [    4,   6,     5,    7,    6,   21,   11,   9]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,   5]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1, 0.1]
    # wait_time_list=      [    7,   7,     7,     7,    7,   7,    7,   7]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,    0, 0.1]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0,    0, 0.9]



    scan_p={"start":alpha_start_list,
        "stop":alpha_stop_list,
        "n":number_points_list,
        "atten":auto_atten_list,
        "s2vg":s2_vg_list,
        "exp_time":exp_time_list,
        "pre_time":precount_time_list,
        "wait_time":wait_time_list,
        "x2_offset_start":x2_offset_start_list,
        "x2_offset_stop":x2_offset_stop_list,
        "beam_block_offset":block_offset_list}
        

        


    print(scan_p)
    yield from bps.mv(geo.det_mode,1)
    yield from reflection_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=lambda_det, 
        tilt_stage=False,)


def xrf_scan1(name):
    #9.7kev
    alpha_start_list =   [ 0.03, 0.12]
    alpha_stop_list =    [ 0.11, 0.32]
    number_points_list = [   7,   5]
    auto_atten_list =    [   0,  0] 
    s2_vg_list =         [ 0.04, 0.04] 
    exp_time_list =      [   8,   8]
    precount_time_list=  [  0.1, 0.1]
    wait_time_list=      [    5,   5]
    x2_offset_start_list=[    0.8,   0.8]
    x2_offset_stop_list= [    0.8,   0.8]


    scan_p={"start":alpha_start_list,
        "stop":alpha_stop_list,
        "n":number_points_list,
        "atten":auto_atten_list,
        "s2vg":s2_vg_list,
        "exp_time":exp_time_list,
        "pre_time":precount_time_list,
        "wait_time":wait_time_list,
        "x2_offset_start":x2_offset_start_list,
        "x2_offset_stop":x2_offset_stop_list}

    print(scan_p)
    yield from bps.mv(geo.det_mode,1)
    yield from reflection_fluorescence_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=xs, 
        tilt_stage=False,)

def gid_scan_tth(name):
    '''
    Run GID scans with respect to two-theta, a slit is mounted in the front of the flight path
    This method calls 'gid_scan_stitch'.
    '''
    import numpy as np
    stth_list = list(np.linspace(16,19,15))

    point_num = len(stth_list)
    det_saxs_y_list = [5]*point_num
    det_saxs_y_offset_list = [0]*point_num
    exp_time_list  = [5]*point_num
    x2_offset_list = [0]*point_num
    atten_2_list = [0]*point_num
    wait_time_list = [5]*point_num
    beam_stop_x = [30]*point_num
    beam_stop_y = [-20]*point_num


    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
        "beam_stop_x":beam_stop_x,
        "beam_stop_y":beam_stop_y,}


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    yield from bps.mv(fp_saxs.y1,11,fp_saxs.y2,22)
    print("Run gid over two-theta scan")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.07)




def gid_scan1(name):
    det_saxs_y_list         = [-20,-20,65,65]
    det_saxs_y_offset_list  = [0,1,0,1]
    stth_list               = [11.5,11.5,11.5,11.5]
    exp_time_list           = [20,20,20,20]
    x2_offset_list          = [0,0,0,0]
    atten_2_list            = [0,0,0,0]
    wait_time_list          = [5,5,5,5]
    beam_stop_x             = [-65,-65,-65,-65]
    beam_stop_y             = [-24,-24,-24,-24]


    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
        "beam_stop_x":beam_stop_x,
        "beam_stop_y":beam_stop_y,}


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    # yield from bps.mv(geo.sh,-1)
    yield from bps.mv(fp_saxs.y1,11,fp_saxs.y2,22)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.06)

def gid_scan1a(name):
    det_saxs_y_list         = [-20,-20,65,65]
    det_saxs_y_offset_list  = [0,1,0,1]
    stth_list               = [10.5,10.5,10.5,10.5]
    exp_time_list           = [20,20,20,20]
    x2_offset_list          = [0,0,0,0]
    atten_2_list            = [0,0,0,0]
    wait_time_list          = [5,5,5,5]
    beam_stop_x             = [-65,-65,-65,-65]
    beam_stop_y             = [-24,-24,-24,-24]


    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
        "beam_stop_x":beam_stop_x,
        "beam_stop_y":beam_stop_y,}


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    # yield from bps.mv(geo.sh,-1)
    yield from bps.mv(fp_saxs.y1,11,fp_saxs.y2,22)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.06)


def gid_scan2(name):
    det_saxs_y_list         = [-20,-20,-20,-20]
    det_saxs_y_offset_list  = [0,0,0,0]
    stth_list               = [4,7,10,13]
    exp_time_list           = [20,20,20,20]
    x2_offset_list          = [0,0,0,0]
    atten_2_list            = [0,0,0,0]
    wait_time_list          = [5,5,5,5]
    beam_stop_x             = [-65,-65,-65,-65]
    beam_stop_y             = [-24,-24,-24,-24]


    scan_dict={"det_saxs_y":det_saxs_y_list, 
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
        "beam_stop_x":beam_stop_x,
        "beam_stop_y":beam_stop_y,}


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    yield from bps.mv(geo.sh,-1)
    yield from bps.mv(fp_saxs.y1,0,fp_saxs.y2,0)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.06)

def gid_direct(name):
    det_saxs_y_list         = [5]
    det_saxs_y_offset_list  = [0]
    stth_list               = [0]
    exp_time_list           = [1]
    x2_offset_list          = [0]
    atten_2_list            = [6]
    wait_time_list          = [1]
    beam_stop_x             = [30]
    beam_stop_y             = [-20]


    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
        "beam_stop_x":beam_stop_x,
        "beam_stop_y":beam_stop_y,}


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    yield from bps.mv(geo.sh,-1)
    yield from bps.mv(fp_saxs.y1,11,fp_saxs.y2,22)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.00)



def gid_single(name,stth_0):
    print(name)
    print(stth_0)
    det_saxs_y_list         = [-20]
    det_saxs_y_offset_list  = [0]
    stth_list               = [stth_0]
    exp_time_list           = [1]
    x2_offset_list          = [0]
    atten_2_list            = [0]
    wait_time_list          = [1]
    beam_stop_x             = [-65]
    beam_stop_y             = [-24]


    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
        "beam_stop_x":beam_stop_x,
        "beam_stop_y":beam_stop_y,}


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    yield from bps.mv(geo.sh,-1)
    yield from bps.mv(fp_saxs.y1,0,fp_saxs.y2,0)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.06)


