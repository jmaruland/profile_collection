from pathlib import Path

from event_model import RunRouter
from suitcase import tiff_series, csv
import suitcase.jsonl
import datetime
from bluesky_darkframes import DarkSubtraction
from bluesky.callbacks.zmq import RemoteDispatcher
import databroker.assets.handlers

USERDIR = '/nsls2/xf12id1/user/2021_2/308360_vaknin/GID_data'

dispatcher = RemoteDispatcher('localhost:5578')

def factory(name, start_doc):

    SWserializer = tiff_series.Serializer(file_prefix=('{start[cycle]}/'
                                                       '{start[proposal_id]}/auto/'
                                                       '{start[project_name]}/'
                                                       '{start[scan_id]}/'
                                                       '{start[scan_id]}-'
                                                       '{start[sample_name]}-'
                                                       ),
                                          directory=USERDIR)

    name, doc = SWserializer(name, start_doc)

    def subfactory(dname, descriptor_doc):
        dname, ddoc = dname, descriptor_doc
        if ddoc['name'] in ['primary', 'dark']:
            
            serializer('start', start_doc)
            serializer('descriptor', descriptor_doc)
            return [serializer]
        else:
            return []

    return [], [subfactory]


handler_registry = {'AD_TIFF': databroker.assets.handlers.AreaDetectorTiffHandler}
rr = RunRouter([factory], handler_registry=handler_registry)
RE.subscribe(rr)
# dispatcher.start()