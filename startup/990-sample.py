################################################################################
#  Code for defining a 'Sample' class, which keeps track of its state, and 
# simplifies the task of aligning, measuring, etc.
# by Honghu Zhang @ OPLS, 01/23/2024
################################################################################

from dataclasses import dataclass
from ophyd import EpicsSignal
import time

### reading from the User Parameters CSS screen

def getUserSampleEpics(slot='A'):
    '''To read the EpicsSignal from User Parameters '''
    
    run    = EpicsSignal(f"XF:12ID1:User{slot}-Run", name=f"Sam{slot}_run")
    seq    = EpicsSignal(f"XF:12ID1:User{slot}-RunNum", name=f"Sam{slot}_seq")
    name   = EpicsSignal(f"XF:12ID1:User{slot}-Run.DESC", name=f"Sam{slot}_name")
    x2     = EpicsSignal(f"XF:12ID1:User{slot}-X2Pos", name=f"Sam{slot}_x2")
    xrr    = EpicsSignal(f"XF:12ID1:User{slot}-XRR", name=f"Sam{slot}_xrr")
    xrf    = EpicsSignal(f"XF:12ID1:User{slot}-XRF", name=f"Sam{slot}_xrf")
    gisaxs = EpicsSignal(f"XF:12ID1:User{slot}-GISAXS", name=f"Sam{slot}_gisaxs")
    gid    = EpicsSignal(f"XF:12ID1:User{slot}-GID", name=f"Sam{slot}_gid")

    return [run, seq, name, x2, xrr, xrf, gisaxs, gid]


class SampleEpicsSignal():
    '''the Epics signal for all the sample-related PVs'''
    def __init__(self, slot):
        run, seq, name, x2, xrr, xrf, gisaxs, gid = getUserSampleEpics(slot)
        self.run = run
        self.seq_num = seq
        self.name = name
        self.x2 = x2
        self.xrr = xrr
        self.xrf = xrf
        self.gisaxs = gisaxs
        self.gid = gid
        self.slot = slot

    def __str__(self):
        return f'Epics Signal Components for Sample Slot {self.slot}'

    def __repr__(self):
        return f'SampleEpicsSignal(Slot: {self.slot})'


@dataclass
class Sample_Generic:
    '''A general sample class'''
    name: str = 'best_sample_ever'
    seq_num: int = 1
    x2: float = 10.0
    sh_offset: float = None
    clock_o: time = time.time()
    run: bool = False
    xrr: bool = False
    xrf: bool = False
    gisaxs: bool = False
    gid: bool = False


class Sample(Sample_Generic):
    '''Sample defined by the sample-related PVs'''
    def __init__(self, slot):
        self.sample_epics = SampleEpicsSignal(slot)
        self.update()

    def update(self):
        self.run = True if self.sample_epics.run.get() else False
        self.seq_num = int(self.sample_epics.seq_num.get())
        self.name = self.sample_epics.name.get()
        self.x2 = self.sample_epics.x2.get()
        self.xrr = True if self.sample_epics.xrr.get() else False
        self.xrf = True if self.sample_epics.xrf.get() else False
        self.gisaxs = True if self.sample_epics.gisaxs.get() else False
        self.gid = True if self.sample_epics.gid.get() else False

    def sh_offset_update(self):
        self.sh_offset = sh.user_offest.value if not IN_SIM_MODE else None # could not read user_offset in SIM_mode

    def reset_clock(self):
        self.clock_o = time.time()

    def clock(self):
        time_delta = time.time() - self.clock_o
        return time_delta


class TroughChamber():
    '''a chamber contains multiple troughs'''
    pass



