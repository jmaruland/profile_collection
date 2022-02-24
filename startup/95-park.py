def park():
    yield from bps.mov(shutter,0)
    # this parks the two tables.
#    yield from bps.mov(geo.stblx,820)
    yield from bps.mov(tab1.x,270)
    yield from bps.mov(ih,100)
    # this moves the th and two theta
    yield from bps.mov(geo.th,20,geo.tth,30,geo.stblx,350)
    yield from bps.mov(geo.th,40,geo.tth,50,geo.stblx,450)
    yield from bps.mov(geo.th,60,geo.tth,70,geo.stblx,550)
    yield from bps.mov(geo.th,90,geo.tth,70,geo.stblx,650)
    # this moves the height of the crystal 
    yield from bps.mov(tab1.y,-68) # the low limit is -68.32


def unpark():
    #yield from bps.mov(shutter,0)
    # this restores the height of the crystal 
    yield from bps.mov(tab1.y,0)
    #this restores the th and two theta
    yield from bps.mov(geo.th,60,geo.tth,70,geo.stblx,650)
    yield from bps.mov(geo.th,40,geo.tth,50,geo.stblx,500)
    yield from bps.mov(geo.th,20,geo.tth,30,geo.stblx,375)
    yield from bps.mov(geo.th,0,geo.tth,20,geo.stblx,250)
    #this restores the two tables.
    yield from bps.mov(ih,0)
    yield from bps.mov(tab1.x,0)
    yield from bps.mov(geo.stblx,250)
