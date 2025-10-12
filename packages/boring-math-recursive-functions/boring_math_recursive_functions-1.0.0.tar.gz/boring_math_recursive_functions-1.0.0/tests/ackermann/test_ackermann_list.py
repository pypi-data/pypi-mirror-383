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

from boring_math.recursive_functions.ackermann import ackermann_list

class Test_ackerman:
    def test_ack_list(self) -> None:
        assert ackermann_list(0, 0) == 1
        assert ackermann_list(0, 5) == 6
        assert ackermann_list(1, 0) == 2
        assert ackermann_list(1, 1) == 3
        assert ackermann_list(1, 2) == 4
        assert ackermann_list(1, 3) == 5
        assert ackermann_list(1, 4) == 6
        assert ackermann_list(1, 5) == 7
        assert ackermann_list(1, 6) == 8
        assert ackermann_list(1, 7) == 9
        assert ackermann_list(1, 8) == 10
        assert ackermann_list(1, 27) == 29      # inferring from patterns
        assert ackermann_list(2, 0) == 3
        assert ackermann_list(2, 1) == 5
        assert ackermann_list(2, 2) == 7
        assert ackermann_list(2, 3) == 9
        assert ackermann_list(2, 4) == 11
        assert ackermann_list(2, 5) == 13
        assert ackermann_list(2, 6) == 15
        assert ackermann_list(2, 13) == 29      # inferring from patterns
        assert ackermann_list(3, 0) == 5
        assert ackermann_list(3, 1) == 13
        assert ackermann_list(3, 2) == 29       # inferring from patterns
        assert ackermann_list(3, 3) == 61       # inferring from patterns
        assert ackermann_list(3, 4) == 125
        assert ackermann_list(3, 8) == 2045     # not hand computed
        assert ackermann_list(4, 0) == 13
      # assert ackermann(4, 1) == 65533    # not hand computed!
        assert ackermann_list(0, 21) == 22
        assert ackermann_list(4, 0) == ackermann_list(3, 1)
        assert ackermann_list(3, 7) == ackermann_list(2, ackermann_list(3, 6))

