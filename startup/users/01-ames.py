# 9.7 keV
proposal_id("2022_1","30011_ames")
from pdb import post_mortem

#    "PNIPAM_3k_AuNPs_5",
#    "PNIPAM_6k_AuNPs_5",
#    "PNIPAM_3k_AuNPs_10",
#    "PNIPAM_6k_AuNPs_10"


sample_names =[
    "COOH_PEG5k_AuNP10_100mM_NaCl",
    "PEG5k_AuNP10_1mM_HCl",
    "PEG5k_AuNP10_1mM_NaOH",
    # "NH2_PEG5k_AuNP10_10mM_NaOH"
]0
sample_pos =[
  -77,
  -38.5,
   0,
#    37.6
]

def ames_m2():
    for i in range(len(sample_names)):
        if i == 0:
            yield from ames_1(sample_names[i],sample_pos[i])
        else:
            yield from ames_2(sample_names[i],sample_pos[i])


def ames_m():
    for i in range(len(sample_names)):
        yield from ames_1(sample_names[i],sample_pos[i])
  

def ames_2(name,pos):
    """
    Putting sleep(5) to allow time for opening and closing
    the Photon Shutter if this is really needed"""

    detector=lambda_det
    pos1=pos-1
    pos2=pos+1
    print(name,pos,pos1,pos2)
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
    # yield from one_xrr(name,pos)
    yield from check_ih()  #Align the spectrometer  height
   # yield from check_tth() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   
    yield from gisaxs_scan1(name+"_1",pos1)
    yield from gisaxs_scan1(name+"_2",pos2)
    yield from he_off()# stops the He flow
    yield from shclose()
    yield from bps.sleep(5)


def ames_1(name,pos):
    """
    Putting sleep(5) to allow time for opening and closing
    the Photon Shutter if this is really needed"""

    detector=lambda_det
    pos1=pos-1
    pos2=pos+1
    print(name,pos,pos1,pos2)
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
    yield from one_xrr(name,pos)
    yield from sample_height_set_fine_o(detector=detector)   
    yield from gisaxs_scan1(name+"_1",pos1)
    yield from gisaxs_scan1(name+"_2",pos2)
    yield from he_off()# stops the He flow
    yield from shclose()
    yield from bps.sleep(5)

def one_xrr(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)# reflectivity mode
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(shutter,1) # open shutter
    yield from check_ih()  #Align the spectrometer  height
   # yield from check_tth() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
    yield from xr_scan1(name)
    yield from bps.mv(shutter,0) # close shutter
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
    #9.7kev
    alpha_start_list =   [ 0.04, 0.16, 0.24, 0.40,  0.7,  1.5]
    alpha_stop_list =    [ 0.16, 0.24, 0.40, 0.70,  1.5,  2.0]
    number_points_list = [    7,   6,     9,   11,   17,   11]
    auto_atten_list =    [    7,   6,     5,    4,    3,    2]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04]
    exp_time_list =      [    5,   5,     5,    5,     5,    5]
    precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1]
    wait_time_list=      [    5,   5,     5,     5,    5,   5 ]
    x2_offset_start_list=[    0,   0,     0,     0,    0,   0 ]
    x2_offset_stop_list= [    0,   0,     0,     0,    0,   0 ]


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


def xr_scan2(name):
    #9.7kev
    alpha_start_list =   [ 0.04, 0.16, 0.24, 0.40,  0.7,  1.4,  2.0, 3.0 ]
    alpha_stop_list =    [ 0.16, 0.24, 0.40, 0.70,  1.4,  2.0,  3.0, 4.0 ]
    number_points_list = [    7,   6,    5,     7,    8,    7,   6 ,  6  ]
    auto_atten_list =    [    7,   6,    5,     4,    3,    2,    1,  0  ] 
    s2_vg_list =         [ 0.04, 0.04,0.04,  0.04, 0.04, 0.04,  0.04,0.04] 
    exp_time_list =      [    5,   5,    5,    5,     5,    5,   5,   5  ]
    precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1,  0.1, 0.1 ]
    wait_time_list=      [    7,   7,    7,     7,    7,   7,    7,   7  ]
    x2_offset_start_list=[    0,   0,    0,     0,    0,   0,  0,     0  ]
    x2_offset_stop_list= [    0,   0,    0,     0,    0,   0,  0,     0  ]


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

    
def gisaxs_scan1(name,xpos):
    det_saxs_y_list         = [0,0]
    det_saxs_y_offset_list  = [0,1]
    stth_list               = [0,0]
    exp_time_list           = [2,2]
    x2_offset_list          = [-0.2,0.2]
    atten_2_list            = [0,0]
    wait_time_list          = [5,6]
    beam_stop_x             = [0,0]
    beam_stop_y             = [-20,-20]


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
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from shopen()
    yield from beta_gid(1.8,0)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.1)


def gid_direct(name):
    det_saxs_y_list         = [0]
    det_saxs_y_offset_list  = [0]
    stth_list               = [0]
    exp_time_list           = [1]
    x2_offset_list          = [0]
    atten_2_list            = [5]
    wait_time_list          = [1]
    beam_stop_x             = [-10]
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
    yield from bps.mv(fp_saxs.y1,9,fp_saxs.y2,18)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.00)


