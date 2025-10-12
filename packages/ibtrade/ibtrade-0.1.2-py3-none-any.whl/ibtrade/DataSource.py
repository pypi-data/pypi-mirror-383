"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
import psycopg2
from atexit import register
from atexit import unregister
from threading import Lock
from ibapi.contract import Contract
from ibapi.contract import ContractDetails
from evtdis import Dispatcher
from evtdis import EventType

from .Configurator import Configurator
from .DBConnectionProfile import DBConnectionProfile
from .IBCallback import IBCallback
from .OhlcBar import OhlcBar
from .Simulation import Simulation

# Setup logging
_LOGGER = logging.getLogger(__name__)


########################################################################################################################
# Data source
########################################################################################################################

class DataSource(Dispatcher):
    """
    The DataSource defines an interface that must implemented by all data source subclasses.
    """

    class Input:
        SubscribeRealTimeBars = EventType(name='SubscribeRealTimeBars', id=int,
                                          contract=Contract, seriesType=str, regularTradeHours=bool)
        CancelRealTimeBars = EventType(name='CancelRealTimeBars', id=int)
        RequestContractInfo = EventType(name='RequestContractInfo', id=int, contract=Contract)
        RequestHistoricalBars = EventType(name='RequestHistoricalBars', id=int, contract=Contract,
                                          endDateTime=str, durationStr=str, barSizeSetting=str, whatToShow=str,
                                          useRTH=int, formatDate=int, keepUpToDate=bool)

    class Output:
        Data = EventType(name='Data', priority=5, bar=OhlcBar)
        ContractInfo = EventType(name='ContractInfo', id=int, contractDetails=ContractDetails)
        ContractInfoEnd = EventType(name='ContractInfoEnd', id=int)
        HistoricalBar = EventType(name='HistoricalBar', id=int, bar=OhlcBar)
        HistoricalBarEnd = EventType(name='HistoricalBarEnd', id=int, start=str, end=str)

    # Private class attributes
    _instance = None

    # Private class methods
    @staticmethod
    def deleteInstance() -> None:
        _LOGGER.info('Delete Instance')
        if DataSource._instance is not None:
            DataSource._instance.triggerExit()
            DataSource._instance.join()
            del DataSource._instance
            DataSource._instance = None
        unregister(DataSource.deleteInstance)

    # Public class methods
    @staticmethod
    def instance() -> Dispatcher:
        if DataSource._instance is None:
            DataSource._instance = DataSourceFactory()
            register(DataSource.deleteInstance)
            DataSource._instance.start()
        return DataSource._instance

    def __init__(self, name: str, qsize: int=256) -> None:
        _LOGGER.info('DataSource initializing')
        Dispatcher.__init__(self, name=name, qsize=qsize)

        if self.__class__ is DataSource:
            raise RuntimeError('Only subclasses of DataSource can be instantiated')

        # Attributes
        self._orderId: int = 0
        self._reqIdLock: Lock = Lock()
        self._reqId: int = 1

        # Internal events.
        self.setDefaultStartAndExit(startCall=self.startingCB, exitCall=self.exitingCB)

        # Command events that can be invoked.
        self._subscribeInputEvent(eventType=DataSource.Input.SubscribeRealTimeBars, call=self.inSubscribeRealTimeBarsCB)
        self._subscribeInputEvent(eventType=DataSource.Input.CancelRealTimeBars, call=self.inCancelRealTimeBarsCB)
        self._subscribeInputEvent(eventType=DataSource.Input.RequestContractInfo, call=self.inRequestContractInfoCB)
        self._subscribeInputEvent(eventType=DataSource.Input.RequestHistoricalBars, call=self.inRequestHistoricalBarsCB)

        # Output events available to subscribers.
        self._registerOutputEvent(eventType=DataSource.Output.Data)
        self._registerOutputEvent(eventType=DataSource.Output.ContractInfo)
        self._registerOutputEvent(eventType=DataSource.Output.ContractInfoEnd)
        self._registerOutputEvent(eventType=DataSource.Output.HistoricalBar)
        self._registerOutputEvent(eventType=DataSource.Output.HistoricalBarEnd)

    def nextRequestIdentifier(self) -> int:
        with self._reqIdLock:
            id = self._reqId
            self._reqId += 1
        return id

    ####################################################################################################################
    # Internal event processing
    ####################################################################################################################

    def startingCB(self):
        pass

    def exitingCB(self):
        pass

    ####################################################################################################################
    # Input command event processing.
    ####################################################################################################################

    def inSubscribeRealTimeBarsCB(self, id: int, contract: Contract, seriesType: str, regularTradeHours: bool) -> None:
        _LOGGER.info('requesting real-time bars')

    def inCancelRealTimeBarsCB(self, id: int) -> None:
        _LOGGER.info('canceling real-time bars')

    def inRequestContractInfoCB(self, id: int, contract: Contract):
        _LOGGER.info('requesting contract info')

    def inRequestHistoricalBarsCB(self, id: int, contract: Contract, endDateTime: str, durationStr: str,
                                  barSizeSetting: str, whatToShow: str, useRTH: int, formatDate: int, keepUpToDate: bool):
        _LOGGER.info('requesting historical bars')

