
def run1():
    # proposal_id("2022_2","310190_arjunkrishna2")
    proposal_id("2022_3","311090_arjunkrishna2")

    # yield from bps.sleep(5)
    # yield from shopen()
    # yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {

        1: 'PFDA_10ppm_1mMCaCl2_2', 
        2: 'PFDA_10ppm_10mMCaCl2_2', 
        3: 'PFDA_10ppm_0p01mMCaCl2_2',
        
    }

    sam_x2_dict ={

       1: -64,       #-66, flat from -65 to -60  #-65, #-62, # (-63.5,-6.14), # front
       2: -13.5,     #-19, flat from -15 to -10 # -9, # (-9, 3.5), # middle trough
       3:  36,       # 32 flat from 34.5 to 39.5  #42, # (38, 5.1), # back

    }

    xrr_run_dict = {
        1: False,
        2: True,
        3: True,
    }

    xrf_run_dict = {
        1: False,
        2: False,
        3: True,
    }



    for key in samp_name_dict:
        samp_name = samp_name_dict[key]
        samp_x2 = sam_x2_dict[key]
        print(f'Now start running sample: {samp_name}')
        yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos

        if xrr_run_dict[key]:
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from bps.mv(S2.hg, 1)
            yield from one_xrr(samp_name,samp_x2)

        if xrf_run_dict[key]:
            print('Starting XRF measurement')
            yield from bps.mv(S2.hg, 0.2)
            yield from bps.mv(abs3,1) ## using abs3 to avoid saturation
            yield from bps.mv(geo.stblx2,samp_x2-0.5)  #move the  Sample Table X2 to xpos
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from sample_height_set_coarse(detector=detector)
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from xrf_scan1(samp_name)
            
            # quadem.averaging_time.put(1)

        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    # yield from he_off()# stops the He flow
    # yield from shclose()


    



def one_xrr(name,xpos,blocky=0, tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    # yield from bps.mv(block.y,blocky)  #move the  block to xpos
    yield from bps.mv(shutter,1) # open shutter
    yield from check_ih()  #Align the spectrometer  height
    yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
   # yield from check_tth() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
    yield from xr_scan1(name)
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
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-1.2,1.2,15,per_step=shutter_flash_scan), local_peaks)
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
    # yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.10,0.10,20,per_step=shutter_flash_scan), local_peaks)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.15,0.15,21,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)


def xr_scan1(name):
 
