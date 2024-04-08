from pyrsistent import s


#a comment goes here  test and again
def ocko_1():
    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)


  #  proposal_id("2023_1","311915_ocko2")
    proposal_id("2022_3","309891_tu")
    # yield from bps.sleep(5)
    # yield from shopen()
    # yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {
        #1: 'water_30ml_1', 
        # 2: 'Water_30mL', 
        # 2: 'DPPC_42mNm', # 16uL 1mg/ml DPPC on 30mL water 
        # 2: 'PFOS_100mMCaCl2_1000ppm', # 42mL trough, 37mL samples, a little over the rim
        2: 'PFOS_100mMCaCl2_approx300ppm', # 40mL sample in trough
     #   3: 'ODA_10mN_2mMKI',
    }

    sam_x2_pos ={
        # 1: -57,
        # 2: -17,
        # 2: 18,
        2: -25,
        # 1: -73, #-66, #-68flat from -65 to -60  #-65, #-62, # (-63.5,-6.14), # front
        # 2: -17, #-19, flat from -15 to -10 # -9, # (-9, 3.5), # middle trough
        # 3: 39, #32 flat from 34.5 to 39.5  #42, # (38, 5.1), # back
    }

    sam_sh_offset ={
        # 1: -105.198,
        1: -26.68,
        2: -26,
        # 3: -26.76,
    }

    xr_run_dict = {
        1: False,
        2: True,
        3: False,
    }

    xrf_run_dict = {
        1: False,
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
      
        for key in samp_name_dict:
            samp_name = samp_name_dict[key]
            samp_x2 = sam_x2_pos[key]
            yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from check_ih()
            
            if sh_offset_dict[key]:
                print('Starting fast sample height set using offset position')
                sh.user_offset.set(sam_sh_offset[key]) 
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            else:
                print('Starting full sample height set')
                yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                sam_sh_offset[key]=sh.user_offset.value
                print('Setting sh_offset to',sh.user_offset.value)

            if xr_run_dict[key]:
                print('Starting XRR measurement')
                # yield from one_xrr_new(samp_name+f'_run{ii+1}',samp_x2)
                yield from one_xrr_new(samp_name+f'_run{ii+1}',expo_time = 5, wait_time = 10)
            
            if xrf_run_dict[key]:
                print('Starting XRF measurement')
                yield from xrf_scan1(samp_name)

            if gisaxs_run_dict[key]:
                print('Starting GISAXS measurement')

                for kk,slit_hg in enumerate(slit_hg_gisaxs):
                    print('Slit horizontal gap is set to %.2f'%slit_hg)
                    yield from bps.mv(S2.hg, slit_hg)
                    yield from bps.mv(geo.stblx2,samp_x2+3+slit_hg*kk*2)  #move the  Sample Table X2 to xpos
                    # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
                    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
                    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                    yield from gisaxs_scan1(samp_name+f'slit_hg_{slit_hg}')

        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    # yield from he_off()# stops the He flow
    # yield from shclose()




def ocko_multi_xrr():
    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)

    proposal_id("2022_3","311547_ocko")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {
         1: 'Water_Noise_Test',
    }

    sam_x2_pos ={
        1: 0,
    }


    run_cycle = 2
    for ii in range(run_cycle):
        for key in samp_name_dict:
            samp_name = samp_name_dict[key]
            samp_x2 = sam_x2_pos[key]
            yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos

            
            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runA{ii+1}',expo_time = 5, wait_time = 10, reverse_mode = True)
            yield from bps.mv(abs2,6)
            # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)

            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runB{ii+1}',expo_time = 5, wait_time = 10, reverse_mode = False)
            yield from bps.mv(abs2,6)
            # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)

            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runC{ii+1}',expo_time = 5, wait_time = 30, reverse_mode = False)
            yield from bps.mv(abs2,6)
            # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
            
            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runD{ii+1}',expo_time = 30, wait_time = 10, reverse_mode = False)
            yield from bps.mv(abs2,6)
            # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)

            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runE{ii+1}',expo_time = 5, wait_time = 30, reverse_mode = True)
            yield from bps.mv(abs2,6)
            # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)


        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    yield from he_off()# stops the He flow
    yield from shclose()


