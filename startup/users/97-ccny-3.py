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
# run RE(sample_height_set_fine_o()) to fine the exact sh
# set title below for ccny_1
# run cntrl S to save the file
# from blue sky you need to reread the macro
# %run -i .ipython/profile_collection/startup/users/97-ccny-3.py
# RE(ccny_1())

#if the direct beam is not in the middle of the center box (up down) this means that astth is off.
#mov astth by hand using the screen, counting at each time till it is in the middle of the box
#RE(set_astth(22.566))

#from a terminal screen
#conda activate smi_analysis
#jupyter notebook

def ccny_1():
    proposal_id("2022_2","309891_tu")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {
        
#        2: '10wtSiNP-1pt5mMCTAB_2',
        #2: '10wtSiNP-1pt5mMCTAB_50uL_c16_1em3',
        #2: '10wtSiNP-2mMCTAB_1',
        #2: '10wtSiNP-2mMCTAB_50uL_c16_1em3',
        #2: 'SF_5x_82uL_smalltrough_1',
        #2: 'SF_5x_82uL_smalltrough_5compress',

        # 1: 'TbCl_in_PIPES_1mM', 
        # 2: 'PIPES_only',


        # 1: 'BR-WT10uM_Tb0p7mM_45min_wait', # 
        # 2: 'BR-Leu10uM_Tb0p7mM_45min_wait',

        # 1: 'BR-WT5uM_Tb0p35mM_45min_wait', # 
        # 2: 'BR-WT2uM_Tb0p14mM_45min_wait', #

        # #### The 2nd runs of the previous samples at the same spots have radiation damage.
        # #### modify the code to use fresh area for each run


        1: 'BR-WT20uM_Tb1p4mM_45min_wait', ### The absorber 2 is off a lot for these two scans, %mov abs2 1.15, set to 0.5
        2: 'BR-Leu20uM_Tb1p4mM_45min_wait', ###


    }

    sam_x2_dict ={
        # 1: 37, # flat from 34.5 to 39.5  #42, # (38, 5.1), # back
        # 2: -43, # flat from -15 to -10 # -9, # (-9, 3.5), # middle trough
        # 3: -64, #flat from -65 to -60  #-65, #-62, # (-63.5,-6.14), # front

        1: 18.2, # (16,20.5), # back
        2: -32.5, # (-35, -30), # front
    }

    samp_run_dict = {
        
        1: True,
        2: True,
        # 3: False,

    }

    run_cycle = 2
    for ii in range(run_cycle):
        run = ii+1

        for key in samp_name_dict:
            if samp_run_dict[key]:
                samp_name = samp_name_dict[key]
                samp_x2 = sam_x2_dict[key]+ii*2.2 ## Move by 2.2mm for 2nd runs (each run spans 2mm)
                yield from one_xrr(samp_name+f'_run{run}',samp_x2)
                yield from bps.mv(geo.stblx2,samp_x2+0.5)  #move the  Sample Table X2 to xpos
                yield from det_exposure_time_new(detector, 1.0, 1.0) # reset exposure time to 1s
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                # yield from gisaxs_scan1(samp_name+f'_run{run}')
                yield from xrf_scan1(samp_name+f'_xrf1_run{run}')
                yield from xrf_scan2(samp_name+f'_xrf2_run{run}')


                # print("Starting waiting for 5 min...")  
                # yield from bps.sleep(5*60)


    yield from det_exposure_time_new(detector, 1.0, 1.0) # reset exposure time to 1s
    yield from bps.mv(abs2,5)

    yield from he_off()# stops the He flow
    yield from bps.mv(geo.det_mode,1)
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
    number_points_list = [    8,   8,     8,    9,    9,   23,   13,   10]
    auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,    0]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04, 0.04]
    exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,    5]
    precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1,  0.1]
    wait_time_list=      [    5,   5,     5,     5,    5,    5,   5,    5]
    x2_offset_start_list=[    0,   0,     0,     0,    0,   0,    0,-0.75]
    x2_offset_stop_list= [    0,   0,     0,     0,    0,   0, -0.7, -2.0]
    block_offset_list=   [    0,   0,     0,     0,    0,   0,    0,    0]

    # #9.7kev Qz to 0.04-0.19 to check beam damage
    # alpha_start_list =   [ 0.24, 0.40, 0.65]
    # alpha_stop_list =    [ 0.44, 0.72, 1.05]
    # number_points_list = [ 8,    9,    9   ]
    # auto_atten_list =    [ 5,    4,    3   ]
    # s2_vg_list =         [ 0.04, 0.04, 0.04]
    # exp_time_list =      [ 5,    5,    5   ]
    # precount_time_list=  [ 0.1,  0.1,  0.1 ]
    # wait_time_list=      [ 5,    5,    5   ]
    # x2_offset_start_list=[ 0,    0,    0   ]
    # x2_offset_stop_list= [ 0,    0,    0   ]
    # block_offset_list=   [ 0,    0,    0   ]





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
   # alpha_start_list =   [ 0.04, 0.14]
   # alpha_stop_list =    [ 0.12, 0.34]
   # number_points_list = [    5,   11]
   # auto_atten_list =    [   1,    2] 
   # s2_vg_list =         [ 0.04, 0.04] 
   # exp_time_list =      [   8,   8]
   # precount_time_list=  [  0.1, 0.1]
   # wait_time_list=      [   10,   10]
   # x2_offset_start_list=[   0.8,   0.8]
   # x2_offset_stop_list= [   0.8,   0.8]

      #9.7kev
   # alpha_start_list =   [ 0.04, 0.24]
   # alpha_stop_list =    [ 0.22, 0.34]
   # number_points_list = [    11,   5]
   # auto_atten_list =    [   2,    3] 
   # s2_vg_list =         [ 0.04, 0.04] 
   # exp_time_list =      [   8,   8]
   # precount_time_list=  [  0.1, 0.1]
   # wait_time_list=      [   10,   10]
   # x2_offset_start_list=[   0.8,   0.8]
   # x2_offset_stop_list= [   0.8,   0.8]


    alpha_start_list =   [0.03]
    alpha_stop_list =    [0.33]
    number_points_list = [  16]
    auto_atten_list =    [   2] #[   0,  0] 
    s2_vg_list =         [0.04] 
    exp_time_list =      [8   ]
    precount_time_list=  [0.1 ]
    wait_time_list=      [10  ]
    x2_offset_start_list=[ 0.8]
    x2_offset_stop_list= [ 0.8]



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



def xrf_scan2(name):
    # 9.7kev
    alpha_start_list =   [ 0.04, 0.14]
    alpha_stop_list =    [ 0.12, 0.34]
    number_points_list = [    5,   11]
    auto_atten_list =    [    1,    2] 
    s2_vg_list =         [ 0.04, 0.04] 
    exp_time_list =      [   8,     8]
    precount_time_list=  [  0.1,  0.1]
    wait_time_list=      [   10,   10]
    x2_offset_start_list=[   0.8, 0.8]
    x2_offset_stop_list= [   0.8, 0.8]
    
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