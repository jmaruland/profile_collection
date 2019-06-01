import matplotlib.pyplot as plt
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.callbacks import LiveTable, LivePlot

from ophyd.sim import hw

hw = hw()

def ascan(start, stop, num, md=None):
    '''
    Scan the diffractometer motors while reading the beam intensity.
    '''
    dets = [hw.rand]
    motor = geo # ip.th
    cols = ['geo_alpha', 'rand'] # ip_th

    plan = bp.scan(dets, motor, start, stop, num, md=md)

    yield from plan