########################################################################################################################
# DBDataSource
########################################################################################################################


class DBDataSource(DataSource):

    def __init__(self) -> None:
        DataSource.__init__(self, name='DBDataSource', qsize=2048)

        self.chunkSize: int = 1024
        self.count: int = 0

        # Database attributes
        self.conn = None
        self.cursor = None
        self.rows = None
        self.rowIter = None
        self.rowcnt: int = 0

        # Command events that can be invoked.
        self._subscribeInputEvent(eventType=Simulation.Events.SimulationStepComplete,
                                  call=self.inSimulationStepComplete)

    def __del__(self):
        _LOGGER.info('DBDataSource deleted')

    def _connect(self) -> None:
        _LOGGER.info('Connecting to postgres database')
        # Connect to Postgres database.
        self.conn = psycopg2.connect(
            host=DBConnection.host,
            port=DBConnection.port,
            dbname=DBConnection.dbname,
            user=DBConnection.user,
            password=DBConnection.password)
        self.cursor = self.conn.cursor()

    def pushData(self):
        exceptionMsg = 'Postgres fetch issue'

        try:
            # Try to push one row.
            row = next(self.rowIter)
            self._publishExternalEvent(event=DataSource.Output.Data(bar=OhlcBar(*row)))

        except StopIteration:
            # End of row list. Try to read more data
            self.rows = self.cursor.fetchmany(size=self.chunkSize)
            if not self.rows:
                # No more data so exit.
                self._publishInternalEvent(event=Dispatcher.Evt.Exiting())
            else:
                self.rowIter = iter(self.rows)
                row = next(self.rowIter)
                self._publishExternalEvent(event=DataSource.Output.Data(bar=OhlcBar(*row)))

        except psycopg2.Error:
            _LOGGER.exception(exceptionMsg, exc_info=True, stack_info=True)

        except psycopg2.Warning:
            _LOGGER.warning(exceptionMsg, exc_info=True, stack_info=True)

        except Exception:
            _LOGGER.exception(exceptionMsg, exc_info=True, stack_info=True)

        finally:
            self.count += 1
            #_LOGGER.info('Count = [%s]', self.count)

    ####################################################################################################################
    # Internal event processing
    ####################################################################################################################

    def startingCB(self) -> None:
        _LOGGER.info('Data source running')
        self._connect()

    def exitingCB(self) -> None:
        self.cursor.close()
        self.conn.close()

    ####################################################################################################################
    # Input command event processing.
    ####################################################################################################################

    def inSimulationStepComplete(self):
        # First row of data is pushed on subscription.
        _LOGGER.info("In simulation complete")
        self.pushData()

    def inSubscribeRealTimeBarsCB(self, id: int, contract: Contract, seriesType: str, regularTradeHours: bool) -> None:
        _LOGGER.info('requesting real-time bars')
        exceptionMsg = 'Postgres query issue'

        try:
            # Execute the query on the server.
            self.cursor.execute('''
                    select *
                    from hist.mmmstksmartusdtrades5secsb9516f93e439440db0f38f726f21af5b
                    limit 10000;
                ''')

            # Pull the first set of rows back to the client.
            self.rows = self.cursor.fetchmany(size=self.chunkSize)
            if not self.rows:
                _LOGGER.error('No data returned on query')
                # No data so exit.
                self._publishInternalEvent(event=Dispatcher.Evt.Exiting())

            # Set the row iterator to the first row.
            self.rowIter = iter(self.rows)
            # Push the first row to subscribers.
            self.pushData()

        except psycopg2.Error:
            _LOGGER.exception(exceptionMsg, exc_info=True, stack_info=True)

        except psycopg2.Warning:
            _LOGGER.warning(exceptionMsg, exc_info=True, stack_info=True)

        except Exception:
            _LOGGER.exception(exceptionMsg, exc_info=True, stack_info=True)


########################################################################################################################
# IBDataSource
########################################################################################################################

