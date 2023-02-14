
print(f'Loading {__file__}')

from ophyd import ( Component as Cpt, EpicsSignal, ROIPlugin, TransformPlugin,
                    PilatusDetector, OverlayPlugin, TIFFPlugin )
from ophyd.areadetector.filestore_mixins import FileStoreTIFFIterativeWrite
from ophyd.areadetector.cam import PilatusDetectorCam
from ophyd.areadetector.detectors import PilatusDetector
from ophyd.areadetector.base import EpicsSignalWithRBV as SignalWithRBV
from nslsii.ad33 import StatsPluginV33, SingleTriggerV33

class PilatusDetectorCamV33(PilatusDetectorCam):
    '''This is used to update the Pilatus to AD33.'''

    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',
                           string=True, kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()

    file_path = Cpt(SignalWithRBV, 'FilePath', string=True)
    file_name = Cpt(SignalWithRBV, 'FileName', string=True)
    file_template = Cpt(SignalWithRBV, 'FileName', string=True)        
    file_number = Cpt(SignalWithRBV, 'FileNumber')


class PilatusDetector(PilatusDetector):
    cam = Cpt(PilatusDetectorCamV33, 'cam1:')
    

class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    ...


class Pilatus(SingleTriggerV33, PilatusDetector):
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix="TIFF1:",
               write_path_template="/nsls2/xf12id1/data/pilatus100k/%Y/%m/%d/",
               read_path_template= "/nsls2/xf12id1/data/pilatus100k/%Y/%m/%d/",
            #    root='/nsls2/xf12id1/data'
               root='/nsls2/data/smi/legacy/xf12id1/data'
               )

    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')

    stats1 = Cpt(StatsPluginV33, 'Stats1:', read_attrs=['total'])
    stats2 = Cpt(StatsPluginV33, 'Stats2:', read_attrs=['total'])
    stats3 = Cpt(StatsPluginV33, 'Stats3:', read_attrs=['total'])
    stats4 = Cpt(StatsPluginV33, 'Stats4:', read_attrs=['total'])

    over1 = Cpt(OverlayPlugin, 'Over1:')
    trans1 = Cpt(TransformPlugin, 'Trans1:')


    def set_primary_roi(self, num):
        st = f'stats{num}'
        self.read_attrs = [st, 'tiff']
        getattr(self, st).kind = 'hinted'


def set_detector(det):
    det.tiff.kind = 'normal' 
    det.stats1.kind = 'hinted'
    det.stats2.kind = 'hinted'
    det.stats3.kind = 'hinted'
    det.stats4.kind = 'hinted'

    det.stats1.total.kind = 'hinted'
    det.stats2.total.kind = 'hinted'
    det.stats3.total.kind = 'normal'
    det.stats4.total.kind = 'normal'

    det.stats1.kind='hinted'
    det.stats1.centroid.x.kind = 'hinted' 
    det.stats1.centroid.y.kind = 'hinted' 
    det.stats2.centroid.kind = 'hinted'

    det.stats2.max_value.kind = 'normal'
    det.stats4.max_value.kind = 'normal'

    det.cam.ensure_nonblocking()

# on 10/10/22 we commented out the following 4 lines since the 100k server was not working
#pilatus100k = Pilatus("XF:12ID1-ES{Det:P100k}", name="pilatus100k")
#set_detector(pilatus100k)
#pilatus100k.tiff.write_path_template = "/nsls2/xf12id1/data/pilatus100k/%Y/%m/%d/"
#pilatus100k.tiff.read_path_template = "/nsls2/xf12id1/data/pilatus100k/%Y/%m/%d/"


try:
    pilatus100k = Pilatus("XF:12ID1-ES{Det:P100k}", name="pilatus100k")
    set_detector(pilatus100k)
    # pilatus300k.tiff.write_path_template = "/nsls2/xf12id1/data/pilatus300k/%Y/%m/%d/"
    # pilatus300k.tiff.read_path_template = "/nsls2/xf12id1/data/pilatus300k/%Y/%m/%d/"

    pilatus100k.tiff.write_path_template = "/nsls2/data/smi/legacy/xf12id1/data/pilatus100k/%Y/%m/%d/"
    pilatus100k.tiff.read_path_template = "/nsls2/data/smi/legacy/xf12id1/data/pilatus100k/%Y/%m/%d/"

except:
    # pilatus100k=pilatus100k
    print('Pilatus 100k is not connected')


try:
    pilatus300k = Pilatus("XF:12ID1-ES{Det:P300k}", name="pilatus300k")
    set_detector(pilatus300k)
    # pilatus300k.tiff.write_path_template = "/nsls2/xf12id1/data/pilatus300k/%Y/%m/%d/"
    # pilatus300k.tiff.read_path_template = "/nsls2/xf12id1/data/pilatus300k/%Y/%m/%d/"

    pilatus300k.tiff.write_path_template = "/nsls2/data/smi/legacy/xf12id1/data/pilatus300k/%Y/%m/%d/"
    pilatus300k.tiff.read_path_template = "/nsls2/data/smi/legacy/xf12id1/data/pilatus300k/%Y/%m/%d/"

except:
    # pilatus300k=pilatus100k
    print('Pilatus 300k is not connected')


def det_exposure_time_pilatus(exp_t, meas_t=1):
    yield from bps.mov(
        pilatus100k.cam.acquire_time, exp_t,
        pilatus100k.cam.acquire_period, exp_t+0.2,
        pilatus100k.cam.num_images, int(meas_t/exp_t))
    try:
        yield from bps.mov(
            pilatus300k.cam.acquire_time, exp_t,
            pilatus300k.cam.acquire_period, exp_t+0.2,
            pilatus300k.cam.num_images, int(meas_t/exp_t))
    except:
        print('Pilatus 300KW is not connected')


def det_exposure_time_new(detector, exp_t, meas_t=1):
    yield from bps.mov(
        detector.cam.acquire_time, exp_t,
        detector.cam.acquire_period, exp_t+0.2,
        detector.cam.num_images, int(meas_t/exp_t))

'''
def sample_id(*, user_name, sample_name, tray_number=None):
    # DIRTY HACK, do not copy
    pilatus100k.cam.file_name.put(fname)
    pilatus100k.cam.file_number.put(1)
'''
pil1m_roi2 = EpicsSignal('XF:12ID1-ES{Det:P100k}Stats1:Total_RBV', name= 'test')                                                                                   
#pilatus100k.set_primary_roi(2)        



