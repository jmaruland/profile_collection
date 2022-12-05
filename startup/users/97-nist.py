from pyrsistent import s



def xrr_kibron():

    proposal_id("2022_3","310438_satija")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # open the He flow
    detector=lambda_det


    HOST, PORT = "10.66.91.26", 9897 ## HZ
    sock = mtx.connect(HOST, PORT)
    device = mtx.Trough(sock)
    kibron = KibronTrough(device, sock)

    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)


    
    # samp_name = 'MEA19_1mMCdCl2_0p1mMNaCO3' # _80uL_0p92mgpml'

    # pressure_list = [7, 14] ## no abs in high angle
    # samp_x2_list = [-7, -14]

    # pressure_list = [14, 21, 28, 35, 42] ## keep abs = 1 for high angles to minimize radiation demage
    # samp_x2_list = [-20, -26, -32, -38, -44]

    
    # samp_name = 'MEA19_0p1mMCd_0p1mMNa_quickGID' # _80uL_0p92mgpml'

    # pressure_list = [  8,  15,  22,  29,  36,  43] ## keep abs = 1 for high angles to minimize radiation demage
    # samp_x2_list =  [-49, -40, -31, -22, -13,  -4] ## move more for fresh area
    # samp_x2_list =  [-49, -40, -31, -22, -13,  -4] ## move more for fresh area


    # ## Manually run pressure 3.5, 2, 1.5 1.4 at x2 = -70, -68, -66, -64
    # ## Auto-run the next list
    # pressure_list = list(range(3,18,3)) + list(range(20, 35, 5)) # [3, 6, 9, 12, 15, 20, 25, 30]
    # samp_x2_list = [-62+step*2 for step in range(len(pressure_list))] # change 2mm per step


    # pressure_list = [40]
    # samp_x2_list = [-46]


    # #### Night run 2022-11-29
    # samp_name = 'MEA19_0p1mMCd_0p1mMNa_pH5p7' # _80uL_0p92mgpml'

    # # pressure_list = [10]
    # # samp_x2_list = [-68]

    # pressure_list = [15, 20, 25, 30, 35, 40]
    # samp_x2_list = [-60+step*8 for step in range(len(pressure_list))] # [-60, -52, -44, -36, -28, -20]


    #### Run 2022-11-30
    samp_name = 'MEA19_0p1mMCd_0p1mMNa_pH6' # _25uL_0p92mgpml, G4_medium'

    # pressure_list = [5]
    # samp_x2_list = [-72]

    pressure_list = [15, 20, 25, 30, 35]
    samp_x2_list = [-64+step*8 for step in range(len(pressure_list))]  #





    xr_run = True
    gisaxs_run = True

    usekibron_gid = True
    compress_gid = True

    samp_sh_offset = None
    sh_offset = False

    slit_hg_gisaxs = [0.2]

    # run_cycle = 1
    for ii,(one_pressure, samp_x2) in enumerate(zip(pressure_list,samp_x2_list)):
        runNum = ii+1


        yield from bps.mv(S2.hg, 0.3)
        yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos
        yield from check_ih()
        yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)

        # if sh_offset and samp_sh_offset != None:
        #     print('Starting fast sample height set using offset position: %.2f'%samp_sh_offset)
        #     sh.user_offset.set(samp_sh_offset)
        #     yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
        #     samp_sh_offset=sh.user_offset.value
        #     print('Re-setting sh_offset to:', sh.user_offset.value)
        
        # else:
        #     print('Starting full sample height set')
        #     yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1.5 to 1.5 with 41 points
        #     yield from sample_height_set_fine_o(detector=detector) #scan the detector arm height from -0.2 to 0.2 with 21 points
        #     samp_sh_offset=sh.user_offset.value
        #     print('Setting sh_offset to:', sh.user_offset.value)


        yield from sample_height_set_fine_o(detector=detector) #scan the detector arm height from -0.2 to 0.2 with 21 points

        if xr_run:
            print('Starting XRR measurement')
            samp_name_new = samp_name+f'_pressure{one_pressure}'
            yield from one_xrr_kibron(samp_name_new, expo_time = 5, wait_time = 20, usekibron = True, trough = kibron, compress = True, target_pressure = one_pressure)



        yield from bps.mv(geo.stblx2,samp_x2+7)  #move the  Sample Table X2 to xpos
        yield from bps.sleep(10)
        if usekibron_gid:
            trough = kibron
            if compress_gid: # to use compression mode
                target_pressure = one_pressure
                print('Compress before the GID')
                
                trough.update() # to update the kibron parameters
                if target_pressure - trough.pressure.get() > 0.5:
                    print(f'Target pressure is {target_pressure} mN/m')
                    print(f'Current pressure is {trough.pressure.get()} mN/m')
                    print('Need to compress!')
                    trough.runPressureManual(target_pressure = target_pressure, target_speed = 10)
                    ### codes below ro do a sh alignment
                # yield from det_exposure_time(1,1)
                # yield from sample_height_set_fine_o(detector=lambda_det)


        if gisaxs_run:
            print('Starting GISAXS measurement')
            
            for kk,slit_hg in enumerate(slit_hg_gisaxs):
                print('Slit horizontal gap is set to %.2f'%slit_hg)
                yield from bps.mv(S2.hg, slit_hg)
                # yield from bps.mv(geo.stblx2,samp_x2+7)  #move the  Sample Table X2 to xpos
                yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                yield from gisaxs_scan1(samp_name+f'_pressure{one_pressure}')


        # if xr_run:
        #     print('Starting XRR measurement')
        #     samp_name_new = samp_name+f'_pressure{one_pressure}'

        #     yield from bps.mv(geo.stblx2,samp_x2+2)  #move the  Sample Table X2 to xpos
        #     yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
        #     yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points

        #     yield from one_xrr_kibron(samp_name_new, expo_time = 5, wait_time = 10, usekibron = True, trough = kibron, compress = True, target_pressure = one_pressure)

        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    # print('Here is the sample height offsets after alignment:')
    # print(samp_sh_offset)


    kibron.close()
    print('Kibron socket is closed.')


    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    # yield from he_off()# stops the He flow
    yield from shclose()



