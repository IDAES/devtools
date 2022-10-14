"""
This module stores instantiated plugin objects to be loaded by pytest (both plugins have side effects)
"""

from . import plugin


collect = plugin.Collect()
