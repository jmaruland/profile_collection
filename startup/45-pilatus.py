
print(f'Loading {__file__}')

import uuid
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
    auto_increment = Cpt(EpicsSignal, 'AutoIncrement', kind='config')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        self.stage_sigs['auto_increment'] = 1
        self.stage_sigs['file_number'] = 0

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()

    def stage(self):
        self.file_name.set(f"pil_img_{str(uuid.uuid4())[:8]}")
        super().stage()

    file_path = Cpt(SignalWithRBV, 'FilePath', string=True)
    file_name = Cpt(SignalWithRBV, 'FileName', string=True)
    file_template = Cpt(SignalWithRBV, 'FileName', string=True)        
    file_number = Cpt(SignalWithRBV, 'FileNumber')


class PilatusDetector(PilatusDetector):
    cam = Cpt(PilatusDetectorCamV33, 'cam1:')
    

class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    ...


class Pilatus(SingleTriggerV33, PilatusDetector):
    tiff = Cpt(
        TIFFPluginWithFileStore,
        suffix="TIFF1:",
        write_path_template = "",
    )

    def stage(self, *args, **kwargs):
        folder_name = f"opls-{self.name.lower()}"    # e.g. 'opls-pilatus100k'
        self.tiff.write_path_template = assets_path() + f'{folder_name}/%Y/%m/%d/'
        self.tiff.read_path_template = assets_path() + f'{folder_name}/%Y/%m/%d/'
        self.tiff.reg_root = assets_path() + f'{folder_name}'
        return super().stage(*args, **kwargs)

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


try:
    pilatus100k = Pilatus("XF:12ID1-ES{Det:P100k}", name="pilatus100k")
    set_detector(pilatus100k)
except:
    print('Pilatus 100k is not connected')


try:
    pilatus100kA = Pilatus("XF:12ID1-ES{Det:P100K-A}", name="pilatus100kA")
    set_detector(pilatus100kA)
except:
    print('Pilatus 100k is not connected')


try:
    pilatus1m = Pilatus("XF:12ID1-ES{Det:P1M}", name="pilatus1m")
    set_detector(pilatus1m)
except:
    print('Pilatus 100k is not connected')


try:
    pilatus300k = Pilatus("XF:12ID1-ES{Det:P300k}", name="pilatus300k")
    set_detector(pilatus300k)
except:
    print('Pilatus 300k is not connected')
