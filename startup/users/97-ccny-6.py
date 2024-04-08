'''
### by HZ, 2022-08-11
Step 0. Check the beam and shutter
    RE(shopen())
    Move absorber to 5 by typing "%mov abs2 5"
    In Lamda Det. set Esposure Time to 1.0 s and Aquire Period to 1.2 s
Step 1. Sample height alignment
    RE(mabt(0,0,0)) # alpha_i = 0
    Open shutter in bottom left of 12ID_geo
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
        Manully move "Smpl:X2" to find its range in which the reflected beam always remains in the ROI2
        (Need to open and close the shutter to protect the sample)
        (Every time move the "Smpl:X2", Need to wait for a few seconds to let vibrations go away)
    Use the middle point of the "Smpl:X2" range as the "sam_x2_pos" in the scripts below 
    Move absorber to 5 by typing "%mov abs2 5" # Move back the abs2 to 5 if you need to check other settings

    After any adjustments to this macro file save by typing "Ctrl + s"


If you need to cancel an operation hit "Ctrl + c" wait for the program to stop then type "RE.abort()"
If you need to search for a command hit "Ctrl + r" and type any part of the command
#sets the dry helium valve opening (5 is the max)
def dry_he_on(value):
    yield from mov(flow2,value)

def dry_he_off(value):
    yield from mov(flow2,0.0)

'''  
# proposal_id("2023_1","311781_tu")
#proposal_id("2023_2","310747_tu")


from pyrsistent import s


def run_ccny():

    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)

    # proposal_id("2023_1","311781_tu")
    # yield from bps.sleep(5)
    # yield from shopen()
    # yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {

        # 1: 'Tb_20mM_ref', # front, 13mL + 1mL
        # 2: 'GA_50mM',  # -18.5 to -21
        # 3: 'Water',  # back
        # 3: 'LBT1-3_Tb_GA_1400uL', # 5:35am 06/08/2023
        # 1: 'La_20mM'True
        #1: 'LBT100La400GA5mM',
        #1: 'LBT100Tb400GAp5mM',
        #1: 'LBT100Tb400GA1mM',
        #1: 'LBT100Tb400GA5mM',
        #1: 'Tb_20mM',
        #1: 'Tb_20mM_run2',
        1: '3mMKBr_3.7pH_ODA_12mN',

    }

    sam_x2_pos ={
   
        # 1: -60.5,  # -68, # -16-54,
        # 2: -10.5,  # -19,
        # 3:  40.5,  #  42, # -19+54, back
        #1: -17.5,
         #1: -16,
         1: -12,
    }

    sam_sh_offset ={
        1: -26.3,
        2: -26.3,
        3: -26.3,
    }

    xr_run_dict = {
        1: False,
        2: False,
        3: False,
    }

    gid_run_dict = {
        1: False,
        2: False,
        3: False,
    }
    xrf_run_dict = {
        1: True,
        2: False,
        3: False,
    }

    gisaxs_run_dict = {
        1: False,
        2: False,
        3: False,
    }

    sh_offset_dict = {
        1: False,
        2: False,
        3: False,
    }

    slit_hg_gisaxs = [0.3]

    run_cycle = 1
    for ii in range(run_cycle):
        runNum = ii+1

        for key in samp_name_dict:

            # if key == 2: # for the 2nd run
            #     runNum == runNum+1

            samp_name = samp_name_dict[key] # +f'_run{runNum}'
            samp_x2 = sam_x2_pos[key]
            # yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos
            # try:
            #     yield from bps.mv(block.y,samp_x2-5)
            # except:
            #     print('beam block is not connected.')
            
            yield from det_set_exposure([detector,quadem], exposure_time=1, exposure_number = 1)
            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)

            if sh_offset_dict[key]:
                print('Starting fast sample height set using offset position')
         #       sh.user_offset.set(sam_sh_offset[key]) 
            #    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            else:
                print('Starting full sample height set')
            #    yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                sam_sh_offset[key]=sh.user_offset.value
                print('Setting sh_offset to',sh.user_offset.value)

            if xr_run_dict[key]:
                print('Starting XRR measurement')
                yield from one_xrr_new(samp_name)
                # for kk in range(10):
                #     yield from one_xrr_new(samp_name+f'_radiation_run{kk+1}',samp_x2)
                # if key == 2:
                #     yield from one_xrr_new1(samp_name)
                # elif key == 3:
                #     yield from one_xrr_new2(samp_name)

            if xrf_run_dict[key]:
                print('Starting XRF measurement')
                # if key == 2:
                    # x2_off = 0
                # elif key == 3:
                    # x2_off = -2
                x2_off = -2
                yield from bps.mv(geo.stblx2,samp_x2+x2_off)  #move the  Sample Table X2 to xpos
                yield from bps.mv(S2.vg, 0.02)
                yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
                yield from bps.mv(shutter,1) # open shutter
                yield from sample_height_set_fine_o_xrf(sh_offset =-0.000, detector=detector)   #scan 
                yield from xrf_scan1(samp_name)

            if gisaxs_run_dict[key]:
                print('Starting GISAXS measurement')

                for kk,slit_hg in enumerate(slit_hg_gisaxs):
                    print('Slit horizontal gap is set to %.2f'%slit_hg)
                    yield from bps.mv(S2.hg, slit_hg)
                    yield from bps.mv(S2.vg, 0.02) # added the vertical gap for gisaxs
                    yield from bps.mv(geo.stblx2,samp_x2-1)  #move the  Sample Table X2 to xpos
                    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
                    yield from bps.mv(shutter,1) # open shutter
                    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                    yield from gisaxs_scan1(samp_name+f'slit_hg_{slit_hg}')


            if gid_run_dict[key]:
                print('Start gid_soller measurements')
                yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
                 
                yield from bps.mv(geo.stblx2,samp_x2+3)
                yield from bps.mv(block.y,samp_x2-2)
                yield from sample_height_set_fine_o(detector=detector) 
                yield from bps.mv(block.y,samp_x2+3)
                yield from gid_soller1(samp_name)


            yield from det_set_exposure([detector,quadem], exposure_time=1, exposure_number = 1)
        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    # yield from he_off()# stops the He flow
    # yield from shclose()


