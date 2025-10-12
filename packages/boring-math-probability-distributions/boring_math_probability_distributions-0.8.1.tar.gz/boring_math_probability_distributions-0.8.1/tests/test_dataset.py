# Copyright 2025 Geoffrey R. Scheller
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

from boring_math.probability_distributions.datasets import DataSet

class Test_dataset:
    def test_data(self) -> None:
        tup0: tuple[float, ...] = ()
        data_tup0 = DataSet(*tup0)
        assert not data_tup0

        data0 = DataSet()
        assert not data0

        ds5 = DataSet(2, 4, 3, 5, 1)
        assert ds5._mean.get() == 3.0
        assert ds5._median.get() == 3.0
        assert ds5._quartiles.get() == (1.5, 3, 3.5)
        assert round(ds5._stdev.get(), 8) == 1.41421356

