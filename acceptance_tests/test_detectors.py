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


test_quadem()
test_lambda()
test_pilatus300k()

