


def nwu_1():
    proposal_id("2022_1","308307_dutta")
    yield from he_on() # starts the He flow
    yield from one_xrf("4 KI_5mM_pH7,ODA,pressure 34,#1",-51)
    yield from one_ref("4 KI_5mM_pH7,ODA,pressure 34,#1",-51)
    yield from he_off() # starts the He flow


def nwu_2():
    proposal_id("2022_1","308307_dutta")
    yield from he_on() # starts the He flow
    yield from one_xrf("21_5mM_KI_ODA_pH3.5,#2",17)
    #yield from one_ref("21_5mM_KI_ODA_pH3.5,#1",17)
    yield from one_xrf("22_5mM_KBr_ODA_pH3.5,#2",-51)
    #yield from one_ref("22_5mM_KBr_ODA_pH3.5,#1",-51)
    yield from he_off() # starts the He flow




def one_ref(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(shutter,1) # open shutter
   # yield from check_ih()  #Align the spectrometer  height
   # yield from check_tth() #Align the spectrometer rotation angle
   # yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
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
    yield from bps.mv(abs3,3)
    yield from xrf_scan1(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)

        
def sample_height_set_coarse(value=0,detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,6)
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



def xr_scan1(name):
    #9.7kev
    alpha_start_list =   [ 0.04, 0.14, 0.20, 0.40,  0.7,  1.2,  2.2]
    alpha_stop_list =    [ 0.14, 0.20, 0.40, 0.70,  1.2,  2.2,  3.0]
    number_points_list = [    6,   4,    6,     4,    6,    12,    8]
    auto_atten_list =    [    6,   5,    4,     3,    2,    1,    0] 
    s2_vg_list =         [ 0.04, 0.04,0.04,  0.04, 0.04, 0.04,  0.04] 
    exp_time_list =      [   5,    5,    5,    5,     5,   5,    5 ]
    precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1,  0.1]
    wait_time_list=      [    7,   7,    5,     5,    5,   5,    5 ]
    x2_offset_start_list=[    0,   0,    0,     0,    0,   0,   0]
    x2_offset_stop_list= [    0,   0,    0,     0,    0,   0,   0]


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
    yield from reflection_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=lambda_det, 
        tilt_stage=False,)


def xrf_scan1(name):
    #9.7kev
    alpha_start_list =   [ 0.03, 0.12]
    alpha_stop_list =    [ 0.11, 0.32]
    number_points_list = [   7,   5]
    auto_atten_list =    [   1,  1] 
    s2_vg_list =         [ 0.04, 0.04] 
    exp_time_list =      [   60,   60]
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








def gid_scan1(name):
    det_saxs_y_list         = [-20,-20,65,65]
    det_saxs_y_offset_list  = [0,1,0,1]
    stth_list               = [14,14,14,14]
    exp_time_list           = [20,20,20,20]
    x2_offset_list          = [1,1,1,1]
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
    yield from bps.mv(fp_saxs.y1,9,fp_saxs.y2,18)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.06)


def gid_direct(name):
    det_saxs_y_list         = [-20]
    det_saxs_y_offset_list  = [0]
    stth_list               = [0]
    exp_time_list           = [1]
    x2_offset_list          = [0]
    atten_2_list            = [5]
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
    yield from bps.mv(fp_saxs.y1,9,fp_saxs.y2,18)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.00)


    