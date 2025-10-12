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
Fibonacci examples
==================

Example implementations for Fibonacci functions.

"""

from collections.abc import Iterator
from typing import Protocol, Self

__all__ = ['orderable_generator']


class Orderable(Protocol):
    def __lt__(self: Self, other: Self) -> bool: ...


class Ring(Protocol):
    def __add__(self: Self, other: Self) -> Self: ...
    def __sub__(self: Self, other: Self) -> Self: ...
    def __mult__(self: Self, other: Self) -> Self: ...
    def __mod__(self: Self, other: Self) -> Self: ...


class OrderedRing(Orderable, Ring, Protocol):
    def __mod__(self: Self, other: Self) -> Self: ...


def orderable_generator[T: OrderedRing](
    fib0: T, fib1: T, forward: bool = True
) -> Iterator[T]:
    """
    Generate a Fibonacci or reverse Fibonacci sequence.

    - ``fib0=0, fib1=1`` generates

      - the sequence ``0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89 ...``

    - ``fib0=5, fib1=3, forward = False`` generates

      - the sequence ``5, 3, 2, 1, 1, 0, 1, -1, 2, -3, 5, -8, ...``

    :param fib0: Zeroth numeric element of the sequence.
    :param fib1: Next numeric element of the sequence.
    :param reverse: Generate sequence in reverse order.
    :returns: An iterator iterating over a Fibonacci sequence.

    """
    if forward:
        while True:
            yield fib0
            fib0, fib1 = fib1, fib0 + fib1
    else:
        while True:
            yield fib0
            fib0, fib1 = fib1, fib0 - fib1
