"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
from typing import Optional
from ibapi.contract import Contract
from evtdis import Dispatcher
from .Configurator import Configurator
from .DataSource import DataSource
from .Simulation import Simulation
from .TransactionAgent import TransactionAgent

# Setup logging
_LOGGER = logging.getLogger(__name__)


class StrategyParameters(object):
    """
    Commom parameters required by any strategy.
    """

    def __init__(self) -> None:
        self.account: Optional[str] = None
        self.seriesType: Optional[str] = None
        self.contract: Optional[Contract] = None


class Strategy(Dispatcher):
    """
    The Strategy class contains common behavior required by all specific strategies.
    """

    def __init__(self, name: str, parameters: StrategyParameters, qsize: int = 256):
        Dispatcher.__init__(self, name=name, qsize=qsize)

        self.parameters = parameters

        # Subscribe to remote events
        if Configurator.instance().getMode() is Configurator.Mode.Simulation:
            self.subscribeToRemoteOutputEvent(
                eventType=Simulation.Events.TransactionOutputComplete,
                source=TransactionAgent.instance(),
                call=self.transactionOutputCompleteCB)

    def updateCompleteCB(self):
        _LOGGER.info("update complete")
        if Configurator.instance().getMode() is Configurator.Mode.Simulation:
            # If the strategy is running in simulation mode, notify the
            # transaction agent all of the initial processing is complete.
            TransactionAgent.instance().deliverInputEvent(event=Simulation.Events.StrategyInputComplete())

    def transactionOutputCompleteCB(self):
        _LOGGER.info('transaction output complete')
        if Configurator.instance().getMode() is Configurator.Mode.Simulation:
            DataSource.instance().deliverInputEvent(event=Simulation.Events.SimulationStepComplete())