def one_xrr_new1(name,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
 #   yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
 #   yield from bps.mv(block.y,xpos)  #move the  block to xpos
    yield from bps.mv(shutter,1) # open shutter
    # yield from xr_scan1(name)
    yield from ref_scan_new1(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)


def ref_scan_new1(name):
    '''test the new ref scans, 2023-06-01
    scan_param with the order of:
    alpha_start, alpha_stop, number_points, atten_2, exp_time, wait_time, precount_time, s2_vg, x2_offset_start, x2_offset_stop
    '''
    scan_params = {
#    scan:   a_0,  a_1, num, att, exp, wait, pre, s2vg, x2_0, x2_1
        0: [0.03, 0.13,  11,   6,  10,   10, 0.2, 0.04,    0,   0],
        1: [0.12, 0.22,  11,   5,  10,   10, 0.2, 0.04,    0,   0],
        2: [0.20, 0.42,  12,   4,  10,   10, 0.2, 0.04,    0,   0],
        3: [0.40, 0.80,  11,   3,  10,   10, 0.2, 0.04,    0,   0],
        4: [0.72, 1.60,  12,   2,  10,   10, 0.2, 0.04,    0,   0],
        5: [1.52, 2.40,  12,   1,  20,   10, 0.2, 0.04,    0,   0],
        6: [2.40, 3.00,   7,   0,  20,   10, 0.2, 0.04,    0,   0],

    }
    yield from bps.mv(geo.det_mode,1)
    print(scan_params)
    yield from ref_scan_multi(scan_params=scan_params, md={'sample_name': name})


def one_xrr_new2(name,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
 #   yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
 #   yield from bps.mv(block.y,xpos)  #move the  block to xpos
    yield from bps.mv(shutter,1) # open shutter
    # yield from xr_scan1(name)
    yield from ref_scan_new2(name)
    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)


def ref_scan_new2(name):
    '''test the new ref scans, 2023-06-01
    scan_param with the order of:
    alpha_start, alpha_stop, number_points, atten_2, exp_time, wait_time, precount_time, s2_vg, x2_offset_start, x2_offset_stop
    '''
    scan_params = {
#    scan:   a_0,  a_1, num, att, exp, wait, pre, s2vg, x2_0, x2_1
        0: [0.03, 0.13,  11,   6,  10,   10, 0.2, 0.04,    0,   0],
        1: [0.12, 0.22,  11,   5,  10,   10, 0.2, 0.04,    0,   0],
        2: [0.20, 0.42,  12,   4,  10,   10, 0.2, 0.04,    0,   0],
        3: [0.40, 0.80,  11,   3,  10,   10, 0.2, 0.04,    0,   0],
        4: [0.72, 1.60,  12,   2,  10,   10, 0.2, 0.04,    0,   0],
        5: [1.52, 2.40,  12,   1,  20,   10, 0.2, 0.04,    0,   0.5],
        6: [2.40, 2.80,   5,   1,  20,   10, 0.2, 0.04,    0.7, 2.5],


    #  #14.4kev for running kibron, keep 1 abs for BRoll
    # alpha_start_list =   [ 0.03, 0.12, 0.20, 0.40,  0.72, 1.52,  2.5]
    # alpha_stop_list =    [ 0.13, 0.22, 0.42, 0.80,  1.60,  2.4,  3.0]
    # number_points_list = [   11,   11,   12,   11,    12,   12,    6]
    # auto_atten_list =    [    6,    5,    4,    3,     2,    1,    1]
    # s2_vg_list =         [ 0.04, 0.04, 0.06,  0.06, 0.08, 0.08, 0.08]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   15]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    # wait_time_list=      [    5,   5,     5,    5,     5,   10,   10]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,    0,  0.7]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,  0.5,  2.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]


    }
    yield from bps.mv(geo.det_mode,1)
    print(scan_params)
    yield from ref_scan_multi(scan_params=scan_params, md={'sample_name': name})


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

def one_xrr_new(name,tiltx=0,detector=lambda_det):
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
    yield from bps.mv(abs2,6)
    yield from mabt(0.05,0.05,0)
    tmp1=geo.sh.position
    print('Start the height scan before GID')
    Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]
    # yield from det_exposure_time_new(detector, 1,1)
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-1.5,1.5,40,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)