def one_xrr_kibron_constantP():

    '''
    Use the constant pressure mode from the kibron (using laptop)
    '''

    proposal_id("2022_3","310438_satija")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # open the He flow
    detector=lambda_det


    HOST, PORT = "10.66.91.26", 9897 ## HZ
    sock = mtx.connect(HOST, PORT)
    device = mtx.Trough(sock)
    kibron = KibronTrough(device, sock)

    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)

    yield from bps.mv(S2.hg, 0.3)


    samp_name = 'MEA19_0p1mMCd_0p1mMNa_constantP40'
    samp_x2 = -42



    
    yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos
    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points

    yield from one_xrr_kibron(samp_name, expo_time = 5, wait_time = 10, usekibron = True, trough = kibron, compress = False)

    kibron.close()
    print('Kibron socket is closed.')


    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    # yield from he_off()# stops the He flow
    # yield from shclose()





def one_xrr_kibron(name,expo_time = 10, wait_time = 10, usekibron = False, trough = None, compress = False, target_pressure = 0, tiltx=0, detector=lambda_det):
   #     '''Conduct reflectivity measurments'''
    print("file name=",name)    
    yield from bps.mv(abs2,5)
    yield from bps.mv(abs3,0)
    yield from bps.mv(shutter,1) # open shutter


    yield from xr_scan_kibron(name, 
                expo_time = expo_time, 
                wait_time = wait_time, 
                usekibron = usekibron, 
                trough = trough, 
                compress = compress,
                target_pressure = target_pressure, 
                detector=detector) 

    yield from bps.mv(shutter,0) # open shutter
    yield from mabt(0.2,0.2,0)





