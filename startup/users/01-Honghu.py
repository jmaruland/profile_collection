# pull various motors into the global name space

def cfn(name):
    # This takes the reflectivity
    yield from bps.mv(geo.stblx2,0.2)

    yield from bps.mv(flow3,3.2) # need to change back to 3.1
    yield from bps.mv(geo.det_mode,1)
    
    # sets sample height at alpha=0.08
    yield from sample_height_set()

    print('Sleeping time before reflectivity')
    yield from bps.sleep(10)
    yield from bps.mv(flow3,2.7)
    
    # takes the reflectivity
    yield from fast_scan(name)

    # sets sample height at alpha=0.08 so that it is ready for GID
    yield from bps.mv(abs2,6)
    yield from mabt(0.08,0.08,0)
    
    print('Start the height scan before GID')
    yield from sample_height_set()

    # This takes the GID
    yield from bps.mv(geo.det_mode,2)
    alphai = 0.11
    yield from gid_new(md={'sample_name': name+'_GID'},
                       exp_time = 1,
                       detector = 'pilatus100k',
                       alphai = alphai,
                       attenuator=1)

    yield from bps.mvr(geo.stblx2,2)
    yield from sample_height_set()
    yield from bps.mv(geo.det_mode,2)
    alphai = 0.11
    yield from gid_new(md={'sample_name': name+'_fresh1_GID'},
                       exp_time = 1,
                       detector = 'pilatus100k',
                       alphai = alphai,
                       attenuator=1)

    yield from bps.mvr(geo.stblx2,-4)
    yield from sample_height_set()
    yield from bps.mv(geo.det_mode,2)
    alphai = 0.11
    yield from gid_new(md={'sample_name': name+'_fresh2_GID'},
                       exp_time = 1,
                       detector = 'pilatus100k',
                       alphai = alphai,
                       attenuator=1)
    
    yield from bps.mv(flow3,2.7)
    yield from bps.mv(geo.stblx2,0.2)



gid_dets = [pilatus100k, quadem]
@bpp.stage_decorator(gid_dets)
def gid_cfn_cal(md=None, exp_time=1, detector = 'pilatus100k', alphai = 0.1, attenuator=2):
    # Bluesky command to record metadata
    base_md = {'plan_name': 'gid',
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


    yield from bps.mv(abs2, 6)
    yield from mabt(alphai, 0, -1) # gid poistion without beam stop
    yield from bps.sleep(5)

    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)


    yield from bps.mv(abs2, 6)
    yield from mabt(alphai, 0, -2) # gid poistion without beam stop
    yield from bps.sleep(5)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    # Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    # yield from bps.mv(abs2, 5)
    print('The gid is over')
                       
                       



                







