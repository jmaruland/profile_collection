# for water 9.7 keV
def cfn_Dec2021():
    '''
    Three troughs in a row; lipid compositions: 100%, 0%, 20%
    With DNA-Au10 in the trough, 5nM
    12/12/21

    '''
    # # Run 1: 12 mL 5nM AuNPs, no lipid, no salt, 1:20 am, run at 2:00 am
    # samp_name_dict = {
    #     1: 'DSPE-DNA_100pc_water_run1',
    #     2: 'DSPE-DNA_0pc_water_run1',
    #     3: 'DSPE-DNA_20pc_water_run1',
    # }

    # # Run 2: spread lipid, spread 35 uL lipid at 3:30am, pressure up to 35, drop to 32-34, 
    # # run at 3:50am, 4:36am, 5:13am
    # samp_name_dict = {
    #     1: 'DSPE-DNA_20pc_water_run2',
    #     2: 'DSPE-DNA_0pc_water_run2',
    #     3: 'DSPE-DNA_100pc_water_run2',
    # }

    # Run 3: spread lipid, add NaCl to 300mM at 6:01am, pressure increase to 31 and 27 
    # samp_name_dict = {
    #     1: 'DSPE-DNA_20pc_water_run3', # un at 6:46am, p drop to 28, 25
    #     2: 'DSPE-DNA_0pc_water_run3',  # run at 6:07am, r
    #     3: 'DSPE-DNA_100pc_water_run3', # run at 7:25am, p drop t0 26, 25
    # }

    # Run 4: Continue runs
    # samp_name_dict = {
    #     1: 'DSPE-DNA_20pc_water_run4', # run at 8:42am, p drop to 25 25
    #     2: 'DSPE-DNA_0pc_water_run4',  # run at 8:03am, p drop to 25 25
    #     3: 'DSPE-DNA_100pc_water_run4', # run at 9:21am, p drop to 24 25
    # }

    # Run 5: move x2 -1, Continue runs
    samp_name_dict = {
        1: 'DSPE-DNA_20pc_water_run5', # run at 10:37am p stay at 24 25
        2: 'DSPE-DNA_0pc_water_run5',  # run at 9:59am, p stay at 24 25
        3: 'DSPE-DNA_100pc_water_run5', # run at 11:16am, p stay at 23 25
    }


    yield from shopen()
    #trough2, 0%
    # yield from bps.mv(block.y,-31.5) ### ???
    yield from bps.mv(x2,-10-1) ### no pressure
    yield from xr_checks_all()
    yield from xr_scan1(samp_name_dict[2])
    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from check_sh_fine(0.05,detector=detector)
    yield from gid_scan1(samp_name_dict[2])
    yield from gisaxs_scan1(samp_name_dict[2])

    #trough1, 20%
    # yield from bps.mv(block.y,-31.5) ### ???
    yield from bps.mv(x2,-60-1) ### pressure 2
    yield from xr_checks_all()
    yield from xr_scan1(samp_name_dict[1])
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_sh_fine(0.05,detector=detector)
    yield from gid_scan1(samp_name_dict[1])
    yield from gisaxs_scan1(samp_name_dict[1])

    ###trough3, 100%
    yield from bps.mv(block.y,9) ## ???
    yield from bps.mv(x2,33.5-1) ### pressure 1
    yield from xr_checks_all()
    yield from xr_scan1(samp_name_dict[3])
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_sh_fine(0.05,detector=detector)
    yield from gid_scan1(samp_name_dict[3])
    yield from gisaxs_scan1(samp_name_dict[3])

    yield from shclose()


def colorado():
    yield from shopen()
    #trough2
    yield from bps.mv(block.y,9)
    yield from bps.mv(x2,35)
    yield from xr_checks_all()
    yield from xr_scan1("POPC_pH=5-P=25_protein_3")
     #trough1
    yield from bps.mv(x2,-53)
    yield from xr_checks_all()
 #   yield from check_sh_coarse(0.05,detector=detector) 
  #  yield from check_sh_fine(0.05,detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    yield from bps.mv(block.y,-31.5)
    yield from xr_scan1("POPC_pH=7-P=25_protein_3")
    yield from shclose()

def day():
    yield from shopen()
    yield from bps.mv(x2,-43)
    yield from xr_checks()
    yield from xr_scan2("DMPG_50uL_1")
    yield from shclose()

#yield from mov("XF:12ID1-ES{Det:Lambda}cam1:OperatingMode",2)

def ref_s1():
#sample/position 1
        yield from bps.mv(x2,-57)
        yield from xr_checks_all()
        yield from xr_scan2("PFDA_100ppm_DI_1")

def ref_s2():
#sample/position 2
        yield from bps.mv(x2,-9)
        yield from xr_checks()
     #   yield from xr_scan2("PFDA_100ppm_0.1MCaCl_1")
     #   yield from xr_scan2("PFOS_300ppm_0.03MCaCl_1")
        yield from xr_scan2("PFDA_10ppm_DI_1")

