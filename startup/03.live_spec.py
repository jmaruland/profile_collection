# Initialize the filename to today's date.
import time
from event_model import RunRouter
from suitcase.specfile import Serializer


def spec_factory(name, doc):
    directory = "/nsls2/xf12id1/specfiles/"
    file_prefix = "chx_spec_" + time.strftime("%Y_%m_%d")
    spec_cb = Serializer(directory, file_prefix=file_prefix, flush=True)
    return [spec_cb], []


run_router = RunRouter([spec_factory])

RE.subscribe(run_router)