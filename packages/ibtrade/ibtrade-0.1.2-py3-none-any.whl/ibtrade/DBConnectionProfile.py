"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

from collections import namedtuple

DBConnectionProfile = namedtuple(
    'DBConnectionProfile', [
        'host',
        'port',
        'dbname',
        'user',
        'password'
    ])


