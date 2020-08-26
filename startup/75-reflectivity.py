print(f'Loading {__file__}')

# area_dets = [pilatus100k]
# all_area_dets = [pilatus100k, tetramm]

area_dets = [lambda_det]
all_area_dets = [lambda_det, quadem]


@bpp.stage_decorator(all_area_dets)
def reflection_scan(alpha_start, alpha_stop, num, detector='lambda_det', precount_time=1, exp_time=1,
                    default_att=1e-7, md=None):

    for alpha in np.linspace(alpha_start, alpha_stop, num):
        # Move to the good geometry position
        yield from mabt(alpha, alpha, 0)
        yield from bps.sleep(5)

        # Move the default attenuator in for the pre-count
        def_att = yield from put_default_absorbers(energy.energy.position,
                                                   default_attenuation=default_attenuation.value)

        # Set the exposure time to for the pre-count
        yield from det_exposure_time(precount_time, precount_time)

        # Take the pre-count data
        yield from bps.mv(shutter, 1)
        ret = yield from bps.trigger_and_read(area_dets, name='precount')
        yield from bps.mv(shutter, 0)
        
        if ret is None:
            # in simulation mode
            continue
        else:
            # Read the maximum count on a pixel from the detector
            i_max = ret['%s_stats4_max_value'%detector]['value']

            # look at the maximum count of the pre-count and adjust the default attenuation
            while (i_max < 100 or i_max > 200000) and default_attenuation.value < 1:
                if i_max > 200000:
                    # If i_max to high, attenuate more
                    default_attenuation.value = default_attenuation.value / 10
                elif i_max < 100:
                    # If i_max to low, attenuate less
                    default_attenuation.value = default_attenuation.value * 10
                else:
                    print('You should not be there!')
                    break    

                def_att = yield from put_default_absorbers(energy.energy.position,
                                                           default_attenuation=default_attenuation.value)

                # Re-take the pre-count data
                yield from bps.mv(shutter, 1)
                ret = yield from bps.trigger_and_read(area_dets,
                                                      name='precount')
                yield from bps.mv(shutter, 0)

                # Re-read the maximum count on a pixel from the detector
                i_max = ret['%s_stats4_max_value'%detector]['value']
                        
            # Adjust the absorbers to avoid saturation of detector
            best_att, attenuation_factor, best_att_name = calculate_and_set_absorbers(energy=energy.energy.position,
                                                                                      i_max=i_max,
                                                                                      att=def_att,
                                                                                      precount_time=precount_time)
            
            # Upload the attenuation factor for the metadata
            attenuation_factor_signal.value = attenuation_factor
            attenuator_name_signal.value = best_att_name

        # Set the exposure time to the define exp_time for the measurement
        yield from det_exposure_time(exp_time, exp_time)
        exposure_time.value = exp_time

        # ToDo: is that really usefull now
        yield from bps.mv(shutter, 1)
        # Add this because the QuadEM I0
        yield from bps.sleep(1)

        yield from bps.trigger_and_read(all_area_dets +
                                        [geo] +
                                        [attenuation_factor_signal] +
                                        [attenuator_name_signal] +
                                        [exposure_time],
                                        name='primary')
        yield from bps.mv(shutter, 0)
        

def night_scan():
    yield from expert_reflection_scan(md={'sample_name': 'test_water10'})
    yield from expert_reflection_scan(md={'sample_name': 'test_water11'})
    yield from expert_reflection_scan(md={'sample_name': 'test_water12'})


def fast_scan():
    yield from expert_reflection_scan(md={'sample_name': 'water_reigler_fast1'})


def expert_reflection_scan(md=None, detector='lambda_det'):
    """
    Macros to set all the parameters in order to record all the required information for further analysis,
    such as the attenuation factors, detectors, ROIS, ...

    Parameters:
    -----------
    :param md: A string liking the path towards the saved txt data containing CXRO files
    :type md: string
    :param detector: A string which is the detector name
    :type detector: string, can be either 'lambda_det' or 'pilatus100k'
    """

    # Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_scan',
               'detector': detector, 
               'energy': energy.energy.position,
               'rois': [200, 278, 298, 318]
               }
    base_md.update(md or {})

    global attenuation_factor_signal, exposure_time, attenuator_name_signal, default_attenuation

    attenuator_name_signal = Signal(name='attenuator_name', value='abs1')
    attenuation_factor_signal = Signal(name='attenuation', value=1)
    exposure_time = Signal(name='exposure_time', value=1)
    default_attenuation = Signal(name='default-attenuation', value=1e-7)

    # Disable the plot during the reflectivity scan
    bec.disable_plots()

    # Bluesky command to start the document
    yield from bps.open_run(md=base_md)

    print('1st set starting')

    # Move stable X2
    yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.05, 0.2, 20, 2, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               precount_time=precount_time,
                               exp_time=exp_time,
                               md=md)
    
    print('1st set done')
    print('2nd set starting')

    # Move stable X2
    yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.2, 0.6, 17, 2, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)
    
    print('2nd set done', 'default attenuation is', default_attenuation)
    print('3rd set starting')

    # Move stable X2
    yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.6, 1, 9, 5, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)

    print('3rd set done')
    print('4th set starting')

    # Move stable X2
    yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 1, 2, 11, 5, 0.1 
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)

    print('4th set done')
    print('5th set starting')

    # Move stable X2
    yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(5)
    alpha_start, alpha_stop, num, exp_time, precount_time = 2, 3, 11, 10, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               exp_time=exp_time,
                               precount_time=precount_time,
                               md=md)

    print('5th set done')

    # Bluesky command to stop recording metadata
    yield from bps.close_run()

    # Enable the plot during the reflectivity scan
    bec.enable_plots()

    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')


gid_dets = [pilatus100k]
@bpp.stage_decorator(gid_dets)
def gid(md=None, energy=9700, exp_time=1, detector = 'pilatus100k'):
    # Bluesky command to record metadata
    base_md = {'plan_name': 'gid',
               'detector': detector, 
               'energy': energy.energy.position,
            # ...
           }
    base_md.update(md or {})
    bec.disable_plots()
    yield from bps.open_run(md=base_md)

    
    # Creation of a fignal to record the attenuation
    attenuation_factor_signal = Signal(name='attenuation', value = 1)

    exposure_time = Signal(name='exposure_time', value = 1)

    # Move the default attenuator in for the precount
    def_att = yield from put_default_absorbers(energy)

    # Set the exposure time to 0.1 for the precount
    det_exposure_time(0.1, 0.1)

    # Move to the good geometry position
    yield from bps.mv(shutter,0)
    # yield from mabt(0.1,1,0.6) # gid poistion with beam stop
    yield from mabt(0.1,1.5,0.38) # gid poistion with beam stop

    yield from bps.sleep(5)
    yield from bps.mv(shutter,1)

    # Take the pre-count data
    ret = yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.mv(shutter,0)

    # yield from bps.mv(abs2, 0)
    yield from bps.mv(abs2, 3)# to avoid pilatus saturation
    attenuation_factor_signal.value = 1

    # Set the exposure time to the define exp_time for the measurment
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



    # Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    yield from bps.mv(abs2, 5)
    print('The gid is over')