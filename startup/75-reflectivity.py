print(f'Loading {__file__}')

# area_dets = [pilatus100k]
# all_area_dets = [pilatus100k, tetramm]

area_dets = [lambda_det]
all_area_dets = [lambda_det, quadem]

#@bpp.stage_decorator(area_dets)
@bpp.stage_decorator(all_area_dets)

def reflection_scan(alpha_start, alpha_stop, num, detector = 'lambda_det', precount_time = 1, exp_time=1, default_att = 1e-7, md=None):
    #creation of a signal to record the attenuation

    for alpha in np.linspace(alpha_start, alpha_stop, num):
        print('alpha', alpha)
        #move to the good geometry position
        yield from mabt(alpha, alpha, 0)
        # yield from bps.sleep(2) 
        yield from bps.sleep(5)


        #Move the default attenuator in for the precount
        def_att = yield from put_default_absorbers(energy.energy.position, default_attenuation = default_attenuation.value)

        #set the exposure time to 0.1 for the precount
        yield from det_exposure_time(precount_time, precount_time)

        #Take the pre-count data
        yield from bps.mv(shutter,1)
        ret = yield from bps.trigger_and_read(area_dets, name='precount')
        yield from bps.mv(shutter,0)
        
        print(ret)
        if ret is None:
            # in simulation mode
            print('not OK')
            continue
        else:
            #Read the maximum count on a pixel from the detector
            i_max = ret['%s_stats4_max_value'%detector]['value']

            while (i_max < 100 or i_max > 200000) and default_attenuation.value < 1:
                if i_max > 200000:
                    default_attenuation.value = default_attenuation.value / 10
                elif i_max < 100:
                    default_attenuation.value = default_attenuation.value * 10
                else:
                    print('You should not be there!')
                    break    
                def_att = yield from put_default_absorbers(energy.energy.position, default_attenuation = default_attenuation.value)

                #Re-take the pre-count data
                yield from bps.mv(shutter,1)
                ret = yield from bps.trigger_and_read(area_dets, name='precount')
                yield from bps.mv(shutter,0)

                #Re-read the maximum count on a pixel from the detector
                i_max = ret['%s_stats4_max_value'%detector]['value']
                        
            #Adjust the absorbers to avoid saturation of detector
            best_att, attenuation_factor, best_att_name = calculate_and_set_absorbers(energy.energy.position, i_max, def_att,
                                                                        precount_time=precount_time, exp_time=exp_time)
            
            yield from set_attenuator(best_att)
            #upload the attenuation factor for the metadata
            attenuation_factor_signal.value = attenuation_factor
            attenuator_name_signal.value = best_att_name


        #set the exposure time to the define exp_time for the measurment
        yield from det_exposure_time(exp_time, exp_time)
        exposure_time.value = exp_time
        yield from bps.mv(shutter,1)
        yield from bps.sleep(1) # add this because the QuadEM I0
        #monitor_count.value = tetramm.current3.mean_value.value
        #print(monitor_count.value)

        yield from bps.trigger_and_read(all_area_dets + [geo] + [attenuation_factor_signal] + [attenuator_name_signal] + [exposure_time],
                                        name='primary')
        yield from bps.mv(shutter,0)
        

def night_scan():
    yield from expert_reflection_scan(md={'sample_name': 'test_water10'})
    yield from expert_reflection_scan(md={'sample_name': 'test_water11'})
    yield from expert_reflection_scan(md={'sample_name': 'test_water12'})

def fast_scan():
    yield from expert_reflection_scan(md={'sample_name': 'water_reigler_fast1'})
   


def expert_reflection_scan(md=None, detector = 'lambda_det'):
    """
    detector can be either lambda_det or pilatus100k for now. This is used to read the maximum count from teh used detector 
    """

    #Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_scan',
               'detector': detector, 
               'energy': energy.energy.position,
               'rois': [200, 278, 298, 318] # beam center 306 # [200, 185, 205, 225]
            # ...
            }
    base_md.update(md or {})

    global attenuation_factor_signal, exposure_time, monitor_count, attenuator_name_signal, default_attenuation

    attenuator_name_signal = Signal(name='attenuator_name', value = 'abs1')
    attenuation_factor_signal = Signal(name='attenuation', value = 1)
    exposure_time = Signal(name='exposure_time', value = 1)
    default_attenuation = Signal(name='default-attenuation', value = 1e-7)


    bec.disable_plots()
    yield from bps.open_run(md=base_md)
    print('1st set starting')

    yield from bps.mvr(geo.stblx2, -0.5) # move stable X2
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.05, 0.2, 20, 2, 0.1 # 0.07, 14
    yield from reflection_scan(alpha_start= alpha_start,
                               alpha_stop = alpha_stop,
                               num = num,
                               detector = detector,
                               precount_time=precount_time,
                               exp_time=exp_time,
                               md=md)
    
    print('1st set done')
    print('2nd set starting')

    yield from bps.mvr(geo.stblx2, -0.5) # move stable X yield from expert_reflection_scan(md={'sample_name': 'test_water14'})
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.2, 0.6, 17, 2, 0.1 # 9
    yield from reflection_scan(alpha_start= alpha_start,
                               alpha_stop = alpha_stop,
                               num = num,
                               detector = detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)
    
    print('2nd set done', 'default attenuation is', default_attenuation)
    print('3rd set starting')

    yield from bps.mvr(geo.stblx2, -0.5) # move stable X2
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.6, 1, 9, 5, 0.1 # 9
    yield from reflection_scan(alpha_start= alpha_start,
                               alpha_stop = alpha_stop,
                               num = num,
                               detector = detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)
    print('3rd set done')
    print('4th set starting')

    yield from bps.mvr(geo.stblx2, -0.5) # move stable X2
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 1, 2, 11, 5, 0.1 
    yield from reflection_scan(alpha_start= alpha_start,
                               alpha_stop = alpha_stop,
                               num = num,
                               detector = detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)
    print('4th set done')
    print('5th set starting')

    yield from bps.mvr(geo.stblx2, -0.5) # move stable X2
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 2, 3, 11, 10, 0.1 # 2, 4
    yield from reflection_scan(alpha_start= alpha_start,
                               alpha_stop = alpha_stop,
                               num = num,
                               detector = detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)
    print('5th set done')

    #Bluesky command to stop recording metadata
    yield from bps.close_run()
    bec.enable_plots()
    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')


