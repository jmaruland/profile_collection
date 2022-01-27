def reflection_fluorescence_scan_full(scan_param, md=None, detector=xs, tilt_stage=False):
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
    


    base_md = {'plan_name': 'reflection_fluorescence_scan',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
               'detector': detector.name, 
               'energy': energy.energy.position,
               'geo_param': [geo.L1.get(), geo.L2.get(), geo.L3.get(), geo.L4.get()],
               'slit_s1': [S1.top.position - S1.bottom.position, S1.outb.position - S1.inb.position],
               'slit_s2': [S2.vg.position, S2.hg.position],
               'x2': [geo.stblx2.position],
               'tilt stage': tilt_stage,
               }
    base_md.update(md or {})
    global attenuation_factor_signal, exposure_time, attenuator_name_signal, default_attenuation
    attenuator_name_signal = Signal(name='attenuator_name', value='abs1')
    attenuation_factor_signal = Signal(name='attenuation', value=1e-7)
    exposure_time = Signal(name='exposure_time', value=1)
    default_attenuation = Signal(name='default-attenuation', value=1e-7)
    # Disable the plot during the reflectivity scan
    bec.disable_plots()
    # Bluesky command to start the document
    yield from bps.open_run(md=base_md)
    x2_nominal= geo.stblx2.position

    for i in range(N):
        print('%sst set starting'%i)
        yield from bps.sleep(3) 
        print(scan_param)
        yield from reflection_fluorescence_scan(scan_param,i, detector=detector, md=md, tilt_stage=tilt_stage, x2_nominal=x2_nominal)                      
        print('%sst set done'%i)

    # Bluesky command to stop recording metadata
    yield from bps.close_run()
    bec.enable_plots()
    # puts in absorber to protect the detctor      
    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')
