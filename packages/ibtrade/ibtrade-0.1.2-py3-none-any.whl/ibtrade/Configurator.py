"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
import atexit
from enum import auto
from enum import Enum
from threading import Condition
from threading import Thread
from ibapi.client import EClient
from .IBClient import IBClient
from .IBCallback import IBCallback

# Setup logging
_LOGGER = logging.getLogger(__name__)


########################################################################################################################
# Configurator
########################################################################################################################

class Configurator(object):

    class Mode(Enum):
        RealTime = auto()
        Simulation = auto()

    # Private class properties
    _mode: Mode = Mode.Simulation
    _instance = None

    # Private class methods
    @staticmethod
    def deleteInstance() -> None:
        _LOGGER.info('Delete Instance')
        if Configurator._instance is not None:
            del Configurator._instance
            Configurator._instance = None
        atexit.unregister(Configurator.deleteInstance)

    # Public class methods
    @staticmethod
    def getMode() -> Enum:
        return Configurator._mode

    @staticmethod
    def setMode(mode: Mode) -> None:
        Configurator._mode = mode

    @staticmethod
    def instance() -> object:
        if Configurator._instance is None:
            Configurator._instance = ConfiguratorFactory()
            atexit.register(Configurator.deleteInstance)
        return Configurator._instance

    def __init__(self) -> None:
        if self.__class__ is Configurator:
            raise RuntimeError('Only subclasses of Configurator can be instantiated')

    def __del__(self) -> None:
        _LOGGER.info('Configurator deleted')
        pass

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass


########################################################################################################################
# Simulation configurator
########################################################################################################################

class SimulationConfigurator(Configurator):

    def __init__(self) -> None:
        Configurator.__init__(self)

    def __del__(self):
        _LOGGER.info('SimulationConfigurator deleted')

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass


########################################################################################################################
# IB message loop thread
########################################################################################################################

class IBMessageLoop(Thread):
    """
    The IBMessageLoop is provides a thread of execution to run the IB EClient main loop.
    """

    def __init__(self, client: EClient) -> None:
        Thread.__init__(self, group=None, name='IBMessageLoop')
        self.client: EClient = client

    def run(self) -> None:
        _LOGGER.info("Entering IB message loop")
        self.client.run()
        _LOGGER.info("Exiting IB message loop")


########################################################################################################################
# IB configurator
########################################################################################################################

class IBConfigurator(Configurator):

    def __init__(self) -> None:
        Configurator.__init__(self)

        self._connected = False
        self._condition = Condition()

        # Interface for IB related classes.
        self._ibcallback: IBCallback = IBCallback()
        self._ibclient: IBClient = IBClient(callback=self._ibcallback)
        self._messageLoop: IBMessageLoop = IBMessageLoop(self._ibclient)

        # Subscribe to connected and disconnected events.
        self._ibcallback.subscribe(eventType=IBCallback.Output.Connected, call=self.connectedCB)
        self._ibcallback.subscribe(eventType=IBCallback.Output.Disconnected, call=self.disconnectedCB)

    @property
    def IBIncoming(self) -> IBCallback:
        return self._ibcallback

    @property
    def IBOutgoing(self) -> IBClient:
        return self._ibclient

    def __del__(self):
        _LOGGER.info('IBConfigurator deleted')

    # Internal callback processing
    def connectedCB(self) -> None:
        _LOGGER.info('connected to IB')
        if self._connected:
            return
        if self._ibclient.asynchronous:
            self._ibclient.startApi()
        with self._condition:
            self._connected = True
        self._messageLoop.start()

    def disconnectedCB(self) -> None:
        _LOGGER.info('disconnected from IB')
        if not self._connected:
            return
        # with self._condition:
        self._connected = False

    # Public interface
    def connect(self) -> None:
        _LOGGER.info('attempting to connect to IB')
        with self._condition:
            self._ibclient.connect(host='127.0.0.1', port=4001, clientId=10)
            self._condition.wait_for(predicate=lambda: self._connected, timeout=20.0)

    def disconnect(self) -> None:
        _LOGGER.info('attempting to disconnect from IB')
        # with self._condition:
        # self._ibclient.disconnect()
        self._ibclient.done = True
        self._messageLoop.join()
        # self._condition.wait_for(predicate=lambda: not self._connected, timeout=20.0)

########################################################################################################################
# Configurator factory
########################################################################################################################


class ConfiguratorFactoryMeta(type):

    def __call__(cls, *args, **kwargs) -> Configurator:
        if Configurator._instance is None:
            if Configurator.getMode() == Configurator.Mode.Simulation:
                return SimulationConfigurator.__call__(*args, **kwargs)
            elif Configurator.getMode() == Configurator.Mode.RealTime:
                return IBConfigurator.__call__(*args, **kwargs)
        else:
            return Configurator._instance


class ConfiguratorFactory(Configurator, metaclass=ConfiguratorFactoryMeta):
    pass
