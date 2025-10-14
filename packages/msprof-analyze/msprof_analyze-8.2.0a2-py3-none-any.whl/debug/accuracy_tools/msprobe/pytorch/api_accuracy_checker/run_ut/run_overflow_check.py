#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import argparse
import os
import sys

try:
    import torch_npu
except ImportError:
    is_gpu = True
    current_device = "cuda"
else:
    is_gpu = False
    current_device = "npu"
import torch
from tqdm import tqdm
from msprobe.pytorch.api_accuracy_checker.run_ut.run_ut import generate_device_params, get_api_info
from msprobe.pytorch.api_accuracy_checker.run_ut.run_ut_utils import exec_api, is_unsupported_api, ExecParams
from msprobe.core.common.file_utils import check_link, FileChecker
from msprobe.pytorch.api_accuracy_checker.common.utils import extract_basic_api_segments
from msprobe.core.common.const import FileCheckConst, Const
from msprobe.core.common.utils import check_op_str_pattern_valid
from msprobe.pytorch.common.log import logger
from msprobe.pytorch.common.parse_json import parse_json_info_forward_backward
from msprobe.core.common.decorator import recursion_depth_decorator


def check_tensor_overflow(x):
    if isinstance(x, torch.Tensor) and x.numel() != 0 and x.dtype != torch.bool:
        if len(x.shape) == 0:
            tensor_max = x.cpu().detach().float().numpy().tolist()
            tensor_min = tensor_max
        else:
            tensor_max = torch.max(x).cpu().detach().float().numpy().tolist()
            tensor_min = torch.min(x).cpu().detach().float().numpy().tolist()
        # inf
        if tensor_max == float('inf') or tensor_min == float('-inf'):
            return True
        # nan
        elif tensor_max != tensor_max or tensor_min != tensor_min:
            return True
        else:
            return False
    elif isinstance(x, bool) or isinstance(x, int) or isinstance(x, float):
        if x == float('inf') or x == float('-inf') or x != x:
            return True
        else:
            return False
    else:
        return False


@recursion_depth_decorator("check_data_overflow")
def check_data_overflow(x, device):
    if isinstance(x, (tuple, list)):
        if not x:
            return False
        return any(check_data_overflow(item, device) for item in x)
    else:
        if device == Const.CPU_LOWERCASE:
            return check_tensor_overflow(x)
        else:
            return torch_npu.npu.utils.npu_check_overflow(x)


@recursion_depth_decorator("is_bool_output")
def is_bool_output(x):
    if isinstance(x, (tuple, list)):
        if not x:
            return False
        return any(is_bool_output(item) for item in x)
    else:
        return isinstance(x, bool)


def run_overflow_check(forward_file):
    logger.info("start UT test")
    forward_content, _, real_data_path = parse_json_info_forward_backward(forward_file)
    if real_data_path:
        dump_path = os.path.dirname(forward_file)
        real_data_path = os.path.join(dump_path, Const.DUMP_TENSOR_DATA)
    for api_full_name, api_info_dict in tqdm(forward_content.items()):
        check_op_str_pattern_valid(api_full_name)
        if is_unsupported_api(api_full_name, is_overflow_check=True):
            continue
        try:
            run_torch_api(api_full_name, api_info_dict, real_data_path)
        except Exception as err:
            _, api_name, _ = api_full_name.split(Const.SEP)
            if "not implemented for 'Half'" in str(err):
                logger.warning(f"API {api_name} not support half tensor in CPU. This API does not support overflow "
                               "check, so it will be skipped.")
            elif "expected scalar type Long" in str(err):
                logger.warning(f"API {api_name} not support int32 tensor in CPU, please add {api_name} to CONVERT_API "
                               "'int32_to_int64' list in accuracy_tools/msprobe/core/common/const.py file.")
            elif "could not create a primitive descriptor for a matmul primitive" in str(err):
                logger.warning(f"API {api_name} not support matmul primitive in CPU due to pytorch bug, "
                               "so it will be skipped.")
            else:
                logger.error(f"Run {api_full_name} UT Error: %s" % str(err))


def run_torch_api(api_full_name, api_info_dict, real_data_path):
    torch.npu.clear_npu_overflow_flag()
    api_type, api_name = extract_basic_api_segments(api_full_name)
    args, kwargs, need_grad = get_api_info(api_info_dict, api_name, real_data_path)
    if not need_grad:
        logger.warning("%s function with out=... arguments don't support automatic differentiation, skip backward." 
                       % api_full_name)
    device_info_kwargs = kwargs.get(Const.DEVICE)
    if device_info_kwargs and device_info_kwargs.get(Const.VALUE):
        kwargs[Const.DEVICE] = current_device
    npu_args, npu_kwargs = generate_device_params(args, kwargs, False, api_name)
    if kwargs.get(Const.DEVICE):
        del kwargs[Const.DEVICE]
    cpu_exec_params = ExecParams(api_type, api_name, Const.CPU_LOWERCASE, args, kwargs, False, None)
    device_exec_params = ExecParams(api_type, api_name, Const.NPU_LOWERCASE, npu_args, npu_kwargs, False, None)
    out = exec_api(cpu_exec_params)
    npu_out = exec_api(device_exec_params)
    if out is None and npu_out is None:
        logger.warning("The %s overflow is a normal overflow, out and npu_out is None." % api_full_name)
        return
    if is_bool_output(out) or is_bool_output(npu_out):
        logger.warning("The output of %s is bool type.This dtype not support overflow, so it will be skipped."
                       % api_full_name)
        return

    cpu_overflow = check_data_overflow(out, Const.CPU_LOWERCASE)
    npu_overflow = check_data_overflow(npu_out, Const.NPU_LOWERCASE)
    if cpu_overflow == npu_overflow:
        logger.warning("The %s overflow is a normal overflow." % api_full_name)
    else:
        logger.warning("The %s overflow is an abnormal overflow." % api_full_name)
    return


def _run_overflow_check_parser(parser):
    parser.add_argument("-api_info", "--api_info_file", dest="api_info_file", default="",
                        help="<Required> The api param tool result file: generate from api param tool, "
                             "a json file.",
                        required=True)
    parser.add_argument("-j", "--jit_compile", dest="jit_compile", help="<optional> whether to turn on jit compile",
                        default=False, required=False)
    parser.add_argument("-d", "--device", dest="device_id", type=int, help="<optional> set NPU device id to run ut",
                        default=0, required=False)


def _run_overflow_check(parser=None):
    if not parser:
        parser = argparse.ArgumentParser()
    _run_overflow_check_parser(parser)
    args = parser.parse_args(sys.argv[1:])
    _run_overflow_check_command(args)
    logger.info("UT task completed.")


def _run_overflow_check_command(args):
    torch.npu.set_compile_mode(jit_compile=args.jit_compile)
    npu_device = "npu:" + str(args.device_id)
    api_info_file_checker = FileChecker(file_path=args.api_info_file, path_type=FileCheckConst.FILE, 
                                            ability=FileCheckConst.READ_ABLE, file_type=FileCheckConst.JSON_SUFFIX)
    api_info = api_info_file_checker.common_check()
    try:
        torch.npu.set_device(npu_device)
    except Exception as error:
        logger.error(f"Set NPU device id failed. device id is: {args.device_id}")
        raise NotImplementedError from error
    run_overflow_check(api_info)
