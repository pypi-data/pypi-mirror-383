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

import math
from boring_math.combinatorics import comb, perm

class Test_comb:
    def test_edge_cases(self) -> None:
        assert comb(0, 0) == 1
        assert comb(0, 1) == 0
        assert comb(4, 0) == 1
        assert comb(0, 5) == 0
        assert comb(4, 5) == 0

        try:
            comb(5, 3)
        except ValueError:
            assert False
        else:
            assert True

        try:
            comb(5, -3)
        except ValueError:
            assert True
        else:
            assert False

        try:
            comb(-5, 3)
        except ValueError:
            assert True
        else:
            assert False

        try:
            comb(-5, -3)
        except ValueError:
            assert True
        else:
            assert False

        try:
            comb(-5, 0)
        except ValueError:
            assert True
        else:
            assert False

        try:
            comb(0, -3)
        except ValueError:
            assert True
        else:
            assert False

    def test_small(self) -> None:
        assert comb(5, 0) == 1
        assert comb(5, 1) == 5
        assert comb(5, 2) == 10
        assert comb(5, 3) == 10
        assert comb(5, 4) == 5
        assert comb(5, 5) == 1
        assert comb(20, 4) == 20*19*18*17/(4*3*2*1)
        assert comb(37, 7) == comb(37, 37 - 7)
        assert comb(31, 7) == comb(30, 6) + comb(30, 7)

    def test_with_math_version(self) -> None:
        assert comb(11, 8) == math.comb(11, 8)
        assert comb(211, 80) == math.comb(211, 80)
        assert comb(514, 213) == math.comb(514, 213)
        assert comb(300, 299) == math.comb(300, 299) == 300
        assert comb(2000, 60) == math.comb(2000, 60)
        assert comb(20001, 601) == math.comb(20001, 601)
        assert comb(200012, 6012) == math.comb(200012, 6012)
        assert comb(2000, 4) == math.comb(2000, 4)
        assert comb(2001, 30) == math.comb(2001, 30)
        assert comb(2002, 200) == math.comb(2002, 200)
        assert comb(2003, 1000) == math.comb(2003, 1000)
        assert comb(130061, 45411) == math.comb(130061, 45411)

    def test_paramenters(self) -> None:
        assert comb(3000, 45) == comb(3000, 45, 1, 1)
        assert comb(1300, 450) == comb(1300, 450, 2, 2)
        assert comb(13000, 454) == comb(13000, 454, 100, 4)
        assert comb(20000, 15) == comb(20000, 15, 400, 5) == math.comb(20000, 15)
        assert comb(2000, 500) == comb(2000, 1500, 150, 8) == math.comb(2000, 1500)

class Test_perm:
    def test_edge_cases(self) -> None:
        assert perm(0, 0) == 1
        assert perm(0, 1) == 0
        assert perm(4, 0) == 1
        assert perm(0, 5) == 0
        assert perm(4, 5) == 0

        try:
            perm(5, 3)
        except ValueError:
            assert False
        else:
            assert True

        try:
            perm(5, -3)
        except ValueError:
            assert True
        else:
            assert False

        try:
            perm(-5, 3)
        except ValueError:
            assert True
        else:
            assert False

        try:
            perm(-5, -3)
        except ValueError:
            assert True
        else:
            assert False

        try:
            perm(-5, 0)
        except ValueError:
            assert True
        else:
            assert False

        try:
            perm(0, -3)
        except ValueError:
            assert True
        else:
            assert False

    def test_small(self) -> None:
        assert perm(5, 0) == 1
        assert perm(5, 1) == 5
        assert perm(5, 2) == 20
        assert perm(5, 3) == 60
        assert perm(5, 4) == 120
        assert perm(5, 5) == 120
        assert perm(20, 4) == 20*19*18*17
        assert perm(37, 7) == 37*36*35*34*33*32*31

    def test_with_math_version(self) -> None:
        assert perm(11, 8) == math.perm(11, 8)
        assert perm(211, 80) == math.perm(211, 80)
        assert perm(514, 213) == math.perm(514, 213)
        assert perm(300, 299) == math.perm(300, 299)
        assert perm(2000, 60) == math.perm(2000, 60)
        assert perm(20001, 601) == math.perm(20001, 601)
        assert perm(200012, 6012) == math.perm(200012, 6012)
        assert perm(2000, 4) == math.perm(2000, 4)
        assert perm(2001, 30) == math.perm(2001, 30)
        assert perm(2002, 200) == math.perm(2002, 200)
        assert perm(2003, 1000) == math.perm(2003, 1000)
        assert perm(130061, 45411) == math.perm(130061, 45411)

