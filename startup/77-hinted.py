#################################################
# Code for set the "kind" of detectors and motors
# by HZ @ 2022-05-04
#################################################

##### core methods
def hinted_one(object, read_attr, kind='hinted'):
    '''
    Set an arttribute of an object to hinted
    Input: object_name, read_attr (string), kind that can be 'hinted' or 'normal'    
    '''
    getattr(object, read_attr).kind = kind

def hinted_motor(motor, read_attr='user_readback', kind='hinted'):
    '''Set an arttribute of a motor to hinted'''
    hinted_one(motor, read_attr, kind)

def hinted_det(detector, attrs_list, kind='hinted'):
    '''Set arttributes of a detector to hinted'''
    if not isinstance(attrs_list, list):
        attrs_list = [attrs_list]
    for read_attr in attrs_list:
        hinted_one(detector, read_attr, kind)



##### Hinted settings for x-ray reflectivity
def hinted_ref():
    '''
    hinted settings for reflectivity scans; these motors are defined in the 99-shortcut.py
    '''
    # 
    motor_list = [th, phi, phix, ih, ia, sh, oh, oa, astth, stblx, tth, chi]
    for one_motor in motor_list:
        try:
            hinted_motor(one_motor, read_attr='user_readback', kind='hinted')
        except:
            hinted_motor(one_motor, read_attr='readback', kind='hinted') # for simulation mode


def unhinted_ref():
    '''hinted settings back to normal after reflectivity scans'''
    # these motors are defined in the 99-shortcut.py
    motor_list = [th, phi, phix, ih, ia, sh, oh, oa, astth, stblx, tth, chi]
    for one_motor in motor_list:
        try:
            hinted_motor(one_motor, read_attr='user_readback', kind='normal')
        except:
            hinted_motor(one_motor, read_attr='readback', kind='normal') # for simulation mode



##### Hinted settings for quadem detector
# omitted setting for quadem detector to clean up the data table() in databroker or spec-like file
def omitted_quadem(kind='omitted'):
    '''
    The omitted attributes will not show in the data table. 
    Note: The original setting is "normal"
    '''
    detector = quadem
    attrs_list = ['position_offset_calc_x', 'position_offset_calc_y', 
                  'position_offset_x', 'position_offset_y', 
                  'position_scale_x', 'position_scale_Y',
                  'em_range'
                  ]
    hinted_det(detector, attrs_list, kind)

    # some configuration attrs have read_attrs, need to asign a kind to all of them
    config_names = ['current_names', 'current_offsets', 'current_offset_calcs', 'current_scales']
    read_attrs = [f'ch{i}' for i in range(1,5)]
    for config_name in config_names:
        hinted_det(getattr(detector,config_name), read_attrs, kind)


# Hinted setting for quadem detector, mean_value channels
def hinted_quadem_mean(channel_list=[2,3], attrs_list=['mean_value']):
    '''
    Set selected channels in quadem to be hinted
    first set all 4 channels to normal, then hinted for selected channels
    '''
    for i in range(1,5):
        hinted_det(getattr(quadem, f"current{i}"), attrs_list, kind='normal')

    for k in channel_list:
        hinted_det(getattr(quadem, f"current{k}"), attrs_list, kind='hinted')



#### TODO need to check omitted.
# Hinted setting for lambda detector, 
def hinted_lambda_single(channel, kind='hinted'):
    '''hinted setting for single channel of lambda_det with sub read_attrs'''
    detector = lambda_det
    hinted_det(detector, channel, kind=kind)

    # set the sub read_attrs to be hinted
    det_channel = getattr(detector,channel)
    read_attrs = getattr(det_channel, 'read_attrs')
    hinted_det(det_channel, read_attrs, kind=kind)


def hinted_lambda(channel_list=['stats2','stats4']):
    '''
    hinted settings for lambda_det including sub read_attrs
    first set all 4 channels to normal, then hinted for selected channels
    stats2: ['total]; stats4: ['max_value', 'total']
    '''

    for i in range(1,5):
        one_channel = f"stats{i}"
        hinted_lambda_single(one_channel, kind='normal') ## TODO: some need to set to omitted

    for channel in channel_list:
        hinted_lambda_single(channel, kind='hinted')




##### for testing
def print_attrs_kind(detector):
    '''
    print all the configuration_attrs that have "kind" attribute
    '''
    config_names = getattr(detector,'configuration_attrs')
    for config_name in config_names:
        config = getattr(detector,config_name)
        if hasattr(config, 'kind'):
            print(config_name, config.kind.value)

def print_attrs_kind_quandem():
    '''
    print configuration_attrs that are shown in data table
    '''
    config_names = ['current_names', 'current_offsets', 'current_offset_calcs', 'current_scales',
                    'position_offset_calc_x', 'position_offset_calc_y', 
                    'position_offset_x', 'position_offset_y', 
                    'position_scale_x', 'position_scale_Y',
                    'em_range'
                  ]

    detector = quadem
    for config_name in config_names:
        config = getattr(detector,config_name)
        if hasattr(config, 'kind'):
            print(config_name, config.kind.value)
        if hasattr(config, 'read_attrs'):
            read_attrs = getattr(config, 'read_attrs')
            for read_attr in read_attrs:
                print(read_attr, getattr(config, read_attr).kind.value)



def print_attrs_kind_motors():
    motor_list = [th, phi, phix, ih, ia, sh, oh, oa, astth, stblx, tth, chi]
    for one_motor in motor_list:
        print(one_motor.name, one_motor.user_readback.kind)