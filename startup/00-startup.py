from nslsii import configure_base
from IPython import get_ipython
from bluesky.callbacks.zmq import Publisher

configure_base(get_ipython().user_ns, "jpls")

publisher = Publisher("xf12id1-ws2:5577")
RE.subscribe(publisher)

# Optional: set any metadata that rarely changes.
RE.md["beamline_id"] = "JPLS"


# THIS NEEDS TO MOVE UPSTREAM
async def reset_user_position(msg):
    obj = msg.obj
    (val,) = msg.args

    old_value = obj.position
    obj.set_current_position(val)
    print(f"{obj.name} reset from {old_value} to {val}")


RE.register_command("reset_user_position", reset_user_position)
