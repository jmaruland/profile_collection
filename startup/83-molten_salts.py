    
def fast_scan_ms(name = 'test', tilt_stage=True):
    print("in bens routine")
    yield from expert_reflection_scan_full(md={'sample_name': name}, detector=lambda_det, tilt_stage=tilt_stage)




def ms_align():
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(abs2,3)
    yield from nab(-0.1,-0.1)
    yield from bp.scan([lambda_det],sh,-0.3,0.3,31)
    yield from bps.sleep(1)
    tmp = peaks.cen['lambda_det_stats2_total']
    yield from bps.mv(sh,tmp)
    yield from set_sh(0)
    yield from bp.rel_scan([lambda_det],tilt.y,-0.1,0.1,21)
    tmp = peaks.cen['lambda_det_stats2_total']
    yield from bps.mv(tilt.y,tmp)
    yield from set_tilty(-0.1)





    