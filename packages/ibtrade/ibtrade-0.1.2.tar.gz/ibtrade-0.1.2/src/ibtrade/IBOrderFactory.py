"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

from typing import List
from ibapi.order import Order
from .orders import Action
from .orders import OcaType
from .orders import OrderType
from .orders import TriggerMethod
from .orders import MarketOrder
from .orders import LimitOrder
from .orders import StopOrder
from .orders import StopLimitOrder
from .orders import TrailingStopOrder


class IBOrderFactory(object):
    """
    The IBOrderFactory is responsible for converting MathTix generic order type
    into Interactive Brokers API specific orders.
    """

    def __init__(self):

        self._actionToIBAction = {
            Action.Invalid: 'INVALID',
            Action.EnterLong: 'BUY',
            Action.EnterShort: 'SELL',
            Action.ExitLong: 'SELL',
            Action.ExitShort: 'BUY'}

        self._triggerToIBTrigger = {
            TriggerMethod.Default: 0,
            TriggerMethod.DoubleBidAsk: 1,
            TriggerMethod.Last: 2,
            TriggerMethod.DoubleLast: 3,
            TriggerMethod.BidAsk: 4,
            TriggerMethod.LastOrBidAsk: 7,
            TriggerMethod.Midpoint: 8}

        self._ocaTypeToIBOca = {
            OcaType.Invalid: 0,
            OcaType.CancelAllWithBlock: 1,
            OcaType.ReduceWithBlock: 2,
            OcaType.ReduceNoBlock: 3}

        self._convert = {
            MarketOrder: self.marketOrderToIBOrder,
            LimitOrder: self.limitOrderToIBOrder,
            StopOrder: self.stopOrderToIBOrder,
            StopLimitOrder: self.stopLimitOrderToIBOrder,
            TrailingStopOrder: self.trailingStopOrderToIBOrder}

        self._outsideRth = True

    def actionToIBAction(self, action: Action) -> str:
        if action is Action.Invalid:
            raise RuntimeError('Invalid action')
        return self._actionToIBAction[action]

    def ocaTypeToIBOca(self, ocaType : OcaType) -> int:
        return self._ocaTypeToIBOca[ocaType]

    def triggerMethodToIBTrigger(self, triggerMethod: TriggerMethod):
        return self._triggerToIBTrigger[triggerMethod]

    def baseOrderToIBOrder(self, order: OrderType) -> Order:
        ibOrder: Order = Order()
        ibOrder.orderId = order.id
        ibOrder.totalQuantity = order.quantity
        ibOrder.parentId = 0 if order.parent is None else order.parent.id
        ibOrder.action = self.actionToIBAction(order.action)
        ibOrder.tif = 'DAY'
        ibOrder.outsideRth = self._outsideRth
        ibOrder.orderRef = '{}'.format(order.id)
        ibOrder.account = order.account
        ibOrder.transmit = False

        ibOrder.triggerMethod = self.triggerMethodToIBTrigger(order.triggerMethod)
        ibOrder.ocaType = self.ocaTypeToIBOca(order.ocaType)
        if order.ocaGroup is not None:
            ibOrder.ocaGroup = order.ocaGroup

        return ibOrder

    def marketOrderToIBOrder(self, order: MarketOrder) -> Order:
        ibOrder: Order = self.baseOrderToIBOrder(order)
        ibOrder.orderType = 'MKT'
        return ibOrder

    def limitOrderToIBOrder(self, order: LimitOrder) -> Order:
        ibOrder: Order = self.baseOrderToIBOrder(order)
        ibOrder.orderType = 'LMT'
        ibOrder.lmtPrice = order.limitPrice
        return ibOrder

    def stopOrderToIBOrder(self, order: StopOrder) -> Order:
        ibOrder: Order = self.baseOrderToIBOrder(order)
        ibOrder.orderType = 'STP'
        ibOrder.auxPrice = order.triggerPrice
        return ibOrder

    def stopLimitOrderToIBOrder(self, order: StopLimitOrder) -> Order:
        ibOrder: Order = self.baseOrderToIBOrder(order)
        ibOrder.orderType = 'STP LMT'
        ibOrder.lmtPrice = order.limitPrice
        ibOrder.auxPrice = order.triggerPrice
        return ibOrder

    def trailingStopOrderToIBOrder(self, order: TrailingStopOrder) -> Order:
        ibOrder: Order = self.baseOrderToIBOrder(order)
        ibOrder.orderType = 'TRAIL'
        if order.trailType is TrailingStopOrder.Type.Offset:
            ibOrder.auxPrice = order.offset
            ibOrder.trailStopPrice = order.initialPrice
        elif order.trailType is TrailingStopOrder.Type.Percent:
            ibOrder.lmtPriceOffset = order.offset
            ibOrder.trailStopPrice = order.initialPrice
        else:
            raise RuntimeError('Invalue trailing stop order type')
        return ibOrder

    def convert(self, order: OrderType) -> List[Order]:
        orderList = list()

        # Add the parent order
        orderList.append(self._convert[order.__class__](order))
        if order.children is not None:
            # Add the children.
            for child in order.children:
                orderList.append(self._convert[child.__class__](child))
        # Ensure the last order in the chain transmits all.
        orderList[-1].transmit = True
        return orderList
