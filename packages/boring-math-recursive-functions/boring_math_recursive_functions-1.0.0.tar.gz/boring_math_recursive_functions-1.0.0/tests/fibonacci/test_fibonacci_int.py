# Copyright 2023-2024 Geoffrey R. Scheller
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

from collections.abc import Callable, Iterator
from typing import cast
from boring_math.recursive_functions.fibonacci import orderable_generator

fib_gen = cast(
    Callable[[int, int], Iterator[int]],
    lambda n, m: orderable_generator(n, m, forward=True),
)

fib_rev_gen = cast(
    Callable[[int, int], Iterator[int]],
    lambda n, m: orderable_generator(n, m, forward=False),
)


class Test_fibonacci_int:
    def test_int(self) -> None:
        int_fibs: list[int] = []
        fibs = fib_gen(0, 1)
        fib = next(fibs)
        while fib < 60:
            int_fibs.append(fib)
            fib = next(fibs)
        assert int_fibs == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

        int_fibs = []
        fib0 = 1
        fib1 = 1
        fibs = fib_gen(fib0, fib1)
        fib = next(fibs)
        while fib < 90:
            int_fibs.append(fib)
            fib = next(fibs)
        assert int_fibs == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

        int_fibs = []
        fib0 = 1
        fib1 = 1
        fibs = fib_rev_gen(fib0, fib1)
        for _ in range(11):
            fib = next(fibs)
            int_fibs.append(fib)
        assert int_fibs == [1, 1, 0, 1, -1, 2, -3, 5, -8, 13, -21]

        int_fibs = []
        fibs = fib_rev_gen(1, -1)
        for _ in range(10):
            fib = next(fibs)
            int_fibs.append(fib)
        assert int_fibs == [1, -1, 2, -3, 5, -8, 13, -21, 34, -55]

        int_fibs = []
        fibs = fib_gen(5, 3)
        for _ in range(9):
            fib = next(fibs)
            int_fibs.append(fib)
        assert int_fibs == [5, 3, 8, 11, 19, 30, 49, 79, 128]

        int_fibs = []
        fibs = fib_gen(-21, 13)
        fib = next(fibs)
        while fib < 15:
            int_fibs.append(fib)
            fib = next(fibs)
        assert int_fibs == [-21, 13, -8, 5, -3, 2, -1, 1, 0, 1, 1, 2, 3, 5, 8, 13]

        int_fibs = []
        fibs = fib_gen(20, -14)
        fib = next(fibs)
        while fib > -35:
            int_fibs.append(fib)
            fib = next(fibs)
        assert int_fibs == [20, -14, 6, -8, -2, -10, -12, -22, -34]
