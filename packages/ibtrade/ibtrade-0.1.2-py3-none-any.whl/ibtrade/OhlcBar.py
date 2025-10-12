"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

from collections import namedtuple
from datetime import datetime

OhlcBase = namedtuple(
    'OhlcBase', [
        'timestamp',
        'open',
        'high',
        'low',
        'close',
        'volume'
    ]
)


class OhlcBar(OhlcBase):
    """
    A single bar of an open, high, low, close (OHLC) time series.
    """

    def __str__(self) -> str:
        tmstp = self.timestamp.strftime('%Y-%m-%d %H:%M:%S:%f')
        return '[OhlcBar: timestamp=({}), open=({}), high=({}), low=({}), close=({}), volume=({})]'.format(
            tmstp, self.open, self.high, self.low, self.close, self.volume)


