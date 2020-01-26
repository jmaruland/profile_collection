from nslsii import configure_base
from IPython import get_ipython
from bluesky.callbacks.zmq import Publisher

configure_base(get_ipython().user_ns, "jpls")

publisher = Publisher('xf12id1-ws2:5577')
RE.subscribe(publisher)

# Optional: set any metadata that rarely changes.
RE.md["beamline_id"] = "JPLS"
