"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
Hierarchy of order classes as needed to track orderes in the execution environment.
"""

from enum import auto
from enum import Enum
from typing import List
from typing import Optional
from typing import Union
from ibapi.contract import Contract


class Action(Enum):
    """
    Action to be taken at the exchange.
    """
    Invalid = auto()
    EnterLong = auto()
    ExitLong = auto()
    EnterShort = auto()
    ExitShort = auto()


class Intention(Enum):
    """
    The intention the strategy is attempting to achieve.
    """
    Invalid = auto()
    LongEntry = auto()
    LongStopExit = auto()
    LongTrailExit = auto()
    ShortEntry = auto()
    ShortStopExit = auto()
    ShortTrailExit = auto()
    LongClosePosition = auto()
    ShortClosePosition = auto()


class State(Enum):
    """
    The current known state of the order at the exchange. Latency may cause this
    to be out of date with the true state.
    """
    Invalid = auto()
    Inactive = auto()
    Active = auto()
    PartialFill = auto()
    Filled = auto()
    Cancelled = auto()


class OcaType(Enum):
    Invalid = auto()
    CancelAllWithBlock = auto()
    ReduceWithBlock = auto()
    ReduceNoBlock = auto()


class TriggerMethod(Enum):
    Default = auto()
    DoubleBidAsk = auto()
    Last = auto()
    DoubleLast = auto()
    BidAsk = auto()
    LastOrBidAsk = auto()
    Midpoint = auto()


def inverseAction(action: Action) -> Action:
    """
    Copnvert and action to its inverse. For example EnterLong -> ExitLong.
    :param action: The enumerated value of the action to be inverted.
    :return: The inverse of the input action.
    """
    inverse = Action.Invalid
    if action is Action.Invalid:
        raise RuntimeError('No inverse to Action.{}'.format(action.name),)
    elif action is Action.EnterLong:
        inverse = Action.ExitLong
    elif action is Action.EnterShort:
        inverse = Action.ExitShort
    elif action is Action.ExitLong:
        inverse = Action.EnterLong
    elif action is Action.ExitShort:
        inverse = Action.EnterShort
    return inverse


class OrderState(object):
    """
    The collected state of an order including quantity filed and remaining.
    """

    def __init__(self):
        self.state: State = State.Invalid
        self.filled: int = 0
        self.remaining: int = 0
        self.brokerId: int = 0

    def __str__(self) -> str:
        state = 'State: state={}, filled={}, remaining={}, brokerId={}'.format(
            self.state, self.filled, self.remaining, self.brokerId)
        return state


class BaseOrder(OrderState):
    """
    Order state common to all order types.
    """

    def __init__(self):
        OrderState.__init__(self)
        self.id: int = 0
        self.quantity: int = 0
        self.action: Action = Action.Invalid
        self.intention: Intention = Intention.Invalid
        self.account: Optional[str] = None
        self.instrument: Optional[Contract] = None
        self.triggerMethod: int = TriggerMethod.Default
        self.ocaType: OcaType = OcaType.Invalid
        self.ocaGroup: Optional[str] = None

        self.parent: Optional[OrderType] = None
        self.children: Optional[List[OrderType]] = None

    def __str__(self) -> str:
        state = OrderState.__str__(self)
        base = 'BaseOrder: id={}, quantity={}, action={}, intention={}, account={}, instrument={}, '.format(
            self.id, self.quantity, self.action, self.intention, self.account, self.instrument.symbol) + state
        if self.parent is not None:
            base = base + ', parent={}'.format(self.parent.id if self.parent is not None else 0)
        if self.children is not None:
            base += ',children=['
            first = True
            for child in self.children:
                if first:
                    base += '{}'.format(child.id)
                    first = False
                else:
                    base += ', {}'.format(child.id)
            base += ']'
        return base


class MarketOrder(BaseOrder):
    """
    Market order to execute a current bid or ask price.
    """
    def __init__(self):
        BaseOrder.__init__(self)

    def __str__(self):
        return BaseOrder.__str__(self)


class LimitOrder(BaseOrder):

    def __init__(self):
        BaseOrder.__init__(self)
        self.limitPrice: float = 0.0

    def __str__(self):
        base = BaseOrder.__str__(self)
        limit = 'LimitOrder: limitPrice={}, '.format(self.limitPrice) + base
        return limit


class StopOrder(MarketOrder):
    """
    Becomes a market entry or exit order when price reaches a specific target.
    """

    def __init__(self):
        MarketOrder.__init__(self)
        self.triggerPrice: float = 0.0

    def __str__(self):
        market = MarketOrder.__str__(self)
        stop = 'StopOrder: triggerPrice={}, '.format(self.triggerPrice) + market
        return stop


class StopLimitOrder(LimitOrder):
    """
    Becomes a entry or exit limit order when price reaches a specific target.
    """
    def __init__(self):
        LimitOrder.__init__(self)
        self.triggerPrice: float = 0.0
        self.executable: bool = False

    def __str__(self):
        limit = LimitOrder.__str__(self)
        stopLimit = 'StopLimitOrder: triggerPrice={}, '.format(self.triggerPrice) + limit
        return stopLimit


class TrailingStopOrder(BaseOrder):
    """
    Trail the current price by a specific single directional amount and become a market order if price reverses
    direction reaches current stop level.
    """

    class Type(Enum):
        Invalid = auto()
        Percent = auto()
        Offset = auto()

    def __init__(self):
        BaseOrder.__init__(self)
        self.trailType: TrailingStopOrder.Type = TrailingStopOrder.Type.Invalid
        self.initialPrice: float = 0.0
        self.offset: float = 0.0

    def __str__(self):
        base = BaseOrder.__str__(self)
        trailStop = 'TrailingStopOrder: initialPrice={}, offset={}, '.format(self.initialPrice, self.offset) + base
        return trailStop


OrderType = Union[
    OrderState,
    BaseOrder,
    MarketOrder,
    LimitOrder,
    StopOrder,
    StopLimitOrder,
    TrailingStopOrder
]
