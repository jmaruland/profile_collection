#!/usr/bin/env python3
'''
bluesky magic commands
'''
from IPython.core.magic import (register_line_magic)
from . import env
from . import TangoIfc
from . import docHandler
from bluesky import RunEngine
import blueskyDESY
import shlex
import PyTango
import HasyUtils

deviceList = None

def makeSpockGenerator( line): 
    """
    returns generators for the spock commands
    """
    def gen(): 
        from bluesky.plans import scan, rel_scan, list_scan, count
        from bluesky.plan_stubs import mv

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
            
            env.setSampleTime( float( lst[5]))
            mg = TangoIfc.Experiment()
            #mg = TangoIfc.Experiment( read_attrs = env.getActiveMntGrp()['counters'] + \
            #                          env.getActiveMntGrp()['mcas'])
            motor = TangoIfc.motorTango( lst[1])
            yield from scan( [mg], motor, float( lst[2]), float( lst[3]), int( lst[4]))
        #
        # a2scan eh_mot65 0 0.1 eh_mot66 0.2 0.3 10 0.1
        #
        elif lst[0] == 'a2scan':
            if len( lst) != 9:
                print( "magics.a2scan, expecting 9 tokens")
                print( "%s" % repr( lst))
                return None
            env.setSampleTime( float( lst[8]))
            mg = TangoIfc.Experiment()
            #mg = TangoIfc.Experiment( read_attrs = env.getActiveMntGrp()['counters'])
            mot1 = TangoIfc.motorTango( lst[1])
            mot2 = TangoIfc.motorTango( lst[4])
            yield from scan( [mg], 
                             mot1, float( lst[2]), float( lst[3]), 
                             mot2, float( lst[5]), float( lst[6]), 
                             int( lst[7]))
        #
        # dscan motor 0 10 10 0.1
        #
        elif lst[0] == 'dscan':
            if len( lst) != 6:
                print( "magics.dscan, expecting 6 tokens")
                print( "%s" % repr( lst))
                return None
            env.setSampleTime( float( lst[5]))
            mg = TangoIfc.Experiment()
            #mg = TangoIfc.Experiment( read_attrs = env.getActiveMntGrp()['counters'])
            motor = TangoIfc.motorTango( lst[1])
            yield from rel_scan( [mg], motor, float( lst[2]), float( lst[3]), int( lst[4]))
        #
        # d2scan eh_mot65 -0.1 0.1 eh_mot66 -0.2 0.2 10 0.1
        #
        elif lst[0] == 'd2scan':
            if len( lst) != 9:
                print( "magics.d2scan, expecting 9 tokens")
                print( "%s" % repr( lst))
                return None
            env.setSampleTime( float( lst[8]))
            mg = TangoIfc.Experiment()
            #mg = TangoIfc.Experiment( read_attrs = env.getActiveMntGrp()['counters'])
            mot1 = TangoIfc.motorTango( lst[1])
            mot2 = TangoIfc.motorTango( lst[4])
            yield from rel_scan( [mg], 
                             mot1, float( lst[2]), float( lst[3]), 
                             mot2, float( lst[5]), float( lst[6]), 
                             int( lst[7]))
        #
        # mv eh_mot65 0.1
        #
        elif lst[0] == 'mv':
            if len( lst) != 3:
                print( "magics.mv, expecting 3 tokens")
                print( "%s" % repr( lst))
                return None
            mot1 = TangoIfc.motorTango( lst[1])
            yield from mv( mot1, float( lst[2]))
        else:
            print( "magics.makeSpockGenerator: failed to identify %s" % line)
            return 

        return
    return gen()

@register_line_magic
def ascan(line):
    '''
    execute an ascan, e.g.: ascan eh_mot65 0 1 10 0.1    
      scan eh_mot65 from 0 to 1, 10 points, sample time 0.1
    '''
    print( "magics.ascan, called with %s" % line)
    RE = RunEngine() 
    RE.subscribe( docHandler.docCallback())
    RE( makeSpockGenerator( 'ascan ' + line))
    return 

