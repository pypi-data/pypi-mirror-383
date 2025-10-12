"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
from typing import Optional
from datetime import datetime
from .OhlcBar import OhlcBar

# Setup logging
_LOGGER = logging.getLogger(__name__)


class BarConverter(object):

    def __init__(self):
        self._initialized: bool = False
        self._bar: Optional[OhlcBar] = None
        self._timestamp: datetime = datetime.today()
        self._open: float = 0.0
        self._high: float = 0.0
        self._low: float = 0.0
        self._close: float = 0.0
        self._volume = 0

    def newBar(self, bar: OhlcBar) -> Optional[OhlcBar]:
        if int(bar.timestamp.second) == 0:
            # Initialize the next one minute bar.
            # Capture the timestamp and open price.
            self._timestamp = bar.timestamp
            self._open = bar.open
            self._high = bar.high
            self._low = bar.low
            self._close = 0.0
            self._volume = bar.volume
            self._initialized = True

        if self._initialized:
            # Aggregate the one minute bar.
            self._high = max(self._high, bar.high)
            self._low = min(self._low, bar.low)
            self._close = bar.close
            self._volume += bar.volume
            self._bar = OhlcBar(timestamp=self._timestamp, open=self._open, high=self._high,
                                low=self._low, close=self._close, volume=self._volume)

        _LOGGER.info('Current bar data %s', self._bar)

        if self._initialized and int(bar.timestamp.second) == 55:
            return self._bar

        return None
