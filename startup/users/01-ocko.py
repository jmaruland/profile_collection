# for water 9.7 keV

def xr_checks():
    yield from bps.mv(shutter,1) # open shutter
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_ih()  #Align the spectrometer  height
    yield from check_tth() #Align the spectrometer rotation angle
    #yield from check_sh_coarse(0.05,detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from check_sh_fine(0.05,detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affec


def xr_scan1(name):
    alpha_start_list =   [ 0.03, 0.06, 0.10, 0.14,  0.30,  0.5,  1.0]
    alpha_stop_list =    [ 0.06, 0.10, 0.14, 0.30,  0.50,  1.0,  2.2]
    number_points_list = [    4,   5,    5,    9,    7,    10,   20]
    auto_atten_list =    [    5,   5,    4,    3,    2,    1,   0 ] 
    s2_vg_list =         [0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04] 
    exp_time_list =      [    4,   4,    4,    4,    4,    4,   4 ]
    precount_time_list=  [  0.1, 0.1,  0.1,  0.1,  0.1,  0.1,  0.1]
    wait_time_list=      [    4,   4,    4,    4,    4,    4,   4 ]
    x2_offset_list=      [    0,   0,    0,    0,    0,    0,   0 ]


    scan_p={"start":alpha_start_list,
        "stop":alpha_stop_list,
        "n":number_points_list,
        "atten":auto_atten_list,
        "s2vg":s2_vg_list,
        "exp_time":exp_time_list,
        "pre_time":precount_time_list,
        "wait_time":wait_time_list,
        "x2_offset":x2_offset_list}

    yield from reflection_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=lambda_det, 
        tilt_stage=False,)
    yield from mabt(0.2,0.2,0)


# print_summary(gid_scan1('bob'))

def gid_scan1(name):
    det_saxs_y_list         = [0,0,80,80]
    det_saxs_y_offset_list  = [0,1,0,1]
    stth_list               = [16,16,16,16]
    exp_time_list           = [2,2,2,2]
    x2_offset_list          = [0,0,0,0]
    atten_2_list            = [0,0,0,0]
    wait_time_list          = [2,2,2,2]

    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,}


    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict, md={'sample_name': name}, detector = pilatus300k, alphai = 0.1)


    
