print(f'Loading {__file__}')

from ophyd import ( Component as Cpt, ADComponent, Device, PseudoPositioner,
                    EpicsSignal, EpicsSignalRO, EpicsMotor,
                    ROIPlugin, ImagePlugin,
                    SingleTrigger, PilatusDetector,
                    OverlayPlugin, FilePlugin, TIFFPlugin)

from ophyd.areadetector.filestore_mixins import FileStoreTIFFIterativeWrite
from ophyd.areadetector.cam import PilatusDetectorCam
from ophyd.areadetector.detectors import PilatusDetector
from ophyd.areadetector.base import EpicsSignalWithRBV as SignalWithRBV

from ophyd.utils import set_and_wait
from databroker.assets.handlers_base import HandlerBase
import os
import bluesky.plans as bp
import time
from nslsii.ad33 import StatsPluginV33
from nslsii.ad33 import SingleTriggerV33
import pandas as pds






#ToDo: Call the lambda from ophyd + create path to folders
# lamdba_detector = Pilatus("XF:12IDB-BI{Lambda-Cam:1}", name="lambda_detector")
# write_path_template="/disk2/jpls_data/data/lambda/%Y/%m/%d/",
# read_path_template="/nsls2/jpls/data/lambda/%Y/%m/%d/",

# set_detector(lamdba_detector)