def ocko_test_xrr():
    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)

    proposal_id("2022_3","311547_ocko")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {
         1: 'Water_Noise_Test_Quadem_precount',
    }

    sam_x2_pos ={
        1: 0,
    }


    run_cycle = 1
    for ii in range(run_cycle):
        for key in samp_name_dict:
            samp_name = samp_name_dict[key]
            samp_x2 = sam_x2_pos[key]
            yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos

            
            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runA{ii+4}',expo_time = 10, wait_time = 10, reverse_mode = False)
            yield from bps.mv(abs2,6)
            # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)

  
        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    # yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    yield from he_off()# stops the He flow
    yield from shclose()



def ocko_2():
    proposal_id("2022_1","309773_ocko")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
 #   yield from one_ref("DMPG(85uL)_2_no_atten_0+AB(x2)+0.75hr",23)
 #   yield from gid_scan1a("DMPG(85uL)_2_no_atten_0+AB(x2)+0.75hr")

    yield from one_ref("water_final_2",22)
    yield from gid_scan1a("water_fina_2l")
    yield from he_off() # stops the He flow
    yield from shclose()

#def ccny_gid():gid_scan2
#    yield from gid_single("GDS_gid_run11_7",7)
#    yield from gid_single("GDS_gid_run11_10",10)
#    yield from gid_single("GDS_gid_run11_13",13)



