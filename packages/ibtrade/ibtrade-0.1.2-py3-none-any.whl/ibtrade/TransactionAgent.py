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
from copy import copy
from typing import Dict
from typing import List
from typing import Optional
from ibapi.common import OrderId
from ibapi.contract import Contract
from ibapi.order import Order
from evtdis import Dispatcher
from evtdis import EventType
from .Configurator import Configurator
from .Exchange import Exchange
from .Simulation import Simulation
from .IBCallback import IBCallback
from .IBClient import IBClient
from .IBOrderFactory import IBOrderFactory
from .orders import Action
from .orders import Intention
from .orders import State
from .orders import TriggerMethod
from .orders import MarketOrder
from .orders import LimitOrder
from .orders import StopLimitOrder
from .orders import TrailingStopOrder
from .orders import OrderType
from .orders import inverseAction


# Setup logging
_LOGGER = logging.getLogger(__name__)


OrderChain = namedtuple(
    'OrderChain', [
        'entry',
        # 'stop',
        'trail'
    ]
)


########################################################################################################################
# Transaction Agent
########################################################################################################################

class TransactionAgent(Dispatcher):

    class Input:
        PlaceBracketOrder = EventType(
            name='PlaceBracketOrder',
            action=Action,
            entry=float,
            limit=float,
            stop=float,
            trail=float,
            trigger=TriggerMethod,
            quantity=int,
            contract=Contract,
            account=str)

        CancelOrder = EventType(
            name='CancelOrder',
            orderId=int)

        ClosePosition = EventType(
            name='ClosePosition',
            account=str,
            contract=Contract)

        UpdateTrailingStopOrder = EventType(
            name='UpdateTrailingStopOrder',
            orderId=int,
            initialPrice=float,
            offset=float)

    class Output:
        PendingOrderIdentifier = EventType(
            name='PendingOrderIdentifier',
            priority=1,
            intention=Intention,
            identifier=tuple,
            contract=Contract,
            account=str)

        OrderStatus = EventType(
            name='OrderStatus',
            priority=1,
            id=int,
            intention=Intention,
            state=State,
            filled=int,
            remaining=int)

        PositionUpdate = EventType(
            name='PositionUpdate',
            priority=1,
            account=str,
            contract=Contract,
            position=float)

    # Private class attributes
    _instance = None

    # Private class methods
    @staticmethod
    def deleteInstance() -> None:
        _LOGGER.info('Delete Instance')
        if TransactionAgent._instance is not None:
            TransactionAgent._instance.triggerExit()
            TransactionAgent._instance.join()
            del TransactionAgent._instance
            TransactionAgent._instance = None
        unregister(TransactionAgent.deleteInstance)

    # Public class methods
    @staticmethod
    def instance() -> Dispatcher:
        if TransactionAgent._instance is None:
            TransactionAgent._instance = TransactionAgentFactory()
            register(TransactionAgent.deleteInstance)
            TransactionAgent._instance.start()
        return TransactionAgent._instance

    def __init__(
            self,
            name: str,
            qsize: int = 1024
            ) -> None:

        Dispatcher.__init__(self, name=name, qsize=qsize)

        # Instance data must be synchronized during updates and access.
        self._uuid = uuid.uuid1()
        self._orderId: int = 1
        self._active: Dict[int, OrderType] = dict()
        self._retired: Dict[int, OrderType] = dict()
        self._positions: Dict[str, Dict[str, int]] = dict()

        # Internal events.
        self.setDefaultStartAndExit(startCall=self.startingCB, exitCall=self.exitingCB)

        # Command events that can be invoked.
        self._subscribeInputEvent(eventType=TransactionAgent.Input.PlaceBracketOrder, call=self.inPlaceBracketOrderCB)
        self._subscribeInputEvent(eventType=TransactionAgent.Input.CancelOrder, call=self.inCancelOrderCB)
        self._subscribeInputEvent(eventType=TransactionAgent.Input.ClosePosition, call=self.inClosePositionCB)
        self._subscribeInputEvent(eventType=TransactionAgent.Input.UpdateTrailingStopOrder,
                                  call=self.inUpdateTrailingStopOrderCB)

        # Output events available to subscribers.
        self._registerOutputEvent(eventType=TransactionAgent.Output.PendingOrderIdentifier)
        self._registerOutputEvent(eventType=TransactionAgent.Output.OrderStatus)
        self._registerOutputEvent(eventType=TransactionAgent.Output.PositionUpdate)

    def nextOrderId(self) -> int:
        id: int = self._orderId
        self._orderId += 1
        return id

    ####################################################################################################################
    # Internal event processing
    ####################################################################################################################

    def startingCB(self) -> None:
        _LOGGER.info('Running event received')

    def exitingCB(self) -> None:
        _LOGGER.info('Exit event received')

    ####################################################################################################################
    # Common venue event processing
    ####################################################################################################################

    def orderStatusCB(
            self,
            orderId: OrderId ,
            status: str,
            filled: float,
            remaining: float,
            avgFillPrice: float,
            permId: int,
            parentId: int,
            lastFillPrice: float,
            clientId: int,
            whyHeld: str,
            mktCapPrice: float
            ) -> None:

        _LOGGER.info(('Order Status: id = %s  status = %s  filled = %s  remaining = %s average fill price = %s '
                      'perm id = %s parent id = %s client id = %s why held = %s mkt cap price = %s'),
                     orderId, status, filled, remaining, avgFillPrice, permId, parentId, clientId, whyHeld, mktCapPrice)

        # Get the order information.
        if orderId in self._active:
            order = self._active[orderId]

            if order.brokerId == 0:
                order.brokerId = permId

            # Always update filled and remaining as a partial entry will cause a change
            # in the reamaining fields of an associated stop exit or trailing stop order.
            order.filled = int(filled)
            order.remaining = int(remaining)

            if status == 'Cancelled' or status == 'ApiCancelled':
                order.state = State.Cancelled
                del self._active[order.id]
                self._retired[order.id] = order
            elif status == 'Filled':
                order.state = State.Filled
                del self._active[order.id]
                self._retired[order.id] = order
            else:
                if order.filled > 0:
                    order.state = State.PartialFill
                else:
                    order.state = State.Active

            _LOGGER.info('Updated order history: %s', order)

            self._publishExternalEvent(
                event=TransactionAgent.Output.OrderStatus(
                    id=order.id,
                    intention=order.intention,
                    state=order.state,
                    filled=order.filled,
                    remaining=order.remaining))

    def positionUpdateCB(
            self,
            account: str,
            contract: Contract,
            position: float,
            avgCost: float
            ) -> None:

        _LOGGER.info('Positions: %s', self._positions)

        # Synchronize updates and access to class data.
        if account not in self._positions:
                self._positions[account] = dict()
        self._positions[account][contract.symbol] = position
        _LOGGER.info('Positions: %s', self._positions)

        self._publishExternalEvent(
            event=TransactionAgent.Output.PositionUpdate(
                account=account,
                contract=contract,
                position=position))

    def positionEnd(self) -> None:
        _LOGGER.info('Positions end: %s', self._positions)

    ####################################################################################################################
    # Input command event processing.
    ####################################################################################################################

    # TODO: Generalize to multiple order types.
    def inPlaceBracketOrderCB(
            self,
            action: Action,
            entry: float,
            limit: float,
            stop: float,
            trail: float,
            trigger: TriggerMethod,
            quantity: int,
            contract: Contract,
            account: str
            ) -> LimitOrder:

        if action == Action.EnterLong:
            entryIntention = Intention.LongEntry
            trailIntention = Intention.LongTrailExit
        elif action == Action.EnterShort:
            entryIntention = Intention.ShortEntry
            trailIntention = Intention.ShortTrailExit
        else:
            raise Exception('Only entry actions are accepted for bracket orders')

        # ocaGroup: str = uuid.uuid4()

        oentry = LimitOrder()
        oentry.limitPrice = limit
        # oentry.triggerPrice = entry

        oentry.id = self.nextOrderId()
        oentry.quantity = quantity
        oentry.action = action
        oentry.intention = entryIntention
        oentry.account = account
        oentry.instrument = contract
        oentry.triggerMethod = trigger

        otrail = TrailingStopOrder()
        otrail.id = self.nextOrderId()
        otrail.parent = oentry
        otrail.action = inverseAction(action)
        otrail.intention = trailIntention
        otrail.quantity = quantity
        otrail.initialPrice = stop
        otrail.trailType = TrailingStopOrder.Type.Offset
        otrail.offset = math.fabs(entry-trail)
        otrail.account = account
        otrail.instrument = contract
        otrail.triggerMethod = trigger

        oentry.children = [otrail]  # [ostop, otrail]

        self._active[oentry.id] = oentry
        # self._active[ostop.id] = ostop
        self._active[otrail.id] = otrail

        _LOGGER.info('Entry: %s', oentry)
        # _LOGGER.info('Entry: %s', ostop)
        _LOGGER.info('Entry: %s', otrail)

        self._publishExternalEvent(
            event=TransactionAgent.Output.PendingOrderIdentifier(
                intention=oentry.intention,
                identifier=OrderChain(oentry.id,  # ostop.id,
                                      otrail.id),
                contract=contract,
                account=account))

        return oentry

    def inCancelOrderCB(self, orderId: int) -> None:
        # Handled by subclasses.
        pass

    def inClosePositionCB(
            self,
            account: str,
            contract: Contract
            ) -> Optional[MarketOrder]:

        if account in self._positions and contract.symbol in self._positions[account]:
            quantity: int = int(self._positions[account][contract.symbol])
            if quantity != 0:
                order = MarketOrder()
                order.id = self.nextOrderId()

                if quantity < 0:
                    order.action = Action.ExitShort
                    order.intention = Intention.ShortClosePosition
                else:
                    order.action = Action.ExitShort
                    order.intention = Intention.LongClosePosition

                order.quantity = abs(quantity)
                order.account = account
                order.instrument = contract

                _LOGGER.info("Order: %s", order)

                self._active[order.id] = order

                self._publishExternalEvent(
                    event=TransactionAgent.Output.PendingOrderIdentifier(
                        intention=order.intention,
                        identifier=(order.id, ),
                        contract=contract,
                        account=account))

                return order
        return None

    def inUpdateTrailingStopOrderCB(
            self,
            orderId: int,
            initialPrice: float,
            offset: float
            ) -> TrailingStopOrder:

        _LOGGER.info('In base update trailing stop order')
        if orderId in self._active:
            active: TrailingStopOrder = self._active[orderId]
            assert isinstance(active, TrailingStopOrder)

            order: TrailingStopOrder = copy(active)
            order.initialPrice = initialPrice
            order.offset = offset

            return order
        else:
            raise RuntimeError('Attempt to update non-existent trailing stop order %s', orderId)


