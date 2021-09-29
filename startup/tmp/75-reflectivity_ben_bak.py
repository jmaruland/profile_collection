print(f'Loading {__file__}')

# area_dets = [pilatus100k]
# all_area_dets = [pilatus100k, tetramm]

area_dets = [lambda_det]
all_area_dets = [lambda_det, quadem]




@bpp.stage_decorator(all_area_dets)
def reflection_scan_ben(alpha_start, alpha_stop, num, detector='lambda_det', exp_time=1, tilt_stage=False, absorber="auto", md=None):
    
    for alpha in np.linspace(alpha_start, alpha_stop, num):
        # Move to the good geometry position
        if tilt_stage:
            yield from nabt(alpha, alpha, alpha*0.025)
        else:
             yield from mabt(alpha, alpha, 0)

        # yield from mabt(geo.alpha=0,geo.samchi=x,geo.beta=2*x)
        yield from bps.sleep(5)
                        

        # Set the exposure time to the define exp_time for the measurement
        yield from det_exposure_time(exp_time, exp_time)
        yield from bps.mv(exposure_time, exp_time)

        # Set the absorber time to the define exp_time for the measurement
        if absorber == "auto":
            att = calc_att_from_ai(alpha) 
        else:
            att=absorber

        yield from bps.mv(abs2, att)
        yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][att])
        yield from bps.mv(attenuator_name_signal, att_bar1['name'][att])


        # ToDo: is that really usefull now
        yield from bps.mv(shutter, 1)
        yield from bps.sleep(1)
        yield from bps.trigger_and_read(all_area_dets +
                                        [geo] +
                                        [attenuation_factor_signal] +
                                        [attenuator_name_signal] +
                                        [exposure_time],
                                        name='primary')
        yield from bps.mv(shutter, 0)
        



def calc_att_from_ai(alphai):
    q_start=0.35
    if alphai<0.3:
        return 7
    elif 0.3<alphai<q_start:
        return 6
    elif q_start*math.pow(0)<alphai<q_start*math.pow(1.7,1):
        return 5
    elif q_start*math.pow(1)<alphai<q_start*math.pow(1.7,2):
        return 4
    elif q_start*math.pow(2)<alphai<q_start*math.pow(1.7,3):
        return 3
    elif q_start*math.pow(3)<alphai<q_start*math.pow(1.7,4):
        return 2
    elif q_start*math.pow(4)<alphai<q_start*math.pow(1.7,5):
        return 1
    elif q_start*math.pow(5)<alphai<q_start*math.pow(1.7,6):
        return 0


# def calc_att_auto(alphai, precount_time=1):
#     # Move the default attenuator in for the pre-count
#     def_att = yield from put_default_absorbers(energy.energy.position,
#                                                default_attenuation=default_attenuation.get())

#     # Set the exposure time to for the pre-count
#     yield from det_exposure_time(precount_time, precount_time)

#     # Take the pre-count data
#     yield from bps.mv(shutter, 1)
#     ret = yield from bps.trigger_and_read(area_dets, name='precount')
#     yield from bps.mv(shutter, 0)

#     if ret is None:
#         continue

#     else:
#         # Read the maximum count on a pixel from the detector
#         i_max = ret['%s_stats4_max_value'%detector]['value']

#         # look at the maximum count of the pre-count and adjust the default attenuation
#         while (i_max < 100 or i_max > 40000) and default_attenuation.get() < 1:
#             if i_max > 40000:
#                 # If i_max to high, attenuate more
#                 yield from bps.mv(default_attenuation, default_attenuation.get() / 10)
#             elif i_max < 100:
#                 # If i_max to low, attenuate less
#                 yield from bps.mv(default_attenuation, default_attenuation.get() * 10)
#             else:
#                 print('You should not be there!')
#                 break    
            


#             def_att = yield from put_default_absorbers(energy.energy.position,
#                                                         default_attenuation=default_attenuation.get())

#             # Re-take the pre-count data
#             yield from bps.mv(shutter, 1)
#             ret = yield from bps.trigger_and_read(area_dets,
#                                                     name='precount')
#             yield from bps.mv(shutter, 0)
                                    
#             # Re-read the maximum count on a pixel from the detector
#             i_max = ret['%s_stats4_max_value'%detector]['value']
                    
#         # Adjust the absorbers to avoid saturation of detector
#         best_at, attenuation_factor, best_att_name = yield from calculate_and_set_absorbers(energy=energy.energy.position,
#                                                                                             i_max=i_max,
#                                                                                             att=def_att,
#                                                                                             precount_time=precount_time)
        
#         # Upload the attenuation factor for the metadata

#         yield from bps.mv(attenuation_factor_signal, attenuation_factor)
#         yield from bps.mv(attenuator_name_signal, best_att_name)




# def night_scan():
#     yield from expert_reflection_scan(md={'sample_name': 'test_water10'})
#     yield from expert_reflection_scan(md={'sample_name': 'test_water11'})
#     yield from expert_reflection_scan(md={'sample_name': 'test_water12'})


