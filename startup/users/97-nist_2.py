
proposal_id("2023_1","310438_satija")

from pyrsistent import s


def run_nist_kibron():
    proposal_id("2023_1","310438_satija")
    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)

    detector=lambda_det

    #### Run 2023-03-21
    samp_name = 'MEA19_275uL_0p1mMCd_pH6' #

    # pressure_list = list(range(3,46))
    # samp_x2_list = [-17+step*2 for step in range(len(pressure_list))]  #

    # pressure_list = [0]
    # samp_x2_list = [-40+step*8 for step in range(len(pressure_list))]  #

    # pressure_list = [5]  # 10, 15 20, 25, 30, 35, 40, 45]
    # samp_x2_list = [-32+step*8 for step in range(len(pressure_list))]  #\

    # pressure_list = [10, 15]
    # samp_x2_list = [-24+step*8 for step in range(len(pressure_list))]  #

    # pressure_list = [20]
    # samp_x2_list = [-6+step*8 for step in range(len(pressure_list))]  #

    # pressure_list = [25]
    # samp_x2_list = [2+step*8 for step in range(len(pressure_list))]  #

    # pressure_list = [30, 35, 40, 45]
    # samp_x2_list = [21+step*8 for step in range(len(pressure_list))]  #

    samp_name = 'MEA19_200uL_0p1mMCd_pH6' #
    pressure_list = [40]
    samp_x2_list = [-38+step*15 for step in range(len(pressure_list))]  #

    
    gisaxs_run = False
    gid_run = True
    xr_run = True


    slit_hg_gisaxs = [0.2]
    for ii,(one_pressure, samp_x2) in enumerate(zip(pressure_list,samp_x2_list)):
        runNum = ii+1
        yield from bps.mv(S2.hg, 0.3)
        yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos

        # kibron.runConstantPressure(target_pressure=one_pressure, target_speed = 10)
        # print('Sleep to wait for target pressure')
        # yield from bps.sleep(3*60)

        yield from bps.mv(shutter,1) # open shutter
        yield from check_ih()
        yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)

        if gisaxs_run:
            print('Starting GISAXS measurement')
            for kk,slit_hg in enumerate(slit_hg_gisaxs):
                print('Slit horizontal gap is set to %.2f'%slit_hg)
                yield from bps.mv(S2.hg, slit_hg)
                yield from bps.mv(S2.vg, 0.04) # added the vertical gap for gisaxs
                yield from det_set_exposure([detector], exposure_time=1, exposure_number = 1)
                # yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                yield from gisaxs_scan1(samp_name+f'_P{one_pressure}')
                yield from det_set_exposure([detector,quadem], exposure_time=1, exposure_number = 1)

        
        if gid_run:
            print('Starting GID measurement')
            yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(S2.vg, 0.04) 
            yield from bps.mv(geo.stblx2,samp_x2+1.5)  #move the  Sample Table X2 to xpos
            yield from bps.sleep(5)
            yield from sample_height_set_fine_o(detector=detector) #scan the detector arm height from -0.2 to 0.2 with 21 points
            samp_name_new = samp_name+f'_P{one_pressure}'
            yield from gid_soller1(samp_name_new)
            yield from det_set_exposure([detector,quadem], exposure_time=1, exposure_number = 1)
        
        if xr_run:
            print('Starting XRR measurement')
            yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(S2.vg, 0.04)
            yield from bps.mv(geo.stblx2,samp_x2+8)  #move the  Sample Table X2 to xpos
            yield from bps.sleep(5)
            yield from sample_height_set_fine_o(detector=detector) #scan the detector arm height from -0.2 to 0.2 with 21 points
            samp_name_new = samp_name+f'_P{one_pressure}'
            # yield from one_xrr_kibron_constantP(samp_name, target_pressure=one_pressure)
            yield from one_xrr_new(samp_name_new)
            yield from det_set_exposure([detector,quadem], exposure_time=1, exposure_number = 1)

        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

        yield from det_set_exposure([detector,quadem], exposure_time=1, exposure_number = 1)
        yield from bps.mv(geo.det_mode,1)
        yield from mabt(0,0,0)

    
################### TO USE KIBRON ####################
# To start, run these commands in the bluesky below
    # HOST, PORT = "10.66.91.26", 9897 ## HZ
    # sock = mtx.connect(HOST, PORT)
    # device = mtx.Trough(sock)
    # kibron = KibronTrough(device, sock)
# To stop the remote server:
    # kibron.close()
######################################################

