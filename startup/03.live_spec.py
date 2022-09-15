# Initialize the filename to today's date.
import time
from event_model import RunRouter
from suitcase.specfile import Serializer


def spec_factory(name, doc):
    directory = "/nsls2/xf12id1g/specfiles/"
    file_prefix = "opls_spec_" + time.strftime("%Y_%m_%d")
    # Add plan names to this list to live export additional types of plans
    plan_alowed_list = {'scan', 'rel_scan', 'gid', 'count'}
    if doc.get('plan_name', '') in plan_alowed_list:
        return [Serializer(directory, file_prefix=file_prefix, flush=False)], []
    else:
        return [], []


run_router = RunRouter([spec_factory])
RE.subscribe(run_router)


#run_router = RunRouter([spec_factory])
#RE.subscribe(run_router)
# NotImplementedError: The suitcase.specfile.Serializer is not designed to handle more than one descriptor.  If you need this functionality, please request it at https://github.com/NSLS-II/suitcase/issues. Until that time, this DocumentToSpec callback will raise a NotImplementedError if you try to use it with two event streams.

#this is run to install pymca
#conda create -n pymca_testing python
#conda activate pymca_testing
#conda install -c conda-forge pymca pyqt
# conda install -c conda-forge matplotlib
#pymca