def ref_s3():
#sample/position 3
        yield from bps.mv(x2,-9+38)
        yield from xr_checks_all()
        yield from xr_scan2("PFOS_5000ppm_0.1MCaCl_1")


def gid_s2():
        yield from (beta_gid(1.4,0)) 
        yield from gid_scan1("DMPG_50uL_4")
        yield from bps.mv(detsaxs.y, 0)



def xr_checks(detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(shutter,1) # open shutter
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_ih()  #Align the spectrometer  height
  #  yield from check_tth() #Align the spectrometer rotation angle
    #yield from check_sh_coarse(0.05,detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from check_sh_fine(0.05,detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affec


def xr_checks_all(detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(shutter,1) # open shutter
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_ih()  #Align the spectrometer  height
    #yield from check_tth() #Align the spectrometer rotation anglebeta_gid
    yield from check_sh_coarse(0.05,detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from check_sh_fine(0.05,detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affec



def xr_scan1(name):
    #9.7kev
    alpha_start_list =   [ 0.04, 0.16, 0.30, 0.50,  0.8,  1.0,  1.5]
    alpha_stop_list =    [ 0.16, 0.30, 0.50, 0.80,  1.0,  1.5,  3.9]
    number_points_list = [    7,   8,    6,     7,    6,   11,   16]
    auto_atten_list =    [    6,   5,    4,     3,    2,    1,    0] 
    s2_vg_list =         [ 0.03, 0.03,0.03,  0.03, 0.03, 0.03,  0.03] 
    exp_time_list =      [   10,  10,   10,    10,   10,   10,  10 ]
    precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1,  0.1]
    wait_time_list=      [    5,    5,   5,     5,    5,    5,   5 ]
    x2_offset_start_list=[    0,   0,    0,     0,    0,   0,   0.2]
    x2_offset_stop_list= [    1,   0,    0,     0,    0,   0.2,  0.7]


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
    alpha_start_list =   [ 0.04, 0.16, 0.30, 0.50,  0.8,  1.0,  1.5]
    alpha_stop_list =    [ 0.16, 0.30, 0.50, 0.80,  1.0,  1.5,  3.9]
    number_points_list = [    7,   8,    6,     7,    3,   11,   15]
    auto_atten_list =    [    6,   5,    4,     3,    2,    1,    0] 
    s2_vg_list =         [0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04] 
    exp_time_list =      [    4,   4,    4,     4,    4,    4,   4 ]
    precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1,  0.1]
    wait_time_list=      [    4,   4,    4,     4,    4,    4,   4 ]
    x2_offset_start_list=[    0,   0,    0,     0,    0,   0,   0.1]
    x2_offset_stop_list= [    0,   0,    0,     0,    0,   0,   0.1]



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
    yield from mabt(0.2,0.2,0)


# print_summary(gid_scan1('bob'))

def gid_scan1(name):
    det_saxs_y_list         = [-20,-20,65,65]
    det_saxs_y_offset_list  = [0,1,0,1]
    stth_list               = [16,16,16,16]  # [17,17,17,17]
    exp_time_list           = [20,20,20,20]
    x2_offset_list          = [-0.6,-0.2,0.2,0.4]
    atten_2_list            = [0,0,0,0]
    wait_time_list          = [5,5,5,5]
    beam_stop_x             = [81.7,81.7,81.7,81.7]
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
    yield from beta_gid(1.3,0)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.1)


    
def gisaxs_scan1(name):
    det_saxs_y_list         = [0,0]
    det_saxs_y_offset_list  = [0,1]
    stth_list               = [0,0]
    exp_time_list           = [20,20]
    x2_offset_list          = [-0.4,0.4]
    atten_2_list            = [0,0]
    wait_time_list          = [5,5]
    beam_stop_x             = [81.7,81.7]
    beam_stop_y             = [24,24]


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


# ### need to modify the beta_gid function to below
# detector = lambda_det
# def beta_gid(beta1,beta_off):
#                              ...:     y1=650*np.deg2rad(beta1+beta_off)
#                              ...:     y2=1333*np.deg2rad(beta1+beta_off)
#                              ...:  #   y3=1500*np.deg2rad(beta1)
#                              ...:  #   yield from bps.mv(fp_saxs.y1,y1,fp_saxs.y2,y2,detsaxs.y,y3)
#                              ...:     yield from bps.mv(fp_saxs.y1,y1,fp_saxs.y2,y2)


# use a quick scan to check q range
def gid_scan1_quick(name):
    det_saxs_y_list         = [-20,-20,65,65]
    det_saxs_y_offset_list  = [0,1,0,1]
    stth_list               = [16,16,16,16]
    exp_time_list           = [1,1,1,1]
    x2_offset_list          = [-0.6,-0.2,0.2,0.4]
    atten_2_list            = [0,0,0,0]
    wait_time_list          = [5,5,5,5]
    beam_stop_x             = [81.7,81.7,81.7,81.7]
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
    yield from beta_gid(1.3,0)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.1)