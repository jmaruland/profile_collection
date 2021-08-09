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
    if '{start[plan_name]}' == 'gid':
        serializer = tiff_series.Serializer(file_prefix=('{start[sample_name]}_'
                                                        ),
                                            directory=USERDIR)
        serializer('start', start_doc)

    def subfactory(name, descriptor_doc):
        if descriptor_doc['name'] == 'primary':
            # Tell RunRouter to give the serializer all the data from this stream.
            serializer('descriptor', descriptor_doc)
            return [serializer]
        else:
            # Tell RunRouter we don't care about this stream.
            return []
    return [], [subfactory]


handler_registry = {'AD_TIFF': databroker.assets.handlers.AreaDetectorTiffHandler}
rr = RunRouter([factory], handler_registry=handler_registry)
RE.subscribe(rr)
# dispatcher.start()