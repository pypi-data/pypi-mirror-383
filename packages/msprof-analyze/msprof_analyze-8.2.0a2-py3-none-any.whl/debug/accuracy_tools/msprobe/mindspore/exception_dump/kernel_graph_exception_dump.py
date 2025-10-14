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

import os

from msprobe.core.common.file_utils import create_directory, save_json
from msprobe.mindspore.common.log import logger
from msprobe.mindspore.debugger.debugger_config import DebuggerConfig


class KernelGraphExceptionDump:

    def __init__(self, config: DebuggerConfig):
        self.dump_json = dict()
        self.dump_json["common_dump_settings"] = dict()
        self.dump_json["common_dump_settings"]["dump_mode"] = 0
        self.dump_json["common_dump_settings"]["path"] = ""
        self.dump_json["common_dump_settings"]["net_name"] = "Net"
        self.dump_json["common_dump_settings"]["iteration"] = "all"
        self.dump_json["common_dump_settings"]["saved_data"] = "tensor"
        self.dump_json["common_dump_settings"]["input_output"] = 0
        self.dump_json["common_dump_settings"]["kernels"] = []
        self.dump_json["common_dump_settings"]["support_device"] = [0, 1, 2, 3, 4, 5, 6, 7]
        self.dump_json["common_dump_settings"]["op_debug_mode"] = 4
        self.dump_json["common_dump_settings"]["file_format"] = "npy"
        self.dump_json["e2e_dump_settings"] = dict()
        self.dump_json["e2e_dump_settings"]["enable"] = not config.async_dump
        self.dump_json["e2e_dump_settings"]["trans_flag"] = True

        if config.stat_cal_mode and config.device_stat_precision_mode:
            self.dump_json["e2e_dump_settings"]["stat_calc_mode"] = config.stat_cal_mode
            self.dump_json["e2e_dump_settings"]["device_stat_precision_mode"] = config.device_stat_precision_mode
        self.dump_json["common_dump_settings"]["path"] = config.dump_path
        if len(config.step) > 0:
            logger.warning("Step would change to all in this task.")
        if len(config.rank) > 0:
            self.dump_json["common_dump_settings"]["support_device"] = config.rank

    def handle(self):
        json_path = self.dump_json["common_dump_settings"]["path"]
        create_directory(json_path)
        json_path = os.path.join(json_path, "kernel_graph_exception_check.json")
        save_json(json_path, self.dump_json, indent=4)
        logger.info(json_path + " has been created.")
        os.environ["MINDSPORE_DUMP_CONFIG"] = json_path