def sample_height_set_fine_o(value=3,detector=lambda_det):
    geo.sh.user_readback.kind = 'hinted'
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
    yield from mabt(0.05,0.05,0)
    tmp1=geo.sh.position
    print('Start the height scan')
    Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)


def sample_height_set_fine_o_xrf(sh_offset = 0.008, value=3,detector=lambda_det):
    geo.sh.user_readback.kind = 'hinted'
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,5)
    yield from mabt(0.05,0.05,0)
    tmp1=geo.sh.position
    print('Start the height scan')
    Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    #yield from bps.mv(sh,tmp2-0.00)
    #yield from set_sh(tmp1)
    yield from bps.mv(sh,tmp2-0.00)
    # yield from set_sh(tmp1-0.008)
    yield from set_sh(tmp1-sh_offset)
    Msg('reset_settle_time', sh.settle_time, 0)




def xr_scan1(name):
 
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

    # #9.7kev for Oct2022 reduced waiting time to 5 sec from 10 sec since there is glass
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


     #14.4kev for running kibron, keep 1 abs for BRoll
    alpha_start_list =   [ 0.03, 0.12, 0.20, 0.40,  0.72,  1.6]
    alpha_stop_list =    [ 0.13, 0.22, 0.42, 0.80,  1.60,  2.4]
    number_points_list = [   11,   11,   12,   11,    12,    9]
    auto_atten_list =    [    5,    4,    3,    2,     1,    1]
    s2_vg_list =         [ 0.04, 0.04, 0.06,  0.06, 0.08, 0.08]
    exp_time_list =      [    5,   5,     5,    5,     5,   20]
    precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2]
    wait_time_list=      [   8,    8,     8,    8,     8,   8 ]
    x2_offset_start_list=[    0,   0,     0,    0,     0,  0.5]
    x2_offset_stop_list= [    0,   0,     0,    0,    0.5, 2.5]
    block_offset_list=   [    0,   0,     0,    0,     0,    0]


    # #14.4kev for running kibron, keep 1 abs for 5nm AuNPs
    # alpha_start_list =   [ 0.03, 0.12, 0.20, 0.40,  0.72, 1.52,  2.5]
    # alpha_stop_list =    [ 0.13, 0.22, 0.44, 0.80,  1.60,  2.4,  3.0]
    # number_points_list = [   21,   21,   17,   17,    12,   12,    6]
    # auto_atten_list =    [    6,    5,    4,    3,     2,    1,    1]
    # s2_vg_list =         [ 0.04, 0.04, 0.06,  0.06, 0.08, 0.08, 0.08]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   20]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    # wait_time_list=      [   10,  10,    10,   10,    10,   10,   10]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,    0,  0.7]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,  0.5,  2.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]





    # #14.4kev for testing exposure time and reverse mode
    # alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72,  1.7,  2.6]
    # alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,   1.7,  2.5,  3.0]
    # #number_points_list = [  21,   21,   15,   11,    9,    7,    11]
    # number_points_list = [   11,   11,   15,   11,   23,   13,    5]
    # # number_points_list = [   3,   3,   3,   3,      3,     3,    3] # for code testing, HZ, Feb2023
    # auto_atten_list =    [    6,    5,    4,    3,    2,    1,     1]
    # s2_vg_list =         [ 0.04, 0.04, 0.06,  0.06, 0.08, 0.08, 0.08]
    # exp_time_list =      [   5,   5,     5,    5,     5,    5,    40]
    # #exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    # wait_time_list=      [   10,  10,    10,   10,    10,   15,   20]
    # # wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]
    # # wait_time_list=      [1 for _ in range(len(alpha_start_list))] # for code testing, HZ
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  -0.5]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, -0.5,   -2]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]

 







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

    # #14.4kev
    # alpha_start_list =   [ 0.03, 0.09, 0.15]
    # alpha_stop_list =    [ 0.08, 0.15, 0.24]
    # number_points_list = [    6,    7,    5]
    # auto_atten_list =    [    1,    2,    2] 
    # s2_vg_list =         [ 0.02, 0.02, 0.02] 
    # exp_time_list =      [   15,   5,    5]
    # precount_time_list=  [  0.1,  0.1,  0.1]
    # wait_time_list=      [    3,    3,    3]
    # x2_offset_start_list=[  0.0,  0.0,  0.0]
    # x2_offset_stop_list= [  0.0,  0.0,  0.0]

    alpha_start_list =   [ 0.036, 0.09,0.15]
    alpha_stop_list =    [ 0.08,  0.15,0.19]
    number_points_list = [   12,    13,   3]
    auto_atten_list =    [    0,    2,    2] 
    s2_vg_list =         [ 0.02, 0.02, 0.02] 
    exp_time_list =      [   5,     5,    5]
    precount_time_list=  [  0.2,  0.2,  0.2]
    wait_time_list=      [   5,    5,    5 ]
    x2_offset_start_list=[ -2.5,  0.0,  0.0]
    x2_offset_stop_list= [ -0.5,  0.0,  0.0]




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
  #  yield from bps.mv(abs3,1)
    yield from reflection_fluorescence_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=xs, 
        tilt_stage=False,)
    yield from bps.mv(abs3,0)