@register_line_magic
def a2scan(line):
    '''
    execute an a2scan, e.g.: ascan eh_mot65 0 0.1 eh_mot66 0.1 0.3 10 0.1
      scan eh_mot65 from 0 to 1, eh_mot66 from 0.1 to 0.3 10 points, sample time 0.1
    '''
    print( "magics.ascan, called with %s" % line)
    RE = RunEngine() 
    RE.subscribe( docHandler.docCallback())
    RE( makeSpockGenerator( 'a2scan ' + line))
    return 

@register_line_magic
def dscan(line):
    '''
    execute an dscan, e.g.: dscan eh_mot65 -0.1 0.1 10 0.1
      scan eh_mot65 from (<currentPos> - 0.1) to (<currentPos> + 0.1), 
        10 points, sample time 0.1
    '''
    print( "magics.dscan, called with %s" % line)
    RE = RunEngine() 
    RE.subscribe( docHandler.docCallback())
    RE( makeSpockGenerator( 'dscan ' + line))
    return 

@register_line_magic
def d2scan(line):
    '''
    execute an d2scan, e.g.: d2scan eh_mot65 -0.1 0.1 eh_moy66 -0.2 0.2 10 0.1
      scan eh_mot65 from (<currentPos> - 0.1) to (<currentPos> + 0.1), 
           eh_mot66 from (<currentPos> - 0.2) to (<currentPos> + 0.2), 
           10 points, sample time 0.1
    '''
    print( "magics.dscan, called with %s" % line)
    RE = RunEngine() 
    RE.subscribe( docHandler.docCallback())
    RE( makeSpockGenerator( 'd2scan ' + line))
    return 

@register_line_magic
def mv(line):
    '''
    move a motor to a destination, e.g. mv eh_mot65 0.1
    '''
    print( "magics.mv: called with %s" % line)
    RE = RunEngine() 
    RE( makeSpockGenerator( 'mv ' + line))

@register_line_magic
def wa(line):
    '''
    show the position of all motors
    '''
    global deviceList
    if deviceList is None: 
        deviceList = HasyUtils.getOnlineXML()

    count = 0
    for elm in deviceList: 
        if elm[ 'type'] != 'stepping_motor' and \
           elm[ 'module'] != 'motor_tango':
            continue
        pos = None
        try: 
            p = PyTango.DeviceProxy( elm[ 'name'])
            pos = p.position
        except: 
            pass
        if pos is None: 
            print( "%14.14s %-15.15s " % (elm[ 'name'], repr( pos)), end='')
        else: 
            print( "%14.14s %-15.15g " % (elm[ 'name'], pos), end='')
            
        count += 1
        if count == 4: 
            count = 0
            print( "")

    return 

@register_line_magic
def wm(line):
    '''
    show the position of a motor, e.g. wm eh_mot65
    '''
    lst = line.split()
    if len( lst) != 1: 
        print( "magics.wm: wrong syntax, %s" % line)
        return 
    mot = blueskyDESY.motorTango( lst[0])
    print( "%s at %g" % ( lst[0], mot.position))
    return 

@register_line_magic
def lsct(line):
    '''
    lsct, list counter and timer
    '''
    global deviceList
    if deviceList is None: 
        deviceList = HasyUtils.getOnlineXML()

    for elm in deviceList: 
        if elm[ 'type'] != 'counter' and \
           elm[ 'type'] != 'timer':
            continue
        print( "%14.14s| %15.15s| %12.12s| %22.22s| %16.16s" % (elm[ 'name'], elm[ 'type'], elm[ 'module'], elm[ 'device'], elm[ 'hostname']))
    return 

@register_line_magic
def lsenv(line):
    '''
    lsenv, list the environment
    '''
    env.lsenv()
    return 

@register_line_magic
def lsm(line):
    '''
    lsm, list motors
    '''
    global deviceList
    if deviceList is None: 
        deviceList = HasyUtils.getOnlineXML()

    for elm in deviceList: 
        if elm[ 'type'] != 'stepping_motor' and \
           elm[ 'module'] != 'motor_tango':
            continue
        print( "%14.14s| %15.15s| %12.12s| %22.22s| %16.16s" % (elm[ 'name'], elm[ 'type'], elm[ 'module'], elm[ 'device'], elm[ 'hostname']))
    return 


