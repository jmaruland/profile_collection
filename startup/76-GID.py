
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
    yield from bps.mv(attenuation_factor_signal, 1)

    # Set the exposure time to the define exp_time for the measurment
    det_exposure_time(exp_time, exp_time)
    yield from bps.mv(exposure_time, exp_time)
    yield from bps.mvr(geo.stblx2, -1) # move stable X2
    print(exposure_time.get())
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from bps.mv(abs2, 5)
    yield from mabt(0.1,1.5,0) # gid poistion without beam stop
    yield from bps.sleep(5)
    yield from bps.mv(exposure_time, 1)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from mabt(0.1,1.5,0.76) # gid poistion without beam stop
    yield from bps.sleep(5)
    yield from bps.mv(exposure_time, 1)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from mabt(0.1,1.5,-0.38) # gid poistion without beam stop
    yield from bps.sleep(5)
    yield from bps.mv(exposure_time, 1)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    yield from mabt(0.1,1.5,-0.76) # gid poistion without beam stop
    yield from bps.sleep(5)
    yield from bps.mv(exposure_time, 1)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(area_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)



    # Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    yield from bps.mv(abs2, 5)
    print('The gid is over')


gid_dets = [pilatus100k, quadem]
@bpp.stage_decorator(gid_dets)
def gid_new(md=None, exp_time=1, detector = 'pilatus100k', alphai = 0.1, attenuator=2):
    # Bluesky command to record metadata
    base_md = {'plan_name': 'gid',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['cycle'] + '_' + RE.md['cycle'],
               'detector': detector, 
               'energy': energy.energy.position,
               'alphai': alphai,
            # ...
           }

    base_md.update(md or {})
    bec.disable_plots()
    yield from bps.open_run(md=base_md)

    # Creation of a fignal to record the attenuation
    yield from bps.mv(abs2, attenuator)# to avoid pilatus saturation
    attenuation = calculate_att_comb([np.sum(current_att_thickness[0:attenuator+1])], ['Mo'], energy.energy.position)
    attenuation_factor_signal = Signal(name='attenuation', value = attenuation[0])

    # Set and record the exposure time to 0.1 for the precount
    exposure_time = Signal(name='exposure_time', value = exp_time)
    yield from det_exposure_time_pilatus(exp_time, exp_time)

    # Move to the good geometry position
    yield from mabt(alphai, 0, 0) # gid poistion with beam stop
    yield from bps.sleep(5)

    # yield from bps.mv(abs2, 0)
    # yield from bps.mv(abs2, 3)# to avoid pilatus saturation
    # yield from bps.mv(attenuation_factor_signal, 1)

    # yield from bps.mvr(geo.stblx2, -1) # move stable X2
    
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    # Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    # yield from bps.mv(abs2, 5)
    print('The gid is over')
