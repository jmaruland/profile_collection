'''
### by HZ, 2022-08-11
Step 0. Check the beam and shutter
    RE(shopen())
    Move absorbe to 5 by typing "%mov abs2 5"
    In Lamda Det. set Esposure Time to 1.0 s and Aquire Period to 1.2 s
Step 1. Sample height alignment
    RE(mabt(0,0,0)) # alpha_i = 0
    Open sshutter in bottom left of 12ID_geo
    Manually move "Table Y (sh)" up and down to cut the beam by viewing the direct beam in Lambda detector by pressing Aquire
    RE(set_sh(0)) # When the sample cut the beam
    RE(sample_height_set_fine_o())
Step 2: Check the flat area of the sample
    RE(mabt(1,1,0)) # alpha_i = 1
    Move absorbe to 3 by typing "%mov abs2 3"
    View the reflected beam in Lambda detector by pressing Aquire
        If the reflected beam is not in the center of the ROI2 (middle box), manually move "Smpl:X2" to move it the center
    RE(mabt(3,3,0)) # alpha_i = 3
    %mov abs2 1
    View the reflected beam in Lambda detector
        Munaully move "Smpl:X2" to find its range in which the reflected beam always remains in the ROI2
        (Need to open and close the shutter to protect the sample)
        (Every time move the "Smpl:X2", Need to wait for a few seconds to let vibrations go away)
    Use the middle point of the "Smpl:X2" range as the "sam_x2_pos" in the scripts below 
    Move absorbe to 5 by typing "%mov abs2 5" # Move back the abs2 to 5 if you need to check other settings

    After any adjustments to this macro file save by typing "Ctrl + s"


If you need to cancle an operation hit "Ctrl + c" wait for the program to stop then type "RE.abort()"
If you need to search for a command hit "Ctrl + r" and type any part of the command
#sets the dry helium valve opening (5 is the max)
def dry_he_on(value):
    yield from mov(flow2,value)

If XRF detector froze, restart ioc: in the ioc terminal, ctrl+x
restart bluesky: exit, bsui

'''

from pyrsistent import s
from sqlalchemy import false


def run_nwu():
    proposal_id("2022_3","308307_dutta")
    yield from bps.sleep(5)
    yield from shopen()
    # yield from he_on() # starts the He flow
    detector=lambda_det

    ### two trough (12mL small ones) in the center of the chamber
    ### they are next to each other
    samp_name_dict = {

         2: 'Sample27_water',
         1: 'Sample28_ODA_KI_0p2mM',

    }

    sam_x2_pos ={

        1:  42, # flat +/- 2 back
        2:  -70, # flat +/- 2 front

    }

    sam_sh_offset ={
        # 1: -24.29,
        # 2: -25.3,
        1: None,
        2: None,
    }

    xr_run_dict = {
        1: True,
        2: True,
        3: False,
    }

    xrf_run_dict = {
        1: True,
        2: True,
        3: False,
    }

    gisaxs_run_dict = {
        1: False,
        2: False,
        3: False,
    }

    sh_offset_dict = {
        1: True,
        2: True,
        3: False,
    }

    slit_hg_gisaxs = [0.3]

    run_cycle = 1
    for ii in range(run_cycle):
        runNum = ii+1

        for key in samp_name_dict:

            samp_name = samp_name_dict[key] # +f'_run{runNum}'
            samp_x2 = sam_x2_pos[key]
            yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos
            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)

            if sh_offset_dict[key] and sam_sh_offset[key] != None:
                print('Starting fast sample height set using offset position: %.2f'%sam_sh_offset[key])
                sh.user_offset.set(sam_sh_offset[key])
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                sam_sh_offset[key]=sh.user_offset.value
                print('Re-setting sh_offset to:', sh.user_offset.value)
            
            else:
                print('Starting full sample height set')
                yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1.5 to 1.5 with 41 points
                yield from sample_height_set_fine_o(detector=detector) #scan the detector arm height from -0.2 to 0.2 with 21 points
                sam_sh_offset[key]=sh.user_offset.value
                print('Setting sh_offset to:', sh.user_offset.value)


            if xrf_run_dict[key]:
                print('Starting XRF measurement')
                yield from bps.mv(S2.hg, 0.2)

                yield from xrf_scan1(samp_name)


            if xr_run_dict[key]:
                print('Starting XRR measurement')
                if key == 1:
                    samp_x2_offset = -2
                elif key ==2:
                    samp_x2_offset = 2

                yield from bps.mv(geo.stblx2,samp_x2+samp_x2_offset)  #move the  Sample Table X2 to xpos
                sh.user_offset.set(sam_sh_offset[key])
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                sam_sh_offset[key]=sh.user_offset.value
                print('Re-setting sh_offset to:', sh.user_offset.value)

                yield from one_xrr_new(samp_name,samp_x2+samp_x2_offset)

            # if xrf_run_dict[key]:
            #     print('Starting XRF measurement')
            #     yield from bps.mv(S2.hg, 0.2)
            #     yield from bps.mv(geo.stblx2,samp_x2+2)  #move the  Sample Table X2 to xpos

            #     sh.user_offset.set(sam_sh_offset[key])
            #     yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            #     sam_sh_offset[key]=sh.user_offset.value
            #     print('Re-setting sh_offset to:', sh.user_offset.value)

            #     yield from xrf_scan1(samp_name)

            if gisaxs_run_dict[key]:
                print('Starting GISAXS measurement')

                for kk,slit_hg in enumerate(slit_hg_gisaxs):
                    print('Slit horizontal gap is set to %.2f'%slit_hg)
                    yield from bps.mv(S2.hg, slit_hg)
                    yield from bps.mv(geo.stblx2,samp_x2-2)  #move the  Sample Table X2 to xpos
                    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
                    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                    yield from gisaxs_scan1(samp_name+f'slit_hg_{slit_hg}')

        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    print('Here is the sample height offsets after alignment:')
    print(sam_sh_offset)

    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    # yield from he_off()# stops the He flow
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
    yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)

   # yield from check_tth() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affect OFFSET
    yield from xr_scan1(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)