#      9.7kev Qz to 0.65, more overlap
#    alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  True0.65,  0.9,  1.9,  2.9]
#   alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.1,  3.8]
#    number_points_list = [    8,   8,     8,    9,    9,   13,   13,   10]
#    auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,    0]
#    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04, 0.04]
#    exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,    5]
#    precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1,  0.1]
#    wait_time_list=      [    5,   5,     5,     5,    5,   5,    5,    5]
#    x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0.0, 0.0]
#    x2_offset_stop_list= [    0,   0,     0,     0,    0,   0,   0.0,   0]
#    block_offset_list=   [    0,   0,     0,     0,    0,   0,    0,    0]  
    
    # #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.18, 0.30,  0.4,  0.7,  1.2,  2.0, 3.1]
    # alpha_stop_list =    [ 0.18, 0.30, 0.40,  0.8,  1.3,  2.0,  3.0, 3.9]
    # number_points_list = [    8,   5,     6,    5,    7,    9,   11,   5]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,   5,    5,  20]
    # precount_time_list=  [  0.1, 0.1,   0.1,  0.1,   0.1, 0.1,  0.1, 0.1]
    # wait_time_list=      [    5,   5,     5,    5,     5,   5,    5,   5]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,    0,   0]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,   0,    0,   0]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,    0,   0]

    #     #14.4lkev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72,  1.3,  1.9]
    # alpha_stop_list =    [ 0.12, 0.20, 0.46, 0.80,  1.36,  2.0,  2.8]
    # number_points_list = [   10,  11,    15,   11,    9,    8,    10]
    # auto_atten_list =    [    5,   4,     3,    2,    1,    0,     0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,   5,     5]
    # precount_time_list=  [  0.1, 0.1,   0.1,  0.1,   0.1, 0.1,   0.1]
    # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,   0.5]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, 0.5,     2]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]



    #14.4kev for running kibron, keep 1 abs
    alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72, 1.52, 2.00]
    alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.60, 2.08, 2.72]
    number_points_list = [   11,   11,   15,   11,   12,     8,   10]
    auto_atten_list =    [    6,    5,    4,    3,    2,     1,    1]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]
    exp_time_list =      [    5,   5,     5,    5,     5,    5,   20]
    precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    wait_time_list=      [    8,   8,     8,    8,     8,    8,    8]
    x2_offset_start_list=[    0,   0,     0,    0,     0,    0,  0.6]
    x2_offset_stop_list= [    0,   0,     0,    0,     0,  0.5,  2.0]
    block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]



  #  alpha_start_list =   [ 1.8, 3.0]
  #  alpha_stop_list =    [ 3.0, 3.8]
  #  number_points_list = [  5,  5]
  #  auto_atten_list =    [  1,   1]
  #  s2_vg_list =         [ 0.04,0.04]
  #  exp_time_list =      [   5,   20]
  #  precount_time_list=  [    0.1, 0.1]
  #  wait_time_list=      [      5,   5]
  #  x2_offset_start_list=[      0,   0]





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
    # alpha_start_list =   [ 0.03, 0.12, 0.25]
    # alpha_stop_list =    [ 0.11, 0.24, 0.65]
    # number_points_list = [   8,    6,  9  ]
    # auto_atten_list =    [   0,    2,   2  ] 
    # s2_vg_list =         [ 0.04,0.04, 0.04 ] 
    # exp_time_list =      [  2 ,   10,  10  ]
    # precount_time_list=  [  0.1, 0.1,  0.1 ]
    # wait_time_list=      [    0,   0,   0  ]
    # x2_offset_start_list=[  0.0,   0.0, 0.0]
    # x2_offset_stop_list= [  0.0,   0.0, 0.0]

    # alpha_start_list =   [ 0.03, 0.11, 0.13, 0.25]
    # alpha_stop_list =    [ 0.10, 0.12, 0.24, 0.65]
    # number_points_list = [    8,    2,    6,    9]
    # auto_atten_list =    [    0,    1,    2,    2] 
    # s2_vg_list =         [ 0.04, 0.04, 0.04, 0.04] 
    # exp_time_list =      [    2,   10,   10,   10]
    # precount_time_list=  [  0.1,  0.1,  0.1,  0.1]
    # wait_time_list=      [    0,    0,    0,    0]
    # x2_offset_start_list=[  0.0,  0.0,  0.0,  0.0]
    # x2_offset_stop_list= [  0.0,  0.0,  0.0,  0.0]

    alpha_start_list =   [ 0.03, 0.09, 0.14, 0.25]
    alpha_stop_list =    [ 0.08, 0.13, 0.24, 0.45]
    number_points_list = [    6,    5,    6,    5]
    auto_atten_list =    [    1,    2,    2,    2] 
    s2_vg_list =         [ 0.04, 0.04, 0.04, 0.04] 
    exp_time_list =      [   20,   10,   10,   10]
    precount_time_list=  [  0.2,  0.2,  0.2,  0.2]
    wait_time_list=      [    0,    0,    0,    0]
    x2_offset_start_list=[  0.0,  0.0,  0.0,  0.0]
    x2_offset_stop_list= [  0.0,  0.0,  0.0,  0.0]




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
    stth_list               = [11.5,11.5,11.5,11.5]
    exp_time_list           = [20,20,20,20]
    x2_offset_list          = [0,0,0,0]
    atten_2_list            = [0,0,0,0]
    wait_time_list          = [5,5,5,5]
    # beam_stop_x             = [-65,-65,-65,-65]
    beam_stop_y             = [-24,-24,-24,-24]
    ## beam_stop for GISAXS
    beam_stop_x             = [81.4,81.4, 81.4,81.4]


    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
        "beam_stop_x":beam_stop_x,
        "beam_stop_y":beam_stop_y,
        }


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    yield from bps.mv(geo.sh,-1)
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
    # beam_stop_x             = [-65,-65,-65,-65]
    beam_stop_y             = [-24,-24,-24,-24]
    ## beam_stop for GISAXS
    beam_stop_x             = [81.4,81.4, 81.4,81.4]



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
    det_saxs_y_list         = [0]
    det_saxs_y_offset_list  = [0]
    stth_list               = [0]
    exp_time_list           = [1]
    x2_offset_list          = [0]
    atten_2_list            = [2]
    wait_time_list          = [1]
    beam_stop_x             = [0]
    beam_stop_y             = [0]


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
    yield from bps.mv(geo.det_mode,2)
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


    
def gisaxs_scan1(name):
    det_saxs_y_list         = [0,0]
    det_saxs_y_offset_list  = [0,1]
    stth_list               = [0,0]
    exp_time_list           = [10,10] # [20,20]
    x2_offset_list          = [-0.4,0.4]
    atten_2_list            = [0,0]
    wait_time_list          = [5,5]
    beam_stop_x             = [0,0]
    # beam_stop_y             = [-20,-20]
    beam_stop_y             = [0,0]


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
    yield from bps.mv(geo.det_mode,2)
    # yield from beta_gid(2.3,0)
    yield from bps.mv(fp_saxs.y1,11,fp_saxs.y2,22)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.1)

    yield from bps.mv(abs2,5)


def xr_checks(detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(shutter,1) # open shutter
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_ih()  #Align the spectrometer  height
  #  yield from check_tth() #Align the spectrometer rotation angle
    #yield from check_sh_coarse(0.05,detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    # yield from check_sh_fine(0.05,detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affec

        # yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points