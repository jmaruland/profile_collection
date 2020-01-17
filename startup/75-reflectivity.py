def reflection_scan(geo, area_dets, i0, alpha_start, alpha_stop, num, 
                    canary=''pilatus100k_stats2_total'', *, md=None):
    
    base_md = {'plan_name': 'reflection_scan',
            # ...
           }
    base_md.update(md or {})
    yield from bps.open_run(md=base_md)
    for alpha in np.linspace(alpha_start, aplha_stop, num):

        yield from bps.mv(geo.alpha, alpha, geo.beta, beta)

        #yield from put_in_all_the_absorbers()
        ret = yield from bps.trigger_and_read(area_dets, stream_name='precount')
        if ret is None:
            # in simulation mode
            continue
        else:
            val = ret[canary]['value']
            # do logic!
            yield from setup_absorbers(val)
        yield from bps.trigger_and_read(area_dets + [i0, geo] + absorbers, 
                                        stream_name='primary')
    yield from close_run()


# Define which absrober we want to put in as default
# List of info needed: energy, I0, Slits size
# What info are we really want to focus on, max, mean
# Function which calculate the good amount of absorber