def one_xrr_new(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
 #   yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
 #   yield from bps.mv(block.y,xpos)  #move the  block to xpos
    yield from bps.mv(shutter,1) # open shutter
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
    #yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
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
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-1.5,1.5,19,per_step=shutter_flash_scan), local_peaks)
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
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)

def xr_scan1(name):
#14.4lkevev Qz to 0.65, more overlap
    alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72,  1.3,  1.9]
    alpha_stop_list =    [ 0.12, 0.20, 0.46, 0.80,  1.36,  2.0,  2.8]
    number_points_list = [   10,  11,    15,   11,    9,    8,    10]
    auto_atten_list =    [    5,   4,     3,    2,    1,    0,     0]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]
    exp_time_list =      [    5,   5,     5,    5,     5,   5,     5]
    precount_time_list=  [  0.1, 0.1,   0.1,  0.1,   0.1, 0.1,   0.1]
    wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  -0.5]
    x2_offset_stop_list= [    0,   0,     0,    0,     0, -0.5,   -2]
    block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]

 
# #      9.7kev Qz to 0.65, more overlap
#     alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  0.65,  0.9,  1.9,  2.9]
#     alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.1,  3.9]
#     number_points_list = [    8,   8,     8,    9,    9,   13,   13,   11]
#     auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,    0]
#     s2_vg_list =         [ 0.02, 0.02, 0.04,  0.04, 0.04, 0.04,0.04, 0.04]
#     exp_time_list =      [    5,   5,     5,    5,     5,    5,   5,    5]
#     precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,  0.1, 0.1,  0.1]
#     wait_time_list=      [    5,   5,     5,     5,    5,   5,    5,    5]
#     x2_offset_start_list=[    0,   0,     0,     0,    0,   0,   0.0, 0.0]
#     x2_offset_stop_list= [    0,   0,     0,     0,    0,   0,   0.0,   0]
#     block_offset_list=   [    0,   0,     0,     0,    0,   0,    0,    0]
  
    # alpha_start_list =   [ 0.9,  1.9,  2.9]
    # alpha_stop_list =    [ 2.1,  3.1,  3.9]
    # number_points_list = [  13,   13,   11]
    # auto_atten_list =    [   2,    1,    0]
    # s2_vg_list =         [ 0.04,0.04, 0.04]
    # exp_time_list =      [    5,   5,    5]
    # precount_time_list=  [  0.1, 0.1,  0.1]
    # wait_time_list=      [   5,    5,    5]
    # x2_offset_start_list=[   0,   0.0, 0.0]
    # x2_offset_stop_list= [   0,   0.0,   0]
    # block_offset_list=   [   0,    0,    0]  
    
    # #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.18, 0.30,  0.4,  0.7,  1.2,  2.0, 3.1]
    # alpha_stop_list =    [ 0.18, 0.30, 0.40,  0.8,  1.3,  2.0,  3.0, 3.9]
    # number_points_list = [    8,   5,     6,    5,    7,    9,   11,   5]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,   5,    5,  20]
    # precount_time_list=  [  0.1, 0.1,   0.1,  0.1,   0.1, 0.1,  0.1, 0.1]
    # wait_time_list=      [   15,  15,    15,   15,    15,  15,   15,  15]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  0.5, 1.5]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, 0.5,  1.5, 2.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,    0,   0]


    # #9.7kev for Aug022_ccny
    # alpha_start_list =   [ 0.04, 0.14, 0.24,  0.40,  0.65,  0.9,   1.9,  2.9]
    # alpha_stop_list =    [ 0.18, 0.28, 0.44,  0.72,  1.05,  2.1,   3.1,  3.8]
    # number_points_list = [    8,   8,     8,     9,    9,    19,    13,   10]
    # auto_atten_list =    [    7,   6,     5,     4,    3,     2,     1,    1]
    # s2_vg_list =         [ 0.02, 0.02, 0.04,   0.04, 0.04, 0.04,  0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,     5,    5,     5,     5,   10]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,   0.1,   0.1,  0.1]
    # wait_time_list=      [    7,   7,     7,     7,    7,     7,     7,    7]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,     0,  -0.2,  0.2]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,     0,  -1.7,  1.7]
    # block_offset_list=   [    0,   0,     0,     0,    0,     0,     0,    0]

    #     #9.7kev for Oct2022
    # alpha_start_list =   [ 0.04, 0.14, 0.24,  0.40,  0.65,  0.9,   1.9,  2.9]
    # alpha_stop_list =    [ 0.18, 0.28, 0.44,  0.72,  1.05,  2.1,   3.1,  3.8]
    # number_points_list = [    8,   8,     8,     9,    9,    19,    13,   10]
    # auto_atten_list =    [    7,   6,     5,     4,    3,     2,     1,    1]
    # s2_vg_list =         [ 0.02, 0.02, 0.04,   0.04, 0.04, 0.04,  0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,     5,    5,     5,     5,   10]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,   0.1,   0.1,  0.1]
    # wait_time_list=      [   10,  10,    10,    10,   10,    10,    10,   10]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,     0,  -0.2,  0.2]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,     0,  -1.7,  1.7]
    # block_offset_list=   [    0,   0,     0,     0,    0,     0,     0,    0]

    #         #9.7kev for Oct2022 reduced waiting time to 5 sec from 10 sec since there is glass
    # alpha_start_list =   [ 0.04, 0.14, 0.24,  0.40,  0.64,  0.9,   1.9,  2.9]
    # alpha_stop_list =    [ 0.18, 0.28, 0.44,  0.72,  1.00,  2.1,   3.1,  3.8]
    # number_points_list = [    8,   8,     6,     9,   10,    25,    13,   10]
    # auto_atten_list =    [    7,   6,     5,     4,    3,     2,     1,    1]
    # s2_vg_list =         [ 0.02, 0.05, 0.06,   0.06, 0.06, 0.08,  0.08, 0.08]
    # exp_time_list =      [    5,   5,     5,     5,    5,     5,     5,   10]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1,   0.1,   0.1,  0.1]
    # wait_time_list=      [   10,  10,    10,    10,   10,    10,    10,   10]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,     0,     0,    0]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,     0,     0,    0]
    # block_offset_list=   [    0,   0,     0,     0,    0,     0,     0,    0]


 
    # #9.7kev Qz to 0.65, for overlapping check_HZ
    # alpha_start_list =   [ 0.04, 0.14, 0.24, 0.40,  0.65, 0.95,  1.9, 2.9]
    # alpha_stop_list =    [ 0.18, 0.28, 0.44, 0.72,  1.05,  2.1,  3.1, 3.9]
    # number_points_list = [    8,   8,     8,    9,    9,   13,   13,   11]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,    0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,     5,    5,   5,    5,    5]
    # precount_time_list=  [  0.1, 0.1,   0.1,   0.1,  0.1, 0.1,  0.1,  0.1]
    # wait_time_list=      [   15,  15,    15,    15,   15,  15,   15,   15]
    # x2_offset_start_list=[    0,   0,     0,     0,    0,   0,    0,    0]
    # x2_offset_stop_list= [    0,   0,     0,     0,    0,   0,    0,    0]
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
    # #9.7kev
    # alpha_start_list =   [ 0.03, 0.11, 0.13, 0.25]
    # alpha_stop_list =    [ 0.10, 0.12, 0.23, 0.45]
    # number_points_list = [    8,    2,    6,    5]
    # auto_atten_list =    [    1,    1,    2,    2] 
    # s2_vg_list =         [ 0.02, 0.02, 0.02, 0.02] 
    # exp_time_list =      [   20,   10,   10,   10]
    # precount_time_list=  [  0.1,  0.1,  0.1,  0.1]
    # wait_time_list=      [    0,    0,    0,    0]
    # x2_offset_start_list=[  0.0,  0.0,  0.0,  0.0]
    # x2_offset_stop_list= [  0.0,  0.0,  0.0,  0.0]

    # #9.7kev
    # alpha_start_list =   [ 0.03, 0.11, 0.13, 0.15]
    # alpha_stop_list =    [ 0.10, 0.12, 0.14, 0.24]
    # number_points_list = [    8,    2,    2,    5]
    # auto_atten_list =    [    0,    0,    2,    2] 
    # s2_vg_list =         [ 0.02, 0.02, 0.02, 0.02] 
    # exp_time_list =      [   15,   10,   10,    5]
    # precount_time_list=  [  0.1,  0.1,  0.1,  0.1]%t
    # wait_time_list=      [    0,    0,    0,    0]
    # x2_offset_start_list=[  0.0,  0.0,  0.0,  0.0]
    # x2_offset_stop_list= [  0.0,  0.0,  0.0,  0.0]


     #14.4kev
    alpha_start_list =   [ 0.03, 0.09, 0.12]
    alpha_stop_list =    [ 0.08, 0.12, 0.24]
    number_points_list = [    6,    4,    7]
    auto_atten_list =    [    0,    1,    1] 
    s2_vg_list =         [ 0.01, 0.01, 0.01] 
    exp_time_list =      [   30,   30,   30]
    precount_time_list=  [  0.1,  0.1,  0.1]
    wait_time_list=      [   10,   10,   10]
    x2_offset_start_list=[  0.0,  0.0,  0.0]
    x2_offset_stop_list= [  0.0,  0.0,  0.0]






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
    yield from bps.mv(geo.det_mode,1)

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
    det_saxs_y_list         = [0, 0]
    det_saxs_y_offset_list  = [0, 1]
    stth_list               = [0, 0]
    exp_time_list           = [1, 1]
    x2_offset_list          = [0, 0]
    atten_2_list            = [3, 3]
    wait_time_list          = [1, 1]
    beam_stop_x             = [0, 0]
    beam_stop_y             = [0, 0]


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
    det_saxs_y_list         = [0]
    det_saxs_y_offset_list  = [0]
    stth_list               = [stth_0]
    exp_time_list           = [1]
    x2_offset_list          = [0]
    atten_2_list            = [6]
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



def gisaxs_scan1(name):
    det_saxs_y_list         = [0,0,30]
    det_saxs_y_offset_list  = [0,1,0]
    stth_list               = [0,0,0]
    exp_time_list           = [10,10,10] # [20,20]
    x2_offset_list          = [-0.4,0.4,-0.4]
    atten_2_list            = [1,1,1]
    wait_time_list          = [5,5,5]
    beam_stop_x             = [0,0,0]
    # beam_stop_y             = [-20,-20]
    beam_stop_y             = [0,0,0]


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