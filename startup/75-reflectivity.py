print(f'Loading {__file__}')

def reflection_scan(alpha_start, alpha_stop, num, detector=lambda_det, precount_time=1, exp_time=1, tilt_stage=False, low_abs_limit=1):
    """
    Run reflectivity scans

    Parameters:
    -----------
    :param alpha_start, alpha_stop, num: Incident angles start (deg), stop (deg) and number of angles
    :type alpha_start, alpha_stop, num: float, float, int
    :param detector: detector object that will be used to collect the data
    :type detector: ophyd object (for OPLS either pillatus100k, pilatus300k or lambda_det
    :param precount_time, exp_time: Exposure time in seconds for the precount (used to calculate the attenuation) and the data
    :type precount_time, exp_time: float, float
    :param tilt_stage: Boolean to define if using or not a specific tilt stage
    :type tilt_stage: Boolean
    :param low_abs_limit: Integer to define the lowest amount of attenuation required
    :type low_abs_limit: Integer
    """

    @bpp.stage_decorator([quadem, detector])
    def reflection_method(alpha_start, alpha_stop, num, detector, precount_time, exp_time, tilt_stage, low_abs_limit):

        for alpha in np.linspace(alpha_start, alpha_stop, num):
            # Move to the good geometry position
            if tilt_stage:
                yield from nabt(alpha, alpha, alpha*0.025)
            else:
                yield from mabt(alpha, alpha, 0)

            # Sleep to reduce sample vibration
            yield from bps.sleep(5)

            # Move the default attenuator in for the pre-count
            def_att = yield from put_default_absorbers(energy.energy.position,
                                                    default_attenuation=default_attenuation.get())

            # Set the exposure time to for the pre-count
            yield from det_exposure_time_new(detector, precount_time, precount_time)

            # Open shutter, Take the pre-count data, Close shutter
            yield from bps.mv(shutter, 1)
            ret = yield from bps.trigger_and_read(detector, name='precount')
            yield from bps.mv(shutter, 0)


            if ret is None:
                # in simulation mode
                continue
            else:
                # Read the maximum count on a pixel from the detector
                i_max = ret['%s_stats4_max_value'%detector.name]['value']
                i_trigger = 100000

                # look at the maximum count of the pre-count and adjust the default attenuation
                while (i_max < 100 or i_max > i_trigger) and default_attenuation.get() < 1:
                    if i_max > 2*i_trigger:
                        # If i_max to high, attenuate more
                        yield from bps.mv(default_attenuation, default_attenuation.get() / 10)
                    elif i_max < 100:
                        # If i_max to low, attenuate less
                        yield from bps.mv(default_attenuation, default_attenuation.get() * 10)
                    else:
                        print('You should not be there!')
                        break    
                    
                    def_att = yield from put_default_absorbers(energy.energy.position,
                                                            default_attenuation=default_attenuation.get())

                    # Re-take the pre-count data
                    yield from bps.mv(shutter, 1)
                    ret = yield from bps.trigger_and_read(area_dets,
                                                        name='precount')
                    yield from bps.mv(shutter, 0)
                                        
                    # Re-read the maximum count on a pixel from the detector
                    i_max = ret['%s_stats4_max_value'%detector.name]['value']
                            
                # Adjust the absorbers to avoid saturation of detector
                best_at, attenuation_factor, best_att_name = yield from calculate_and_set_absorbers(energy=energy.energy.position,
                                                                                                    i_max=i_max,
                                                                                                    att=def_att,
                                                                                                    precount_time=precount_time)
                
                # Upload the attenuation factor and name for the metadata
                yield from bps.mv(attenuation_factor_signal, attenuation_factor)
                yield from bps.mv(attenuator_name_signal, best_att_name)

                #Check if the required absorption is lower than the defined low limit. If so, set the absorber back to the limit
                if best_att_name < att_bar1['name'][low_abs_limit+1]:
                    yield from bps.mv(abs2, low_abs_limit)
                    yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][low_abs_limit])
                    yield from bps.mv(attenuator_name_signal, att_bar1['name'][low_abs_limit])


            # Set the exposure time to the define exp_time for the measurement
            yield from det_exposure_time_new(detector, exp_time, exp_time)
            yield from bps.mv(exposure_time, exp_time)

            # Open shutter, sleep to initiate quadEM, collect data, close shutter
            yield from bps.mv(shutter, 1)
            yield from bps.sleep(1)
            yield from bps.trigger_and_read([detector, quadem, geo, attenuation_factor_signal, attenuator_name_signal, exposure_time],
                                            name='primary')
            yield from bps.mv(shutter, 0)


    yield from reflection_method(alpha_start=alpha_start,
                                 alpha_stop=alpha_stop,
                                 num=num,
                                 detector=detector,
                                 precount_time=precount_time,
                                 exp_time=exp_time,
                                 tilt_stage=tilt_stage, 
                                 low_abs_limit=low_abs_limit)
        
