"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import math


def round2cent(price: float, cent: int) -> float:
    """
    Round the input price to a specific cent interval based on a minimum price change specifications.
    :param price: The value to be rounded to the given cent increment.
    :param cent: The valid price increment in cents.
    :return: A floating point value of the input price rounded to the specified number of cents.
    """
    if cent == 1:
        ret = math.trunc(100.0 * price) / 100.0
    else:
        ret = 0.1 * cent * round(number=(1.0 / (0.1 * cent)) * price, ndigits=1)
    return ret