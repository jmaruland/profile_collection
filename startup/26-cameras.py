print(f'Loading {__file__}')

from ophyd import EpicsMotor, EpicsSignal, Device, Component as C

from ophyd import (ProsilicaDetector, SingleTrigger, TIFFPlugin, ImagePlugin,
                    EpicsSignal, ROIPlugin, TransformPlugin, ProcessPlugin)

from ophyd.areadetector.filestore_mixins import (FileStoreTIFFIterativeWrite)

from ophyd import Component as Cpt, Signal
from ophyd.utils import set_and_wait
from nslsii.ad33 import StatsPluginV33 as StatsPlugin


class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    pass

class StandardProsilica(SingleTrigger, ProsilicaDetector):
    image = Cpt(ImagePlugin, 'image1:')
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
               write_path_template='/tmp/%Y/%m/%d/',
               read_path_template='/tmp/%Y/%m/%d/',
               root='/tmp/')


FS = StandardProsilica('XF:12ID1-BI{Scr:1}', name='FS')


FS.read_attrs = ['stats1', 'stats2', 'stats3', 'stats4']
FS.stats1.read_attrs = ['total']
FS.stats2.read_attrs = ['total']
FS.stats3.read_attrs = ['total']
FS.stats4.read_attrs = ['total']