def xrf_scan2(name):

    alpha_start_list =   [ 0.036]
    alpha_stop_list =    [ 0.08]
    number_points_list = [   12]
    auto_atten_list =    [    0] 
    s2_vg_list =         [ 0.02] 
    exp_time_list =      [   2]
    precount_time_list=  [  0.2]
    wait_time_list=      [   2]
    x2_offset_start_list=[ 0]
    x2_offset_stop_list= [ 0]






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
  #  yield from bps.mv(abs3,1)
    yield from reflection_fluorescence_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=xs, 
        tilt_stage=False,)
    yield from bps.mv(abs3,0)

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



# def gisaxs_scan1(name):
#     det_saxs_y_list         = [0,0,30]
#     det_saxs_y_offset_list  = [0,1,0]
#     stth_list               = [0,0,0]
#     exp_time_list           = [10,10,10] # [20,20]
#     x2_offset_list          = [-0.4,0.4,-0.4]
#     atten_2_list            = [1,1,1]
#     wait_time_list          = [5,5,5]
#     beam_stop_x             = [0,0,0]
#     # beam_stop_y             = [-20,-20]
#     beam_stop_y             = [0,0,0]


#     scan_dict={"det_saxs_y":det_saxs_y_list,
#         "det_saxs_y_offset":det_saxs_y_offset_list,
#         "stth":stth_list,
#         "exp_time":exp_time_list,
#         "x2_offset":x2_offset_list,
#         "atten_2":atten_2_list,
#         "wait_time":wait_time_list,
#         "beam_stop_x":beam_stop_x,
#         "beam_stop_y":beam_stop_y,}


