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
    '''Sample defined by the sample-related PVs based on given slots (e.g., 'A')'''
    def __init__(self, slot):
        self.sample_epics = SampleEpicsSignal(slot)
        self.slot = slot
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
        '''Read the sh.user_offset value after the sample height alignment'''
        self.sh_offset = sh.user_offest.value if not IN_SIM_MODE else None # could not read user_offset in SIM_mode

    def sh_offset_set(self):
        '''Set the sh.user_offset value if the sample height has been aligned'''
        if self.sh_offset is not None:
            sh.user_offset.set(self.sh_offset)
        else:
            raise ValueError(f'The sh of <{self.name}> has NOT been aligned yet!') 

    def reset_clock(self):
        self.clock_o = time.time()

    def clock(self):
        time_delta = time.time() - self.clock_o
        return time_delta


class TroughChamber():
    '''a chamber contains multiple troughs'''
    
    def __init__(self):
        self._samples = {}
        self.reset_clock()
        self.addSamples()
        self.seq_dict = {}
        self.seq_nums = set()
        self.addSeq()

    def reset_clock(self):
        self.clock_o = time.time()

    def clock(self):
        time_delta = time.time() - self.clock_o
        return time_delta

    def addSamples(self):
        """Add samples from epics."""
        for slot in ['A', 'B', 'C', 'D']:
            self._samples[slot] = Sample(slot)

    def getSamples(self):
        '''Get sample list'''
        samples_list = []
        for sample_slot, sample in sorted(self._samples.items()):
            samples_list.append(sample)
        return samples_list
    
    def listSamples(self):
        """Print a list of the current samples associated with this holder"""
        for sample_slot, sample in sorted(self._samples.items()):
            # print("{}: {:s} --> run: {}".format(sample_slot, sample.name, sample.run))
            print(f"{sample_slot: <2}: {sample.name: <25} run-->", sample.run)

    def addSeq(self):
        '''Add sequence number for the run. They needs to be unique numbers.'''
        for _sam in self.getSamples():
            if _sam.run:
                if _sam.seq_num in self.seq_nums:
                    raise ValueError(f'Seq Num {_sam.seq_num} is not unique!')
                self.seq_nums.add(_sam.seq_num)
                self.seq_dict[_sam.seq_num] = _sam.slot

    def listRuns(self):
        '''List sample run info.'''
        # formating
        sample_len = []
        for _seq in self.seq_nums:
            sample_len.append(len(self._samples[self.seq_dict[_seq]].name))
        sample_len_max = max(sample_len)+1

        print('----------------------------------------------------------------------')
        print('Samples to run:')
        for _seq in self.seq_nums:
            sample = self._samples[self.seq_dict[_seq]]
            measure_type = [measure.upper() for measure in ['xrr', 'xrf', 'gisaxs', 'gid'] if getattr(sample,measure)]
            print(f'Seq: {sample.seq_num}, x2 = {sample.x2:>4.1f}, {sample.name: <{sample_len_max}}: {measure_type} ')

        print('----------------------------------------------------------------------')



## for testing
if False:
    # sam = Sample('A')
    # print(sam)
    chamber = TroughChamber()
    chamber.listSamples()
    chamber.listRuns()



