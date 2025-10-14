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

import os
import types
from collections import defaultdict

import mindspore
from mindspore import nn
from mindspore._c_expression import PyNativeExecutor_

try:
    from mindspore.common.api import _MindsporeFunctionExecutor
except ImportError:
    from mindspore.common.api import _JitExecutor as _MindsporeFunctionExecutor

from msprobe.core.common.log import logger
from msprobe.core.common.const import Const
from msprobe.core.common.utils import ThreadSafe
from msprobe.core.common.runtime import Runtime
from msprobe.core.data_dump.data_processor.base import ModuleForwardInputsOutputs, ModuleBackwardInputsOutputs
from msprobe.mindspore.common.const import Const as MsConst
from msprobe.mindspore.dump.hook_cell.api_register import get_api_register

_api_register = get_api_register()


def dump_jit(name, in_feat, out_feat, is_forward):
    pid = os.getpid()
    name = name if name else "JitFunction"
    if not JitDump.need_dump():
        return
    with ThreadSafe():
        if is_forward:
            if name in JitDump.jit_count:
                JitDump.jit_count[name] += 1
            else:
                JitDump.jit_count[name] = 0
            name_template = (Const.JIT + Const.SEP + name + Const.SEP +
                             str(JitDump.jit_count[name]) + Const.SEP + Const.FORWARD)
            JitDump.data_collector.update_api_or_module_name(name_template)
            module_input_output = ModuleForwardInputsOutputs(args=in_feat, kwargs={}, output=out_feat)
            JitDump.data_collector.forward_data_collect(name_template, None, pid, module_input_output)
        else:
            name_template = Const.JIT + Const.SEP + name + Const.SEP + str(JitDump.jit_count[name]) + Const.SEP + \
                            Const.BACKWARD
            JitDump.data_collector.update_api_or_module_name(name_template)
            module_input_output = ModuleBackwardInputsOutputs(grad_input=in_feat, grad_output=out_feat)
            JitDump.data_collector.backward_data_collect(name_template, None, pid, module_input_output)


class JitDump(_MindsporeFunctionExecutor):
    dump_config = None
    jit_enable = False
    jit_dump_switch = False
    jit_count = defaultdict(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = None
        if len(args) > 0:
            self.name = args[0].__name__
        self._executor = PyNativeExecutor_.get_instance()

    def __call__(self, *args, **kwargs):
        _api_register.restore_all_api()
        out = super().__call__(*args, **kwargs)
        if JitDump.jit_dump_switch and len(args) > 0 and self.name:
            if self.name != "construct":
                dump_jit(self.name, args, out, True)
            elif Runtime.run_mode != MsConst.PYNATIVE_GRAPH_MODE and isinstance(args[0], nn.Cell):
                dump_jit(args[0].__class__.__name__, args, out, True)
            JitDump.jit_enable = True
        elif len(args) == 0:
            logger.warning(f"The jit function {self.name} has no input arguments, nothing will be dumped.")
        _api_register.register_all_api()
        return out

    @classmethod
    def set_config(cls, value):
        cls.dump_config = value

    @classmethod
    def set_data_collector(cls, value):
        cls.data_collector = value

    @classmethod
    def need_dump(cls):
        if cls.dump_config.task != Const.TENSOR and cls.dump_config.task != Const.STATISTICS:
            return False
        if not cls.data_collector or cls.data_collector.data_processor.is_terminated:
            return False
        return True

    def grad(self, obj, grad, weights, grad_position, *args, **kwargs):
        if JitDump.jit_dump_switch and JitDump.jit_enable:
            _api_register.restore_all_api()
        if mindspore.__version__ >= "2.5":
            output = self._executor.grad(grad, obj, weights, grad_position, False, *args, *(kwargs.values()))
        else:
            output = self._executor.grad(grad, obj, weights, grad_position, *args, *(kwargs.values()))
        if JitDump.jit_dump_switch and JitDump.jit_enable:
            if isinstance(obj, types.FunctionType):
                dump_jit(obj.__name__, args, None, False)
            elif Runtime.run_mode != MsConst.PYNATIVE_GRAPH_MODE and isinstance(obj, nn.Cell):
                dump_jit(obj.__class__.__name__, args, None, False)
            _api_register.register_all_api()
        return output
