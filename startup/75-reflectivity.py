def reflection_scan_full(scan_param, md=None, detector=lambda_det, tilt_stage=False, stth_corr_par=None):
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
    yield from bps.open_run(md=base_md)
    x2_nominal= geo.stblx2.position
    blocky_nominal= block.y.position ## add blocky pos (HZ, 06102022)

    for i in range(N):
        print('%sst set starting'%i)
        yield from bps.sleep(3) 
  #      print(scan_param)
        yield from reflection_scan(scan_param,i, detector=detector, md=md, tilt_stage=tilt_stage, x2_nominal=x2_nominal,blocky_nominal=blocky_nominal)                      
        print('%sst set done'%i)

    # Bluesky command to stop recording metadata
    yield from bps.close_run()
    bec.enable_plots()
    # puts in absorber to protect the detctor      
    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')
    hinted_ref() ## change hinted settings
print(f'Loading {__file__}')
all_area_dets = [quadem, lambda_det, AD1, AD2, o2_per]

 
@bpp.stage_decorator(all_area_dets)
def reflection_scan(scan_param, i, detector='lamda_det', md={}, tilt_stage=False,x2_nominal=0,blocky_nominal=0):
        
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
    block_offset   =     scan_param["beam_block_offset"][i]

# setting up so that if alpha is moved negative that there is an extra wait
    alpha_old=5
    print(alpha_start,"----",alpha_stop,atten_2)
    for alpha in np.linspace(alpha_start, alpha_stop, number_points):
        # Move to the good geometry position
        if tilt_stage:
             yield from nab(alpha, alpha,0.022)
        else:
            if alpha >= alpha_old:
                yield from mabt(alpha, alpha, 0)
            else:
                yield from mabt(alpha-0.1, alpha-0.1, 0)
                yield from mabt(alpha, alpha, 0)


        #yield from mabt(geo.alpha=0,geo.samchi=x,geo.beta=2*x)
        fraction  = (alpha-alpha_start)/(alpha_stop-alpha_start)
        x2_fraction =fraction*(x2_offset_stop-x2_offset_start) + x2_offset_start ## Need to add x2_offset_start (HZ)
        # Set the exposure time to the define exp_time for the measurement
        yield from det_exposure_time(exp_time, exp_time)
        yield from bps.mv(exposure_time, exp_time)
        yield from bps.mv(S2.vg,s2_vg)
        yield from bps.mv(geo.stblx2,x2_nominal+x2_fraction)
        # yield from bps.mv(block.y,x2_nominal+x2_fraction+block_offset) # large trough
        # yield from bps.mv(block.y,blocky_nominal+x2_fraction+block_offset) # small trough, multiple slits
        if x2_offset_stop != x2_offset_start: 
            yield from bps.sleep(2) # sleep every time after x2 move (HZ)
        yield from bps.sleep(wait_time)    
        if alpha <= alpha_old:
            yield from bps.sleep(10)  
            print("wating an extra 10 sec")  
        alpha_old =alpha


        #Attenuator MODE
        # Set the absorber time to the define exp_time for the measurement
        # AUTO MODE FIGURES OUT THE APPROPIRAE ATTENUATOR BY DOING TESTS WITH HIGH ATTENUATOR NUMBERS
        if atten_2 == "auto":
            yield from calc_att_auto(alpha, precount_time=precount_time,detector=detector)
        # CALC MODE FIGURES OUT THE APPROPIRAE ATTENUATOR USING A FORMULA
        elif atten_2 == "calc":
            att = calc_att_from_ai(alpha)
            yield from bps.mv(abs2, atten_2)
        # THE ATTENUATOR NUMBER IS GIVEN BUT THE OUTPUT ON THE ATTENUATO VALU IS INCORRECT
        else:            
            if isinstance(atten_2,int):
                att=atten_2
                yield from bps.mv(abs2, att)
                
            # else:
            #     print('The absorber should be auto, calc, or int. Here will use auto.')
            #     yield from calc_att_auto(alphai, precount_time=1)
        #set metadata
        # IF NOT EQUAL TO AUTO SETTING THE META DATA, THIS CHOOSES THE att_bar data structure to use
        #  THIS IS INCORRECT SINCE ATTENUATOR VALUES ARE NOT KNOWN.
        if atten_2 != "auto":
            yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][att])
            yield from bps.mv(attenuator_name_signal, att_bar1['name'][att])

        # ToDo: is that really usefull now
       # if alpha == alpha_start:
       #     print("first point in the scan")
       #     yield from bps.mv(shutter, 1)
       #     yield from bps.trigger_and_read(all_area_dets, name='precount')
       #     yield from bps.mv(shutter, 0)
       #     yield from bps.sleep(wait_time)
       #     print("finished dummy count")

        yield from bps.mv(shutter, 1)
    #    yield from bps.sleep(2)
        yield from det_exposure_time(1,1)
        yield from bps.mv(exposure_time, 1)
        yield from bps.trigger_and_read([quadem], name='precount')
        yield from det_exposure_time(exp_time, exp_time)
        yield from bps.mv(exposure_time, exp_time)
        yield from bps.trigger_and_read(all_area_dets +
                                        [geo] + 
                                        [S2] +
                                        [attenuation_factor_signal] +
                                        [attenuator_name_signal] +
                                        [exposure_time],
                                        name='primary')
        yield from bps.mv(shutter, 0)
        