########################################################################################################################
# Simulation Transaction Agent
########################################################################################################################

class SimulationTransactionAgent(TransactionAgent):

    def __init__(self) -> None:
        TransactionAgent.__init__(self, name='SimulationTransactionAgent', qsize=1024)

        # Command events that can be invoked.
        self._subscribeInputEvent(eventType=Simulation.Events.StrategyInputComplete, call=self.inStrategyInputCompleteCB)

        # Output events available to subscribers.
        self._registerOutputEvent(eventType=Simulation.Events.TransactionOutputComplete)

        # Subscribe to remote events
        self.subscribeToRemoteOutputEvent(
            eventType=Simulation.Events.ExchangeOutputComplete,
            source=Exchange.instance(),
            call=self.exchangeOutputCompleteCB)

    def __del__(self) -> None:
        _LOGGER.info("SimulationTransactionAgent deleted")

    ####################################################################################################################
    # Internal event processing
    ####################################################################################################################

    def startingCB(self) -> None:
        _LOGGER.info('Running event received')
        super().startingCB()

    def exitingCB(self) -> None:
        _LOGGER.info('Exit event received')
        Exchange.deleteInstance()
        super().exitingCB()

    ####################################################################################################################
    # Remote event event processing.
    ####################################################################################################################

    def exchangeOutputCompleteCB(self):
        _LOGGER.info('exchage output complete')
        self._publishExternalEvent(event=Simulation.Events.TransactionOutputComplete())

    ####################################################################################################################
    # Input command event processing.
    ####################################################################################################################

    def inStrategyInputCompleteCB(self) -> None:
        _LOGGER.info('strategy input complete')
        Exchange.instance().deliverInputEvent(event=Simulation.Events.TransactionInputComplete())

    def inPlaceBracketOrderCB(self, action: Action, entry: float, limit: float,
                              stop: float, trail: float, trigger: TriggerMethod,
                              quantity: int, contract:Contract, account: str) -> None:
        _LOGGER.info('Place bracket order')
        order = super().inPlaceBracketOrderCB(
            action=action,
            entry=entry,
            limit=limit,
            stop=stop,
            trail=trail,
            trigger=trigger,
            quantity=quantity,
            contract=contract,
            account=account)
        self.pendingOrders.add(order.id)

    def inCancelOrderCB(self, orderId: int) -> None:
        _LOGGER.info('Cancel order')
        super().inCancelOrderCB(orderId)
        self.canceledOrders.add(orderId)

    def inClosePositionCB(self, account: str, contract: Contract) -> None:
        _LOGGER.info('Close position')
        id: int = super().inClosePositionCB(account=account, contract=contract)
        self.pendingOrders.add(id)

    def inUpdateTrailingStopOrderCB(self, orderId: int, initialPrice: float, offset: float) -> None:
        _LOGGER.info('Update stop order id=[%s]', orderId)
        order = super().inUpdateTrailingStopOrderCB(orderId=orderId, initialPrice=initialPrice, offset=offset)
        self.updatedStopOrders.append(order)