# #mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
#     yield from bps.mv(geo.det_mode,2)
#     # yield from beta_gid(2.3,0)
#     yield from bps.mv(fp_saxs.y1,11,fp_saxs.y2,22)
#     print("calling GID_stitch")
#     yield from gid_scan_stitch(scan_dict,
#                                 md={'sample_name': name}, 
#                                 detector = pilatus300k,
#                                 alphai = 0.1)

#     yield from bps.mv(abs2,5)



def gisaxs_scan1(name):
    '''For Luis's AuNPs 5nm'''
    det_saxs_y_list         = [0,0]
    det_saxs_y_offset_list  = [0,1]
    stth_list               = [0,0]
    exp_time_list           = [10,10] # [20,20]
    x2_offset_list          = [-0.4,0.4]
    atten_2_list            = [1,1]
    wait_time_list          = [5,5]
    beam_stop_x             = [-17,-17]
    beam_stop_y             = [20,20]


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
    yield from bps.mv(fp_saxs.y1,20,fp_saxs.y2,40)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.1)

    yield from bps.mv(abs2,5)


def gid_single(name,stth_0, alpha=0.1):
    '''for calibrate the direct beam and reflected beam'''
    print(name)
    print(stth_0)
    det_saxs_y_list         = [0]
    det_saxs_y_offset_list  = [0]
    stth_list               = [stth_0]
    exp_time_list           = [1]
    x2_offset_list          = [0]
    atten_2_list            = [6]
    wait_time_list          = [1]
    beam_stop_x             = [-17]
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
    yield from bps.mv(fp_saxs.y1,20,fp_saxs.y2,40)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = alpha)


def gid_soller1(name):
    stth_start_list =    [8] # 8
    stth_stop_list =     [19] # 15
    number_points_list = [91]
    exp_time_list      = [5]
    x2_range_list      = [11]
    atten_2_list       = [1]
    wait_time_list     = [10]

    scan_dict={
        "start":stth_start_list, 
        "stop":stth_stop_list,
        "n":number_points_list,
        "exp_time":exp_time_list,
        "x2_range":x2_range_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,
      }
#mode 4 is for GID with soller
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(geo.track_mode,2)
    print("calling GID_soller")
    yield from gid_scan_soller(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus100k,
                                alphai = 0.07,
                                beamstop = False,
                                )
    # yield from bps.mv(geo.track_mode,1)
    yield from bps.mv(abs2,5)




