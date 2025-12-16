#print(f'Loading {__file__}')

from ophyd import EpicsMotor, EpicsSignal, Device, Component as C

from ophyd import (ProsilicaDetector, SingleTrigger, TIFFPlugin, ImagePlugin,
                    EpicsSignal, ROIPlugin, TransformPlugin, ProcessPlugin, ProsilicaDetectorCam)

from ophyd.areadetector.filestore_mixins import (FileStoreTIFFIterativeWrite)

from ophyd import Component as Cpt, Signal
from ophyd.utils import set_and_wait
from nslsii.ad33 import StatsPluginV33 as StatsPlugin


class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    pass

class ProsilicaDetectorCamV33(ProsilicaDetectorCam):
    """This is used to update the standard prosilica to AD33."""

    wait_for_plugins = Cpt(EpicsSignal, "WaitForPlugins", string=True, kind="config")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs["wait_for_plugins"] = "Yes"

    def ensure_nonblocking(self):
        self.stage_sigs["wait_for_plugins"] = "Yes"
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, "ensure_nonblocking"):
                cpt.ensure_nonblocking()

class StandardProsilica(SingleTrigger, ProsilicaDetector):
    image = Cpt(ImagePlugin, 'image1:')
    cam = Cpt(ProsilicaDetectorCamV33, "cam1:")
    stats1 = Cpt(StatsPlugin, 'Stats1:')
    stats2 = Cpt(StatsPlugin, 'Stats2:')
    stats3 = Cpt(StatsPlugin, 'Stats3:')
    stats4 = Cpt(StatsPlugin, 'Stats4:')
    stats5 = Cpt(StatsPlugin, 'Stats5:')
    trans1 = Cpt(TransformPlugin, 'Trans1:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')

    def set_primary_roi(self, num):
        st = f'stats{num}'
        self.hints = {'fields': [getattr(self, st).total.name]}
        self.read_attrs = [st]

class StandardProsilicaWithTIFF(StandardProsilica):
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix='TIFF1:',
               write_path_template='',
               root='/')
    
    def stage(self, *args, **kwargs):
        folder_name = f"opls-{self.name.lower()}"
        self.tiff.write_path_template = assets_path() + f'{folder_name}/%Y/%m/%d/'
        self.tiff.read_path_template = assets_path() + f'{folder_name}/%Y/%m/%d/'
        self.tiff.reg_root = assets_path() + f'{folder_name}'
        return super().stage(*args, **kwargs)


FS = StandardProsilicaWithTIFF('XF:12ID1-BI{Scr:1}', name='webcam-1')

FS.image.kind = 'hinted'
FS.tiff.kind = 'hinted' 

FS.read_attrs = ['stats1', 'stats2', 'stats3', 'stats4', 'tiff']
FS.stats1.read_attrs = ['total']
FS.stats2.read_attrs = ['total']
FS.stats3.read_attrs = ['total']
FS.stats4.read_attrs = ['total']

FS.cam.ensure_nonblocking()
FS.configuration_attrs = ['cam.acquire_time']
FS.tiff.read_attrs = []
FS.cam.ensure_nonblocking()
