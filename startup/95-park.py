def park():
    yield from bps.mov(shutter,0)
    # this parks the two tables.
    # yield from bps.mov(geo.stblx,650,geo.tth,30)
    yield from bps.mov(geo.stblx,650,geo.tth,25) # change tth 30 to 25, HZ, Aug2022

    yield from bps.mov(ih,100)
    # this moves the th and two theta
    yield from bps.mov(geo.th,20,geo.tth,30)
    yield from bps.mov(geo.th,40,geo.tth,50)
    yield from bps.mov(geo.th,60,geo.tth,70)
    yield from bps.mov(geo.th,90,geo.tth,70)
    # this moves the height of the crystal 
    yield from bps.mov(tab1.y,-68,tab1.x,270) # the low limit is -68.32

def unpark():
    #yield from bps.mov(shutter,0)
    # this restores the height of the crystal 
   
    #this restores the th and two theta
    yield from bps.mov(geo.th,60,geo.tth,70)
    yield from bps.mov(geo.th,40,geo.tth,50)
    yield from bps.mov(geo.th,20,geo.tth,30)
    yield from bps.mov(geo.th,0, geo.tth,30)
    yield from bps.mov(geo.th,0, geo.tth,20) # HZ, June2023
    #this restores the two tables.
    yield from bps.mov(ih,0)
    yield from bps.mov(tab1.y,0,tab1.x,0,geo.stblx,450)


#If tth doesnt start then
# buttons in htch and back of module on roor
# reset logic button for MC1
# reboot IOC
