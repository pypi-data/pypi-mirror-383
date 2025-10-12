"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
from datetime import datetime
from ibapi import wrapper
from ibapi.common import TickerId
from ibapi.common import OrderId
from ibapi.common import BarData
from ibapi.contract import Contract
from ibapi.contract import ContractDetails
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.execution import Execution
from ibapi.commission_and_fees_report import CommissionAndFeesReport
from evtdis import EventType
from evtdis import Publisher
from .OhlcBar import OhlcBar

# Setup logging
_LOGGER = logging.getLogger(__name__)


class IBCallback(wrapper.EWrapper, Publisher):
    """
    The IBCallback class implements the IB EWrapper interface and is the point of reception for all data
    and messages flowing from Interactive Brokers.
    """

    class Output():
        Connected: type = EventType(name='Connected')
        ContractInfo: type = EventType(name='ContractInfo', reqId=int, contractDetails=ContractDetails)
        ContractInfoEnd: type = EventType(name='ContractInfoEnd', reqId=int)
        Disconnected: type = EventType(name='Disconnected')
        HistoricalBar: type = EventType(name='HistoricalBar', reqId=int, bar=OhlcBar)
        HistoricalBarEnd: type = EventType(name='HistoricalBarEnd', reqId=int, start=str, end=str)
        OrderId: type = EventType(name='OrderId', orderId=int)
        OrderStatus: type = EventType(name='OrderStatus', priority=1, orderId=int , status=str, filled=float,
                                      remaining=float, avgFillPrice=float, permId=int, parentId=int,
                                      lastFillPrice=float, clientId=int, whyHeld=str, mktCapPrice=float)
        PositionUpdate: type = EventType(name='PositionUpdate', priority=1, account=str, contract=Contract,
                                         position=float, avgCost=float)
        RealTimeBar: type = EventType(name='RealTimeBar', reqId=int, bar= OhlcBar)

    def __init__(self) -> None:
        Publisher.__init__(self, name='IBCallback')
        _LOGGER.info("IBCallback initializing")

        # Events published to clients.
        self.registerEvent(eventType=IBCallback.Output.Connected)
        self.registerEvent(eventType=IBCallback.Output.ContractInfo)
        self.registerEvent(eventType=IBCallback.Output.ContractInfoEnd)
        self.registerEvent(eventType=IBCallback.Output.Disconnected)
        self.registerEvent(eventType=IBCallback.Output.HistoricalBar)
        self.registerEvent(eventType=IBCallback.Output.HistoricalBarEnd)
        self.registerEvent(eventType=IBCallback.Output.OrderId)
        self.registerEvent(eventType=IBCallback.Output.OrderStatus)
        self.registerEvent(eventType=IBCallback.Output.PositionUpdate)
        self.registerEvent(eventType=IBCallback.Output.RealTimeBar)

    def __del__(self):
        _LOGGER.info("IBCallback deleted")

    ####################################################################################################################
    # EClient interface implementation.
    ####################################################################################################################

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        """
        Prints warings and error messages from the IB client and server.
        :param reqId: The id of the request which generated the error.
        :param errorCode: The IB specific error code.
        :param errorString: A string which contains the message
        associated with the error code.
        """
        if 100 <= errorCode < 500 or errorCode > 10000:
            _LOGGER.error('IB TWS error: TickerId = %s errorCode = %s - %s', reqId, errorCode, errorString)
        elif 500 <= errorCode < 600 or errorCode > 10000:
            _LOGGER.error('IB TWS error: TickerId = %s errorCode = %s - %s', reqId, errorCode, errorString)
        elif 1000 <= errorCode < 2000:
            _LOGGER.error('IB connectivity error: TickerId = %s errorCode = %s - %s', reqId, errorCode, errorString)
        elif 2000 <= errorCode < 3000:
            _LOGGER.warning('IB Warning: TickerId = %s errorCode = %s - %s', reqId, errorCode, errorString)
        else:
            _LOGGER.error('IB Error: TickerId = %s errorCode = %s - %s', reqId, errorCode, errorString)

    def connectAck(self):
        """
        Called when the connection to IB completes.
        """
        _LOGGER.info("Connection to IB established")
        self.publish(event=IBCallback.Output.Connected())

    def commissionAndFeesReport(self, commissionAndFeesReport: CommissionAndFeesReport):
        _LOGGER.debug('Commision and Fess Report: %s', commissionAndFeesReport)

    def connectionClosed(self):
        _LOGGER.info("Connection to IB closed")
        self.publish(event=IBCallback.Output.Disconnected())

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        self.publish(event=IBCallback.Output.ContractInfo(reqId=reqId, contractDetails=contractDetails))

    def contractDetailsEnd(self, reqId:int):
        self.publish(event=IBCallback.Output.ContractInfoEnd(reqId=reqId))

    def execDetails(self, reqId: int, contract: Contract, execution: Execution):
        pass

    def execDetailsEnd(self, reqId:int):
        pass

    def historicalData(self, reqId: int, bar: BarData):
        tmstp = datetime.strptime(bar.date + "+0000", '%Y%m%d %H:%M:%S%z')
        ohlc: OhlcBar = OhlcBar(timestamp=tmstp, open=bar.open, high=bar.high,
                                low=bar.low, close=bar.close, volume=bar.volume)
        self.publish(event=IBCallback.Output.HistoricalBar(reqId=reqId, bar=ohlc))

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        self.publish(event=IBCallback.Output.HistoricalBarEnd(reqId=reqId, start=start, end=end))

    def nextValidId(self, orderId: int):
        _LOGGER.info("Received next order id: %s", orderId)
        self.publish(event=IBCallback.Output.OrderId(orderId=orderId))

    def openOrder(self, orderId: OrderId, contract: Contract, order:Order, orderState: OrderState):
        #self.logAnswer(current_fn_name(), vars())
        pass

    def openOrderEnd(self):
        #self.logAnswer(current_fn_name(), vars())
        pass

    def orderStatus(self, orderId:OrderId , status:str, filled:float, remaining:float, avgFillPrice:float,
                    permId:int, parentId:int, lastFillPrice:float, clientId:int, whyHeld:str, mktCapPrice: float):
        self.publish(event=IBCallback.Output.OrderStatus(orderId=orderId, status=status, filled=filled,
                                                         remaining=remaining, avgFillPrice=avgFillPrice, permId=permId,
                                                         parentId=parentId, lastFillPrice=lastFillPrice,
                                                         clientId=clientId, whyHeld=whyHeld, mktCapPrice=mktCapPrice))

    def position(self, account: str, contract: Contract, position: float, avgCost: float) -> None:
        self.publish(event=IBCallback.Output.PositionUpdate(account=account, contract=contract,
                                                            position=position, avgCost=avgCost))

    def positionEnd(self):
        pass

    def realtimeBar(self, reqId: TickerId, time: int, open: float, high: float,
                    low: float, close: float, volume: int, wap: float, count: int):
        bar = OhlcBar(timestamp=datetime.fromtimestamp(time), open=open, high=high, low=low, close=close, volume=volume)
        self.publish(event=IBCallback.Output.RealTimeBar(reqId=reqId, bar=bar))
