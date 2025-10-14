# Copyright (c) 2024, Huawei Technologies Co., Ltd.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0  (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from msprof_analyze.compare_tools.compare_backend.utils.common_func import calculate_diff_ratio
from msprof_analyze.compare_tools.compare_backend.utils.excel_config import ExcelConfig

from msprof_analyze.prof_common.constant import Constant


class ApiInfo:
    __slots__ = ['_data_list', 'name', 'total_dur', 'self_time', 'avg_dur', 'number']

    def __init__(self, op_name: str, data_list: list):
        self._data_list = data_list
        self.name = op_name
        self.total_dur = 0.0
        self.self_time = 0.0
        self.avg_dur = 0.0
        self.number = len(data_list)
        self._get_info()

    def _get_info(self):
        for data in self._data_list:
            self.total_dur += data.api_dur
            self.self_time += data.api_self_time
        self.total_dur = round(self.total_dur / 1000.0, 2)
        self.self_time = round(self.self_time / 1000.0, 2)
        self.avg_dur = round(self.total_dur / self.number, 2) if self.number else 0.0


class ApiCompareBean:
    __slots__ = ['_name', '_base_api', '_comparison_api']
    TABLE_NAME = Constant.API_TABLE
    HEADERS = ExcelConfig.HEADERS.get(TABLE_NAME)
    OVERHEAD = ExcelConfig.OVERHEAD.get(TABLE_NAME)

    def __init__(self, op_name: str, base_api: list, comparison_api: list):
        self._name = op_name
        self._base_api = ApiInfo(op_name, base_api)
        self._comparison_api = ApiInfo(op_name, comparison_api)

    @property
    def row(self):
        row = [
            None, self._name,
            self._base_api.total_dur, self._base_api.self_time, self._base_api.avg_dur, self._base_api.number,
            self._comparison_api.total_dur, self._comparison_api.self_time,
            self._comparison_api.avg_dur, self._comparison_api.number
        ]
        diff_fields = [
            calculate_diff_ratio(self._base_api.total_dur, self._comparison_api.total_dur)[1],
            calculate_diff_ratio(self._base_api.self_time, self._comparison_api.self_time)[1],
            calculate_diff_ratio(self._base_api.avg_dur, self._comparison_api.avg_dur)[1],
            calculate_diff_ratio(self._base_api.number, self._comparison_api.number)[1]
        ]
        row.extend(diff_fields)
        return row
