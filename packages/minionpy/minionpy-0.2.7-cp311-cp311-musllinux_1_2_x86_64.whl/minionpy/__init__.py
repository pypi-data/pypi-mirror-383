from .algorithms import *
from .test_functions import *
from .cec import *
from .parallel import *

try : from .cec_2011 import CEC2011
except : pass

# Define the package's version
__version__ = "0.2.7"

# Optionally, define the package name
__name__ = "minionpy"
