# Copyright 2016-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Ackermann examples
==================

Example implementations for Ackermann's function.

"""
__all__ = ['ackermann_list']


def ackermann_list(m: int, n: int) -> int:
    """Ackermann's Function.

    .. note::

        This implementation models the recursion with a Python list
        instead of Python's "call stack". It then evaluates the
        innermost ackermann function first. To naively use call stack
        recursion would result in the loss of stack safety.

    :param m: First argument to Ackermann's function.
    :param n: Second argument to Ackermann's function.
    :returns: A very hard to calculate useless value.

    """
    acker = [m, n]

    while len(acker) > 1:
        mm, nn = acker[-2:]
        if mm < 1:
            acker[-1] = acker.pop() + 1
        elif nn < 1:
            acker[-2] = acker[-2] - 1
            acker[-1] = 1
        else:
            acker[-2] = mm - 1
            acker[-1] = mm
            acker.append(nn - 1)
    return acker[0]