def xr_scan_kibron(name, expo_time = 10, wait_time = 10, usekibron = False, trough = None, compress = False, target_pressure = 0, detector=lambda_det):
 

    # #14.4kev for running kibron
    # alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72,  1.2,  1.9]
    # alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.36,  2.0,  2.8]
    # number_points_list = [   11,   11,   15,   11,    9,    9,    10]
    # auto_atten_list =    [    6,    5,    4,    3,    2,    1,     0]
    # s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]

    # exp_time_list =      [    5,   5,     5,    5,     5,   5,     5]
    # # exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]

    # precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2, 0.2,   0.2]

    # # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    # wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]

    # x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  -0.5]
    # x2_offset_stop_list= [    0,   0,     0,    0,     0, -0.5, -2.5]
    # block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]


    #14.4kev for running kibron, keep 1 abs
    alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72, 1.60,  2.08]
    alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.60, 2.08,  2.78]
    number_points_list = [   11,   11,   15,   11,   12,     7,    8]
    auto_atten_list =    [    6,    5,    4,    3,    2,     1,    1]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]

    exp_time_list =      [    5,   5,     5,    5,     5,   5,    30]
    # exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]

    precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2, 0.2,   0.2]

    # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]

    x2_offset_start_list=[    0,   0,     0,    0,     0,   0,     3]
    x2_offset_stop_list= [    0,   0,     0,    0,     0,   3,     6]
    block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]




    # #14.4kev for test
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
    yield from reflection_scan_full_kibron(scan_param=scan_p, 
        usekibron = usekibron, 
        trough = trough, 
        compress = compress,
        target_pressure = target_pressure, 
        detector=detector, 
        md={'sample_name': name},

        tilt_stage=False,)



def reflection_scan_full_kibron(scan_param, md=None, detector=lambda_det, tilt_stage=False, stth_corr_par=None, usekibron = False, trough = None, compress = False, target_pressure=0):
    """
    Macros to set all the parameters in order to record all the required information for further analysis,
    such as the attenuation factors, detector='lambda_det'
    :param detector: A string which is the detector name
    :type detector: string, can be either 'lambda_det' or 'pilatus100k'
    """
    # Tom's way of checking to see if all lists are the same length
    N = None
    for k, v in scan_param.items():
        if N is None:
            N = len(v)
        if N != len(v):
            raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

    unhinted_ref() ## change all hinted settings to 'normal'
    
 #XF:12ID1-ES{Det:Lambda}ROI1:MinX
    # Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_scan',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
               'detector': detector.name, 
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
               }
    base_md.update(md or {})
    global attenuation_factor_signal, exposure_time, attenuator_name_signal, default_attenuation
    attenuator_name_signal = Signal(name='attenuator_name', value='abs1',kind='normal')
    attenuation_factor_signal = Signal(name='attenuation', value=1e-7,kind='normal')
    exposure_time = Signal(name='exposure_time', value=1)
    default_attenuation = Signal(name='default-attenuation', value=1e-7)
    # Disable the plot during the reflectivity scan
    bec.disable_plots()
    # Bluesky command to start the document
    # moved this line so we get a single UID per sub-scan
    # yield from bps.open_run(md=base_md)
    x2_nominal= geo.stblx2.position
    blocky_nominal= block.y.position ## add blocky pos (HZ, 06102022)

    sample_name = md['sample_name']
    for i in range(N):
        if usekibron:
            if trough is None:
                print('Trough is not defined; it should be set to Kibron.')
                raise ValueError('Trough is not defined!')
            else:
                if compress: # to use compression mode
                    trough.update() # to update the kibron parameters
                    if target_pressure - trough.pressure.get() > 0.5:
                        print(f'Target pressure is {target_pressure} mN/m')
                        print(f'Current pressure is {trough.pressure.get()} mN/m')
                        print('Need to compress!')
                        trough.runPressureManual(target_pressure = target_pressure, target_speed = 10)

                        ### codes below ro do a sh alignment
                        yield from det_exposure_time(1,1)
                        yield from sample_height_set_fine_o(detector=lambda_det)

                        alpha_start = scan_param['start'][0]
                        yield from mabt(alpha_start, alpha_start, 0)
                        yield from bps.sleep(5)

        print('%sst set starting'%i)
        md={'sample_name': sample_name,
            'sample_name_scan': sample_name +f'_scan{i}'}
        base_md.update(md or {})
        yield from bps.open_run(md=base_md)
        yield from bps.sleep(3) 
  #      print(scan_param)
        yield from reflection_scan(scan_param,i, detector=detector, md=md, tilt_stage=tilt_stage, usekibron = usekibron, trough = trough, compress = False, target_pressure=target_pressure, x2_nominal=x2_nominal,blocky_nominal=blocky_nominal)                      
        yield from bps.close_run()
        print('%sst set done'%i)


    # Bluesky command to stop recording metadata
    #moved this to inside the loop
    # yield from bps.close_run()
    bec.enable_plots()
    # puts in absorber to protect the detctor      
    yield from bps.mv(abs2, 5)
    quadem.averaging_time.put(1)
    print('The reflectivity scan is over')
    hinted_ref() ## change hinted settings






