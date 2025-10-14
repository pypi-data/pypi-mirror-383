# Copyright (c) 2025, Huawei Technologies Co., Ltd.
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
class ClusterCommunicationAnalyzerTime:
    def __init__(self, step=None, rank_id=None, hccl_op_name=None, group_name=None,
                 start_timestamp=None, elapsed_time=None, transit_time=None, wait_time=None,
                 synchronization_time=None, idle_time=None, synchronization_time_ratio=None, wait_time_ratio=None):
        self._step = step
        self._rank_id = rank_id
        self._hccl_op_name = hccl_op_name
        self._group_name = group_name
        self._start_timestamp = start_timestamp
        self._elapsed_time = elapsed_time
        self._transit_time = transit_time
        self._wait_time = wait_time
        self._synchronization_time = synchronization_time
        self._idle_time = idle_time
        self._synchronization_time_ratio = synchronization_time_ratio
        self._wait_time_ratio = wait_time_ratio

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value

    @property
    def rank_id(self):
        return self._rank_id

    @rank_id.setter
    def rank_id(self, value):
        self._rank_id = value

    @property
    def hccl_op_name(self):
        return self._hccl_op_name

    @hccl_op_name.setter
    def hccl_op_name(self, value):
        self._hccl_op_name = value

    @property
    def group_name(self):
        return self._group_name

    @group_name.setter
    def group_name(self, value):
        self._group_name = value

    @property
    def start_timestamp(self):
        return self._start_timestamp

    @start_timestamp.setter
    def start_timestamp(self, value):
        self._start_timestamp = value

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @elapsed_time.setter
    def elapsed_time(self, value):
        self._elapsed_time = value

    @property
    def transit_time(self):
        return self._transit_time

    @transit_time.setter
    def transit_time(self, value):
        self._transit_time = value

    @property
    def wait_time(self):
        return self._wait_time

    @wait_time.setter
    def wait_time(self, value):
        self._wait_time = value

    @property
    def synchronization_time(self):
        return self._synchronization_time

    @synchronization_time.setter
    def synchronization_time(self, value):
        self._synchronization_time = value

    @property
    def idle_time(self):
        return self._idle_time

    @idle_time.setter
    def idle_time(self, value):
        self._idle_time = value

    @property
    def synchronization_time_ratio(self):
        return self._synchronization_time_ratio

    @synchronization_time_ratio.setter
    def synchronization_time_ratio(self, value):
        self._synchronization_time_ratio = value

    @property
    def wait_time_ratio(self):
        return self._wait_time_ratio

    @wait_time_ratio.setter
    def wait_time_ratio(self, value):
        self._wait_time_ratio = value