print(f'Loading {__file__}')
all_area_dets_fluo = [quadem, xs, AD1, AD2, o2_per]

 
@bpp.stage_decorator(all_area_dets_fluo)
def reflection_fluorescence_scan(scan_param, i, detector='xs', md={}, tilt_stage=False,x2_nominal=0):
        
    alpha_start =   scan_param["start"][i]
    alpha_stop =    scan_param["stop"][i]
    number_points = scan_param["n"][i]
    atten_2 =       scan_param["atten"][i]
    s2_vg =         scan_param["s2vg"][i]
    exp_time =      scan_param["exp_time"][i]
    precount_time=  scan_param["pre_time"][i]
    wait_time =     scan_param["wait_time"][i]
    x2_offset_start =     scan_param["x2_offset_start"][i]
    x2_offset_stop =     scan_param["x2_offset_stop"][i]

    
    print(alpha_start,"----",alpha_stop,atten_2)
    for alpha in np.linspace(alpha_start, alpha_stop, number_points):
        # Move to the good geometry position
        if tilt_stage:
             print('tilt stage')
             yield from nab(alpha, alpha)
        else:
            print('regular')
         #   yield from mabt(alpha, alpha, 0)
        #yield from mabt(geo.alpha=0,geo.samchi=x,geo.beta=2*x)
        fraction  = (alpha-alpha_start)/(alpha_stop-alpha_start)
        x2_fraction =fraction*(x2_offset_stop-x2_offset_start)
        # Set the exposure time to the define exp_time for the measurement
        yield from det_exposure_time(exp_time, exp_time)
        yield from bps.mv(exposure_time, exp_time)
        yield from bps.mv(S2.vg,s2_vg)
        yield from bps.mv(geo.stblx2,x2_nominal+x2_fraction)
        yield from bps.mv(abs2, atten_2)
        yield from bps.sleep(wait_time)
        yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][atten_2])
        yield from bps.mv(attenuator_name_signal, att_bar1['name'][atten_2])
        # print(all_area_dets_fluo)

        # ToDo: is that really usefull now
        if alpha == alpha_start:
            print("first point in the scan")
            yield from bps.mv(shutter, 1)
            yield from bps.trigger_and_read(all_area_dets_fluo, name='precount')
            yield from bps.mv(shutter, 0)
            yield from bps.sleep(wait_time)
            print("finished dummy count")

        yield from bps.mv(shutter, 1)
        yield from bps.sleep(1)
        yield from bps.trigger_and_read(all_area_dets_fluo +
                                        [geo] + 
                                        [S2] +
                                        [attenuation_factor_signal] +
                                        [attenuator_name_signal] +
                                        [exposure_time],
                                        name='primary')
        yield from bps.mv(shutter, 0)
        

    
    # for water 9.7 keV
    # alpha_start_list =   [ 0.05, 0.15, 0.24, 0.5,  0.8,  1.3,  2.0]
    # alpha_stop_list =    [ 0.15, 0.24, 0.50, 0.8,  1.3,  2.0,  3.6]
    # number_points_list = [   11,   10,   14,   7,   11,    7,   10]
    # auto_atten_list =    [    6,   5,    4,    3,    2,    1,   0 ] 
    # s2_vg_list =         [0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04] 
    # exp_time_list =      [    4,   4,    4,    4,    4,    4,   4 ]
    # precount_time_list=  [  0.1, 0.1,  0.1,  0.1,  0.1,  0.1,  0.1]

    # for NP on water 9.7 keV
     #   alpha_start_list =   [ 0.05, 0.15, 0.24, 0.5,  0.8,  1.4]
     #   alpha_stop_list =    [ 0.15, 0.24, 0.50, 0.8,  1.4,  1.8]
     #   number_points_list = [   11,   10,   14,  11,   16,   11]
     #   auto_atten_list =    [    6,   5,    4,    3,    2,    1] 
     #   s2_vg_list =         [0.04, 0.04, 0.04, 0.04, 0.04, 0.04] 
     #   exp_time_list =      [    4,   4,    4,    4,    4,    4]
     #   precount_time_list=  [  0.1, 0.1,  0.1,  0.1,  0.1,  0.1]

     #  sapphire air 9.7kev
      #  alpha_start_list =   [ 0.05, 0.25, 0.30, 0.55,  0.8,  1.3,  2.5]
      #  alpha_stop_list =    [ 0.25, 0.30, 0.55, 0.80,  1.3,  2.5,  5.1]
      #  number_points_list = [    5,   6,    6,     6,    6,    6,   7]
      #  auto_atten_list =    [    5,   4,    3,     2,    1,    0,   0] 
      #  s2_vg_list =         [0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02] 
      #  exp_time_list =      [    4,   4,    4,    4,    4,    4,   4 ]
      #  precount_time_list=  [  0.1, 0.1,  0.1,  0.1,  0.1,  0.1,  0.1]

 #  sapphire air 23kev
      #  alpha_start_list =   [ -0.05, -0.12, -0.20, -0.30,  -0.6,  -3.2]
      #  alpha_stop_list =    [ -0.12, -0.20, -0.30, -0.60,  -3.2,  -4.0]
      #  number_points_list = [    8,   5,    6,     7,    7,   5]
      #  auto_atten_list =    [    4,   3,    2,     1,    0,   0] 
      #  s2_vg_list =         [0.04, 0.04, 0.04, 0.04, 0.04, 0.04] 
      #  exp_time_list =      [    4,   4,    4,    4,    20,    20]
      #  precount_time_list=  [  0.1, 0.1,  0.1,  0.1,  0.1,  0.1]

    # for water 16.1 keV
    #    alpha_start_list =   [ 0.03, 0.06, 0.10, 0.14,  0.30,  0.5,  1.0]
    #    alpha_stop_list =    [ 0.06, 0.10, 0.14, 0.30,  0.50,  1.0,  2.2]
    #    number_points_list = [    4,   5,    5,    9,    7,    10,   20]
    #    auto_atten_list =    [    5,   5,    4,    3,    2,    1,   0 ] 
    #    s2_vg_list =         [0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04] 
    #    exp_time_list =      [    4,   4,    4,    4,    4,    4,   4 ]
    #    precount_time_list=  [  0.1, 0.1,  0.1,  0.1,  0.1,  0.1,  0.1]

     


