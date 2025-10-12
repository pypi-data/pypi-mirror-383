"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""
import logging.config
from os import path
from unittest import TestCase

#log_file = path.join(path.dirname(path.abspath(__file__)), 'testlog.conf')
#logging.config.fileConfig(fname=log_file, disable_existing_loggers=False)
#_LOGGER = logging.getLogger(__name__)


class TestRealtimeData(TestCase):
    def test_realtime_data(self):
        #_LOGGER.debug('Testing realtime data')
        print('Testing realtime data')

