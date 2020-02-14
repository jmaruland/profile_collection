area_dets = [pilatus100k]
all_area_dets = [pilatus100k, quadem, geo, S3]

@bpp.stage_decorator(all_area_dets)
def reflection_scan(alpha_start, alpha_stop, num, energy=9660, exp_time=1, md=None):
    #Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_scan',
                'exposure_time': exp_time,
                'energy': energy,
            # ...
           }
    base_md.update(md or {})
    bec.disable_plots()
    yield from bps.open_run(md=base_md)
    
    #creation of a fignal to record the attenuation
    attenuation_factor_signal = Signal(name='attenuation', value = 1)
    exposure_time = Signal(name='exposure_time', value = 1)


    for alpha in np.linspace(alpha_start, alpha_stop, num):
        #move to the good geometry position
        yield from mabt(alpha, alpha, 0)
        yield from bps.sleep(5)

        #Move the default attenuator in for the precount
        def_att = yield from put_default_absorbers(energy)

        #set the exposure time to 0.1 for the precount
        det_exposure_time(0.1, 0.1)

        #Take the pre-count data
        yield from bps.mv(shutter,1)
        ret = yield from bps.trigger_and_read(area_dets, name='precount')
        yield from bps.mv(shutter,0)
        
        if ret is None:
            # in simulation mode
            continue
        else:
            #Read the maximum count on a pixel from the detector
            i_max = ret['pilatus100k_stats2_max_value']['value']
            print('imax', i_max)
            
            #Adjust the absorbers to avoid saturation of detector
            best_att, attenuation_factor = calculate_and_set_absorbers(energy, i_max, def_att,
                                                                        precount_time=0.1, exp_time=exp_time)
            
            if alpha > 1.5:
                yield from set_attenuator(0)
                attenuation_factor_signal.value = 1

            else:
                yield from set_attenuator(best_att)
                #upload the attenuation factor for the metadata
                attenuation_factor_signal.value = attenuation_factor

        #set the exposure time to the define exp_time for the measurment
        det_exposure_time(exp_time, exp_time)
        exposure_time.value = exp_time
        yield from bps.mv(shutter,1)
        yield from bps.sleep(1) # add this because the QuadEM I0
        yield from bps.trigger_and_read(all_area_dets + [attenuation_factor_signal] + [exposure_time], name='primary')
        yield from bps.mv(shutter,0)
    
    #Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')

def expert_reflection_scan(energy=9660, md=None):

    # yield from bps.mvr(geo.stblx2, -1) # move stable X2
    alpha_start, alpha_stop, num, exp_time = 0.01, 0.2, 21, 1
    yield from reflection_scan(alpha_start, alpha_stop, num, energy=energy, exp_time=exp_time, md=md)

    yield from bps.mvr(geo.stblx2, -1) # move stable X2
    alpha_start, alpha_stop, num, exp_time = 0.2, 0.6, 21, 1
    yield from reflection_scan(alpha_start, alpha_stop, num, energy=energy, exp_time=exp_time, md=md)

    yield from bps.mvr(geo.stblx2, -1) # move stable X2
    alpha_start, alpha_stop, num, exp_time = 0.6, 1, 21, 1
    yield from reflection_scan(alpha_start, alpha_stop, num, energy=energy, exp_time=exp_time, md=md)
    
    yield from bps.mvr(geo.stblx2, -1) # move stable X2
    alpha_start, alpha_stop, num, exp_time = 1, 2, 21, 1
    yield from reflection_scan(alpha_start, alpha_stop, num, energy=energy, exp_time=exp_time, md=md)
    
    yield from bps.mvr(geo.stblx2, -1) # move stable X2
    alpha_start, alpha_stop, num, exp_time = 2, 4, 21, 10
    yield from reflection_scan(alpha_start, alpha_stop, num, energy=energy, exp_time=exp_time, md=md)


@bpp.stage_decorator(all_area_dets)
def gid(energy=9660, exp_time=0.1, md=None):
    #Bluesky command to record metadata
    base_md = {'plan_name': 'gid',
                'exposure_time': exp_time,
                'energy': energy,
            # ...
           }
    base_md.update(md or {})
    bec.disable_plots()
    yield from bps.open_run(md=base_md)
    
    #creation of a fignal to record the attenuation
    attenuation_factor_signal = Signal(name='attenuation', value = 1)
    exposure_time = Signal(name='exposure_time', value = 1)

    #Move the default attenuator in for the precount
    def_att = yield from put_default_absorbers(energy)

    #set the exposure time to 0.1 for the precount
    det_exposure_time(0.1, 0.1)

    #move to the good geometry position
    yield from bps.mv(shutter,0)
    yield from mabt(0.1,1,0.6) # gid poistion with beam stop
    yield from bps.sleep(5)
    yield from bps.mv(shutter,1)

    #Take the pre-count data
    ret = yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.mv(shutter,0)

    yield from set_attenuator(0)
    attenuation_factor_signal.value = 1

    #set the exposure time to the define exp_time for the measurment
    det_exposure_time(exp_time, exp_time)
    exposure_time.value = exp_time
    yield from bps.mvr(geo.stblx2, -1) # move stable X2
    print(exposure_time.value)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(all_area_dets + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from bps.mv(abs2, 4)
    yield from mabt(0.1,1,0) # gid poistion without beam stop
    yield from bps.sleep(5)
    exposure_time.value = 1
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(all_area_dets + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from mabt(0.1,1,-0.6) # gid poistion without beam stop
    yield from bps.sleep(5)
    exposure_time.value = 1
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(all_area_dets + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    #Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    yield from bps.mv(abs2, 5)
    print('The gid is over')


#ToDo: need to enter the good values here
def put_default_absorbers(energy):
    default_att, default_factor = best_att(0.00001, energy)

    if energy > 9000 and energy < 10000:
        yield from bps.mv(abs2, 2)
    else:
        raise ValueError('error: the energy entered is not correct')
    
    yield from set_attenuator(default_att)
    
    return default_factor


def calculate_and_set_absorbers(energy, i_max, def_att, precount_time=0.1, exp_time=1):
    #Need to enter the attenuation of each absorber at different energies
    i_max_pil = 500000
    print('test', def_att, i_max, precount_time)
    max_theo_precount = i_max / (def_att * precount_time)
    att_needed = 1/(max_theo_precount / (exp_time * i_max_pil))
    print('att_needed', att_needed)

    best_at, attenuation_factor = best_att(att_needed, energy)
    return best_at, attenuation_factor


def set_attenuator(best_att):
    print(best_att)
    att_pos = [0.3, 1, 2, 3, 4, 5, 6, 7]
    yield from bps.mv(abs2, att_pos[best_att])







area_dets = [pilatus100k]
all_area_dets = [pilatus100k, quadem, geo, S3]

@bpp.stage_decorator(all_area_dets)
def test_trirun(md=None):
    base_md = {'plan_name': 'test trigger_and_read methog',
        }
    base_md.update(md or {})

    bec.disable_plots()

    yield from bps.open_run(md=base_md)
    ret =  yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.trigger_and_read(all_area_dets, name='primary')
    
    ret =  yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.trigger_and_read(all_area_dets, name='primary')

    ret =  yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.trigger_and_read(all_area_dets, name='primary')
    yield from close_run()
    bec.enable_plots()

