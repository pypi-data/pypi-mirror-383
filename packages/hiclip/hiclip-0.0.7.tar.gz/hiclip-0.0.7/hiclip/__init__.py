import os
import sys

sys.path.append("{}/Torchelie".format(os.path.dirname(os.path.abspath(__file__))))

from hiclip._data import setup_data
from hiclip._model import HiClip
