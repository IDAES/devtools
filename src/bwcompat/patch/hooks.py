from functools import singledispatch
import logging
from typing import (
    Any,
)

from . import base


_logger = logging.getLogger(__name__)


@singledispatch
def on_installation(obj: Any, **kwargs):
    _logger.info("%s has been installed", obj)


@singledispatch
def on_activation(obj: Any, **kwargs):
    _logger.info("%s has been activated", obj)

