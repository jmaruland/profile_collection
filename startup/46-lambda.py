print(f'Loading {__file__}')

from ophyd import Component as Cpt
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector import ADComponent as ADCpt, DetectorBase

from nslsii.ad33 import StatsPluginV33
from nslsii.ad33 import SingleTriggerV33


class Lambda750kCam(CamBase):
    """
    support for X-Spectrum Lambda 750K detector
    
    https://x-spectrum.de/products/lambda-350k750k/
    """
    _html_docs = ['Lambda750kCam.html']

    config_file_path = ADCpt(EpicsSignal, 'ConfigFilePath')
    firmware_version = ADCpt(EpicsSignalRO, 'FirmwareVersion_RBV')
    operating_mode = ADCpt(SignalWithRBV, 'OperatingMode')
    serial_number = ADCpt(EpicsSignalRO, 'SerialNumber_RBV')
    temperature = ADCpt(SignalWithRBV, 'Temperature')


class LambdaDetector(DetectorBase):
    _html_docs = ['lambda.html']
    cam = Cpt(Lambda750kCam, 'cam1:')


class Lambda(SingleTriggerV33, LambdaDetector):
    # MR20200122: created all dirs recursively in /nsls2/jpls/data/lambda/
    # from 2020 to 2030 with 777 permissions, owned by xf12id1 user.
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix="TIFF1:",
               write_path_template="/disk2/jpls_data/data/lambda/%Y/%m/%d/",
               read_path_template="/nsls2/jpls/data/lambda/%Y/%m/%d/",
               root='/nsls2/jpls/data')

    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')

    stats1 = Cpt(StatsPluginV33, 'Stats1:', read_attrs=['total'])
    stats2 = Cpt(StatsPluginV33, 'Stats2:', read_attrs=['total'])
    stats3 = Cpt(StatsPluginV33, 'Stats3:', read_attrs=['total'])
    stats4 = Cpt(StatsPluginV33, 'Stats4:', read_attrs=['total'])

    low_thr = Cpt(EpicsSignal, 'cam1:LowEnergyThreshold')
    hig_thr = Cpt(EpicsSignal, 'cam1:HighEnergyThreshold')
    oper_mode = Cpt(EpicsSignal, 'cam1:OperatingMode')

lambda_det = Lambda('XF:12ID1-ES{Det:Lambda}', name='lambda_det')
lambda_det.tiff.kind = 'hinted'

lambda_det.roi1.kind = 'hinted'
lambda_det.stats1.kind = 'hinted'
lambda_det.stats1.total.kind = 'hinted'

lambda_det.stats4.total.kind = 'hinted'
lambda_det.stats4.kind = 'hinted'
lambda_det.stats4.total.kind = 'hinted'
lambda_det.stats4.max_value.kind = 'normal'


# Impose Stats4 to be ROI4 if in the future we need to exclude bad pixels
def set_defaut_stat_roi():
    yield from bps.mv(lambda_det.stats1.nd_array_port, 'ROI1')
    yield from bps.mv(lambda_det.stats2.nd_array_port, 'ROI2')
    yield from bps.mv(lambda_det.stats3.nd_array_port, 'ROI3')
    yield from bps.mv(lambda_det.stats4.nd_array_port, 'ROI4')

# Define the region of interest if required
# lambda_det.roi1.size.x.value = 31
# lambda_det.roi1.min_xyz.size_x.value = 100