def ref_scan_test(name):
    '''test the new ref scans, 2023-06-01
    scan_param with the order of:
    alpha_start, alpha_stop, number_points, atten_2, exp_time, wait_time, precount_time, s2_vg, x2_offset_start, x2_offset_stop
    '''
    scan_params = {
#    scan:   a_0,  a_1, num, att, exp, wait, pre, s2vg, x2_0, x2_1
        0: [0.03, 0.13,  11,   6,  5,   10, 0.2, 0.04,    0,   0],
        1: [0.12, 0.22,  11,   5,  5,   10, 0.2, 0.04,    0,   0],
    #    2: [0.18, 0.46,  15,   4,  10,   20, 0.2, 0.04,    0,   0],
    #    3: [0.40, 0.80,  11,   3,  10,   20, 0.2, 0.04,    0,   0],
    #    4: [0.72, 1.60,  12,   2,  10,   20, 0.2, 0.04,    0,   0],
    #    5: [1.52, 2.08,  12,   1,  20,   20, 0.2, 0.04,    0,   0],
    #    6: [2.00, 2.72,  10,   0,  30,   20, 0.2, 0.04,    0,   0],
    }
    yield from bps.mv(geo.det_mode,1)
    print(scan_params)
    yield from ref_scan_multi(scan_params=scan_params, md={'sample_name': name})



    detector=lambda_det
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    yield from he_off()# stops the He flow
    yield from shclose()
    yield from shclose()
    


    # scan_param = [0.03, 0.13,   3,   6,   5,    2, 0.2, 0.04,    0,   0]
    # yield from bps.mv(geo.det_mode,1)
    # print(scan_param)
    # yield from ref_scan_single(scan_param=scan_param, md={'sample_name': name})


from uuid import uuid4

def short_uid():
    return str(uuid4())[:8]

def ref_scan_multi(scan_params, md=None, detector=lambda_det, batch_uid = None, tilt_stage=False, stth_corr_par=None):
    """
    Multiple ref scans
    """
    # Tom's way of checking to see if all lists are the same length
    N = None
    for k, v in scan_params.items():
        if N is None:
            N = len(v)
        if N != len(v):
            raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

    if batch_uid is None:
        batch_uid = short_uid()  # or something

    x2_nominal= geo.stblx2.position
    for i, (j,scan_param) in enumerate(scan_params.items()):

        base_md = {
            'batch_uid': batch_uid,     # #9.7kev
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

    # #14.4kev
    # alpha_start_list =   [ 0.03, 0.09, 0.15]
    # alpha_stop_list =    [ 0.08, 0.15, 0.24]
    # number_points_list = [    6,    7,    5]
    # auto_atten_list =    [    1,    2,    2] 
    # s2_vg_list =         [ 0.02, 0.02, 0.02] 
    # exp_time_list =      [   15,   5,    5]
    # precount_time_list=  [  0.1,  0.1,  0.1]
    # wait_time_list=      [    3,    3,    3]
    # x2_offset_start_list=[  0.0,  0.0,  0.0]
    # x2_offset_stop_list= [  0.0,  0.0,  0.0]
            'total_sub_scans': len(scan_params),
            'sub_scan_number': j, 
            'range_index': i,
        }
        base_md.update(md or {})

        print(f'Sub-scan {i} is starting.')
        print(scan_param)
        yield from ref_scan_single(scan_param,detector=detector, md=base_md, tilt_stage=tilt_stage, x2_nominal=x2_nominal)                      
        print(f'Sub-scan {i} is done.')

    print('The reflectivity scan is over')



def ref_scan_single(scan_param, detector=lambda_det, md=None, x2_nominal=None, batch_uid = None, tilt_stage=False):
    """
    single scan
    """
    global attenuation_factor_signal, exposure_time, attenuator_name_signal, default_attenuation
    attenuator_name_signal = Signal(name='attenuator_name', value='abs1',kind='normal')
    attenuation_factor_signal = Signal(name='attenuation', value=1e-7,kind='normal')
    exposure_time = Signal(name='exposure_time', value=1)
    default_attenuation = Signal(name='default-attenuation', value=1e-7)

    # Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_scan',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
               'detectors': [detector.name, quadem.name],
               'energy': energy.energy.position,
               'rois': [detector.roi1.min_xyz.min_x.get(),
                        detector.roi1.min_xyz.min_y.get(),
                        detector.roi2.min_xyz.min_y.get(),
                        detector.roi3.min_xyz.min_y.get(),
                        detector.roi2.size.x.get(),
                        detector.roi2.size.y.get()],
               'geo_param': [geo.L1.get(), geo.L2.get(), geo.L3.get(), geo.L4.get()],
               'slit_s1': [S1.top.position - S1.bottom.position, S1.outb.position - S1.inb.position],
               'slit_s2': [S2.vg.position, S2.hg.position],
               'x2': [geo.stblx2.position],
               'tilt stage': tilt_stage,
               'atten_material': att_mater_selected,
               }
    base_md.update(md or {})

    unhinted_ref() ## change all hinted settings to 'normal'
    bec.disable_plots()
    if x2_nominal is None:
        x2_nominal= geo.stblx2.position

    yield from bps.open_run(md=base_md)
    yield from bps.sleep(3) 
    print(scan_param)
    yield from ref_scan_base(scan_param, tilt_stage=tilt_stage, x2_nominal=x2_nominal)                      
    yield from bps.close_run()

    bec.enable_plots()
    yield from bps.mv(abs2, 5)
    quadem.averaging_time.put(1)
    # print('The reflectivity scan is over')
    hinted_ref() ## change hinted settings


