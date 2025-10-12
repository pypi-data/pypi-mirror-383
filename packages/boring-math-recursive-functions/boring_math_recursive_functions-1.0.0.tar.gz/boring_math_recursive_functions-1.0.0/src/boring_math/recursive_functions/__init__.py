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
Recursive Functions Package
===========================

Package to explore efficient ways to implement recursive functions.

Ackermann function
------------------

Ackermann's function is an example of a function that is computable
but not primitively recursive. It quickly becomes computationally
intractable for relatively small values of m.

Ackermann function is defined recursively by

    ``ackermann(0,n) = n+1`` for ``n >= 0``

    ``ackermann(m,0) = ackermann(m-1,1)`` for ``m >= 0``

    ``ackermann(m,n) = ackermann(m-1, ackermann(m,n-1))`` for ``m, n > 0``

Fibonacci sequences
-------------------

The Fibonacci sequence is usually taught in grade school as the
first recursive function that is not either an arithmetic or geometric
progression.

The Fibonacci sequence is traditionally defined as

    ``f₁ = 1``

    ``f₂ = 1``

    ``fₙ₊₂ = fₙ₊₁ + fₙ``

Actually, the Fibonacci sequence can be extended in both directions.

    ``..., 13, -8, 5, -3, 2, -1, 1, 0, 1, 1, 2, 3, 5, 6, 13, ...``

"""

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2016-2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'
