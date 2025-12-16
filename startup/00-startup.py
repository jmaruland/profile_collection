import logging

from nslsii import configure_base
from IPython import get_ipython
from bluesky.callbacks.zmq import Publisher
import functools
from ophyd.signal import EpicsSignal, EpicsSignalRO
# Ben added so that Pymca would work
from suitcase.utils import MultiFileManager
from event_model import RunRouter
import event_model
from pathlib import Path
from tiled.client import from_profile
import os
from databroker import Broker

EpicsSignal.set_defaults(connection_timeout=10, timeout=60, write_timeout=60)
EpicsSignalRO.set_defaults(connection_timeout=10, timeout=60)


# Configure a Tiled writing client
tiled_writing_client = from_profile("nsls2", api_key=os.environ["TILED_BLUESKY_WRITING_API_KEY_OPLS"])["opls"]["raw"]

class TiledInserter:
    name = "opls"
    def insert(self, name, doc):
        ATTEMPTS = 20
        error = None
        for _ in range(ATTEMPTS):
            try:
                tiled_writing_client.post_document(name, doc)
            except Exception as exc:
                print("Document saving failure:", repr(exc))
                error = exc
            else:
                break
            time.sleep(2)
        else:
            # Out of attempts
            raise error

tiled_inserter = TiledInserter()

configure_base(
    get_ipython().user_ns,
    broker_name=tiled_inserter,
    publish_documents_with_kafka=True,
    redis_url = "info.smi.nsls2.bnl.gov",
    redis_prefix = "opls-")

print("\nInitializing Tiled reading client...\nMake sure you check for duo push.")
tiled_reading_client = from_profile("nsls2", username=None)["opls"]["raw"]

db = Broker(tiled_reading_client)

publisher = Publisher("xf12id1-ws2:5577")
RE.subscribe(publisher)

# ben commented this out on 3/24/2022 since it gave an error.  Not sure what it is for.
# Optionalte that when an item is *mutated* it is not immediately synced:
#        >>> d['sample'] = {"color": "red"}  # immediately synced
#        >>> d['sample']['shape'] = 'bar'  # not immediately synced
#        bumline_id"] = "OPLS"

# For debug mode
from bluesky.utils import ts_msg_hook
# RE.msg_hook = ts_msg_hook

# THIS NEEDS TO MOVE UPSTREAM
async def reset_user_position(msg):
    obj = msg.obj
    (val,) = msg.args

    old_value = obj.position
    obj.set_current_position(val)
    print(f"{obj.name} reset from {old_value:.4f} to {val:.4f}")

RE.register_command("reset_user_position", reset_user_position)

from pathlib import Path

import appdirs


#this replaces RE() <
from bluesky.utils import register_transform
register_transform('RE', prefix='<')

def proposal_path():
    return f"/nsls2/data/smi/proposals/{RE.md['cycle']}/{RE.md['data_session']}/"

def assets_path():
    return proposal_path() + "assets/"