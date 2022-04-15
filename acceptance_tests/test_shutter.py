def test_fast_shutter():
    print("open shutter")
    RE(bps.mov(shutter, 1))
    RE(bps.sleep(1))
    print("close shutter")
    RE(bps.mov(shutter, 0))

test_fast_shutter()

