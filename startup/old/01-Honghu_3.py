# 14.4 keV
def cfn_Feb2022():
    '''
    Three troughs in a row; suphase: NP-A, water, NP-A, 12 mL
    lipid compositions: 100%A, 100%A, 100%B, 30uL


    '''
    proposal_id("2022_1","309161_zhang")

    # Run 1: 12 mL 5nM AuNPs, no lipid, no salt, load sample 9:12pm
    samp_name_dict = {
        # 1: 't1_NP-A_run1',
        # 2: 't2_Water_run1',
        # 3: 't3_NP-A_run1',

        # ## Run 2: spread lipid 100%A, 100%A, 100%B. 2pm, 2022-02-13; pressure 32.8, 36.5 mN/m.
        # 1: 't1_NP-A_lipid-A_run1',
        # 2: 't2_Water_lipid-A_run1',
        # 3: 't3_NP-A_lipid-B_run1',

        # ## Run 3: inject NaCl to 200 mM NaCl. 3:45pm, 2022-02-13; pressure 31.4, 35.8 mN/m.
        # 1: 't1_NP-A_lipid-A_NaCl_run1',
        # 2: 't2_Water_lipid-A_NaCl_run1',
        # 3: 't3_NP-A_lipid-B_NaCl_run1',

        # ## Run 4: keep running, x2-1 5:16pm, 2022-02-13; pressure 27.8, 32.1 mN/m.
        # 1: 't1_NP-A_lipid-A_NaCl_run2',
        # 2: 't2_Water_lipid-A_NaCl_run2',
        # 3: 't3_NP-A_lipid-B_NaCl_run2',

        # ## Run 5: keep running, x2+1 6:50pm, 2022-02-13; pressure 26.6, 31.0 mN/m.
        # 1: 't1_NP-A_lipid-A_NaCl_run3',
        # 2: 't2_Water_lipid-A_NaCl_run3',
        # 3: 't3_NP-A_lipid-B_NaCl_run3',

        # ## Run 6: keep running, x2-2  8:23pm, 2022-02-13; pressure 25.7, 30.1 mN/m. reduced points in xrr
        # 1: 't1_NP-A_lipid-A_NaCl_run4',
        # 2: 't2_Water_lipid-A_NaCl_run4',
        # 3: 't3_NP-A_lipid-B_NaCl_run4',

        ## Run 7: keep running, x2  9:21pm, 2022-02-13; pressure 25.3, 29.7 mN/m. reduced points in xrr
        1: 't1_NP-A_lipid-A_NaCl_run5',
        2: 't2_Water_lipid-A_NaCl_run5',
        3: 't3_NP-A_lipid-B_NaCl_run5',

    }

    detector=lambda_det
    yield from shopen()
    yield from he_on() # starts the He flow

    if False:
        #trough2, middle
        x2_trough2 = -12.5+1
        yield from one_xrr(samp_name_dict[2], x2_trough2)
        yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
        yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
        yield from gid_scan1(samp_name_dict[2]+'_gid')
        yield from gisaxs_scan1(samp_name_dict[2]+'_gisaxs')


    if True:
        #trough1, front
        x2_trough1 = -61.5-1 ### pressure 1
        yield from one_xrr(samp_name_dict[1], x2_trough1)
        yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
        yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
        # yield from gid_scan1(samp_name_dict[1]+'_gid')
        yield from gisaxs_scan1(samp_name_dict[1]+'_gisaxs')
    

    if True:
        ###trough3, back
        x2_trough3 = 34-1 # 34+1 ### pressure 2
        yield from one_xrr(samp_name_dict[3], x2_trough3)
        yield from det_exposure_time_new(detector, 1.0, 1.0)
        yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
        # yield from gid_scan1(samp_name_dict[3]+'_gid')
        yield from gisaxs_scan1(samp_name_dict[3]+'_gisaxs')

    yield from he_off()# stops the He flow
    yield from shclose()


def cfn_1():
    proposal_id("2022_1","309161_zhang")
    yield from shopen()
    #yield from he_on() # starts the He flow
    #yield from one_xrf("XFR_TbCl2_control_1mM_20220207",-51)
    yield from one_xrr("DMPG_80uL+ECGC(10ml)-ML_last+15hrs",-53)
    yield from he_off()# stops the He flow
    yield from shclose()

def cfn_2():
    proposal_id("2022_1","309161_zhang")
    yield from shopen()
    yield from he_on() # starts the He flow
    #  yield from one_xrf("KI_2mM_pH7,ODA,#3",17)
    yield from one_xrr("DMPG(105)_water",18)
    yield from gid_scan1("GDS_XRR_SF_Run_15_GID_20220206")
    #  yield from one_xrf("KBr_2mM_pH7,ODA,#1",-51)
    yield from one_ref("DMPG(105)_ECGC",-53)
    yield from gid_scan1("DMPG(105)_ECGC")
    yield from he_off() # stops the He flow



def one_xrr(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
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
    # #14.4kev
    # alpha_start_list =   [ 0.04, 0.14, 0.20, 0.40,  0.7,  1.2,  2.0]
    # alpha_stop_list =    [ 0.14, 0.20, 0.40, 0.70,  1.2,  2.0,  3.0]
    # number_points_list = [    6,   4,   11,     7,   11,    9,    6]
    # auto_atten_list =    [    6,   5,    4,     3,    2,    1,    1] 
    # s2_vg_list =         [ 0.03, 0.04,0.04,  0.04, 0.04, 0.04, 0.04] 
    # exp_time_list =      [   5,    5,    5,     5,    5,    5,    5]
    # precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1,  0.1]
    # wait_time_list=      [    7,   7,    7,     7,    7,   7,    7 ]
    # x2_offset_start_list=[    0,   0,    0,     0,    0,   0,   0.2]
    # x2_offset_stop_list= [    0,   0,    0,     0,    0,   0.2, 0.7]

    ## reduce hight angle for monitoring the in situ reaction
    alpha_start_list =   [ 0.04, 0.14, 0.20, 0.40,  0.7,  1.2]
    alpha_stop_list =    [ 0.14, 0.20, 0.40, 0.70,  1.2,  2.0]
    number_points_list = [    6,   4,   11,     7,   11,    9]
    auto_atten_list =    [    6,   5,    4,     3,    2,    1] 
    s2_vg_list =         [ 0.03, 0.04,0.04,  0.04, 0.04, 0.04] 
    exp_time_list =      [   5,    5,    5,     5,    5,    5]
    precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1]
    wait_time_list=      [    7,   7,    7,     7,    7,    7]
    x2_offset_start_list=[    0,   0,    0,     0,    0,    0]
    x2_offset_stop_list= [    0,   0,    0,     0,    0,  0.2]


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
    exp_time_list           = [20,20]
    x2_offset_list          = [-0.4,0.4]
    atten_2_list            = [0,0]
    wait_time_list          = [5,5]
    beam_stop_x             = [81.4,81.4]
    # beam_stop_y             = [-20,-20]
    beam_stop_y             = [-24,-24]


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
    yield from beta_gid(2.3,0)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.1)


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