all_area_dets = [quadem, lambda_det, AD1, AD2, o2_per]
@bpp.stage_decorator(all_area_dets)
def ref_scan_base(scan_param, tilt_stage=False,x2_nominal=None):
    '''
    Scan params consist of a total of 10 param with the order of below:
    alpha_start, alpha_stop, number_points, atten_2, exp_time, wait_time, precount_time, s2_vg, x2_offset_start, x2_offset_stop
    '''
    N = 10
    if len(scan_param) != N:
        raise ValueError(f"The scan params has a length of {len(scan_param)}, expected {N}!")
    else:
        alpha_start, alpha_stop, number_points, atten_2, exp_time, wait_time, precount_time, s2_vg, x2_offset_start, x2_offset_stop = scan_param

    print(f'Running {alpha_start}----{alpha_stop} at atten = {atten_2}')
    # setting up so that if alpha is moved negative that there is an extra wait
    alpha_old=5
    for alpha in np.linspace(alpha_start, alpha_stop, number_points):
        # Move to the good geometry position
        if tilt_stage:
             yield from nab(alpha, alpha)
        else:
            if alpha >= alpha_old:
                yield from mabt(alpha, alpha, 0)
                # if alpha-alpha_old < 0.05: ## added by HZ 2022-10-17 due to low geometry resolution
                #     yield from mabt(alpha-0.1, alpha-0.1, 0)
                #     yield from bps.sleep(1)
                #     yield from mabt(alpha, alpha, 0)
                # else:
                #     yield from mabt(alpha, alpha, 0)
            else:
                yield from mabt(alpha-0.1, alpha-0.1, 0)
                yield from bps.sleep(1)
                yield from mabt(alpha, alpha, 0)
        alpha_old =alpha

        fraction  = (alpha-alpha_start)/(alpha_stop-alpha_start)
        x2_fraction =fraction*(x2_offset_stop-x2_offset_start) + x2_offset_start

        yield from bps.mv(S2.vg,s2_vg)

        if x2_nominal is None:
            x2_nominal= geo.stblx2.position
        if abs(x2_fraction)>0:
            yield from bps.mv(geo.stblx2,x2_nominal+x2_fraction)
            yield from bps.sleep(5) 

        yield from bps.sleep(wait_time)    
        yield from bps.mv(abs2, atten_2)  
        yield from bps.mv(attenuator_name_signal, f'att{atten_2}')
        if att_fact_selected != None:
            yield from bps.mv(attenuation_factor_signal, att_fact_selected[f'att{atten_2}'])
            

        yield from det_set_exposure(detectors_all, exposure_time=precount_time, exposure_number = 1)
        yield from bps.mv(shutter, 1)
        yield from bps.trigger_and_read([quadem],name='precount')

        yield from det_set_exposure(detectors_all, exposure_time=exp_time, exposure_number = 1)
        yield from bps.trigger_and_read(all_area_dets +
                                            [geo] + 
                                            [S2] +
                                            [attenuation_factor_signal] +
                                            [attenuator_name_signal] +
                                            [exposure_time_signal],
                                            name='primary')
        yield from bps.mv(shutter, 0)


def test_sh():
    yield from sample_height_set_fine_o_xrf(sh_offset =-0.00 , detector=lambda_det)   #scan 
    for phase in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]:
        print(phase)
        yield from bps.mv(geo.sh_phase,phase)
        yield from xrf_scan2('test2_'+str(1.*phase))
  