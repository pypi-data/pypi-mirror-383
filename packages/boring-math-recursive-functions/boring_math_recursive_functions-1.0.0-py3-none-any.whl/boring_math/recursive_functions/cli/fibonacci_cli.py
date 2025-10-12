# Copyright 2023-2025 Geoffrey R. Scheller
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
Programs involving Fibonacci sequences. These are installed into the
Python virtual environment.

- **fibonacci:** Prints generated Fibonacci sequences to stdout.

"""

import sys
from collections.abc import Callable, Iterator
from typing import cast
from boring_math.recursive_functions.fibonacci import orderable_generator
from pythonic_fp.iterables.drop_take import take


def fibonacci() -> None:
    """
    Calculate Fibonacci sequences both forward ans backwards.

    Usage: ``fibonacci [-r] f1 f2 n``

    - gets installed into the virtual environment


    """
    nargs = len(args := sys.argv[1:])
    if nargs < 3 or nargs > 4:
        print('Error: Wrong number of arguments given', file=sys.stderr)
        sys.exit(1)
    if nargs == 3:
        try:
            fib1 = int(args[0])
            fib2 = int(args[1])
            n = int(args[2])
            fib_gen = cast(
                Callable[[int, int], Iterator[int]],
                lambda f1, f2: orderable_generator(f1, f2, forward=True),
            )
        except ValueError:
            print('Error: Non-integer argument given', file=sys.stderr)
            sys.exit(1)
    if nargs == 4:
        match args[0]:
            case '-r':
                try:
                    fib1 = int(args[1])
                    fib2 = int(args[2])
                    n = int(args[3])
                    fib_gen = cast(
                        Callable[[int, int], Iterator[int]],
                        lambda f1, f2: orderable_generator(f1, f2, forward=False),
                    )
                except ValueError:
                    print('Error: Non-integer argument given', file=sys.stderr)
                    sys.exit(1)
            case opt:
                print(f'Error: Unknown option "{opt}" given', file=sys.stderr)
                sys.exit(1)

    for fib in take(fib_gen(fib1, fib2), abs(n)):
        print(fib)
