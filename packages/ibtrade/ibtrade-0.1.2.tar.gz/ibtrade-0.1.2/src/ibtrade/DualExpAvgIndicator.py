"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import math
import logging

# Setup logging
_LOGGER = logging.getLogger(__name__)


class DualExpAvgIndicator(object):

    def __init__(self, periodFast: float, periodSlow: float, crossAboveCB, crossBelowCB):
        # Exponential moving average data
        self.init = False
        self.lastPrice: float = 0.0
        self.expmaFast: float = 0.0
        self.expmaSlow: float = 0.0
        self.periodFast: float = 0.0
        self.periodSlow: float = 0.0
        self.alphaFast: float = 0.0
        self.alphaSlow: float = 0.0
        self.invAlphaFast: float = 0.0
        self.invAlphaSlow: float = 0.0
        self.difference: float = 0.0

        self.crossAboveCB = crossAboveCB
        self.crossBelowCB = crossBelowCB

        self.setPeriod(periodFast, periodSlow)

        if not callable(crossAboveCB) or not callable(crossBelowCB):
            raise Exception("Callbacks must be pythod callable objects")

    def setPeriod(self, periodFast: float, periodSlow: float):
        self.periodFast = periodFast
        self.periodSlow = periodSlow
        self.alphaFast = 2.0 / (periodFast + 1)
        self.alphaSlow = 2.0 / (periodSlow + 1)
        self.invAlphaFast = 1.0 - self.alphaFast
        self.invAlphaSlow = 1.0 - self.alphaSlow

    def nextValue(self, price: float):
        self.lastPrice = price

        # Calculate the new fast and slow moving average values.
        if not self.init:
            self.expmaFast = price
            self.expmaSlow = price
            self.init = True
        else:
            expmaFast = self.alphaFast * price + self.invAlphaFast * self.expmaFast
            expmaSlow = self.alphaSlow * price + self.invAlphaSlow * self.expmaSlow

            # Calculate the signed difference of the fast and slow exponential moving averages.
            difference = int(math.copysign(1.0, expmaFast - expmaSlow))

            _LOGGER.debug("Difference = %s", difference)
            if self.difference == -1 and difference == 1:
                self.crossAboveCB()
            elif self.difference == 1 and difference == -1:
                self.crossBelowCB()

            # Update state for next iteration.
            self.expmaFast = expmaFast
            self.expmaSlow = expmaSlow
            self.difference = difference

        _LOGGER.debug("Fast EMA = %s  Slow EMA = %s", self.expmaFast, self.expmaSlow)