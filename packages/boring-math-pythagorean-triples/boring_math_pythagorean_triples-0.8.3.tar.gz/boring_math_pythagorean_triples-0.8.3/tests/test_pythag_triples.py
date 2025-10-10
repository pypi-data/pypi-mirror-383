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

from boring_math.pythagorean_triples.pythag3 import Pythag3

class Test_pythag3:
    def test_triples(self) -> None:
        pythag3 = Pythag3()

        for triple in pythag3.triples(40):
            a, b, c = triple
            assert a*a + b*b == c*c
            assert a <= 40

        for triple in pythag3.triples(2, 60, 100):
            a, b, c = triple
            assert a*a + b*b == c*c
            assert 3 <= a <= 60
            assert 4 <= b <= 100
            assert 5 <= c <= 100

    def test_spot_check(self) -> None:
        pythag3 = Pythag3()

        triples = set(pythag3.triples(3, 40))
        assert (3, 4, 5) in triples
        assert (5, 12, 13) in triples
        assert (8, 15, 17) in triples
        assert (23, 264, 265) in triples

        triples = set(pythag3.triples(1, 200, 500))
        assert (23, 264, 265) in triples
        assert (189, 340, 389) in triples
        assert (87, 416, 425) in triples
        assert (33, 544, 545) not in triples

    def test_extend_squares(self) -> None:
        pythag3 = Pythag3()

        triples = set(pythag3.triples(1060, 1063))
        assert len(triples) == 6

        triples = set(pythag3.triples(2060, 2067, 20000))
        assert len(triples) == 3

        triples = set(pythag3.triples(20000, 20025, 60000))
        assert (20001, 55720, 59201) in triples
        assert (20003, 25596, 32485) in triples
        assert (20007, 27224, 33785) in triples
        assert (20008, 23175, 30617) in triples
        assert (20020, 30099, 36149) in triples
        assert (20025, 21352, 29273) in triples 
        assert (20008, 57855, 61217) not in triples
        assert (3, 4, 5) not in triples
        assert (6, 6, 6) not in triples

