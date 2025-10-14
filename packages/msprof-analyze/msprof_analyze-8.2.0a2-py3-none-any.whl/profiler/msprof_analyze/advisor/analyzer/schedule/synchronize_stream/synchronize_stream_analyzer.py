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
import logging

from msprof_analyze.advisor.analyzer.base_analyzer import BaseAnalyzer
from msprof_analyze.advisor.analyzer.schedule.synchronize_stream.synchronize_stream_checker import \
    SynchronizeStreamChecker
from msprof_analyze.advisor.dataset.timeline_event_dataset import ScheduleAnalysisDataset
from msprof_analyze.advisor.display.html.render import HTMLRender
from msprof_analyze.advisor.result.result import OptimizeResult

logger = logging.getLogger()


class SynchronizeStreamAnalyzer(BaseAnalyzer):
    dataset_cls_list = [ScheduleAnalysisDataset]

    def __init__(self, collection_path, **kwargs):
        super().__init__(collection_path, **kwargs)
        self.result = OptimizeResult()
        self.html_render = HTMLRender()

        key = ScheduleAnalysisDataset.get_key()
        self.timeline_event_dataset = self.get_first_data_by_key(self.dataset_list, key)

    @BaseAnalyzer.check_data((ScheduleAnalysisDataset.get_key(),))
    def optimize(self, **kwargs):
        synchronize_stream_checker = SynchronizeStreamChecker()
        synchronize_stream_checker.check_synchronize(self.timeline_event_dataset)
        synchronize_stream_checker.make_record(self.result)
        synchronize_stream_checker.make_render(self.html_render, priority=self.get_priority(synchronize_stream_checker),
                                               rank=kwargs.get("rank"))
        return self.result

    def get_priority(self, max_mem_op_dur):
        return max_mem_op_dur.priority
