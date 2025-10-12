"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
import math
import uuid
from atexit import register
from atexit import unregister
from collections import namedtuple
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from ibapi.common import OrderId
from ibapi.contract import Contract
from ibapi.order import Order
from evtdis import Dispatcher
from evtdis import EventType
from .Configurator import Configurator
from .DataSource import DataSource
from .DataSource import DBDataSource
from .OhlcBar import OhlcBar
from .Simulation import Simulation
from .IBCallback import IBCallback
from .IBClient import IBClient
from .IBOrderFactory import IBOrderFactory
from .orders import Action
from .orders import Intention
from .orders import State
from .orders import BaseOrder
from .orders import MarketOrder
from .orders import StopOrder
from .orders import StopLimitOrder
from .orders import TrailingStopOrder
from .orders import OrderType
from .orders import TriggerMethod
from .orders import inverseAction


# Setup logging
_LOGGER = logging.getLogger(__name__)


class Exchange(Dispatcher):
    """
    The Exchange class provides order execution, status, modification, and cancellation
    functionality during a simulation as would a real exchange.
    """

    class Input:
        PlaceOrder = EventType(name='PlaceOrder', order=BaseOrder)

    class Output:
        OrderStatus = EventType(
            name='OrderStatus',
            priority=1,
            id=int,
            intention=Intention,
            state=State,
            filled=int,
            remaining=int)

    # Private class attributes
    _instance = None

    # Private class methods
    @staticmethod
    def deleteInstance() -> None:
        _LOGGER.info('Delete Instance')
        if Exchange._instance is not None:
            Exchange._instance.triggerExit()
            Exchange._instance.join()
            del Exchange._instance
            Exchange._instance = None
        unregister(Exchange.deleteInstance)

    # Public class methods
    @staticmethod
    def instance() -> Dispatcher:
        assert Configurator.getMode() == Configurator.Mode.Simulation
        if Exchange._instance is None:
            Exchange._instance = Exchange()
            register(Exchange.deleteInstance)
            Exchange._instance.start()
        return Exchange._instance

    def __init__(self, qsize: int = 256):
        Dispatcher.__init__(self, name='Exchange', qsize=qsize)

        self.data: Optional[OhlcBar] = None

        self.canceledOrders: Set[int] = set()
        self.pendingOrders: Set[int] = set()
        self.updatedStopOrders: List[OrderType] = list()

        # Subscribe to remote data events.
        self.subscribeToRemoteOutputEvent(eventType=DataSource.Output.Data,
                                          source=DataSource.instance(), call=self.dataCB)

        # Command events that can be invoked.
        self._subscribeInputEvent(eventType=Simulation.Events.TransactionInputComplete,
                                  call=self.inTransactionInputCompleteCB)
        self._subscribeInputEvent(eventType=Exchange.Input.PlaceBracketOrder, call=self.inPlaceBracketOrderCB)
        self._subscribeInputEvent(eventType=Exchange.Input.CancelOrder, call=self.inCancelOrderCB)
        self._subscribeInputEvent(eventType=Exchange.Input.ClosePosition, call=self.inClosePositionCB)
        self._subscribeInputEvent(eventType=Exchange.Input.UpdateStopOrder, call=self.inUpdateStopOrderCB)

        # Output events available to subscribers.
        self._registerOutputEvent(eventType=Simulation.Events.ExchangeOutputComplete)
        self._registerOutputEvent(eventType=Exchange.Output.PendingOrderIdentifier)
        self._registerOutputEvent(eventType=Exchange.Output.OrderStatus)
        self._registerOutputEvent(eventType=Exchange.Output.PositionUpdate)

    ####################################################################################################################
    # Internal event processing
    ####################################################################################################################

    def startingCB(self):
        pass

    def exitingCB(self):
        pass

    def dataCB(self, bar: OhlcBar) -> None:
        _LOGGER.info('Data callback %s', bar)
        self.data = bar

    ####################################################################################################################
    #
    ####################################################################################################################

    def placeOrder(self, orderId:OrderId , contract:Contract, order:Order):
        pass

    def cancelOrder(self, orderId:OrderId):
        pass

    def __del__(self) -> None:
        _LOGGER.info("SimulationTransactionAgent deleted")

    def _cancelOrders(self) -> None:
        pass
        # Canceled orders
        # for id in self.canceledOrders:
        #     if id in self._active:
        #         order = self._active[id]
        #         if order.filled == 0:
        #             # Immediately cancel the order.
        #             _LOGGER.info('CANCELLED ORDER: %s', order)
        #             self.orderStatusCB(
        #                 orderId=id,
        #                 status='Cancelled',
        #                 filled=0.0,
        #                 remaining=order.quantity,
        #                 avgFillPrice=0.0,
        #                 permId=id,
        #                 parentId=order.parent.id if order.parent is not None else 0,
        #                 lastFillPrice=0.0,
        #                 clientId=1,
        #                 whyHeld='',
        #                 mktCapPrice=0.0
        #             )
        #             while id in self.pendingOrders:
        #                 self.pendingOrders.remove(id)
        #             # Cancel child orders.
        #             if order.children is not None and len(order.children) > 0:
        #                 for child in order.children:
        #                     _LOGGER.info('CANCELLED ORDER: %s', child)
        #                     self.orderStatusCB(
        #                         orderId=child.id,
        #                         status='Cancelled',
        #                         filled=0.0,
        #                         remaining=order.quantity,
        #                         avgFillPrice=0.0,
        #                         permId=child.id,
        #                         parentId=order.id,
        #                         lastFillPrice=0.0,
        #                         clientId=1,
        #                         whyHeld='',
        #                         mktCapPrice=0.0
        #                     )
        #         else:
        #             # Not currently possible
        #             pass
        #     else:
        #         pass
        #     if id in self.pendingOrders:
        #         self.pendingOrders.remove(id)
        # self.canceledOrders.clear()
        #

    def _updateStopOrders(self) -> None:
        pass
        # Updated stop orders.
        # for update in self.updatedStopOrders:
        #     order = self._active[update.id]
        #     # Update the stop price.
       #     order.triggerPrice = update.triggerPrice
        #     _LOGGER.info('UPDATED STOP ORDER: %s', order)
        # self.updatedStopOrders.clear()

    def _fillOrders(self):
        pass
        # filled: set = set()
        # pending: set = set()
        # for id in self.pendingOrders:
        #     order = self._active[id]
        #     doFill: bool = False
        #     fillPrice: float = 0.0
        #
        #     if isinstance(order, StopLimitOrder):
        #         if order.action is Action.EnterLong:
        #             if self.data.high >= order.triggerPrice:
        #                 order.executable = True
        #             if order.executable and self.data.low <= order.limitPrice:
        #                 doFill = True
        #                 fillPrice = order.triggerPrice
        #         elif order.action is Action.EnterShort:
        #             if self.data.low <= order.triggerPrice:
        #                 order.executable = True
        #             if order.executable and self.data.high >= order.limitPrice:
        #                 doFill = True
        #                 fillPrice = order.triggerPrice
        #     elif isinstance(order, StopOrder):
        #         if order.action is Action.ExitLong and self.data.low <= order.triggerPrice:
        #             doFill = True
        #             fillPrice = order.triggerPrice
        #         elif order.action is Action.ExitShort and self.data.high >= order.triggerPrice:
        #             doFill = True
        #             fillPrice = order.triggerPrice
        #     elif isinstance(order, MarketOrder):
        #         doFill = True
        #         fillPrice = self.data.close
        #     elif isinstance(order, TrailingStopOrder):
        #         if order.action is Action.ExitLong:
        #             if order.trailType is TrailingStopOrder.Type.Offset:
        #                 price = max(self.data.high - order.offset, order.initialPrice)
        #                 if price >= self.data.low:
        #                     doFill = True
        #                     fillPrice = price
        #             elif order.trailType is TrailingStopOrder.Type.Percent:
        #                 pass
        #         elif order.action is Action.ExitShort:
        #             if order.trailType is TrailingStopOrder.Type.Offset:
        #                 price = min(self.data.low + order.offset, order.initialPrice)
        #                 if price <= self.data.high:
        #                     doFill = True
        #                     fillPrice = price
        #             elif order.trailType is TrailingStopOrder.Type.Percent:
        #                 pass
        #
        #     if doFill:
        #         filled.add(id)
        #
        #         if order.children is not None and len(order.children) > 0:
        #             for child in order.children:
        #                 # Activate child orders
        #                 if child.id not in self.pendingOrders:
        #                     pending.add(child.id)
        #
        #         if order.parent is not None:
        #             if order.parent.id in self.pendingOrders:
        #                 # Cancel parent order.
        #                 self.canceledOrders.add(order.parent.id)
        #             for child in order.parent.children:
        #                 if child.id != id:
        #                     # Cancel sibling orders.
        #                     self.canceledOrders.add(child.id)
        #
        #         _LOGGER.info('FILLED ORDER at: %s %s', fillPrice, order)
        #         self.orderStatusCB(
        #             orderId=id,
        #             status='Filled',
        #             filled=order.quantity,
        #             remaining=0.0,
        #             avgFillPrice=fillPrice,
        #             permId=id,
        #             parentId=order.parent.id if order.parent is not None else 0,
        #             lastFillPrice=fillPrice,
        #             clientId=1,
        #             whyHeld='',
        #             mktCapPrice=0.0
        #         )
        #         position = 0.0
        #         if order.account in self._positions:
        #             position = self._positions[order.account][order.instrument.symbol]
        #         _LOGGER.info('POSITION: %s', position)
        #         if order.action in [Action.EnterLong, Action.ExitShort]:
        #             position += float(order.quantity)
        #         if order.action in [Action.EnterShort, Action.ExitLong]:
        #             position -= float(order.quantity)
        #         _LOGGER.info('POSITION: %s', position)
        #         self.positionUpdateCB(
        #             account=order.account,
        #             contract=order.instrument,
        #             position=float(position),
        #             avgCost=self.data.close
        #         )
        #
        # # Reomove the filled orders from the pending.
        # self.pendingOrders = (self.pendingOrders.difference(filled)).union(pending)

    def _simulate(self) -> None:
        _LOGGER.info("Exchange simulation")
        # Currently no partial positions.

        # self._cancelOrders()
        # self._updateStopOrders()
        # self._fillOrders()

    ####################################################################################################################
    # Exchange Interface
    ####################################################################################################################

    def inTransactionInputCompleteCB(self):
        # Perform market simulation.
        _LOGGER.info('transaction input complete')
        self._simulate()
        self._publishExternalEvent(event=Simulation.Events.ExchangeOutputComplete())

    def inPlaceBracketOrderCB(self, action: Action, entry: float, limit: float, stop: float,
                              trail: float, trigger: TriggerMethod, quantity: int, contract:Contract, account: str) -> None:
        _LOGGER.info('Place bracket order')
        order = super().inPlaceBracketOrderCB(action, entry, limit, stop, trail, trigger, quantity, contract, account)
        self.pendingOrders.add(order.id)

    def inCancelOrderCB(self, orderId: int) -> None:
        _LOGGER.info('Cancel order')
        super().inCancelOrderCB(orderId)
        self.canceledOrders.add(orderId)

    def inClosePositionCB(self, account: str, contract: Contract) -> None:
        _LOGGER.info('Close position')
        id: int = super().inClosePositionCB(account=account, contract=contract)
        self.pendingOrders.add(id)

    def inUpdateStopOrderCB(self, orderId: int, stopPrice: float) -> None:
        _LOGGER.info('Update stop order id=[%s]', orderId)
        order = super().inUpdateStopOrderCB(orderId=orderId, stopPrice=stopPrice)
        self.updatedStopOrders.append(order)