def run_kibron_compress(target_pressure=10):

    HOST, PORT = "10.66.91.26", 9897 ## HZ
    sock = mtx.connect(HOST, PORT)
    device = mtx.Trough(sock)
    kibron = KibronTrough(device, sock)
    kibron.runPressureManual(target_pressure=target_pressure, target_speed = 20)
    kibron.close()


def stop_kibron():
    HOST, PORT = "10.66.91.26", 9897 ## HZ
    sock = mtx.connect(HOST, PORT)
    device = mtx.Trough(sock)
    kibron = KibronTrough(device, sock)
    kibron.device.call("StepStop")
    kibron.device.call("StopMeasure")
    kibron.close()

def test_kibron():

    HOST, PORT = "10.66.91.26", 9897 ## HZ
    sock = mtx.connect(HOST, PORT)
    device = mtx.Trough(sock)
    kibron = KibronTrough(device, sock)

    # Bluesky command to start the document
    base_md = {'plan_name': 'kibron'}
    yield from bps.open_run(md=base_md)
    yield from bps.trigger_and_read([kibron], name='primary')
    yield from bps.close_run()
    kibron.close()



def run_nist():

    proposal_id("2022_3","310438_satija")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # open the He flow
    detector=lambda_det


    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)


    #### Run 2022-11-30
    # samp_name = 'MEA19_0p1mMCd_0p1mMNa_pH6' # _25uL_0p92mgpml, G4_medium'

    # pressure_list = [5]
    # samp_x2_list = [-72]

    # pressure_list = [15, 20, 25, 30, 35]
    # samp_x2_list = [-64+step*8 for step in range(len(pressure_list))]  #

    # pressure_list = [15]
    # samp_x2_list = [-64] 

    # pressure_list = [20]
    # samp_x2_list = [-56] 

    # pressure_list = [25]
    # samp_x2_list = [-48] 

    # pressure_list = [30]
    # samp_x2_list = [-40] 

    #### 2022-12-01, night run
    samp_name = 'MEA19_0p1mMCd_10mMPB_pH6' # _25uL_0p92mgpml, G4_medium'

    # pressure_list = [7] # without compression
    # samp_x2_list = [-74] 

    pressure_list = [20,  20,  20,  20] # constant pressure
    samp_x2_list = [-64, -56, -48, -40] 



    xr_run = True
    gisaxs_run = True

    slit_hg_gisaxs = [0.2]

    # run_cycle = 1
    for ii,(one_pressure, samp_x2) in enumerate(zip(pressure_list,samp_x2_list)):
        runNum = ii+1


        yield from bps.mv(S2.hg, 0.3)
        yield from bps.mv(geo.stblx2,samp_x2)  #move the  Sample Table X2 to xpos
        yield from check_ih()
        yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)

        yield from sample_height_set_fine_o(detector=detector) #scan the detector arm height from -0.2 to 0.2 with 21 points

        if xr_run:
            print('Starting XRR measurement')
            samp_name_new = samp_name+f'_pressure{one_pressure}'
            yield from xr_scan_plain(samp_name_new, wait_time = 25)


        if gisaxs_run:
            print('Starting GISAXS measurement')
            
            for kk,slit_hg in enumerate(slit_hg_gisaxs):
                print('Slit horizontal gap is set to %.2f'%slit_hg)
                yield from bps.mv(S2.hg, slit_hg)
                yield from bps.mv(geo.stblx2,samp_x2+7)  #move the  Sample Table X2 to xpos
                yield from bps.sleep(3)
                yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
                yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                yield from gisaxs_scan1(samp_name+f'_pressure{one_pressure}')



    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    # yield from he_off()# stops the He flow
    yield from shclose()




