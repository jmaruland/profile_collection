

def nwu_3():
    yield from he_on()
    yield from one_ref("0.5mM CsCl_ML, small trough_1_abs2", -62,0)
    yield from  one_xf("0.5mM CsCl_ML, small trough_1_abs2", -62)
    yield from one_ref("0.2mM CsBr_ML, small trough_1_abs2", -12,0)
    yield from  one_xf("0.2mM CsBr_ML, small trough_1_abs2", -12)
    yield from one_ref("0.5mM CsI_ML, small trough_1_abs2", 39,0)
    yield from  one_xf("0.5mM CsI_ML, small trough_1_abs2", 39)
    yield from shclose()
    yield from he_off()