gid_dets = [pilatus100k]
@bpp.stage_decorator(gid_dets)
def gid(md=None, energy=9700, exp_time=1, detector = 'pilatus100k'):
    #Bluesky command to record metadata
    base_md = {'plan_name': 'gid',
               'detector': detector, 
               'energy': energy.energy.position,
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
    # yield from mabt(0.1,1,0.6) # gid poistion with beam stop
    yield from mabt(0.1,1.5,0.38) # gid poistion with beam stop

    yield from bps.sleep(5)
    yield from bps.mv(shutter,1)

    #Take the pre-count data
    ret = yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.mv(shutter,0)

    # yield from set_attenuator(0)
    yield from set_attenuator(3) # to avoid pilatus saturation
    attenuation_factor_signal.value = 1

    #set the exposure time to the define exp_time for the measurment
    det_exposure_time(exp_time, exp_time)
    exposure_time.value = exp_time
    yield from bps.mvr(geo.stblx2, -1) # move stable X2
    print(exposure_time.value)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from bps.mv(abs2, 5)
    yield from mabt(0.1,1.5,0) # gid poistion without beam stop
    yield from bps.sleep(5)
    exposure_time.value = 1
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from mabt(0.1,1.5,0.76) # gid poistion without beam stop
    yield from bps.sleep(5)
    exposure_time.value = 1
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from mabt(0.1,1.5,-0.38) # gid poistion without beam stop
    yield from bps.sleep(5)
    exposure_time.value = 1
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from mabt(0.1,1.5,-0.76) # gid poistion without beam stop
    yield from bps.sleep(5)
    exposure_time.value = 1
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)



    #Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    yield from bps.mv(abs2, 5)
    print('The gid is over')


#ToDo: need to enter the good values here
def put_default_absorbers(energy, default_attenuation = 0.0000001):
    default_att, default_factor, default_name = best_att(default_attenuation, energy)

    if energy < 9000 and energy > 10000:
        raise ValueError('error: the energy entered is not correct')
    
    yield from set_attenuator(default_att)
    yield from bps.sleep(1)
    
    return default_factor


def calculate_and_set_absorbers(energy, i_max, def_att, precount_time=0.1, exp_time=1):
    # Need to enter the attenuation of each absorber at different energies
    # i_max_det is the maximum allowed pixel count (nominal value is 1e4)
    i_max_det = 10000 #50000 if lambda, 500000 if pilatus

    precount_time = precount_time
    print('test', def_att, i_max, precount_time)
    max_theo_precount = i_max / (def_att * precount_time)
    att_needed = 1/(max_theo_precount / (i_max_det))
    print('att_needed', att_needed)

    best_at, attenuation_factor, default_name = best_att(att_needed, energy)
    return best_at, attenuation_factor, default_name


def set_attenuator(best_att):
    print(best_att)
    att_pos = [0.22, 1, 2, 3, 4, 5, 6, 7] 
    #att_pos = [1, 2, 3, 4, 5, 6, 7, 8] # add 1 more absorber each att, HZ
    yield from bps.mv(abs2, att_pos[best_att])







# area_dets = [pilatus100k]
# all_area_dets = [pilatus100k, tetramm, geo, S3]
# #all_area_dets = [pilatus100k, quadem, geo, S3]


# @bpp.stage_decorator(all_area_dets)
# def test_trirun(md=None):
#     base_md = {'plan_name': 'test trigger_and_read methog',
#         }
#     base_md.update(md or {})

#     bec.disable_plots()

#     yield from bps.open_run(md=base_md)
#     ret =  yield from bps.trigger_and_read(area_dets, name='precount')
#     yield from bps.trigger_and_read(all_area_dets, name='primary')
    
#     ret =  yield from bps.trigger_and_read(area_dets, name='precount')
#     yield from bps.trigger_and_read(all_area_dets, name='primary')

#     ret =  yield from bps.trigger_and_read(area_dets, name='precount')
#     yield from bps.trigger_and_read(all_area_dets, name='primary')
#     yield from close_run()
#     bec.enable_plots()

