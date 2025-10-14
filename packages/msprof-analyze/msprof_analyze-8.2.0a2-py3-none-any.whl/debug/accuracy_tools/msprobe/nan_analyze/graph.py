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

from dataclasses import dataclass
from msprobe.core.common.const import Const
from msprobe.core.common.log import logger
from msprobe.nan_analyze.utils import FileCache, RankPath, is_ignore_op, check_item_anomaly, NanAnalyseConst
from msprobe.core.common.exceptions import MsprobeException


@dataclass
class DataNode:
    op_name: str
    rank: int
    inputs: list
    input_args: list
    input_kwargs: dict
    outputs: dict
    layer: int = 0  # 和communication_node的layer保持一致
    sub_layer: int = 0  # 调用顺序，越小表示越先调用

    def __init__(self, op_name, rank, op_data, **kwargs):
        self.op_name = op_name
        self.rank = rank
        self.inputs = op_data.get(Const.INPUT, [])
        self.input_args = op_data.get(Const.INPUT_ARGS, [])
        self.input_kwargs = op_data.get(Const.INPUT_KWARGS, {})
        self.outputs = op_data.get(Const.OUTPUT, {})
        self.sub_layer = kwargs.get('sub_layer', 0)

    @staticmethod
    def find_complete_construct(construct_info, op_name):
        construct = [op_name]
        seen = set(op_name)
        while True:
            op_name = construct_info.get(op_name)
            if not op_name or op_name in seen:
                return construct
            construct.insert(0, op_name)
            seen.add(op_name)

    def find_stack(self, stack_info):
        for item in stack_info.values():
            if not isinstance(item, list):
                raise MsprobeException(MsprobeException.UNSUPPORTED_TYPE_ERROR,
                                       f'The value\'s type in stack.json should be a list, not {type(item)}!')
            if len(item) >= 2 and self.op_name in item[0]:
                return item[1]
        return {}

    def is_anomaly(self) -> bool:
        if is_ignore_op(self.op_name):
            return False
        is_input_anomaly = (check_item_anomaly(self.inputs) or check_item_anomaly(self.input_args) or
                            check_item_anomaly(self.input_kwargs))
        is_output_anomaly = check_item_anomaly(self.outputs)
        return (not is_input_anomaly) and is_output_anomaly

    def gen_node_info(self, path: RankPath):
        cache = FileCache()
        construct = cache.load_json(path.construct_path)
        stack = cache.load_json(path.stack_path)
        if Const.FORWARD in self.op_name:
            data_info_list = {Const.INPUT_ARGS: self.input_args, Const.INPUT_KWARGS: self.input_kwargs,
                              Const.OUTPUT: self.outputs}
        else:
            data_info_list = {Const.INPUT: self.inputs, Const.OUTPUT: self.outputs}
        return {'op_name': self.op_name,
                'data_info': data_info_list,
                'construct_info': self.find_complete_construct(construct, self.op_name),
                'stack_info': self.find_stack(stack)}


class CommunicationNode:
    def __init__(self, node_id, rank, data: DataNode, layer=0, **kwargs):
        self.node_id = node_id
        self.rank = rank
        self.data = data
        self.layer = layer
        op_name_split = self.data.op_name.split(Const.SEP)
        if len(op_name_split) < 4:
            logger.error(f'invalid op_name: {self.data.op_name}')
            raise RuntimeError(f'invalid op_name: {self.data.op_name}')
        self.api = op_name_split[1]
        self.call_cnt = op_name_split[2]
        self.pre_node = kwargs.get('pre_node')
        self.link_nodes = kwargs.get('link_nodes', {})
        self.dst_nodes = kwargs.get('dst_nodes', {})
        self.src_nodes = kwargs.get('src_nodes', {})
        self.next_nodes = kwargs.get('next_nodes', {})
        self.compute_ops = kwargs.get('compute_ops', [])
        self.type = self._resolve_type()
        self.connected = False

    def add_next(self, node):
        self.next_nodes[node.node_id] = node
        node.pre_node = self
        node.layer = self.layer + 1
        node.data.layer = node.layer

    def add_link(self, node):
        self.link_nodes[node.node_id] = node
        node.link_nodes[self.node_id] = self
        node.layer = self.layer
        node.data.layer = node.layer
        self.connected = True
        node.connected = True

    def add_dst(self, node):
        self.dst_nodes[node.node_id] = node
        node.src_nodes[self.node_id] = self
        node.layer = self.layer
        node.data.layer = node.layer
        self.connected = True
        node.connected = True

    def delete(self):
        for node in self.next_nodes.values():
            node.pre_node = None
        for node in self.dst_nodes.values():
            node.src_nodes.pop(self.node_id)
        for node in self.src_nodes.values():
            node.dst_nodes.pop(self.node_id)
        for node in self.link_nodes.values():
            node.link_nodes.pop(self.node_id)
        if self.pre_node:
            self.pre_node.next_nodes.pop(self.node_id)

    def has_nan_inf(self):
        return self.input_has_nan_inf() or check_item_anomaly(self.data.outputs)
    
    def input_has_nan_inf(self):
        return check_item_anomaly(self.data.input_args) or check_item_anomaly(self.data.input_kwargs)

    def find_connected_nodes(self):
        """
        根据 api/类型/入参/调用次数 确定相连接的node的op_name
        """
        tar_api = NanAnalyseConst.P2P_API_MAPPING.get(self.api, self.api)
        ranks = set()
        for dst in [NanAnalyseConst.DST, NanAnalyseConst.DST_GROUP]:
            if dst in self.data.input_kwargs:
                dst_value = self.data.input_kwargs.get(dst)
                if dst_value:
                    ranks.add(dst_value.get('value'))
                break
        for src in [NanAnalyseConst.SRC, NanAnalyseConst.SRC_GROUP]:
            if src in self.data.input_kwargs:
                src_value = self.data.input_kwargs.get(src)
                if src_value:
                    ranks.add(src_value.get('value'))
                break
        if not ranks:
            for item in self.data.input_args:
                if isinstance(item, dict) and item.get(Const.TYPE) == 'int':
                    ranks.add(item.get('value'))
        group = self.data.input_kwargs.get('group')
        if group:
            ranks.update(group.get('group_ranks'))
        return {'ranks': ranks, 'api': f'Distributed.{tar_api}',
                'type': NanAnalyseConst.OPPOSITE_DIR.get(self.type, NanAnalyseConst.LINK)}

    def _resolve_type(self):
        for src in [NanAnalyseConst.SRC, NanAnalyseConst.SRC_GROUP]:
            if src in self.data.input_kwargs and self.data.input_kwargs[src]:
                if self.data.input_kwargs[src].get('value') == self.rank:
                    return NanAnalyseConst.SRC
                else:
                    return NanAnalyseConst.DST
        for dst in [NanAnalyseConst.DST, NanAnalyseConst.DST_GROUP]:
            if dst in self.data.input_kwargs and self.data.input_kwargs[dst]:
                if self.data.input_kwargs[dst].get('value') == self.rank:
                    return NanAnalyseConst.DST
                else:
                    return NanAnalyseConst.SRC
        if self.api in NanAnalyseConst.DIRECTED_API:
            for item in self.data.input_args:
                if item.get(Const.TYPE) == 'int':
                    node_type = NanAnalyseConst.DIRECTED_API[self.api]
                    return node_type if item.get('value') == self.rank else NanAnalyseConst.OPPOSITE_DIR[node_type]
        return NanAnalyseConst.LINK
