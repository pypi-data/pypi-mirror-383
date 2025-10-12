"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import math
import logging

# Setup logging
_LOGGER = logging.getLogger(__name__)


class MACDIndicator(object):

    def __init__(self, periodFast: float, periodSlow: float, periodSignal: float, crossAboveCB, crossBelowCB):
        # Exponential moving average data
        self.init = False
        self.lastPrice: float = 0.0

        self.expmaFast: float = 0.0
        self.expmaSlow: float = 0.0
        self.expmaSignal: float = 0.0
        self.macd: float = 0.0

        self.periodFast: float = 0.0
        self.periodSlow: float = 0.0
        self.periodSignal: float = 0.0

        self.alphaFast: float = 0.0
        self.alphaSlow: float = 0.0
        self.alphaSignal: float = 0.0

        self.invAlphaFast: float = 0.0
        self.invAlphaSlow: float = 0.0
        self.invAlphaSignal: float = 0.0

        self.difference: float = 0.0
        self.trigger: int = 0

        self.crossAboveCB = crossAboveCB
        self.crossBelowCB = crossBelowCB

        self.setPeriod(periodFast, periodSlow, periodSignal)

        if not callable(crossAboveCB) or not callable(crossBelowCB):
            raise Exception("Callbacks must be pythod callable objects")

    def setPeriod(self, periodFast: float, periodSlow: float, periodSignal: float):
        self.periodFast = periodFast
        self.periodSlow = periodSlow
        self.periodSignal = periodSignal
        self.alphaFast = 2.0 / (periodFast + 1)
        self.alphaSlow = 2.0 / (periodSlow + 1)
        self.alphaSignal = 2.0 / (periodSignal + 1)
        self.invAlphaFast = 1.0 - self.alphaFast
        self.invAlphaSlow = 1.0 - self.alphaSlow
        self.invAlphaSignal = 1.0 - self.alphaSignal

    def nextValue(self, price: float):
        self.lastPrice = price

        # Calculate the new fast and slow moving average values.
        if not self.init:
            self.expmaFast = price
            self.expmaSlow = price
            self.macd = self.expmaFast - self.expmaSlow
            self.expmaSignal = self.macd
            self.init = True
        else:
            expmaFast = self.alphaFast * price + self.invAlphaFast * self.expmaFast
            expmaSlow = self.alphaSlow * price + self.invAlphaSlow * self.expmaSlow
            macd = expmaFast - expmaSlow
            expmaSignal = self.alphaSignal * macd + self.invAlphaSignal * self.expmaSignal

            # Calculate the signed difference of the MACD and MACD signal.
            difference = macd - expmaSignal
            trigger = int(math.copysign(1.0, difference))

            _LOGGER.debug("Trigger = %s", trigger)
            if self.trigger == -1 and trigger == 1:
                self.crossAboveCB()
            elif self.trigger == 1 and trigger == -1:
                self.crossBelowCB()

            # Update state for next iteration.
            self.expmaFast = expmaFast
            self.expmaSlow = expmaSlow
            self.expmaSignal = expmaSignal
            self.macd = macd
            self.difference = difference
            self.trigger = trigger

        _LOGGER.info("Fast EMA = %s  Slow EMA = %s  MACD = %s  MACD Signal = %s  MACD Difference = %s  Trigger = %s",
                      self.expmaFast, self.expmaSlow, self.macd, self.expmaSignal, self.difference, self.trigger)