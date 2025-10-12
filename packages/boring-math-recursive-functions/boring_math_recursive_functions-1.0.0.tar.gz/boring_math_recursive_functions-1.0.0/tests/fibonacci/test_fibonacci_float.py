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

from collections.abc import Iterator, Callable
from math import sqrt
from typing import cast
from boring_math.recursive_functions.fibonacci import orderable_generator

fib_gen = cast(
    Callable[[float, float], Iterator[float]],
    lambda n, m: orderable_generator(n, m, forward=True),
)

fib_rev_gen = cast(
    Callable[[float, float], Iterator[float]],
    lambda n, m: orderable_generator(n, m, forward=False),
)


class TestFibonacciFloat:
    def test_int(self) -> None:
        float_fibs: list[float] = []
        fibs = fib_gen(0.0, 1.0)
        fib = next(fibs)
        while fib < 60.0:
            float_fibs.append(fib)
            fib = next(fibs)
        assert float_fibs == [0.0, 1.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0, 34.0, 55.0]

        float_fibs = []
        fibs = fib_gen(0.25, 0.5)
        fib = next(fibs)
        while fib < 25.0:
            float_fibs.append(fib)
            fib = next(fibs)
        exact_float_fibs = [0.25, 0.5, 0.75, 1.25, 2.0, 3.25, 5.25, 8.5, 13.75, 22.25]
        for nn in range(10):
            assert abs(float_fibs[nn] - exact_float_fibs[nn]) < 0.000001

        float_fibs = []
        fibs = fib_rev_gen(8.5, 5.25)
        fib = next(fibs)
        while fib > 0.0000025:
            float_fibs.append(fib)
            fib = next(fibs)
        exact_float_fibs = [8.5, 5.25, 3.25, 2.0, 1.25, 0.75, 0.5, 0.25, 0.25]
        assert len(float_fibs) == 9
        for nn in range(9):
            assert abs(float_fibs[nn] - exact_float_fibs[nn]) < 0.000001

class TestFibonacciRatio:
    def test_golden_ratio_1(self) -> None:
        phi = (1 + sqrt(5))/2

        fibs = fib_gen(1.0, 1.0)

        loops, ratio, fib_numerator = 0, -1.0, next(fibs)
        while loops < 100:
            loops += 1
            fib_denominator, fib_numerator = fib_numerator, next(fibs)
            ratio = fib_numerator / fib_denominator
            if abs(ratio - phi) < 0.0000025:
                break

        err = abs(ratio - phi)
        assert err < 0.0000025

        assert loops < 100
        assert loops < 50
        assert loops < 25
        assert loops < 20

    def test_golden_ratio_2(self) -> None:
        phi = (1 + sqrt(5))/2

        fibs = fib_gen(-182.413, 142.1215)

        loops, ratio, fib_numerator = 0, -1.0, next(fibs)
        while loops < 100:
            loops += 1
            fib_denominator, fib_numerator = fib_numerator, next(fibs)
            ratio = fib_numerator / fib_denominator
            if abs(ratio - phi) < 0.0000025:
                break

        err = abs(ratio - phi)
        assert err < 0.0000025

        assert loops < 100
        assert loops < 50
        assert loops < 25
        assert loops < 20

    def test_golden_ratio_3(self) -> None:
        phi = (1 + sqrt(5))/2
        neg_inv_phi = -1.0/phi

        fibs = fib_rev_gen(1.2015, 0.8203)

        loops, ratio, fib_denominator = 0, -1.0, next(fibs)
        while loops < 100:
            loops += 1
            fib_numerator, fib_denominator = fib_denominator, next(fibs)
            ratio = fib_numerator / fib_denominator
            if abs(ratio - neg_inv_phi) < 0.0000025:
                break

        err = abs(ratio - neg_inv_phi)
        assert err < 0.0000025

        assert loops < 100
        assert loops < 50
        assert loops < 25
        assert loops < 20