def calc_att_from_ai(alphai):
    if alphai<0.15:
        return 6
    elif 0.13<alphai<0.16:
        return 5
    elif 0.16<alphai<0.25:
        return 4
    elif 0.25<alphai<0.40:
        return 3
    elif 0.4<alphai<0.6:
        return 2
    elif 0.6<alphai<1.0:
        return 1
    elif alphai>1.0:
        return 0

# THIS DOES A PRECOUNT WITH A HIGH ATTUNATOR VALUE TO DETERMINE THE BEST ATTENUATOR TO USE
def calc_att_auto(alphai, precount_time=1,detector="lambda_det"):
    # Move the default attenuator in for the pre-count based on the value of attenuation define in default_attenuation
    def_att = yield from put_default_absorbers(energy.energy.position,
                                               default_attenuation=default_attenuation.get())
    # Set the exposure time to for the pre-count
    yield from det_exposure_time(precount_time, precount_time)
    # Take the pre-count data
    yield from bps.mv(shutter, 1)
    ret = yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.mv(shutter, 0)
    if ret is None:
        print('No count on the detector')
    else:
        # Read the maximum count on a pixel from the detector
        i_max = ret['%s_stats4_max_value'%detector]['value']
        # look at the maximum count of the pre-count and adjust the default attenuation, can do multiple iterations
        while (i_max < 100 or i_max > 40000) and default_attenuation.get() < 1:
            if i_max > 40000:
                # If i_max to high, attenuate more
                yield from bps.mv(default_attenuation, default_attenuation.get() / 10)
            elif i_max < 100:
                # If i_max to low, attenuate less
                yield from bps.mv(default_attenuation, default_attenuation.get() * 10)
            else:
                print('You should not be there!')
                break   
            ret = yield from bps.trigger_and_read(area_dets,
                                                    name='precount')
            yield from bps.mv(shutter, 0)
                                    
            # Re-read the maximum count on a pixel from the detector
            i_max = ret['%s_stats4_max_value'%detector]['value']                    
        # Adjust the absorbers to avoid saturation of detector
        best_at, attenuation_factor, best_att_name = yield from calculate_and_set_absorbers(energy=energy.energy.position,
                                                                                            i_max=i_max,
                                                                                            att=def_att,
                                                                                            precount_time=precount_time)
        
        # Upload the attenuation factor for the metadata

        yield from bps.mv(attenuation_factor_signal, attenuation_factor)
        yield from bps.mv(attenuator_name_signal, best_att_name)

    
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


