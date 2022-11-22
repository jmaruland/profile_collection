def test_kibron():

    # Bluesky command to start the document
    base_md = {'plan_name': 'kibron'}
    yield from bps.open_run(md=base_md)
    yield from bps.trigger_and_read([kibron], name='primary')
    yield from bps.close_run()


def test_xr_kibron(name,usekibron = True): 

       #9.7kev Qz to 0.65, more overlap
    alpha_start_list =   [ 0.04, 0.14, 0.26,  0.4,  0.7,  1.2,  1.8, 2.9]
    alpha_stop_list =    [ 0.18, 0.30, 0.44,  0.8,  1.3,  2.0,  3.0, 3.8]
    number_points_list = [    8,   9,    10,    9,    7,   9,   13,  10]
    auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   0]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,   5]
    precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1, 0.1]
    wait_time_list=      [    5,   5,     5,     5,    5,   5,    5,   5]
    x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0.5,  1.5]
    x2_offset_stop_list= [    0,   0,     0,     0,    0,   0.5, 1.5,  2.5]
    block_offset_list=   [    0,   0,     0,     0,    0,   0,    0,  0]
    
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
    yield from reflection_scan_full(scan_param=scan_p,usekibron = usekibron,
        md={'sample_name': name},
        detector=lambda_det, 
        tilt_stage=False,)



# 9.7 keV
def hzhang_june2022():
    proposal_id("2022_2","310472_zhang")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {

        # ### Spread monoalyer on 12mL water, 2022-06-10, 10:18pm
        # ### DNA-A, 120uL, P15 (very low!!!), DNA-B, 96uL, 31 (drop from 34), DNA-AB55, 80uL (no visible spreading)
        # 1: 'DSPE-DNA-AB55_Pxx', 
        # 2: 'DSPE-DNA-B_P31',
        # 3: 'DSPE-DNA-A_P15',

        # ### add NaCl to 200mM, 2022-06-11, 12:21am
        # ### DNA-A, 16 mN/m; DNA-B, 30 mN/m; DNA-AB55, pressure unknow
        # 1: 'DSPE-DNA-AB55_NaCl_Pxx', 
        # 2: 'DSPE-DNA-B_NaCl_P30',
        # 3: 'DSPE-DNA-A_NaCl_P16',

        # ### Spread monolayer on 12mL water, 2022-06-11, 12:53pm
        # ### DNA-A, 115uL, P15; DNA-B, 95uL, P17
        # # 1: 'DSPE-DNA-AB55_Pxx', 
        # 2: 'DSPE-DNA-A_prep2_P15',
        # 3: 'DSPE-DNA-B_prep2_P17',

        # ### Spread monolayer on 12mL 5nM DNA-AuNP, 2022-06-11, 3:31pm
        # ### back: DNA-B-NPs, 46uL DSPE-DNA-B prep-2, pressure up to 35, drop to 31
        # ### middle: DNA-A-NPs, 80uL DSPE-DNA-B, prep-1 (P~30 similar to previous run)
        # ### front: DNA-A-NPs, 48uL DSPE-DNA-A prep-2, pressure up to 34, drop to 30
        # 1: 'DSPE-DNA-B_prep2_NP-cB_P31', # repeat GID
        # 2: 'DSPE-DNA-B_prep1_NP-cA_Px', 
        # 3: 'DSPE-DNA-A_prep2_NP-cA_P30',

        # ### spread more DNA-B-prep2 (35uL) until no visible spreading, 2022-06-11, 5:43pm
        # 2: 'DSPE-DNA-B_prep1+2_NP-cA_Px', 

        ### add NaCl to 200mM, pressures are stable, 2022-06-11, 6:32pm
        ### open chamber, gently stir at 11:42pm
        # 1: 'DSPE-DNA-B_prep2_NP-cB_NaCl_P31', 
        # 2: 'DSPE-DNA-B_prep1+2_NP-cA_NaCl_Px', 
        # 3: 'DSPE-DNA-A_prep2_NP-cA_NaCl_P30',
        # ### continue running to 2022-06-12, 11:10am


        # ### Spread monolayer on 12mL 5nM DNA-AuNP, 2022-06-12, 1:24pm
        # ### back: DNA-A-NPs, 75uL DSPE-DNA-AB55 prep-2, pressure up to 35, drop to 31
        # ### middle: DNA-B-NPs, 75uL DSPE-DNA-A, prep-1 (P~30 similar to previous run)
        # ### front: DNA-A-NPs, 75uL DSPE-DNA-AB28 prep-2, pressure up to 34, drop to 31
        # ### Both pressures are stable and similar
        # 1: 'DSPE-DNA-AB55_prep2_NP-cA_P31', 
        # 2: 'DSPE-DNA-A_prep1_NP-cB_Px',  # control
        # 3: 'DSPE-DNA-AB28_prep2_NP-cA_P31',

        ### add NaCl to 200mM, pressures are 31 and 33, 2022-06-12, 2:23, 3:25 and 3:38pm
        ### open chamber and gently stir at 2022-06-13, 3:19am
        # 3: 'DSPE-DNA-AB28_prep2_NP-cA_NaCl_P31',  
        # 2: 'DSPE-DNA-A_prep1_NP-cB_NaCl_Px',  # control
        # 1: 'DSPE-DNA-AB55_prep2_NP-cA_NaCl_P31', 


        # ### Control samples, 2022-06-13, 6:08am
        # ### back: DNA-A-NPs, spread 75 uL pure solvent
        # ### middle: DEG+NPs, 3uL + 3uL (no spreading for the second 3uL)
        # ### front: DNA-A-NPs, inject NaCl to 200 mM
        # 1: 'control_NP-cA_solvent', 
        # 2: 'DEG_NPs', 
        3: 'control_NP-cA_NaCl',


    }

    sam_x2_dict ={

        1: 37, # flat from 34.5 to 39.5  #42, # (38, 5.1), # back
        2: -12.5, # flat from -15 to -10 # -9, # (-9, 3.5), # middle trough
        3: -62.5 +0.5, #flat from -65 to -60  #-65, #-62, # (-63.5,-6.14), # front

    }

    samp_run_dict = {
        
        1: True,
        2: True,
        3: True,

    }

    run_cycle = 2
    for ii in range(run_cycle):
        run = ii+2

        for key in samp_name_dict:
            if samp_run_dict[key]:
                samp_name = samp_name_dict[key]
                samp_x2 = sam_x2_dict[key]
                yield from one_xrr(samp_name+f'_run{run}',samp_x2)

                yield from bps.mv(geo.stblx2,samp_x2-0.5)  #move the  Sample Table X2 to xpos
                yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                yield from gisaxs_scan1(samp_name+f'_run{run}')

        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    yield from he_off()# stops the He flow
    yield from shclose()



