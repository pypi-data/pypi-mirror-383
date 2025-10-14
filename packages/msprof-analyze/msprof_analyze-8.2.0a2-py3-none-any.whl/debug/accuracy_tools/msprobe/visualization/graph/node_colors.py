# Copyright (c) 2024-2024, Huawei Technologies Co., Ltd.
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

from enum import Enum
from msprobe.visualization.utils import GraphConst, ToolTip

SUMMARY_DESCRIPTION = "此节点所有输入输出的统计量相对误差, 值越大代表测量值与标杆值的偏差越大, 相对误差计算方式:|(测量值-标杆值)/标杆值|"
REAL_DATA_DESCRIPTION = (f"此节点所有输入的最小双千分之一和所有输出的最小双千分之一的差值的绝对值, 代表双千指标的变化情况, "
                         f"值越大代表测量值与标杆值的偏差越大, 双千分之一指标计算方式：{ToolTip.ONE_THOUSANDTH_ERR_RATIO}")
MD5_DESCRIPTION_N = "与标杆相比, 此节点任意输入输出的md5值不同"
MD5_DESCRIPTION_Y = "与标杆相比, 此节点所有输入输出的md5值相同"
NOT_MATCHED = "比对过程中节点未匹配上"


class NodeColors(Enum):
    # 枚举值后缀数字越小, 颜色越浅
    # value值左闭右开, 两个值相同代表固定值
    YELLOW_1 = ("#FFFCF3", {
        GraphConst.SUMMARY_COMPARE: {GraphConst.VALUE: [0, 0.2], GraphConst.DESCRIPTION: SUMMARY_DESCRIPTION},
        GraphConst.REAL_DATA_COMPARE: {GraphConst.VALUE: [0, 0.05], GraphConst.DESCRIPTION: REAL_DATA_DESCRIPTION},
        GraphConst.MD5_COMPARE: {GraphConst.VALUE: [1, 1], GraphConst.DESCRIPTION: MD5_DESCRIPTION_Y},
    })
    YELLOW_2 = ("#FFEDBE", {
        GraphConst.SUMMARY_COMPARE: {GraphConst.VALUE: [0.2, 0.4], GraphConst.DESCRIPTION: SUMMARY_DESCRIPTION},
        GraphConst.REAL_DATA_COMPARE: {GraphConst.VALUE: [0.05, 0.1], GraphConst.DESCRIPTION: REAL_DATA_DESCRIPTION}
    })
    ORANGE_1 = ("#FFDC7F", {
        GraphConst.SUMMARY_COMPARE: {GraphConst.VALUE: [0.4, 0.6], GraphConst.DESCRIPTION: SUMMARY_DESCRIPTION},
        GraphConst.REAL_DATA_COMPARE: {GraphConst.VALUE: [0.1, 0.15], GraphConst.DESCRIPTION: REAL_DATA_DESCRIPTION}
    })
    ORANGE_2 = ("#FFC62E", {
        GraphConst.SUMMARY_COMPARE: {GraphConst.VALUE: [0.6, 0.8], GraphConst.DESCRIPTION: SUMMARY_DESCRIPTION},
        GraphConst.REAL_DATA_COMPARE: {GraphConst.VALUE: [0.15, 0.2], GraphConst.DESCRIPTION: REAL_DATA_DESCRIPTION}
    })
    RED = ("#FF704D", {
        GraphConst.SUMMARY_COMPARE: {GraphConst.VALUE: [0.8, 1], GraphConst.DESCRIPTION: SUMMARY_DESCRIPTION},
        GraphConst.REAL_DATA_COMPARE: {GraphConst.VALUE: [0.2, 1], GraphConst.DESCRIPTION: REAL_DATA_DESCRIPTION},
        GraphConst.MD5_COMPARE: {GraphConst.VALUE: [0, 0], GraphConst.DESCRIPTION: MD5_DESCRIPTION_N},
    })
    GREY = ("#C7C7C7", {
        GraphConst.VALUE: [], GraphConst.DESCRIPTION: NOT_MATCHED
    })

    def __init__(self, hex_value, mode_info):
        self.hex_value = hex_value
        self.mode_info = mode_info

    @staticmethod
    def get_node_colors(mode):
        """
        获取不同比对模式下的颜色说明
        Args:
            mode: 比对模式
        Returns: 颜色说明
        """
        return {
            color.hex_value: color.get_info_by_mode(mode) for color in NodeColors if color.get_info_by_mode(mode)
        }

    @staticmethod
    def get_node_error_status(mode, value):
        """
        判断精度数据比对指标是否大于基准值
        Args:
            mode: 比对模式
            value: 精度数据比对指标
        Returns: bool
        """
        info = NodeColors.ORANGE_1.get_info_by_mode(mode)
        if info and GraphConst.VALUE in info:
            value_range = info[GraphConst.VALUE]
            return value > value_range[0]
        return False

    def get_info_by_mode(self, mode):
        if isinstance(self.mode_info, dict):
            # 检查是否是模式特定的信息
            if isinstance(next(iter(self.mode_info.values())), dict):
                return self.mode_info.get(mode, {})
            else:
                # 所有模式共享相同的信息
                return self.mode_info
        return {}
