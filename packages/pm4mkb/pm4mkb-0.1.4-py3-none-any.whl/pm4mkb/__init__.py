import os
import sys
from warnings import simplefilter

# * Point to newer 'pymorphy3' package when any dependency package tries to import 'pymorphy2'
from importlib.abc import MetaPathFinder  # noqa: E402
from importlib.util import find_spec, module_from_spec  # noqa: E402


class PymorphyRedirector(MetaPathFinder):
    def find_module(self, fullname, path=None):
        if fullname == "pymorphy2":
            return self

    def load_module(self, fullname):
        spec = find_spec("pymorphy3")
        # Get the module and load
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        # Add the module to sys scope
        sys.modules[fullname] = module

        return module


# * Insert the redirector to sys path search
sys.meta_path.insert(0, PymorphyRedirector())
# * NO tensorflow logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# * pm4mkb imports
from . import _logging_init  # noqa: F401,E402
from ._version import __version__  # noqa: E402
from .baza import DataHolder, DurationUnits, SuccessInputs, TimeErrors  # noqa: E402

# ! miners, bpmn, conformance checking and ml need visual module
# import of the visual module takes most of the time

simplefilter(action="ignore", category=FutureWarning)


__all__ = [
    "autoinsights",
    "baza",
    "bpmn",
    "imitation",
    "logs",
    "metrics",
    "miners",
    "ml",
    "nlp",
    "visual",
    "DataHolder",
    "DurationUnits",
    "SuccessInputs",
    "TimeErrors",
    "logs",
    "__version__",
]
