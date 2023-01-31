proposal_id("2022_3","309773_ocko")

def nab(alpha_0,beta_0, ssth_corr_par=-0.017):

    """
    Args:
        ssth_corr_par (float): parameter for stth (sample two
                               theta correction)
    """
    stth_corr = (ssth_corr_par)*pow(np.abs(alpha_0),1)
    # print(stth_corr)
    if alpha_0 > 0:
        yield from nabt(alpha_0,beta_0,stth_corr)
    else:
        yield from nabt(alpha_0,beta_0,-1*stth_corr)




def ms_all():
    yield from ms_1()
    yield from ms_2()


def ms_1():
    proposal_id("2022_2","309773_ocko")
    yield from shopen()
    yield from one_xrr1("sapphire_zncl2_450C_2",-16.5)
    yield from shclose()


def ms_2():
    proposal_id("2022_2","309773_ocko")
    yield from shopen()
    yield from one_xrr2("sapphire_crystec1_a1_T",-17.5)
    yield from shclose()

def one_xrr1(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(shutter,1) # open shutter
    yield from sample_height_set_fine_ms(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    yield from sample_tilt_set()
    yield from xr_scan1(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from nabt(0.5,0.5,0)


def one_xrr2(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(shutter,1) # open shutter
    yield from sample_height_set_fine_ms(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    yield from sample_tilt_set()
    yield from xr_scan2(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from nabt(-0.2,-0.2,0)


def sample_height_set_fine_ms(value=0,detector=lambda_det):
    geo.sh.user_readback.kind = 'hinted'
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,3)
    yield from nab(-0.3,-0.3)
    print('Start the height scan before XR')
    Msg('reset_settle_time', sh.settle_time, value)
    yield from det_exposure_time_new(detector, 1,1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.10,0.10,21,per_step=shutter_flash_scan), local_peaks)
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    yield from bps.mv(sh,tmp2)
    yield from set_sh(0)
    Msg('reset_settle_time', sh.settle_time, 0)

def sample_tilt_set(value=0,detector=lambda_det):
    tilt.y.user_readback.kind = 'hinted'
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,3)
    yield from nab(-0.2,-0.2)
    print('Start the height scan before XR')
    Msg('reset_settle_time', tilt.y.settle_time, value)
    yield from det_exposure_time_new(detector, 1,1)
    local_peaks = PeakStats(tilt.y.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],tilt.y,-0.07,0.07,29,per_step=shutter_flash_scan), local_peaks)
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    yield from bps.mv(tilt.y,tmp2)
    yield from set_tilty(-0.2)
    Msg('reset_settle_time', sh.settle_time, 0)




def xr_scan1(name):
    alpha_start_list =   [ 0.05, 0.15, 0.25, 0.50,  1.0,  2.0,  3.0]
    alpha_stop_list =    [ 0.15, 0.25, 0.50, 1.00,  2.0,  3.0,  5.0]
    number_points_list = [    6,    6,    6,    6,    7,   13,   15]
    auto_atten_list =    [    4,    3,    2,    1,    0,    0,    0] 
    s2_vg_list =         [ 0.04, 0.04,0.04,  0.04, 0.04, 0.04, 0.04] 
    exp_time_list =      [   5,   5,     5,    5,     5,   20,   40]
    precount_time_list=  [  0.2, 0.2,  0.2,   0.2,  0.2,  0.2,  0.2]
    wait_time_list=      [    4,   4,    4,     4,    4,   4,    4 ]
    x2_offset_start_list=[    0,   0,    0,     0,    0,   0,    0 ]
    x2_offset_stop_list= [    0,   0,    0,     0,    0,   0,    0 ]
    block_offset_list=   [    0,   0,    0,     0,    0,   0,    0 ]


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
        tilt_stage=True,)


def xr_scan2(name):
    alpha_start_list =   [ -0.05, -0.15, -0.25, -0.50,  -1.0,  -2.0,  -3.0]
    alpha_stop_list =    [ -0.15, -0.25, -0.50, -1.00,  -2.0,  -3.0,  -5.0]
    number_points_list = [    6,    6,    6,    6,    7,   13,   15]
    auto_atten_list =    [    4,    3,    2,    1,    0,    0,    0] 
    s2_vg_list =         [ 0.04, 0.04,0.04,  0.04, 0.04, 0.04, 0.04] 
    exp_time_list =      [   5,   5,     5,    5,     5,   10,   20]
    precount_time_list=  [  0.2, 0.2,  0.2,   0.2,  0.2,  0.2,  0.2]
    wait_time_list=      [    3,   3,    3,     3,    3,   3,    3 ]
    x2_offset_start_list=[    0,   0,    0,     0,    0,   0,    0 ]
    x2_offset_stop_list= [    0,   0,    0,     0,    0,   0,    0 ]
    block_offset_list=   [    0,   0,    0,     0,    0,   0,    0 ]


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
        tilt_stage=True,)