class IBDataSource(DataSource):
    """
    The IBDataSource class manages the connection and data to Interactive Brokers.
    """

    def __init__(self) -> None:
        _LOGGER.info('IBDataSource initializing')
        DataSource.__init__(self, name='IBDataSource', qsize=1024)

        # Configurator events processed directly.
        Configurator.instance().IBIncoming.subscribe(eventType=IBCallback.Output.Disconnected,
                                                     call=DataSource.deleteInstance)

        # Incoming events from IB processed through the message loop.
        # Real-time bar data.
        self.subscribeToRemoteOutputEvent(eventType=IBCallback.Output.RealTimeBar,
                                          source=Configurator.instance().IBIncoming, call=self.wr_realTimeBarCB)
        # Contract Details
        self.subscribeToRemoteOutputEvent(eventType=IBCallback.Output.ContractInfo,
                                          source=Configurator.instance().IBIncoming, call=self.wr_contractDetailsCB)
        # Contract Details End
        self.subscribeToRemoteOutputEvent(eventType=IBCallback.Output.ContractInfoEnd,
                                          source=Configurator.instance().IBIncoming, call=self.wr_contractDetailsEndCB)
        # Historical bar
        self.subscribeToRemoteOutputEvent(eventType=IBCallback.Output.HistoricalBar,
                                          source=Configurator.instance().IBIncoming, call=self.wr_historicalBarCB)
        self.subscribeToRemoteOutputEvent(eventType=IBCallback.Output.HistoricalBarEnd,
                                          source=Configurator.instance().IBIncoming, call=self.wr_historicalBarEndCB)

    def __del__(self):
        _LOGGER.info('IBDataSource deleted')

    ####################################################################################################################
    # Internal event processing
    ####################################################################################################################

    def startingCB(self) -> None:
        _LOGGER.info('Running event received')

    def exitingCB(self) -> None:
        _LOGGER.info('Exit event received')

    ####################################################################################################################
    # IB wrapper event processing
    ####################################################################################################################

    def wr_orderIdCB(self, orderId: int) -> None:
        _LOGGER.info('order id = %s', orderId)
        self._orderId = orderId

    def wr_realTimeBarCB(self, reqId: int, bar: OhlcBar) -> None:
        _LOGGER.debug('%s %s', reqId, bar)
        self._publishExternalEvent(event=DataSource.Output.Data(bar=bar))

    def wr_contractDetailsCB(self, reqId: int, contractDetails: ContractDetails):
        self._publishExternalEvent(event=DataSource.Output.ContractInfo(id=reqId, contractDetails=contractDetails))

    def wr_contractDetailsEndCB(self, reqId: int):
        self._publishExternalEvent(event=DataSource.Output.ContractInfoEnd(id=reqId))

    def wr_historicalBarCB(self, reqId: int, bar: OhlcBar):
        self._publishExternalEvent(event=DataSource.Output.HistoricalBar(id=reqId, bar=bar))

    def wr_historicalBarEndCB(self, reqId: int, start: str, end: str):
        self._publishExternalEvent(event=DataSource.Output.HistoricalBarEnd(id=reqId, start=start, end=end))

    ####################################################################################################################
    # Input command event processing.
    ####################################################################################################################

    def inSubscribeRealTimeBarsCB(self, id: int, contract: Contract, seriesType: str, regularTradeHours: bool) -> None:
        _LOGGER.info('subscribe real-time bars')
        Configurator.instance().IBOutgoing.reqRealTimeBars(reqId=id, contract=contract, barSize=5,
                                       whatToShow=seriesType, useRTH=regularTradeHours, realTimeBarsOptions=[])

    def inCancelRealTimeBarsCB(self, id: int) -> None:
        _LOGGER.info('canceling real-time bars')
        Configurator.instance().IBOutgoing.cancelRealTimeBars(reqId=id)

    def inRequestContractInfoCB(self, id: int, contract: Contract):
        _LOGGER.info('requesting contract into')
        Configurator.instance().IBOutgoing.reqContractDetails(reqId=id, contract=contract)

    def inRequestHistoricalBarsCB(self, id: int, contract: Contract, endDateTime: str, durationStr: str,
                                  barSizeSetting: str, whatToShow: str, useRTH: int, formatDate: int, keepUpToDate: bool):
        _LOGGER.info('requesting historical bars')
        Configurator.instance().IBOutgoing.reqHistoricalData(reqId=id, contract=contract, endDateTime=endDateTime,
                                                             durationStr=durationStr, barSizeSetting=barSizeSetting,
                                                             whatToShow=whatToShow, useRTH=useRTH, formatDate=formatDate,
                                                             keepUpToDate=keepUpToDate, chartOptions=[])

########################################################################################################################
# DataSourceFactory
########################################################################################################################


class DataSourceFactoryMeta(type):

    def __call__(cls, *args, **kwargs) -> DataSource:
        if DataSource._instance is None:
            if Configurator.getMode() == Configurator.Mode.Simulation:
                return DBDataSource.__call__(*args, **kwargs)
            elif Configurator.getMode() == Configurator.Mode.RealTime:
                return IBDataSource.__call__(*args, **kwargs)
        else:
            return DataSource._instance


class DataSourceFactory(DataSource, metaclass=DataSourceFactoryMeta):
    pass