@register_line_magic
def senv(line):
    '''
    senv ScanDir /temp

    senv b [1,2,3]
    senv MG1 "{ 'timer': 'eh_t01', 'counter' : [ 'eh_c01', 'eh_c02']}"
    senv ActiveMntGrp MG1
    '''
    lst = shlex.split( line)
    if len( lst) != 2:
        raise ValueError( "magics.senv, %s, len( lst) == %d != 2" % (line, len( lst)))
       
    val = lst[1]
    #
    # remove quotes
    #
    if val[0] == '"' and val[-1] == '"' or \
       val[0] == "'" and val[-1] == "'":
        val = val[1:-1]
    try: 
        a = int(val)
    except: 
        print( "magics.senv, not int") 
        try: 
            a = float(val)
        except: 
            print( "magics.senv, not float") 
            try: 
                if val.find( "[") or val.find( "{"):
                    a = eval( val)
            except Exception as e: 
                print( "magics.senv, not list or dict, %s" % val) 
                print( repr( e))
                a = val
 
    env.senv( lst[0], a)
    return 

@register_line_magic
def usenv(line):
    '''
    usenv ScanDir, delete a key
    '''
    lst = line.split( ' ')
    if len( lst) != 1:
        raise ValueError( "magics.usenv, %s, len( lst) != 1" % line)
        
    env.usenv( lst[0])
    return 

#from bluesky import RunEngine
#RE = RunEngine({})

#
# --- prepare live visualization
#
#from bluesky.callbacks.best_effort import BestEffortCallback
#bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
#RE.subscribe(bec)
#
# a message says the install_kicker() is no =longer needed
# Make plots update live while scans run.
#from bluesky.utils import install_kicker
#install_kicker()
#
# --- prepare data storage
#
#from databroker import Broker
#db = Broker.named('temp')
# Insert all metadata/data captured into db.
#RE.subscribe(db.insert)

def makeExampleGenerator( name): 
    """
    returns generators for the examples
    """
    def gem(): 
        from ophyd.sim import det1, det2, det3 
        from ophyd.sim import motor1, motor2, motor3
        from bluesky.plans import scan, rel_scan, list_scan, count
        from bluesky.plan_stubs import mv
        dets = [det1, det2, det3]
        if name.lower() == 'simplescan': 
            yield from scan( dets, motor1, -1, 1, 20)
        elif name.lower() == 'simplerelscan': 
            yield from rel_scan( dets, motor1, -1, 1, 20)
        elif name.lower() == 'listscan': 
            points = [ 1, 1, 2, 3, 5, 8, 13]
            yield from list_scan( dets, motor1, points)
        elif name.lower() == "moveandcount": 
            print( "1:motor1 at %g, motor2 at %g" % ( motor1.position, motor2.position))
            yield from mv(motor1, 1, motor2, 10)
            print( "2:motor1 at %g, motor2 at %g" % ( motor1.position, motor2.position))
            yield from count(dets, num=5)
            print( "3:motor1 at %g, motor2 at %g" % ( motor1.position, motor2.position))
            yield from mv(motor1, 0, motor2, 0)
            print( "4:motor1 at %g, motor2 at %g" % ( motor1.position, motor2.position))
        else:
            print( "magis.examples: failed to identify %s" % name)
            return 

        return
    return gen()

@register_line_magic
def examples(line):
    """
    display the examples or execute one
    """

    if line is None or len( line) == 0:
        print( "Examples:")
        print( "  simpleScan")
        print( "  simpleRelScan")
        print( "  listScan")
        print( "  moveAndCount")
        return

    if line.lower() == "testmv": 
        plan = mv( motor1, 0)
        for message in plan: 
            print( message)
        return 

    RE( makeExampleGenerator( line))

    return 


@register_line_magic
def lsmag(line):
    """
    list the DESY specific magic commands
    """
    lst = [ elm.__name__ for elm in magicCommands] 
    print( "%s " % repr( lst))
    return 

magicCommands = [ ascan, a2scan, dscan, d2scan, lsct, lsenv, lsm, lsmag, mv, senv,  usenv, wa, wm, examples] 

for elm in magicCommands: 
    del elm


