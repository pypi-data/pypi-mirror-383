from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import os

try:
    import ixpeobssim
    has_ixpeobssim = True
except:
    has_ixpeobssim = False

if has_ixpeobssim:
    IXPEOBSSIM_PATH = os.path.dirname(ixpeobssim.__file__)
    IXPEOBSSIM_CALDB = os.path.join(IXPEOBSSIM_PATH, 'caldb')

try:
    IXPE_DATA = os.environ['IXPE_DATA']
except KeyError:
    IXPE_DATA = os.path.join(os.path.expanduser('~'), 'ixpedata')

IXPEPY_ROOT = os.path.abspath(os.path.dirname(__file__))