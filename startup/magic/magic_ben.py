# This file should only be run if ipython is being used ... put that check here!
from IPython.core.magic import register_line_magic
import bluesky.plan_stubs as bps
from IPython.terminal.prompts import Prompts, Token

@register_line_magic
def ben(line):
    RE(bps.mv(shutter,int(line)))


#!/usr/bin/env python3
'''
bluesky magic commands
'''
from IPython.core.magic import (register_line_magic)

#deviceList = None

detectors_spec=[quadem,lambda_det]
def makeSpecGenerator( line): 
    """
    returns generators for the spock commands
    """
    print(line)

    from bluesky.plans import scan, rel_scan, list_scan, count
    from bluesky.plan_stubs import mv, mabt
    def gen():

        print( "magics.makeSpockGenerator: received %s" % line)

        lst = line.split( ' ')

        #
        # ascan motor 0 10 10 0.1
        #
        if lst[0] == 'ascan':
            if len( lst) != 6:
                print( "magics.ascan, expecting 6 tokens")
                print( "%s" % repr( lst))
                return None
            motor =  eval(lst[1])
            yield from det_set_exposure([detectors_spec], exposure_time=float(lst[5]), exposure_number = 1)
            yield from scan(detectors_spec, motor, float( lst[2]), float( lst[3]), int( lst[4]))

        #
        # a2scan motor1 0 10  motor2 0 20  10 1
        #
        elif lst[0] == 'a2scan':
            if len( lst) != 9:
                print( "magics.a2ascan, expecting 9 tokens")
                print( "%s" % repr( lst))
                return None
            motor1 =  eval(lst[1])
            motor2 =  eval(lst[4])
            yield from det_set_exposure([detectors_spec], exposure_time=float(lst[8]), exposure_number = 1)
            yield from scan(detectors_spec, motor1, float( lst[2]), float( lst[3]), motor2, float( lst[5]), float( lst[6]), int( lst[7]))

        #
        # dscan motor 0 10 10 0.1
        #
        elif lst[0] == 'dscan':
            if len( lst) != 6:
                print( "magics.dscan, expecting 6 tokens")
                print( "%s" % repr( lst))
                return None
            motor =  eval(lst[1])
            yield from det_set_exposure([detectors_spec], exposure_time=float(lst[5]), exposure_number = 1)
            yield from rel_scan(detectors_spec, motor, float( lst[2]), float( lst[3]), int( lst[4]))
        #
        #
        # d2scan motor1 0 10  motor2 0 20  10 1
        #
        elif lst[0] == 'd2scan':
            if len( lst) != 9:
                print( "magics.d2scan, expecting 9 tokens")
                print( "%s" % repr( lst))
                return None
            motor1 =  eval(lst[1])
            motor2 =  eval(lst[4])
            yield from det_set_exposure([detectors_spec], exposure_time=float(lst[8]), exposure_number = 1)
            yield from rel_scan(detectors_spec, motor1, float( lst[2]), float( lst[3]), motor2, float( lst[5]), float( lst[6]), int( lst[7]))


        # mabt alpha beta tth
        #
        elif lst[0] == 'mabt':
            if len( lst) != 4:
                print( "magics.mv, expecting 4 tokens")
                print( "%s" % repr( lst))
                return None
            yield from mabt(float( lst[0]), float( lst[1]), float( lst[2]))

        else:
            print( "magics.makeSpockGenerator: failed to identify %s" % line)
            return
    return gen()


@register_line_magic
def ascan(line):
    '''
    execute an ascan, e.g.: ascan eh_mot65 0 1 10 0.1    
      scan eh_mot65 from 0 to 1, 10 points, sample time 0.1
    '''
    print( "magics.ascan, called with %s" % line)
    RE( makeSpecGenerator( 'ascan ' + line))
    return 

@register_line_magic
def a2scan(line):
    '''
    execute an a2scan, e.g.: ascan eh_mot65 0 1 ehmot66 0 2 10 0.1    
      scan eh_mot65 from 0 to 1, 10 points, sample time 0.1
    '''
    print( "magics.a2scan, called with %s" % line)
    RE( makeSpecGenerator( 'a2scan ' + line))
    return 


@register_line_magic
def dscan(line):
    '''
    execute an dscan, e.g.: dscan eh_mot65 0 1 10 0.1    
      scan eh_mot65 relative from 0 to 1, 10 points, sample time 0.1
    '''
    print( "magics.dscan, called with %s" % line)
    RE( makeSpecGenerator( 'dscan ' + line))
    return 

@register_line_magic
def d2scan(line):
    '''
    execute an d2scan, e.g.: ascan eh_mot65 0 1 ehmot66 0 2 10 0.1    
      scan eh_mot65 relative from 0 to 1, 10 points, sample time 0.1
    '''
    print( "magics.d2scan, called with %s" % line)
    RE( makeSpecGenerator( 'd2scan ' + line))
    return 


@register_line_magic
def count(line):
    '''
    execute count with the active detectors defined by detector_all, eg count(2)
      counts for 2 seconds
    '''
    print( "magics.count, called with %s" % line)
    lst = line.split( ' ')
    print(detectors_all_auto,lst[0])
    RE(det_set_exposure(detectors_all_auto, exposure_time=float(lst[0]), exposure_number = 1))
    RE(bp.count(detectors_all_auto))
    return 


@register_line_magic
def ben2(line):
    '''
    execute mab alpha beta , e.g.: mabt 1 2
      moves alpha to 1 and beta to 2
    '''
    print( "magics.mabt, called with %s" % line)
    lst = line.split( ' ')
    print(lst[0], lst[1])
#    RE(mabt(float( lst[0]), float( lst[1]), float( lst[2]))
#    RE( makeSpecGenerator( 'mabt ' + line ))
    return 

@register_line_magic
def dscan(line):
    '''
    execute mab alpha beta , e.g.: mabt 1 2
      moves alpha to 1 and beta to 2
    '''
    print( "magics.ddscan, called with %s" % line)
    lst = line.split( ' ')
    print( lst[1])
    print(lst[1],lst[2],lst[3],lst[4])
    yield from dscan( lst[1], float( lst[2]), float( lst[3]), int( lst[4]))
#    RE( lst[1], float( lst[2]), float( lst[3]), int( lst[4]))
#    print(lst[0], lst[1])
    return 




magicCommands = [ ben, ben2, count,  ascan, a2scan, dscan]
del magicCommands

