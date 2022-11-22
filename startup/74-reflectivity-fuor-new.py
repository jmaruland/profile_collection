saturate = EpicsSignal("XF:12ID1-ES{Xsp:1}:C1_ROI1:Value_RBV", name="xs_sum")
#saturate.value
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
    # geo.th.user_readback.kind = 'normal'
    # geo.phi.user_readback.kind = 'normal'
    # geo.phix.user_readback.kind = 'normal'
    # geo.ih.user_readback.kind = 'normal'
    # geo.ia.user_readback.kind = 'normal'
    # geo.sh.user_readback.kind = 'normal'
    # geo.oh.user_readback.kind = 'normal'
    # geo.oa.user_readback.kind = 'normal'
    # geo.astth.user_readback.kind = 'normal'
    # geo.stblx.user_readback.kind = 'normal'
    # geo.oa.user_readback.kind = 'normal'
    # geo.tth.user_readback.kind = 'normal'
    # geo.chi.user_readback.kind = 'normal'
    # geo.astth.user_readback.kind = 'normal'
    unhinted_ref() ## change all hinted settings to 'normal'


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
#Initialize the fluorescence default set-up (i.e. abs to 1 and det mode to 4)
    yield from bps.mv(geo.det_mode,4)
    x2_nominal= geo.stblx2.position
#     #Set the fluorescence detector 
 
    
    for i in range(N):
        print('%sst set starting'%i)
        yield from bps.sleep(3) 
        print(scan_param)
        xs.settings.num_images.value=1
        print("number of frame is 1")
        yield from bps.mv(xs.capture_mode, 1)
        yield from bps.mv(xs.total_points, scan_param["n"][i])
        
        yield from reflection_fluorescence_scan(scan_param,i, detector=detector, md=md, tilt_stage=tilt_stage, x2_nominal=x2_nominal)                      
        print('%sst set done'%i)

    # Bluesky command to stop recording metadata
    yield from bps.close_run()
    bec.enable_plots()
    # puts in absorber to protect the detctor      
    yield from bps.mv(abs2, 5)
    print('The reflectivity_fluorescence scan is over')
    hinted_ref() ## change hinted settings
print(f'Loading {__file__}')
all_area_dets_fluo = [saturate, quadem, xs, AD1, AD2, o2_per]
# all_area_dets_fluo = [quadem, AD1, AD2, o2_per]

 
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
            yield from mabt(alpha, alpha, 0)
        #yield from mabt(geo.alpha=0,geo.samchi=x,geo.beta=2*x)
        fraction  = (alpha-alpha_start)/(alpha_stop-alpha_start)
        x2_fraction =fraction*(x2_offset_stop-x2_offset_start)
        # Set the exposure time to the define exp_time for the measuarement
        xs.settings.acquire_time.set(exp_time)
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
        # if alpha == alpha_start:
        #     print("first point in the scan")
        #     yield from bps.mv(shutter, 1)
        #     yield from bps.trigger_and_read(all_area_dets_fluo, name='precount')
        #     yield from bps.mv(shutter, 0)
        #     yield from bps.sleep(wait_time)
        #     print("finished dummy count")

        yield from bps.mv(shutter, 1)
        yield from bps.sleep(1)
        yield from bps.trigger_and_read(
                                        all_area_dets_fluo +
                                        [geo] + 
                                        [S2] +
                                        [attenuation_factor_signal] +
                                        [attenuator_name_signal] +
                                        [exposure_time],
                                        name='primary')
        yield from bps.mv(shutter, 0)
        

