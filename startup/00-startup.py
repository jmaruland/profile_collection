import logging

from nslsii import configure_base
from IPython import get_ipython
from bluesky.callbacks.zmq import Publisher

configure_base(get_ipython().user_ns, "jpls")

logging.getLogger("ophyd").setLevel(logging.WARN)

publisher = Publisher("xf12id1-ws2:5577")
RE.subscribe(publisher)

# Optional: set any metadata that rarely changes.
RE.md["beamline_id"] = "JPLS"

# For debug mode
from bluesky.utils import ts_msg_hook
# RE.msg_hook = ts_msg_hook

# THIS NEEDS TO MOVE UPSTREAM
async def reset_user_position(msg):
    obj = msg.obj
    (val,) = msg.args

    old_value = obj.position
    obj.set_current_position(val)
    print(f"{obj.name} reset from {old_value:.3f} to {val:.3f}")

RE.register_command("reset_user_position", reset_user_position)

from pathlib import Path

import appdirs


try:
    from bluesky.utils import PersistentDict
except ImportError:
    import msgpack
    import msgpack_numpy
    import zict

    class PersistentDict(zict.Func):
        def __init__(self, directory):
            self._directory = directory
            self._file = zict.File(directory)
            super().__init__(self._dump, self._load, self._file)

        @property
        def directory(self):
            return self._directory

        def __repr__(self):
            return f"<{self.__class__.__name__} {dict(self)!r}>"

        @staticmethod
        def _dump(obj):
            "Encode as msgpack using numpy-aware encoder."
            # See https://github.com/msgpack/msgpack-python#string-and-binary-type
            # for more on use_bin_type.
            return msgpack.packb(
                obj,
                default=msgpack_numpy.encode,
                use_bin_type=True)

        @staticmethod
        def _load(file):
            return msgpack.unpackb(
                file,
                object_hook=msgpack_numpy.decode,
                raw=False)

runengine_metadata_dir = appdirs.user_data_dir(appname="bluesky") / Path("runengine-metadata")

# PersistentDict will create the directory if it does not exist
RE.md = PersistentDict(runengine_metadata_dir)