########################################################################################################################
# IB Transaction Agent
########################################################################################################################

class IBTransactionAgent(TransactionAgent):

    def __init__(self):
        TransactionAgent.__init__(self, name='IBTransactionAgent', qsize=1024)

        self.factory: IBOrderFactory = IBOrderFactory()

        # Configurator events processed directly.
        Configurator.instance().IBIncoming.subscribe(
            eventType=IBCallback.Output.Disconnected,
            call=TransactionAgent.deleteInstance)

        # Incoming events from IB processed through the message loop.
        # Order identifier update
        self.subscribeToRemoteOutputEvent(
            eventType=IBCallback.Output.OrderId,
            source=Configurator.instance().IBIncoming,
            call=self.orderIdCB)

        # Order status.
        self.subscribeToRemoteOutputEvent(
            eventType=IBCallback.Output.OrderStatus,
            source=Configurator.instance().IBIncoming,
            call=self.orderStatusCB)

        # Position update.
        self.subscribeToRemoteOutputEvent(
            eventType=IBCallback.Output.PositionUpdate,
            source=Configurator.instance().IBIncoming,
            call=self.positionUpdateCB)

        # Request position updates for all accounts.
        Configurator.instance().IBOutgoing.reqPositions()

    def __del__(self):
        _LOGGER.info("IBTransactionAgent deleted")

    ####################################################################################################################
    # IB wrapper event processing
    ####################################################################################################################

    def orderIdCB(self, orderId: int) -> int:
        _LOGGER.info('order id = %s', orderId)
        self._orderId = orderId

    def orderStatusCB(
            self,
            orderId: OrderId,
            status: str,
            filled: float,
            remaining: float,
            avgFillPrice: float,
            permId: int,
            parentId: int,
            lastFillPrice: float,
            clientId: int,
            whyHeld: str,
            mktCapPrice: float
            ) -> None:

        super().orderStatusCB(
            orderId=orderId,
            status=status,
            filled=filled,
            remaining=remaining,
            avgFillPrice=avgFillPrice,
            permId=permId,
            parentId=parentId,
            lastFillPrice=lastFillPrice,
            clientId=clientId,
            whyHeld=whyHeld,
            mktCapPrice=mktCapPrice)

    def positionUpdateCB(
            self,
            account: str,
            contract: Contract,
            position: float,
            avgCost: float
            ) -> None:

        super().positionUpdateCB(
            account=account,
            contract=contract,
            position=position,
            avgCost=avgCost)

    ####################################################################################################################
    # Input command event processing.
    ####################################################################################################################

    def inPlaceBracketOrderCB(
            self,
            action: Action,
            entry: float,
            limit: float,
            stop: float,
            trail: float,
            trigger: TriggerMethod,
            quantity: int,
            contract: Contract,
            account: str
            ) -> None:

        _LOGGER.info('Place bracket order')
        order = super().inPlaceBracketOrderCB(
            action=action,
            entry=entry,
            limit=limit,
            stop=stop,
            trail=trail,
            trigger=trigger,
            quantity=quantity,
            contract=contract,
            account=account)

        ibOrders: List[Order] = self.factory.convert(order)
        ibout: IBClient = Configurator.instance().IBOutgoing
        for od in ibOrders:
            ibout.placeOrder(orderId=od.orderId, contract=contract, order=od)

    def inCancelOrderCB(
            self,
            orderId: int
            ) -> None:

        _LOGGER.info('Cancel order')
        super().inCancelOrderCB(orderId=orderId)
        Configurator.instance().IBOutgoing.cancelOrder(orderId=orderId)

    def inClosePositionCB(
            self,
            account: str,
            contract: Contract
            ) -> None:

        _LOGGER.info('Close position')
        order = super().inClosePositionCB(account=account, contract=contract)
        if order is not None:
           ibOrders: List[Order] = self.factory.convert(order)
           assert len(ibOrders) == 1
           ibout: IBClient = Configurator.instance().IBOutgoing
           ibout.placeOrder(orderId=order.id, contract=contract, order=ibOrders[0])

    def inUpdateTrailingStopOrderCB(
            self,
            orderId: int,
            initialPrice: float,
            offset: float
            ) -> None:

        _LOGGER.info('Update stop order id = %s', orderId)
        order = super().inUpdateTrailingStopOrderCB(orderId=orderId, initialPrice=initialPrice, offset=offset)
        ibOrders: List[Order] = self.factory.convert(order)
        assert len(ibOrders) == 1
        ibout: IBClient = Configurator.instance().IBOutgoing
        ibout.placeOrder(orderId=order.id, contract=order.instrument, order=ibOrders[0])


########################################################################################################################
# Transaction Agent Factory
########################################################################################################################

class TransactionAgentFactoryMeta(type):

    def __call__(cls, *args, **kwargs):
        if TransactionAgent._instance is None:
            if Configurator.getMode() == Configurator.Mode.Simulation:
                return SimulationTransactionAgent.__call__(*args, **kwargs)
            elif Configurator.getMode() == Configurator.Mode.RealTime:
                return IBTransactionAgent.__call__(*args, **kwargs)
        else:
            return TransactionAgent._instance


class TransactionAgentFactory(TransactionAgent, metaclass=TransactionAgentFactoryMeta):
    pass
