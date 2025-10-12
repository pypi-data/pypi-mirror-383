"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

from atexit import register
from atexit import unregister
from evtdis import Dispatcher


class Singleton(type):

    _instances = {}

    @staticmethod
    def deleteInstance(cls):
        if cls in cls._instances:
            instance = cls._instances[cls]
            if issubclass(cls, Dispatcher) and instance.is_alive():
                instance.triggerExit()
                instance.join()
            del instance
            del cls._instances[cls]
            if len(cls._instances) == 0:
                unregister(Singleton.deleteInstance)

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
            register(Singleton.deleteInstance, cls)
            if issubclass(cls, Dispatcher) and not instance.is_alive():
                instance.start()
        return cls._instances[cls]