def one_xrr_kibron_constantP(name, target_pressure):
   #     '''Conduct reflectivity measurments after compressure to target pressure'''
  
    result = kibron.runConstantPressure(target_pressure=target_pressure, target_speed = 5)
    # if result == 0:
    #     print('Compression to target pressure failed!!!')
    # else:
    print('Sleep to wait for target pressure')
    yield from bps.sleep(3*60)
    # _pressure = kibron.getPressure()
    # while abs(_pressure-target_pressure)>0.2:
    #     yield from bps.sleep(30)
    #     _pressure = kibron.getPressure()
    #     print(f'Current pressure = {_pressure: .2f} mN/m.')
        
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
#   yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
#   yield from bps.mv(block.y,xpos)  #move the  block to xpos

    yield from bps.mv(shutter,1) # open shutter
    
    filename = name+f'_P{target_pressure}'
    print(f"file name= {filename}")  
    yield from xr_scan1(filename)
    print('RUN XRR...')
    yield from bps.sleep(3)
    print('XRR IS DONE.')

    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0,0,0)


def kibron_stop_measure():
    kibron.device.call("StopMeasure")

##############################################################
def run_nist():
    proposal_id("2023_1","310438_satija")
    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)

    # yield from bps.sleep(5)
    # yield from shopen()
    # yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {
        1: 'water_1', 
    }
 

    sam_x2_pos ={
   
        1: 98, # -16-54,
        # 2: -19,
        # 3: 32, # -19+54,

    }

    sam_sh_offset ={
        1: -26.3,
        2: -26.3,
    }

    xr_run_dict = {
        1: True,
        2: False,
        3: False,
    }

    gid_run_dict = {
        1: False,
        2: False,
        3: False,
    }
#     x2.limits =(-81.60) for large XSRF cover for 3 small troughs with no balance
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
        runNum = ii+1

        for key in samp_name_dict:

            # if key == 2: # for the 2nd run
            #     runNum == runNum+1

            samp_name = samp_name_dict[key] # +f'_run{runNum}'
            samp_x2 = sam_x2_pos[key]
            yield from bps.mv(S2.hg, 0.3)
            yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos
            try:
                yield from bps.mv(block.y,samp_x2-5)
            except:
                print('beam block is not connected.')
            
            yield from det_set_exposure([detector,quadem], exposure_time=1, exposure_number = 1)
            # yield from check_ih()
            # yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)

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
                # for kk in range(10):
                #     yield from one_xrr_new(samp_name+f'_radiation_run{kk+1}',samp_x2)
                yield from one_xrr_new(samp_name)

            if xrf_run_dict[key]:
                print('Starting XRF measurement')
                yield from bps.mv(geo.stblx2,samp_x2+3)  #move the  Sample Table X2 to xpos
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
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-1,1,13,per_step=shutter_flash_scan), local_peaks)
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
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.15,0.15,31,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
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
    alpha_start_list =   [ 0.03, 0.12, 0.20, 0.40,  0.72, 1.84,   2.5]
    alpha_stop_list =    [ 0.13, 0.22, 0.42, 0.80,  1.92,  2.4,   3.0]
    number_points_list = [   11,   11,   12,   11,    16,    8,     6]
    auto_atten_list =    [    6,    5,    4,    3,     2,    1,     1]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,  0.04]
    exp_time_list =      [    5,   5,     5,    5,    10,   15,    20]
    precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,   0.2]
    wait_time_list=      [   10,  10,    10,   10,    10,   10,    10]
    x2_offset_start_list=[    0,   0,     0,    0,     0,  0.2,   2.4]
    x2_offset_stop_list= [    0,   0,     0,    0,     0,  2.2,     6]
    block_offset_list=   [    0,   0,     0,    0,     0,    0,     0]

    #  #14.4kev for running kibron, keep 1 abs for MEA
    # alpha_start_list =   [ 0.03, 0.12, 0.20, 0.40,  0.64, 1.84,   2.5]
    # alpha_stop_list =    [ 0.13, 0.22, 0.42, 0.68,  1.92,  2.4,   3.0]
    # number_points_list = [   11,   11,   12,    8,    17,    8,     6]
    # auto_atten_list =    [    6,    5,    4,    3,     2,    1,     1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04,  0.04]
    # exp_time_list =      [    5,   5,     5,    5,    10,   15,    20]
    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2,  0.2,   0.2]
    # wait_time_list=      [   10,  10,    10,   10,    10,   10,    10]
    # x2_offset_start_list=[    0,   0,     0,    0,     0,  0.2,   2.4]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,  2.2,     6]
    # block_offset_list=   [    0,   0,     0,    0,     0,    0,     0]


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




    # #14.4kev for running kibron, keep 1 abs
    # alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72, 1.60,  2.08]
    # alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.60, 2.08,  2.78]
    # number_points_list = [   11,   11,   15,   11,   12,     7,    8]
    # auto_atten_list =    [    6,    5,    4,    3,    2,     1,    1]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]

    # exp_time_list =      [    5,   5,     5,    5,     5,   5,    30]
    # # exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]

    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2, 0.2,   0.2]

    # # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    # wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]

    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,     3]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0,   3,     6]
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

    #14.4kev
    alpha_start_list =   [ 0.03, 0.09, 0.15]
    alpha_stop_list =    [ 0.08, 0.15, 0.24]
    number_points_list = [    6,    7,    5]
    auto_atten_list =    [    1,    2,    2] 
    s2_vg_list =         [ 0.02, 0.02, 0.02] 
    exp_time_list =      [   15,   5,    5]
    precount_time_list=  [  0.1,  0.1,  0.1]
    wait_time_list=      [    3,    3,    3]
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



