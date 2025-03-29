from .base import *
from .apps import *
from .middleware import *
from .other import *

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from ..local_settings import * # noqa
    except ImportError:
        pass