def one_xrr(name,xpos,tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(block.y,xpos)  #move the  block to xpos    #14.4kev for testing exposure time and reverse mode
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

def one_xrr_new(name,expo_time = 5, wait_time = 10, reverse_mode = False, tiltx=0,detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
 #   yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
 #   yield from bps.mv(block.y,xpos)  #move the  block to xpos
    yield from bps.mv(shutter,1) # open shutter
    # yield from xr_scan1(name)

    yield from xr_scan1(name, expo_time = expo_time, wait_time = wait_time, reverse_mode = reverse_mode) # 2022-11-21, HZ

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
    # yield from det_exposure_time_new(detector, 1,1)
    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
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
    print('Start the height scan')
    Msg('reset_settle_time', sh.settle_time, value)
 #   yield from bp.rel_scan([detector],sh,-0.1,0.1,21,per_step=shutter_flash_scan)
 #   tmp2=peaks.cen['%s_stats2_total'%detector.name]


    yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
    local_peaks = PeakStats(sh.user_readback.name, '%s_stats2_total'%detector.name)
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.1,0.1,20,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)



# table=(
# ("scan1", start, finish, pts,       )
# ("scan2", start, finish, pts,       )

# )
# scan_table = [   
# ]

# def xr_scan_new(name):
#     '''devide into subscans'''



def xr_scan1(name, expo_time = 10, wait_time = 10, reverse_mode = False):



     #14.4kev for running kibron
    alpha_start_list =   [ 0.03, 0.12, 0.20, 0.40,  0.72, 1.52,  2.3]
    alpha_stop_list =    [ 0.13, 0.22, 0.42, 0.80,  1.60,  2.4,  3.0]
    number_points_list = [   6,     6,    6,    6,     6,    6,    8]
    auto_atten_list =    [    5,    4,    3,    2,     1,    0,    0]
    s2_vg_list =         [ 0.04, 0.04, 0.06,  0.06, 0.08, 0.08, 0.08]
    exp_time_list =      [    5,   5,     5,    5,     5,    5,   15]
    precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    wait_time_list=      [   10,  10,    10,   10,    10,   10,   10]
    x2_offset_start_list=[    0,   0,     0,    0,     0,    0,  0.7]
    x2_offset_stop_list= [    0,   0,     0,    0,     0,  0.5,  2.5]
    block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]


    #  #14.4kev for running kibron
    # alpha_start_list =   [ 0.03, 0.12, 0.20, 0.40,  0.72, 1.52,  2.3]
    # alpha_stop_list =    [ 0.13, 0.22, 0.42, 0.80,  1.60,  2.4,  3.0]
    # number_points_list = [   11,   11,   12,   11,    12,   12,    8]
    # auto_atten_list =    [    5,    5,    3,    2,     1,    0,    0]
    # s2_vg_list =         [ 0.04, 0.04, 0.06,  0.06, 0.08, 0.08, 0.08]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   15]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    # wait_time_list=      [   10,  10,    10,   10,    10,   10,   10]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,    0,  0.7]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,  0.5,  2.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]


   # scan1=(0.03,0.13,11,6,0.04,5,0.2,20,0,0,0); scanr=scan1

    # alpha_start_list =   [ scanr(0)]
    # alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.60, 2.08, 2.72]
    # number_points_list = [   11,   11,   15,   11,   12,     8,   10]
    # auto_atten_list =    [    6,    5,    4,    3,    2,     1,    1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   30]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    # wait_time_list=      [   20,  20,    20,   20,    20,   20,   20]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,    0, -0.6]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,  -0.5,-2.6]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]



    #14.4kev for running kibron, keep 1 abs, for PFAS
    # alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72, 1.52, 2.00]
    # alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.60, 2.08, 2.72]
    # number_points_list = [   11,   11,   15,   11,   12,     8,   10]
    # auto_atten_list =    [    6,    5,    4,    3,    2,     1,    1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,    5,   30]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,  0.2]
    # wait_time_list=      [   20,  20,    20,   20,    20,   20,   20]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,    0, -0.6]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,  -0.5,-2.6]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]



    # #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.18, 0.30,  0.4,  0.7,  1.2,  2.0, 3.1]
    # alpha_stop_list =    [ 0.18, 0.30, 0.40,  0.8,  1.3,  2.0,  3.0, 3.9]
    # number_points_list = [    8,   7,     6,    5,    7,    9,   11,   5]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,   5,    5,  20]
    # precount_time_list=  [  0.1, 0.1,   0.1,  0.1,   0.1, 0.1,  0.1, 0.1]
    # wait_time_list=      [   10,  10,    10,   10,    10,  10,   10,  10]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  0.5, 1.5]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, 0.5,  1.5, 2.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,    0,   0]


    # #14.4kev for testing exposure time and reverse mode
    # alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72,  1.2,  2.6]
    # alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.36,  2.5,  3.0]
    # #number_points_list = [  21,   21,   15,   11,    9,    9,    11]
    # number_points_list = [   11,   11,   15,   11,    9,    14,    5]
    # # number_points_list = [   3,   3,   3,   3,    3,    3,    3] # for code testing, HZ, Feb2023
    # auto_atten_list =    [    6,    5,    4,    3,    2,    1,     1]
    # s2_vg_list =         [ 0.04, 0.04, 0.06,  0.06, 0.08, 0.08, 0.08]
    # exp_time_list =      [   5,   5,     5,    5,     5,   5,     30]
    # #exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2, 0.2,   0.2]
    # # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    # wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]
    # # wait_time_list=      [1 for _ in range(len(alpha_start_list))] # for code testing, HZ
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  -0.5]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, -0.5,   -2]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]


    # if reverse_mode:
    #     alpha_start_list, alpha_stop_list = alpha_stop_list, alpha_start_list



    # #14.4kev 
    # alpha_start_list =   [ 0.12, 0.18, ]
    # alpha_stop_list =    [ 0.12, 0.18, ]
    # number_points_list = [    5,    5, ]
    # auto_atten_list =    [    5,    4, ]

    # s2_vg_list =         [ 0.04, 0.04, ]
    # # exp_time_list =      [   5,     5]
    # exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]
    
    # precount_time_list=  [  0.2,   0.2, ]
    # # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    # wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]

    # x2_offset_start_list=[    0,     0, ]
    # x2_offset_stop_list= [    0,     0, ]
    # block_offset_list=   [    0,     0, ]


    # if reverse_mode:
    #     alpha_start_list, alpha_stop_list = alpha_stop_list, alpha_start_list

    

    #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.18, 0.30,  0.4,  0.7,  1.2,  2.0, 3.1]
    # alpha_stop_list =    [ 0.18, 0.30, 0.40,  0.8,  1.3,  2.0,  3.0, 3.9]
    # number_points_list = [    8,   5,     6,    5,    7,    9,   11,   5]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    1,   1]
    # s2_vg_list =         [ 0.02, 0.02, 0.04,  0.04, 0.04, 0.04,0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,   5,    5,  20]
    # precount_time_list=  [  0.1, 0.1,   0.1,  0.1,   0.1, 0.1,  0.1, 0.1]
    # wait_time_list=      [    7,   7,     7,    7,     7,   7,    7,   7]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  0.5, 1.5]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, 0.5,  1.5, 2.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,    0,   0]


    # #9.7kev Qz to 0.65, more overlap
    # alpha_start_list =   [ 0.04, 0.18, 0.30,  0.4,  0.7,  1.2,  2.0]
    # alpha_stop_list =    [ 0.18, 0.30, 0.40,  0.8,  1.3,  2.0,  3.0]
    # number_points_list = [    8,   5,     6,    5,    7,    9,    6]
    # auto_atten_list =    [    7,   6,     5,    4,    3,    2,    2]
    # s2_vg_list =         [ 0.02, 0.02, 0.04,  0.04, 0.04, 0.04,0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,   5,   20]
    # precount_time_list=  [  0.1, 0.1,   0.1,  0.1,   0.1, 0.1,  0.1]
    # wait_time_list=      [    7,   7,     7,    7,     7,   7,    7]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  0.7]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, 0.5,  1.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,    0]

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
    alpha_start_list =   [ 0.03, 0.11, 0.13, 0.25]
    alpha_stop_list =    [ 0.10, 0.12, 0.23, 0.45]
    number_points_list = [    2,    2,    6,    5]
    auto_atten_list =    [    1,    1,    2,    2] 
    s2_vg_list =         [ 0.02, 0.02, 0.02, 0.02] 
    exp_time_list =      [   50,   10,   10,   10]
    precount_time_list=  [  0.1,  0.1,  0.1,  0.1]
    wait_time_list=      [    0,    0,    0,    0]
    x2_offset_start_list=[  0.0,  0.0,  0.0,  0.0]
    x2_offset_stop_list= [  0.0,  0.0,  0.0,  0.0]

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