def xr_scan_plain(name, wait_time = 10, detector=lambda_det):
 

    #14.4kev for running kibron, keep 1 abs
    alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72, 1.60,  2.08]
    alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.60, 2.08,  2.78]
    number_points_list = [   11,   11,   15,   11,   12,     7,    8]
    auto_atten_list =    [    6,    5,    4,    3,    2,     1,    1]
    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]

    exp_time_list =      [    5,   5,     5,    5,     5,   5,    30]
    # exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]

    precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2, 0.2,   0.2]

    # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]

    x2_offset_start_list=[    0,   0,     0,    0,     0,   0,     3]
    x2_offset_stop_list= [    0,   0,     0,    0,     0,   3,     6]
    block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]






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
        detector=detector, 
        tilt_stage=False,)






#a comment goes here  test and again
def ocko_1():
    yield from bps.mv(lambda_det.oper_mode,1)
    yield from bps.mv(lambda_det.low_thr,6.5)


    proposal_id("2022_3","311547_ocko")
    yield from bps.sleep(5)
    yield from shopen()
    yield from he_on() # starts the He flow
    detector=lambda_det

    samp_name_dict = {
     #   1: 'ODA_10mN_2mMKCl', 
     #   2: 'PFDA_100mMZnCl2_50ppm_1', 
     #   3: 'ODA_10mN_2mMKI',


         1: 'Water_Trough_1',
        # 1: 'DPPC_manulCompress_thinBarrier_P33', ## 40 mL water, 11uL 1mg/mL DPPC (should use 37mL water)
        #1: 'KI_10mM'

    }

    sam_x2_pos ={
        # 1: -56,
        1: 0,
        # 1: -73, #-66, #-68flat from -65 to -60  #-65, #-62, # (-63.5,-6.14), # front
        # 2: -17, #-19, flat from -15 to -10 # -9, # (-9, 3.5), # middle trough
        # 3: 39, #32 flat from 34.5 to 39.5  #42, # (38, 5.1), # back
    }

    sam_sh_offset ={
        # 1: -105.198,
        1: -26.68,
        # 2: -26,
        # 3: -26.76,
    }

    xr_run_dict = {
        1: True,
        2: False,
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
                yield from one_xrr_new(samp_name+f'_run{ii+1}',samp_x2)
            
            if xrf_run_dict[key]:
                print('Starting XRF measurement')
                yield from xrf_scan1(samp_name)

            if gisaxs_run_dict[key]:
                print('Starting GISAXS measurement')

                for kk,slit_hg in enumerate(slit_hg_gisaxs):
                    print('Slit horizontal gap is set to %.2f'%slit_hg)
                    yield from bps.mv(S2.hg, slit_hg)
                    yield from bps.mv(geo.stblx2,samp_x2+3+slit_hg*kk*2)  #move the  Sample Table X2 to xpos
                    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
                    yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
                    yield from gisaxs_scan1(samp_name+f'slit_hg_{slit_hg}')

        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
    yield from bps.mv(geo.det_mode,1)
    yield from mabt(0,0,0)

    yield from he_off()# stops the He flow
    yield from shclose()




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
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s

            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runB{ii+1}',expo_time = 5, wait_time = 10, reverse_mode = False)
            yield from bps.mv(abs2,6)
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s

            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runC{ii+1}',expo_time = 5, wait_time = 30, reverse_mode = False)
            yield from bps.mv(abs2,6)
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
            
            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runD{ii+1}',expo_time = 30, wait_time = 10, reverse_mode = False)
            yield from bps.mv(abs2,6)
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s

            yield from check_ih()
            yield from check_phi() #resets phi, the crystal deflector at mab(0,0,0)
            yield from sample_height_set_coarse(detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
            yield from sample_height_set_fine_o(detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
            yield from one_xrr_new(samp_name+f'_runE{ii+1}',expo_time = 5, wait_time = 30, reverse_mode = True)
            yield from bps.mv(abs2,6)
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s


        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
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
            yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s

  
        # print("Starting incubation for 1 hour...")  
        # yield from bps.sleep(1*60*60)

    yield from det_exposure_time_new(detector, 1.0, 1.0) # rest exposure time to 1s
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
    yield from bpp.subs_wrapper(bp.rel_scan([detector],sh,-0.15,0.15,21,per_step=shutter_flash_scan), local_peaks)
    print("at #1")
    tmp2 = local_peaks.cen #get the height for roi2 of detector.name with max intens
    print("at #2")
    yield from bps.mv(sh,tmp2-0.00)
    yield from set_sh(tmp1)
    Msg('reset_settle_time', sh.settle_time, 0)


def xr_scan1(name, expo_time = 10, wait_time = 10, reverse_mode = False):
 

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


    #14.4kev for testing exposure time and reverse mode
    alpha_start_list =   [ 0.03, 0.12, 0.18, 0.40,  0.72,  1.2,  1.9]
    alpha_stop_list =    [ 0.13, 0.22, 0.46, 0.80,  1.36,  2.0,  2.8]
    number_points_list = [   21,   21,   15,   11,    9,    9,    10]
    auto_atten_list =    [    6,    5,    4,    3,    2,    1,     0]

    s2_vg_list =         [ 0.04, 0.04, 0.04,  0.04, 0.04, 0.04, 0.04]
    # exp_time_list =      [    5,   5,     5,    5,     5,   5,     5]
    exp_time_list =      [expo_time for _ in range(len(alpha_start_list))]
    
    precount_time_list=  [  0.2, 0.2,   0.2,  0.2,   0.2, 0.2,   0.2]
    # wait_time_list=      [   10,  10,    10,   10,    10,  10,    10]
    wait_time_list=      [wait_time for _ in range(len(alpha_start_list))]

    x2_offset_start_list=[    0,   0,     0,    0,     0,   0,  -0.5]
    x2_offset_stop_list= [    0,   0,     0,    0,     0, -0.5,   -2]
    block_offset_list=   [    0,   0,     0,    0,     0,   0,     0]


    if reverse_mode:
        alpha_start_list, alpha_stop_list = alpha_stop_list, alpha_start_list



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
    number_points_list = [    8,    2,    6,    5]
    auto_atten_list =    [    1,    1,    2,    2] 
    s2_vg_list =         [ 0.02, 0.02, 0.02, 0.02] 
    exp_time_list =      [   20,   10,   10,   10]
    precount_time_list=  [  0.1,  0.1,  0.1,  0.1]
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
    beam_stop_x             = [-63.8,-63.8]
    beam_stop_y             = [10,10]


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
    exp_time_list           = [5,5,5] # [20,20]
    x2_offset_list          = [-0.4,0,0.4]
    atten_2_list            = [0,0,0]
    wait_time_list          = [5,5,5]
    beam_stop_x             = [-64,-64,-64]
    beam_stop_y             = [20,20,20]


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
                                alphai = 0.06)

    yield from bps.mv(abs2,5)

