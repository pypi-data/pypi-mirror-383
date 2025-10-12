"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
from ibapi import wrapper
from ibapi.client import EClient

# Setup logging
_LOGGER = logging.getLogger(__name__)


class IBClient(EClient):

    def __init__(self, callback: wrapper.EWrapper):
        EClient.__init__(self, wrapper=callback)
        self.callback: wrapper.EWrapper = callback

    def __del__(self):
        _LOGGER.info("IBClient deleted")
