from pathlib import Path

from event_model import RunRouter
from suitcase import tiff_series, csv
import suitcase.jsonl
import datetime
from bluesky_darkframes import DarkSubtraction
from bluesky.callbacks.zmq import RemoteDispatcher
import databroker.assets.handlers


USERDIR = '/nsls2/xf12id1/users/' + RE.md['cycle'] + '/' + RE.md['proposal_number'] + RE.md['main_proposer']
dispatcher = RemoteDispatcher('localhost:5578')

def factory(name, start_doc):
    start_doc = dict(start_doc)
    if start_doc['plan_name'] != 'gid':
        return [], []

    serializer = tiff_series.Serializer(file_prefix=('{start[sample_name]}_'),
                                            directory=USERDIR + '/GID_data')
    # serializer('start', start_doc)

    def subfactory(name, descriptor_doc):
        descriptor_doc = dict(descriptor_doc)
        if descriptor_doc['name'] == 'primary':
            # Tell RunRouter to give the serializer all the data from this stream.
            serializer('descriptor', descriptor_doc)
            def make_doc_a_dict_and_drop_em_range(name, doc):
                doc = dict(doc)
                if name.startswith('event'):
                    doc['data'] = {
                        k: v 
                        for k, v in doc['data'].items() 
                        if not k.startswith('quadem')
                    }
                    
                serializer(name, doc)
            return [make_doc_a_dict_and_drop_em_range]
        else:
            # Tell RunRouter we don't care about this stream.
            return []
    return [], [subfactory]


handler_registry = {'AD_TIFF': databroker.assets.handlers.AreaDetectorTiffHandler}
#rr = RunRouter([factory], handler_registry=handler_registry)
#RE.subscribe(rr)
# dispatcher.start()