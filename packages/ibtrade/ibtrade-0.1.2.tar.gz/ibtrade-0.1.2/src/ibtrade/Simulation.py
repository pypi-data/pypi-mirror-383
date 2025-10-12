"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

from evtdis import EventType


class Simulation(object):

    class Events:
        StrategyInputComplete = EventType(name='StrategyInputComplete', priority=20)
        TransactionInputComplete = EventType(name='TransactionInputComplete', priority=20)
        ExchangeOutputComplete = EventType(name='ExchangeOutputComplete', priority=20)
        TransactionOutputComplete = EventType(name='TransactionOutputComplete', priority=20)
        SimulationStepComplete = EventType(name='SimulationStepComplete', priority=20)

    def __init(self):
        pass