def gid_soller1(name):
    stth_start_list =    [11.0]
    stth_stop_list =     [12.0]
    number_points_list = [11]
    exp_time_list      = [5]
    x2_range_list      = [3]
    atten_2_list       = [0]
    wait_time_list     = [5]

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


def gid_soller_cali(name):
    stth_start_list =    [0.7]
    stth_stop_list =     [3.7]
    number_points_list = [61]
    exp_time_list      = [2]
    x2_range_list      = [0]
    atten_2_list       = [1]
    wait_time_list     = [1]

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
                                alphai = 0,
                                beamstop = True,
                                )
    # yield from bps.mv(geo.track_mode,1)
    yield from bps.mv(abs2,5)


def gid_soller_incident(name='gid_soller_incident007'):
    stth_start_list =    [0]
    stth_stop_list =     [0.1]
    number_points_list = [1]
    exp_time_list      = [1]
    x2_range_list      = [0]
    atten_2_list       = [6]
    wait_time_list     = [1]

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
    yield from bps.mv(geo.det_mode,4)
    yield from bps.mv(geo.track_mode,2)
    print("calling GID_soller")
    yield from gid_scan_soller(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus100k,
                                alphai = 0.07,
                                beamstop = True,
                                )
    # yield from bps.mv(geo.track_mode,1)
    yield from bps.mv(abs2,5)


def gid_soller_direct(name='gid_soller_direct0'):
    stth_start_list =    [0]
    stth_stop_list =     [0.1]
    number_points_list = [1]
    exp_time_list      = [1]
    x2_range_list      = [0]
    atten_2_list       = [6]
    wait_time_list     = [1]

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
                                alphai = 0,
                                beamstop = False,
                                )
    # yield from bps.mv(geo.track_mode,1)
    yield from bps.mv(abs2,5)