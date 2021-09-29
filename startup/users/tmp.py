#RE(one_gid( name='S3, 4ul_DSPEP_P30', xpos=36.8, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13  ))



# sd.baseline= [  o2_per ]
# sd.baseline= [  o2_per ]
# sd.baseline= [    ]
# RE(bp.rel_scan( [pilatus100k, AD1], ih, -0.02,0.02,3))

# RE(bp.rel_scan( [pilatus100k, AD1], ih, 0,0,3))


# h = db[-1]
# get_fields( h )
# list(h.data('o2_percent'))

# list(h.data('geo_ih'))

RE( one_gid( name='test', xpos=-56,  stth = 0, exp_time=2, attenuator=4, beta1=0, beta_off= 0.4 , det_mode=2) )


def cycle_x2():
    for i in range(3):
        bps.mv(geo.stblx2,  -56 + 1 )
        bps.mv(geo.stblx2,  37 + 1 )