def gisaxs_scan1(name):
    '''For MEA19'''
    det_saxs_y_list         = [0, 0, 30]
    det_saxs_y_offset_list  = [0, 1, 0]
    stth_list               = [0, 0, 0]
    exp_time_list           = [5, 5, 5] # [20,20]
    x2_offset_list          = [-0.4, 0, 0.4]
    atten_2_list            = [0, 0, 0]
    wait_time_list          = [5, 5, 5]
    beam_stop_x             = [-41.7, -41.7, -41.7] # [-54.3,-54.3, -54.3]
    beam_stop_y             = [24, 24, 24]


    # det_saxs_y_list         = [0,0,30]
    # det_saxs_y_offset_list  = [0,1,0]
    # stth_list               = [0,0,0]
    # exp_time_list           = [5,5,5] # [20,20]
    # x2_offset_list          = [-0.4,0,0.4]
    # atten_2_list            = [0,0,0]
    # wait_time_list          = [5,5,5]
    # beam_stop_x             = [-64,-64,-64]
    # beam_stop_y             = [20,20,20]


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
                                alphai = 0.07)

    yield from bps.mv(abs2,5)





def gisaxs_incident(name):
    '''For MEA19'''
    det_saxs_y_list         = [0]
    det_saxs_y_offset_list  = [0]
    stth_list               = [0]
    exp_time_list           = [1] # [20,20]
    x2_offset_list          = [0.2]
    atten_2_list            = [6]
    wait_time_list          = [5]
    beam_stop_x             = [-41.7+2]
    beam_stop_y             = [24]


    # det_saxs_y_list         = [0,0,30]
    # det_saxs_y_offset_list  = [0,1,0]
    # stth_list               = [0,0,0]
    # exp_time_list           = [5,5,5] # [20,20]
    # x2_offset_list          = [-0.4,0,0.4]
    # atten_2_list            = [0,0,0]
    # wait_time_list          = [5,5,5]
    # beam_stop_x             = [-64,-64,-64]
    # beam_stop_y             = [20,20,20]


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
                                alphai = 0.07)

    yield from bps.mv(abs2,5)



def gisaxs_direct(name):
    '''For MEA19'''
    det_saxs_y_list         = [0, 0, 0, 0]
    det_saxs_y_offset_list  = [0, 0, 0, 0]
    stth_list               = [-1.5, -1, 1, 1.5]
    exp_time_list           = [1, 1, 1, 1] # [20,20]
    x2_offset_list          = [-0.1, 0, 0.1,0.2]
    atten_2_list            = [6, 6, 6, 6]
    wait_time_list          = [1, 1, 1, 1]
    beam_stop_x             = [-41.7+2, -41.7+2, -41.7+2,-41.7+2]
    beam_stop_y             = [24, 24, 24, 24]


    # det_saxs_y_list         = [0,0,30]
    # det_saxs_y_offset_list  = [0,1,0]
    # stth_list               = [0,0,0]
    # exp_time_list           = [5,5,5] # [20,20]
    # x2_offset_list          = [-0.4,0,0.4]
    # atten_2_list            = [0,0,0]
    # wait_time_list          = [5,5,5]
    # beam_stop_x             = [-64,-64,-64]
    # beam_stop_y             = [20,20,20]


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
                                alphai = 0)

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
    stth_start_list =    [10]
    stth_stop_list =     [13]
    number_points_list = [31]
    exp_time_list      = [10]
    x2_range_list      = [6]
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
    yield from bps.mv(geo.det_mode,4)
    yield from bps.mv(geo.track_mode,2)
    print("calling GID_soller")
    yield from gid_scan_soller(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus100k,
                                alphai = 0.07,
                                beamstop = True,
                                )
    
    yield from bps.mv(abs2,5)
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(geo.track_mode,1)


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
    yield from bps.mv(geo.det_mode,4)
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
    yield from bps.mv(geo.det_mode,4)
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