def night_scan():
    yield from expert_reflection_scan(md={'sample_name': 'test_water10'})
    yield from expert_reflection_scan(md={'sample_name': 'test_water11'})
    yield from expert_reflection_scan(md={'sample_name': 'test_water12'})
    

def fast_scan(name = 'test', tilt_stage=False):
    yield from expert_reflection_scan(md={'sample_name': name},tilt_stage=tilt_stage)


def expert_reflection_scan(md=None, detector=lambda_det, tilt_stage=False):
    """
    Macros to set all the parameters in order to record all the required information for further analysis,
    such as the attenuation factors, detector='lambda_det'
    :param detector: An ophyd detector which is the detector name
    :type detector: string, can be either 'lambda_det' or 'pilatus100k'
    """
 #XF:12ID1-ES{Det:Lambda}ROI1:MinX
    # Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_scan',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
               'detector': detector.name, 
               'energy': energy.energy.position,
               'rois': [202, 190, 202, 214,30,12],
               'geo_param': [geo.L1.get(), geo.L2.get(), geo.L3.get(), geo.L4.get()],
               'slit_s1': [S1.top.position - S1.bottom.position, S1.outb.position - S1.inb.position],
               'slit_s2': [S2.vg.position, S2.hg.position],
               'x2': [geo.stblx2.position],
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

    print('1st set starting')

    # Move stable X2
    #yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(3)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.05, 0.2, 20, 2, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               precount_time=precount_time,
                               exp_time=exp_time,
                               tilt_stage=tilt_stage,
                               low_abs_limit = 1)
    
    print('1st set done')
    print('2nd set starting')

    # Move stable X2
   # yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(3)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.2, 0.6, 17, 2, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               precount_time=precount_time,
                               exp_time=exp_time,
                               tilt_stage=tilt_stage,
                               low_abs_limit = 1)

    print('2nd set done', 'default attenuation is', default_attenuation.get())
    print('3rd set starting')

    # Move stable X2
    #yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(3)
    alpha_start, alpha_stop, num, exp_time, precount_time = 0.6, 1, 9, 2, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               precount_time=precount_time,
                               exp_time=exp_time,
                               tilt_stage=tilt_stage,
                               low_abs_limit = 1)

    print('3rd set done')
    print('4th set starting')

    # Move stable X2
    #yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(3)
    alpha_start, alpha_stop, num, exp_time, precount_time = 1, 2., 11, 2, 0.1 
    yield from reflection_scan(alpha_start=alpha_start,
                               alpha_stop=alpha_stop,
                               num=num,
                               detector=detector,
                               precount_time=precount_time,
                               exp_time=exp_time,
                               tilt_stage=tilt_stage,
                               low_abs_limit = 1)

    print('4th set done')
    print('5th set starting')

    #Move stable X2
    yield from bps.mvr(geo.stblx2, -0.5)
    yield from bps.sleep(3)
    alpha_start, alpha_stop, num, exp_time, precount_time = 2, 3.4, 15, 2, 0.1
    yield from reflection_scan(alpha_start=alpha_start,
                                alpha_stop=alpha_stop,
                                num=num,
                                detector=detector,
                                precount_time=precount_time,
                                exp_time=exp_time,
                               tilt_stage=tilt_stage,
                               low_abs_limit = 1)

    print('5th set done')

    # Bluesky command to stop recording metadata
    yield from bps.close_run()

    # Enable the plot during the reflectivity scan
    bec.enable_plots()

    yield from bps.mv(abs2, 5)
    print('The reflectivity scan is over')