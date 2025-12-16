'''
A new Attenuator class to load, select, and update the attenuator datebase.
The attenuator object will be used in 
    1. the updated quadem signal in 40-quadem.py
    2. trigger_and_read in XRR, XRF measurements (74 and 75)

The database is a csv file with two entries:
    a. date: datetime str,
    b. attenuators: json string, which can be loaded as a dict.

Honghu at SMS-OPLS, 2024-10-23 updated
'''

import os
import json
import datetime
import pandas as pd
import numpy as np


path = '/nsls2/data/smi/opls/shared/config/operations/bsui_parameters/attenuators/'
att_file = 'opls_attenuators_database.csv'

class Attenuator():

    def __init__(self, att_file= path+att_file):

        self.database_file = att_file
        self.att_mater_selected = None
        self.att_dict_selected = None
        self.att_fact_selected = None
        _ = self.att_select()

    def att_load(self, index = None, date = None, infile = path + att_file):
        '''
        Load attenuators file stored in the csv file
        '''
        df = pd.read_csv(infile)

        # read by date key
        if date is not None:
            df = df[df['date'] == date]
            if len(df) == 0:
                raise KeyError('Pleae provide a correct date!')
            else:
                data = df['attenuators'].values[-1]
        
        # read by index
        else:
            if index is None:
                index = -1
            data = df.iloc[index]['attenuators']

        att_dict = json.loads(data)
        return att_dict


    def att_udpate(self, att_dict, outfile = None):
        '''
        Update attenuation values and append to the csv file
        Note: att_dict can be a dict of all the attenuators or just the updated one
        '''
        att_dict_old = self.att_load()
        att_dict_new = {**att_dict_old, **att_dict} # overwrite the old values

        data = json.dumps(att_dict_new) 
        df = pd.DataFrame({
                    'date': datetime.datetime.now(),
                    'attenuators': [data]
                })
        df.to_csv(outfile, mode='a', index = False, header = not os.path.exists(outfile))


    def att_select(self, energy_select=None, att_dict = None, verbosity=1):
        '''
        Select the attenuators based on a given energy [eV]
        '''
        if energy_select is None:
            energy_select = energy.energy.position

        self.energy = energy_select

        if att_dict is None:
            att_dict = self.att_load()

        if energy_select < 10000:
            att_mater = 'Nb_9.7keV'
        elif energy_select < 15200:
            att_mater = 'Si_14.4keV'
        elif energy_select < 17000:
            att_mater = 'Cu_16.1keV'
        else:
            att_mater = 'Al_23keV'
        
        if verbosity <= 1:
            print(f'E = {energy_select:.1f}eV, selected attenuator: {att_mater}.')


        self.att_mater_selected = att_mater
        self.att_dict_selected = att_dict[att_mater]
        self.att_fact_selected = self.att_factorial(self.att_dict_selected)

        return {att_mater: att_dict[att_mater]}


    def att_factorial(self, att_dict):
        '''
        A recursive function to calculate attenuation factors
        '''
        att_dict_copy = att_dict.copy() # avoid mutating the input dict

        if len(att_dict_copy) == 1: # No scaling for the first attenuator
            return att_dict_copy 
        
        k_pop, v_pop = att_dict_copy.popitem() # pop the last item
        att_fact = self.att_factorial(att_dict_copy)
        
        k_last, v_last = _, att_fact[k_last] = att_fact.popitem() # get the last value from the atten_factorial
        att_fact[k_pop] = np.round(v_last*v_pop,2)

        return att_fact


    def get_atten_name(self, one_id, db=None):
        '''
        Get attenuator names based on a scan_id or uid
        '''

        if db is None:
            db = Broker.named('opls')
 
        h = db[one_id]
        df = db.get_table(h, fill=False, stream_name='primary')

        return df['attenuator_name'].values


    def get_atten_fact_array(self, one_id, db=None, energy=None):
        '''
        The attenuention factors based on the energy
        '''
        if db is None:
            db = Broker.named('opls')
            
        
        h = db[one_id]
        
        if energy is None:
            energy = h.start['energy']

        att_selected = self.att_select(energy,verbosity=2)
        att_dict = att_selected[list(att_selected.keys())[0]]
        att_fact = self.att_factorial(att_dict)
        att_name = self.get_atten_name(db=db, one_id=one_id)
        att_fact_array = np.array([att_fact[_name] for _name in att_name])

        return np.round(att_fact_array, 2)


atten = Attenuator() # Need to improve
att_fact_selected = atten.att_fact_selected



from ophyd import Signal

# # global attenuation_factor_signal, attenuator_name_signal, default_attenuation # exposure_time, 
attenuator_name_signal = Signal(name='attenuator_name', value='att6',kind='normal')
attenuation_factor_signal = Signal(name='attenuation', value=1e-7,kind='normal')
default_attenuation = Signal(name='default-attenuation', value=1e-7)


# # global attenuation_factor_signal, exposure_time, attenuator_name_signal, default_attenuation
# attenuator_name_signal = Signal(name='attenuator_name', value='abs1')
# attenuation_factor_signal = Signal(name='attenuation', value=1e-7)
# default_attenuation = Signal(name='default-attenuation', value=1e-7)


