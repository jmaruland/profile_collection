def test_quadem():
    print("counting quadem")
    uid,  = RE(bp.count([quadem]))
    _ = db[uid].table(fill=True)

def test_lambda():
    print("counting lambda")
    uid, = RE(bp.count([lambda_det]))
    _ = db[uid].table(fill=True)

def test_pilatus300k():
    print("counting pilatus300k")
    uid, = RE(bp.count([pilatus300k]))
    _ = db[uid].table(fill=True)

def det_test(detectors=None):
    '''
    test all the all detectors
    '''
    if detectors is None:
        detectors = [quadem, lambda_det, pilatus100kA, xs, pilatus1m]
    yield from det_set_exposure(detectors, exposure_time=1, exposure_number = 1)
    for det in detectors:
        print(f'Currently running {det.name}...')
        yield from bp.count([det])
        yield from bps.sleep(0.1)  
        
det_test()