# def fast_scan_ben(name = 'test', tilt_stage=False):
#     yield from expert_reflection_scan_ben(md={'sample_name': name},tilt_stage=tilt_stage)


# def expert_reflection_scan_ben(md=None, detector='lambda_det',tilt_stage=False):
#     """
#     Macros to set all the parameters in order to record all the required information for further analysis,
#     such as the attenuation factors, detectors, ROIS, ...

#     Parameters:
#     -----------
#     :param md: A string liking the path towards the saved txt data containing CXRO files
#     :type md: string
#     :param detector: A string which is the detector name
#     :type detector: string, can be either 'lambda_det' or 'pilatus100k'
#     """

#     # Bluesky command to record metadata
#     base_md = {'plan_name': 'reflection_scan',
#                'cycle': RE.md['cycle'],
#                'proposal_number': RE.md['cycle'] + '_' + RE.md['main_proposer'],
#                'detector': detector, 
#                'energy': energy.energy.position,
#                'rois': [202, 190, 202, 214]
#                }
#     base_md.update(md or {})

#     global attenuation_factor_signal, exposure_time, attenuator_name_signal, default_attenuation

#     attenuator_name_signal = Signal(name='attenuator_name', value='abs1')
#     attenuation_factor_signal = Signal(name='attenuation', value=1e-7)
#     exposure_time = Signal(name='exposure_time', value=1)
#     default_attenuation = Signal(name='default-attenuation', value=1e-7)

#     # Disable the plot during the reflectivity scan
#     bec.disable_plots()

#     # Bluesky command to start the document
#     yield from bps.open_run(md=base_md)

#     print('1st set starting')

#     # Move stable X2
#     #yield from bps.mvr(geo.stblx2, -0.5)
#     yield from bps.sleep(5)
#     alpha_start, alpha_stop, num, exp_time, precount_time = 0.05, 0.3, 26, 2, 0.1
#     yield from reflection_scan_ben(alpha_start=alpha_start,
#                                alpha_stop=alpha_stop,
#                                num=num,
#                                detector=detector,
#                                precount_time=precount_time,
#                                exp_time=exp_time,
#                                default_att = default_attenuation.value,
#                                md=md,
#                                tilt_stage=tilt_stage)
    
#     print('1st set done')
#     print('2nd set starting')

#     # Move stable X2
#    # yield from bps.mvr(geo.stblx2, -0.5)
#     yield from bps.sleep(5)
#     alpha_start, alpha_stop, num, exp_time, precount_time = 0.3, 1.2, 37, 2, 0.1
#     yield from reflection_scan_ben(alpha_start=alpha_start,
#                                alpha_stop=alpha_stop,
#                                num=num,
#                                detector=detector,
#                                precount_time=precount_time,
#                                exp_time=exp_time,
#                                default_att = default_attenuation.value,
#                                md=md,
#                                tilt_stage=tilt_stage)
    
#     print('2nd set done', 'default attenuation is', default_attenuation)
#     print('3rd set starting')

#     # Move stable X2
#     #yield from bps.mvr(geo.stblx2, -0.5)
#     yield from bps.sleep(5)
#     alpha_start, alpha_stop, num, exp_time, precount_time = 1.2, 2, 17, 2, 0.1
#     yield from reflection_scan_ben(alpha_start=alpha_start,
#                                alpha_stop=alpha_stop,
#                                num=num,
#                                detector=detector,
#                                precount_time=precount_time,
#                                exp_time=exp_time,
#                                default_att = default_attenuation.value,
#                                md=md,
#                                tilt_stage=tilt_stage)

#     print('3rd set done')
#     print('4th set starting')

#     # Move stable X2
#     #yield from bps.mvr(geo.stblx2, -0.5)
#     yield from bps.sleep(5)
#     alpha_start, alpha_stop, num, exp_time, precount_time = 2, 4, 21, 2, 0.1 
#     yield from reflection_scan_ben(alpha_start=alpha_start,
#                                alpha_stop=alpha_stop,
#                                num=num,
#                                detector=detector,
#                                precount_time=precount_time,
#                                exp_time=exp_time,
#                                default_att = default_attenuation.value,
#                                md=md,
#                                tilt_stage=tilt_stage)

#     print('4th set done')
#     print('5th set starting')

#     #Move stable X2
#   #  yield from bps.mvr(geo.stblx2, -0.5)
#     yield from bps.sleep(5)
#     alpha_start, alpha_stop, num, exp_time, precount_time = 4, 8, 21, 5, 0.1
#     yield from reflection_scan_ben(alpha_start=alpha_start,
#                                 alpha_stop=alpha_stop,
#                                 num=num,
#                                 detector=detector,
#                                 precount_time=precount_time,
#                                 exp_time=exp_time,
#                                 default_att = default_attenuation.value,
#                                 md=md,
#                                 tilt_stage=tilt_stage)

#     print('5th set done')

#     # Bluesky command to stop recording metadata
#     yield from bps.close_run()

#     # Enable the plot during the reflectivity scan
#     bec.enable_plots()

#     yield from bps.mv(abs2, 5)
#     print('The reflectivity scan is over')