def one_xrr(name,xpos,blocky=0, tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    # yield from bps.mv(block.y,blocky)  #move the  block to xpos
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
    # #9.7kev Qz to 0.566
    # alpha_start_list =   [ 0.04, 0.16, 0.24, 0.40,  0.7,  1.0,  2.0]
    # alpha_stop_list =    [ 0.16, 0.24, 0.40, 0.70,  1.0,  2.0,  3.3]
    # number_points_list = [    7,   6,     5,    7,    6,   21,   14]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,   1 ]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,  5 ]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1]
    # wait_time_list=      [    7,   7,     7,     7,    7,   7,   7 ]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0 ]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0,   0 ]

    # #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  0.65, 0.95,  1.9, 2.9]
    # alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.1, 3.8]
    # number_points_list = [    8,   8,     8,    9,    9,   23,   13,  10]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,   5]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1, 0.1]
    # wait_time_list=      [    5,   5,     5,     5,    5,   5,    5,   5]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0.5,  1.5]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0.5, 1.5,  2.5]
    # block_offset_list=   [    0,   0,     0,     0,    0,   0,    0,  0]

    # #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  0.65, 0.95,  1.9]
    # alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.3]
    # number_points_list = [    8,   8,     8,    9,    9,   23,   15]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   5]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1]
    # wait_time_list=      [    5,   5,     5,     5,    5,   5,    5]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0.45]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0.4,  1]
    # block_offset_list=   [    0,   0,     0,     0,    0,   0,    0]



    #9.7kev Add more points in low q
    alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  0.65, 0.95,  1.9]
    alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.3]
    number_points_list = [    8,  12,    12,    9,    9,   15,   15]
    auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04]
    exp_time_list =      [    5,   5,     5,    5,     5,    5,   5]
    precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1]
    wait_time_list=      [    5,   5,     5,     5,    5,   5,    5]
    x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0.45]
    x2_offset_stop_list= [    0,   0,     0,     0,    0,   0.4,  1]
    block_offset_list=   [    0,   0,     0,     0,    0,   0,    0]

    #     #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  0.65, 0.95,  1.9,  2.9]
    # alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.1,  3.8]
    # number_points_list = [    8,   8,     8,    9,    9,   23,   13,   10]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,    0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,    5]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1,  0.1]
    # wait_time_list=      [    5,   5,     5,     5,    5,   5,    5,    5]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0.1,-0.4]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0.1, 0.4,   0]
    # block_offset_list=   [    0,   0,     0,     0,    0,   0,    0,    0]


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