# Copyright (c) 2025-2025, Huawei Technologies Co., Ltd.
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

import atexit
from multiprocessing import Pool
import os
import re
import time

import numpy as np
import pandas as pd
import mindspore as ms
from mindspore import nn, ops

from msprobe.core.common.const import Const as CoreConst
from msprobe.core.common.const import FileCheckConst
from msprobe.core.common.file_utils import (
    load_npy, save_json, remove_path, load_yaml,
    create_directory, read_csv, write_df_to_csv, write_csv, move_file, move_directory)
from msprobe.mindspore.common.log import logger
from msprobe.mindspore.dump.cell_dump_process import CellDumpConfig


CONSTRUCT_FILE_NAME = "construct.json"
DEFAULT_RANK_DIR = "rank0"
KEY_LAYERS = "layers"
construct = {}
cell_list = []
KEY_SIDE_EFFECT = "side_effect_io"
KEY_TOPLAYER = "TopLayer"
KEY_FORWARD = CoreConst.FORWARD
KEY_BACKWARD = CoreConst.BACKWARD
KEY_INPUT = CoreConst.INPUT
KEY_OUTPUT = CoreConst.OUTPUT
KEY_DUMP_TENSOR_DATA = "dump_tensor_data_"
KEY_STATISTIC_CSV = "statistic.csv"
KEY_TD_FLAG = "td_flag"
td = ops.TensorDump()
if (ms.__version__ >= "2.5.0"):
    td_in = ops.TensorDump("in")
else:
    td_in = ops.TensorDump()
graph_step_flag = True
try:
    from mindspore._c_expression import _set_init_iter
except ImportError:
    graph_step_flag = False
td.add_prim_attr(KEY_SIDE_EFFECT, False)
td_in.add_prim_attr(KEY_SIDE_EFFECT, False)
td.add_prim_attr(KEY_TD_FLAG, True)
td_in.add_prim_attr(KEY_TD_FLAG, True)
dump_task = CoreConst.STATISTICS
np_ms_dtype_dict = {
    "bool": ms.bool_,
    "int8": ms.int8,
    "byte": ms.byte,
    "int16": ms.int16,
    "short": ms.short,
    "int32": ms.int32,
    "intc": ms.intc,
    "int64": ms.int64,
    "intp": ms.intp,
    "uint8": ms.uint8,
    "ubyte": ms.ubyte,
    "uint16": ms.uint16,
    "ushort": ms.ushort,
    "uint32": ms.uint32,
    "uintc": ms.uintc,
    "uint64": ms.uint64,
    "uintp": ms.uintp,
    "float16": ms.float16,
    "half": ms.half,
    "float32": ms.float32,
    "single": ms.single,
    "float64": ms.float64,
    "double": ms.double,
    "bfloat16": ms.bfloat16,
    "complex64": ms.complex64,
    "complex128": ms.complex128
}


def gen_file_path(dump_path, cell_prefix, suffix, io_type, index):
    data_path = os.path.join(dump_path, '{step}', '{rank}', CoreConst.DUMP_TENSOR_DATA)
    file_name = ""
    if dump_task == CoreConst.TENSOR:
        file_name = cell_prefix + CoreConst.SEP + suffix + CoreConst.SEP + io_type + CoreConst.SEP + str(index)
    if dump_task == CoreConst.STATISTICS:
        file_name = cell_prefix + CoreConst.HYPHEN + suffix + CoreConst.HYPHEN + io_type + CoreConst.HYPHEN + str(index)
    return os.path.join(data_path, file_name)


def partial_func(func, dump_path, cell_prefix, index, io_type):
    def newfunc(*args, **kwargs):
        return func(dump_path, cell_prefix, index, io_type, *args, **kwargs)
    return newfunc


def clip_gradient(dump_path, cell_prefix, index, io_type, dx):
    if io_type == KEY_OUTPUT:
        temp = td(gen_file_path(dump_path, cell_prefix, KEY_BACKWARD, io_type, index), dx)
        dx = ops.depend(dx, temp)
    elif io_type == KEY_INPUT:
        temp = td_in(gen_file_path(dump_path, cell_prefix, KEY_BACKWARD, io_type, index), dx)
        dx = ops.depend(dx, temp)
    return dx


def need_tensordump_in(cell_obj, attr):
    return hasattr(cell_obj, attr) and getattr(cell_obj, attr) == "in"


def cell_construct_wrapper(func, self):
    def new_construct(self, *args, **kwargs):
        new_args = []
        out_list = []

        index = 0
        item = None
        backward_or_all = self.data_mode in ["backward", "all"]
        forward_or_all = self.data_mode in ["forward", "all"]
        # The inputs of the cell.
        for index, item in enumerate(args):
            if backward_or_all and ops.is_tensor(item):
                item = self.output_clips[index](item)
            if forward_or_all and ops.is_tensor(item):
                if need_tensordump_in(self, 'input_dump_mode'):
                    temp = td_in(
                        gen_file_path(self.dump_path, self.cell_prefix, KEY_FORWARD, KEY_INPUT, index),
                        item
                    )
                else:
                    temp = td(
                        gen_file_path(self.dump_path, self.cell_prefix, KEY_FORWARD, KEY_INPUT, index),
                        item
                    )
                item = ops.depend(item, temp)
            new_args.append(item)

        out = func(*new_args, **kwargs)

        # The outputs of the cell.
        if isinstance(out, tuple):
            for index, item in enumerate(out):
                if backward_or_all and ops.is_tensor(item):
                    item = self.input_clips[index](item)
                if forward_or_all and ops.is_tensor(item):
                    if need_tensordump_in(self, 'output_dump_mode'):
                        temp = td_in(
                            gen_file_path(self.dump_path, self.cell_prefix, KEY_FORWARD, KEY_OUTPUT, index),
                            item
                        )
                    else:
                        temp = td(
                            gen_file_path(self.dump_path, self.cell_prefix, KEY_FORWARD, KEY_OUTPUT, index),
                            item
                        )
                    item = ops.depend(item, temp)
                    out_list.append(item)
                elif forward_or_all and not ops.is_tensor(item):
                    out_list.append(item)
            out_list = tuple(out_list)
            return out_list
        else:
            if backward_or_all:
                out = self.input_clips[0](out)
            if forward_or_all and ops.is_tensor(out):
                if need_tensordump_in(self, 'output_dump_mode'):
                    temp = td_in(
                        gen_file_path(self.dump_path, self.cell_prefix, KEY_FORWARD, KEY_OUTPUT, 0),
                        out
                    )
                else:
                    temp = td(
                        gen_file_path(self.dump_path, self.cell_prefix, KEY_FORWARD, KEY_OUTPUT, 0),
                        out
                    )
                out = ops.depend(out, temp)
            return out

    return new_construct.__get__(self, type(self))


# 获取目录下所有文件名并根据TensorDump落盘自增id从小到大排序
def sort_filenames(path):
    filenames = os.listdir(path)
    id_pattern = re.compile(rf'{CoreConst.REPLACEMENT_CHARACTER}(\d+){CoreConst.NUMPY_SUFFIX}$')
    # 只保留能提取到数字id的文件，避免数组越界
    valid_files = []
    for filename in filenames:
        match = id_pattern.findall(filename)
        if match and match[0].isdigit():
            valid_files.append(filename)
        else:
            logger.warning(f"File {filename} does not match the expected pattern and will be ignored.")
    valid_files.sort(key=lambda x: int(id_pattern.findall(x)[0]))
    return valid_files


def rename_filename(path="", data_df=None):
    if dump_task == CoreConst.TENSOR:
        filenames = sort_filenames(path)
    if dump_task == CoreConst.STATISTICS:
        filenames = data_df[CoreConst.OP_NAME].tolist()

    filename_dict = {}
    for index, filename in enumerate(filenames):
        if dump_task == CoreConst.TENSOR:
            name_field = filename.rsplit(CoreConst.REPLACEMENT_CHARACTER, 1)[0]
        if dump_task == CoreConst.STATISTICS:
            name_field = filename

        if name_field in filename_dict:
            filename_dict[name_field] += 1
        else:
            filename_dict[name_field] = 0

        cell_index = filename_dict[name_field]

        # 修改文件名，增加重复调用Cell的序号
        if CoreConst.FORWARD_PATTERN in filename:
            # Format: Cell.{cell_name}.{class_name}.{forward/backward}.{number}.{input/output}.{index}_{dtype}_{id}.npy
            new_file_name = filename.replace(CoreConst.FORWARD_PATTERN,
                                             CoreConst.FORWARD_PATTERN + str(cell_index) + CoreConst.SEP)
        if CoreConst.BACKWARD_PATTERN in filename:
            new_file_name = filename.replace(CoreConst.BACKWARD_PATTERN,
                                             CoreConst.BACKWARD_PATTERN + str(cell_index) + CoreConst.SEP)
        if dump_task == CoreConst.TENSOR:
            move_file(os.path.join(path, filename), os.path.join(path, new_file_name))
        if dump_task == CoreConst.STATISTICS:
            data_df.loc[index, CoreConst.OP_NAME] = new_file_name
    logger.info("==========The rename_filename phase is Finished!==========")


# Extract the field between the first "." and the third to last ".", i.e. {cell_name}
def get_cell_name(string):
    parts = string.split(CoreConst.SEP)
    if len(parts) < 4:
        return None
    start_index = 1
    end_index = len(parts) - 3
    return CoreConst.SEP.join(parts[start_index:end_index])


# Extract the field between the last "." and the second to last ".", i.e. {data_made}
def get_data_mode(string):
    last_dot_index = string.rfind(CoreConst.SEP)
    second_last_dot_index = string.rfind(CoreConst.SEP, 0, last_dot_index)
    data_mode = string[second_last_dot_index + 1:last_dot_index]
    return data_mode


# 判断二者之间是否存在父子关系
def check_relation(cell_name, parent_cell_name):
    layers_pattern = rf"{CoreConst.SEP}{KEY_LAYERS}{CoreConst.SEP}\d+$"
    last_dot_index = cell_name.rfind(CoreConst.SEP)
    if last_dot_index == -1:
        return False
    # 如果cell_name最后一个'.'之前的字段等于parent_cell_name，则判定存在父子关系
    sub_cell_name = cell_name[:last_dot_index]
    if sub_cell_name == parent_cell_name:
        return True
    elif re.search(layers_pattern, cell_name):
        # 如果cell_name以".layer.{layer_id}"结尾，且去掉该字段后等于parent_cell_name，则判定存在父子关系
        sub_cell_name = re.sub(layers_pattern, '', cell_name)
        if sub_cell_name == parent_cell_name:
            return True
    return False


def get_construct(cell_list_input):
    for cell in cell_list_input:
        cell_name = get_cell_name(cell)
        cell_data_mode = get_data_mode(cell)
        found_flag = False
        for parent_cell in cell_list_input:
            parent_cell_name = get_cell_name(parent_cell)
            parent_data_mode = get_data_mode(parent_cell)
            has_relation = check_relation(cell_name, parent_cell_name)
            if has_relation and parent_data_mode == cell_data_mode:
                construct.update({cell: parent_cell})
                found_flag = True
                break
        if not found_flag:
            construct.update({cell: None})


def generate_construct(path):
    global construct
    if dump_task == CoreConst.TENSOR:
        # filename格式：Cell.clip_grad_norm.ClipGradNorm.forward.0.output.1_int32_0.npy
        filenames = sort_filenames(path)
        point_position = 3
    if dump_task == CoreConst.STATISTICS:
        df = read_csv(path)
        # filename格式：Cell.clip_grad_norm.ClipGradNorm.forward.0.output.1
        filenames = df[CoreConst.OP_NAME].tolist()
        point_position = 2

    # 提取文件名中Cell.{cell_name}.{class_name}.{data_mode}.{重复调用此cell的序号}字段，并存入cell_list
    for filename in filenames:
        mid_field = filename.rsplit(CoreConst.SEP, point_position)[0]
        if KEY_INPUT in filename:
            if mid_field in cell_list:
                cell_list.remove(mid_field)
            cell_list.append(mid_field)
        else:
            if mid_field not in cell_list:
                index = filenames.index(filename)
                output_field = mid_field + KEY_OUTPUT
                find_flag = False
                for filename_other in cell_list[index + 1:]:
                    if output_field in filename_other:
                        find_flag = True
                if find_flag is False:
                    cell_list.append(mid_field)

    get_construct(cell_list)

    # 生成JSON文件
    rank_dir = os.path.dirname(path)
    json_path = os.path.join(rank_dir, CONSTRUCT_FILE_NAME)
    save_json(json_path, construct, indent=1)

    # 清空'construct'继续处理下一个路径下的数据
    construct = {}
    logger.info(f"Construct data saved to {json_path}")


def process_file(file_path):
    try:
        # 读取.npy文件内容
        npy_content = load_npy(file_path)
        logger.debug(f"Loaded {file_path}: shape is {npy_content.shape}, dtype is {npy_content.dtype}")

        # 文件名举例:Cell.network._backbone.loss.CrossEntropyLoss.forward.0.input.0_float32_165.npy
        parts = os.path.basename(file_path).split(CoreConst.SEP)
        data_dtype = ""
        # 获取0_float32_165或者0_in_float32_165中的float32
        data_dtype_list = parts[-2].split('_')
        if len(data_dtype_list) > 1:
            data_dtype = data_dtype_list[-2]
        # op_name是Cell.network._backbone.loss.CrossEntropyLoss.forward.0
        op_name = CoreConst.SEP.join(parts[:-3])
        ms_dtype = np_ms_dtype_dict.get(data_dtype)
        if ms_dtype is None:
            logger.warning(f"Get dtype None from file {file_path}")

        # 修改落盘文件名字，去掉TensorDump自带的数据类型和自增id字段
        data_file_name = os.path.basename(file_path)
        data_file_dir = os.path.dirname(file_path)
        parts = data_file_name.split(CoreConst.SEP)
        if len(parts) >= 2:
            param_index = parts[-2].split(CoreConst.REPLACEMENT_CHARACTER)[0]
            pre_parts = CoreConst.SEP.join(parts[:-2])
            new_file_name = pre_parts + CoreConst.SEP + param_index + CoreConst.NUMPY_SUFFIX
            move_file(os.path.join(data_file_dir, data_file_name), os.path.join(data_file_dir, new_file_name))
            logger.debug(f"{data_file_name} is renamed to {new_file_name}")
        else:
            logger.warning(f"Failed to rename {data_file_name}.")
            new_file_name = data_file_name

        tensor_json = {
            CoreConst.TYPE: 'mindspore.Tensor',
            CoreConst.DTYPE: str(ms_dtype),
            CoreConst.SHAPE: list(npy_content.shape),
            CoreConst.MAX: npy_content.max().item(),
            CoreConst.MIN: npy_content.min().item(),
            CoreConst.MEAN: npy_content.mean().item(),
            CoreConst.NORM: np.linalg.norm(npy_content).item(),
            CoreConst.DATA_NAME: new_file_name
        }

        # 根据文件名的最后一个部分（输入或输出）确定是添加到input_args还是output
        if parts[-3] == KEY_INPUT:
            return op_name, CoreConst.INPUT_ARGS, tensor_json
        elif parts[-3] == KEY_OUTPUT:
            return op_name, KEY_OUTPUT, tensor_json
        else:
            return None, None, None

    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None, None, None


def custom_sort(item, key_to_index):
    key = item[0]
    return key_to_index.get(key, float('inf'))


def convert_special_values(value):
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        try:
            return float(value)
        except ValueError:
            return value
    elif pd.isna(value):
        return None
    return value


def process_csv(path):
    data_info = []
    df = read_csv(path)
    df = df.sort_values(by='Op Name', ascending=True)
    columns = df.columns
    colume_to_json_key = {
        'Max Value': CoreConst.MAX,
        'Min Value': CoreConst.MIN,
        'Avg Value': CoreConst.MEAN,
        'L2Norm Value': CoreConst.NORM
    }
    for _, row in df.iterrows():
        # op_name_value格式：Cell.network._backbone.loss.CrossEntropyLoss.forward.0.input.0
        op_name_value = row['Op Name']
        op_name = op_name_value.rsplit(CoreConst.SEP, 2)[0]

        # 获取input/output字段
        io_key = op_name_value.split(CoreConst.SEP)[-2]

        # shape读取出来为字符串类型转为list。"(1,4096)"->[1,4096]
        shape_num = re.findall(r'\d+', row['Shape'])
        shape = [int(num) for num in shape_num]

        tensor_json = {
            CoreConst.TYPE: 'mindspore.Tensor',
            CoreConst.DTYPE: str(np_ms_dtype_dict.get(row['Data Type'])),
            CoreConst.SHAPE: shape
        }
        for col_name, json_key in colume_to_json_key.items():
            if col_name in columns:
                value = convert_special_values(row[col_name])
                tensor_json[json_key] = value
      
        if io_key == KEY_INPUT:
            data_info.append([op_name, CoreConst.INPUT_ARGS, tensor_json])
        elif io_key == KEY_OUTPUT:
            data_info.append([op_name, KEY_OUTPUT, tensor_json])
        else:
            data_info.append([None, None, None])
    return data_info


def generate_dump_info(path):
    if not os.path.exists(path):
        logger.error("The provided path does not exist.")
        return

    if dump_task == CoreConst.TENSOR:
        dump_data = {"task": "tensor", "level": "L0", "dump_data_dir": path, "data": {}}
        with Pool(processes=10) as pool:
            file_paths = []
            for file in os.listdir(path):
                if file.endswith(FileCheckConst.NUMPY_SUFFIX):
                    file_paths.append((os.path.join(path, file),))
            file_paths.sort()
            results = pool.starmap(process_file, file_paths)
    if dump_task == CoreConst.STATISTICS:
        dump_data = {"task": "statistics", "level": "L0", "framework": "mindspore", "dump_data_dir": None, "data": {}}
        results = process_csv(path)

    # 收集结果
    for op_name, key, tensor_json in results:
        if op_name:
            if op_name not in dump_data.get(CoreConst.DATA, {}):
                dump_data.get(CoreConst.DATA, {})[op_name] = {CoreConst.INPUT_ARGS: [],
                                                              CoreConst.INPUT_KWARGS: {},
                                                              KEY_OUTPUT: []}
            if key not in dump_data.get(CoreConst.DATA, {}).get(op_name, {}):
                dump_data.get(CoreConst.DATA, {}).get(op_name, {})[key] = []
            dump_data.get(CoreConst.DATA, {}).get(op_name, {}).get(key, []).append(tensor_json)

    # 根据cell_list排序
    data_dict = dump_data.get(CoreConst.DATA, {})
    key_to_index = {key: index for index, key in enumerate(cell_list)}
    sorted_data_dict = dict(sorted(data_dict.items(), key=lambda item: custom_sort(item, key_to_index)))
    dump_data[CoreConst.DATA] = sorted_data_dict

    # 将数据写入dump.json
    json_path = os.path.join(os.path.dirname(path), 'dump.json')
    save_json(json_path, dump_data, indent=1)

    logger.info(f"Dump data saved to {json_path}")


def generate_stack_info(path):
    if not os.path.exists(path):
        logger.error("The provided path does not exist.")
        return

    stack_data = {}
    for cell_name in cell_list:
        stack_data.update({cell_name: []})

    # 将数据写入stack.json
    json_path = os.path.join(os.path.dirname(path), 'stack.json')
    save_json(json_path, stack_data, indent=1)

    # 删除csv文件
    if dump_task == CoreConst.STATISTICS:
        remove_path(path)

    logger.info(f"Stack data saved to {json_path}")


def is_download_finished(directory, interval=3):
    """
    判断指定目录在一段时间后是否有数据被下载完成
    :param directory: 指定目录的路径
    :param interval: 检查的时间间隔（秒），默认为 3 秒
    :return: 如有数据被下载完成返回 True，否则返回 False
    """
    # 检查目录是否存在
    if not os.path.exists(directory):
        logger.warning(f"The specified directory {directory} does not exist.")
        return False, False
    initial_modification_time = os.path.getmtime(directory)
    time.sleep(interval)
    current_modification_time = os.path.getmtime(directory)
    # 比较初始和当前修改时间
    if current_modification_time > initial_modification_time:
        return False, True
    else:
        return True, False


def process(dump_path):
    rank_id = os.environ.get('RANK_ID')
    rank_dir = DEFAULT_RANK_DIR
    if rank_id is not None:
        rank_dir = CoreConst.RANK + str(rank_id)

    step_dir_list = os.listdir(dump_path)
    for step_dir in step_dir_list:
        step_path = os.path.join(dump_path, step_dir)
        rank_path = os.path.join(step_path, rank_dir)
        npy_path = os.path.join(rank_path, CoreConst.DUMP_TENSOR_DATA)
        check_times = 0
        while True:
            is_finished, is_downloading = is_download_finished(npy_path)
            if not is_finished:
                if not is_downloading:
                    logger.warning(f'{npy_path} does not exist.')
                    break
                check_times += 1
                if check_times < 1000:
                    logger.info("There is data being downloaded in the specified directory, continue checking...")
                else:
                    logger.warning('Download timeout, stop checking.')
                    break
            else:
                logger.info("There is no data being downloaded in the specified directory, stop checking.")
                break
        logger.info("==========Start processing data that has already been stored on the disk!==========")
        rename_filename(path=npy_path)
        generate_construct(npy_path)
        generate_dump_info(npy_path)
        generate_stack_info(npy_path)
        # 单卡场景，rank目录名称为rank
        if rank_id is None:
            new_rank_path = os.path.join(step_path, CoreConst.RANK)
            try:
                move_directory(rank_path, new_rank_path)
                logger.debug(f"Directory was successfully renamed to: {new_rank_path}")
            except Exception as e:
                logger.warning(f"Failed to renamed to {new_rank_path}: {e}")
        logger.info("==========JSON file generation completed!==========")


# 删除csv文件中每行数据最后面的逗号
def remove_trailing_commas(filename):
    csv_data = read_csv(filename, as_pd=False)
    for i in range(1, len(csv_data)):
        if csv_data[i] and csv_data[i][-1] == "":
            csv_data[i].pop()
    write_csv(csv_data, filename, mode="w")


# 将相同step的csv文件合并，并加工后存入相应step目录下
def merge_file(dump_path, rank_dir, file_dict):
    rank_dir = rank_dir.replace(CoreConst.REPLACEMENT_CHARACTER, '')
    for step_dir, file_list in file_dict.items():
        step_dir = CoreConst.STEP + step_dir
        rank_path = os.path.join(dump_path, step_dir, rank_dir)
        create_directory(rank_path)
        output_file = os.path.join(rank_path, KEY_STATISTIC_CSV)

        all_dfs = []
        try:
            for file_path in file_list:
                remove_trailing_commas(file_path)
                df = read_csv(file_path)
                all_dfs.append(df)

            # 合并所有 DataFrame
            merged_df = pd.concat(all_dfs, ignore_index=True)
          
            # 按 Timestamp 字段升序排序
            merged_df = merged_df.sort_values(by='Timestamp', ascending=True)
            # 删除Slot字段为0的数据
            merged_df = merged_df[merged_df['Slot'] != 0]
            # 重置索引，从0开始排序
            merged_df.reset_index(drop=True, inplace=True)

            # 获取op_name并加工为Cell.network._backbone.LlamaForCausalLM.forward.input.0格式
            merged_df[CoreConst.OP_NAME] = merged_df[CoreConst.OP_NAME].str.split(KEY_DUMP_TENSOR_DATA, expand=True)[1]
            merged_df[CoreConst.OP_NAME] = (
                merged_df[CoreConst.OP_NAME].str.split(CoreConst.PIPE_SEPARATOR, expand=True)[0]
            )
            merged_df[CoreConst.OP_NAME] = (
                merged_df[CoreConst.OP_NAME].str.replace(CoreConst.HYPHEN, CoreConst.SEP, regex=False)
            )
            # 重命名op_name，改为Cell.{cell_name}.{class_name}.{forward/backward}.{number}.{input/output}.{index}格式
            rename_filename(data_df=merged_df)

            # 将合并并排序后的 DataFrame 保存到相应step目录下
            write_df_to_csv(merged_df, output_file)
        except FileNotFoundError:
            logger.error("One or more files not found.")
        except KeyError:
            logger.error("The value of the ‘Op Name’ field does not contain KEY_DUMP_TENSOR_DATA,"
                         " and the index is out of bounds.")
        except Exception as e:
            logger.error(f"An error occurred:{e}")


def process_statistics(dump_path):
    rank_id = os.environ.get('RANK_ID')
    rank_dir_kbk = "rank_0"
    if rank_id is not None:
        rank_dir_kbk = CoreConst.RANK + CoreConst.REPLACEMENT_CHARACTER + str(rank_id)
    rank_path_kbk = os.path.join(dump_path, rank_dir_kbk)

    # 按相同step数将csv文件名分组存入file_dict
    file_dict = {}
    depth_limit = 4
    base_depth = rank_path_kbk.count(os.sep)
    for root, _, files in os.walk(rank_path_kbk):
        current_depth = root.count(os.sep) - base_depth
        if current_depth > depth_limit:
            continue
        for file in files:
            if file == KEY_STATISTIC_CSV:
                file_path = os.path.join(root, file)
                step_dir = os.path.basename(os.path.dirname(file_path))
                if step_dir in file_dict:
                    file_dict[step_dir].append(file_path)
                else:
                    file_dict[step_dir] = [file_path]

    # 将相同step的csv文件合并，并加工后存入相应step目录下
    merge_file(dump_path, rank_dir_kbk, file_dict)

    rank_dir = rank_dir_kbk.replace(CoreConst.REPLACEMENT_CHARACTER, '')
    dir_list = os.listdir(dump_path)
    step_dir_list = [d for d in dir_list if d.startswith(CoreConst.STEP)]
    for step_dir in step_dir_list:
        step_path = os.path.join(dump_path, step_dir)
        rank_path = os.path.join(step_path, rank_dir)
        csv_path = os.path.join(rank_path, KEY_STATISTIC_CSV)
        logger.info("==========Start processing data csv!==========")
        generate_construct(csv_path)
        generate_dump_info(csv_path)
        generate_stack_info(csv_path)
        remove_path(rank_path_kbk)
        # 单卡场景，rank目录名称为rank
        if rank_id is None:
            new_rank_path = os.path.join(step_path, CoreConst.RANK)
            try:
                move_directory(rank_path, new_rank_path)
                logger.info(f"Directory was successfully renamed to: {new_rank_path}")
            except Exception as e:
                logger.warning(f"Failed to renamed to {new_rank_path}: {e}")
        logger.info("==========JSON file generation completed!==========")


def get_yaml_keys(yaml_data):
    keys = []
    for key, _ in yaml_data.items():
        keys.append(key)
    return keys


def get_tensordump_mode(input_str):
    left_index = input_str.find('(')
    right_index = input_str.find(')')

    # 提取括号内的字符串
    if left_index != -1 and right_index != -1:
        inner_str = input_str[left_index + 1:right_index]
        # 分割字符串得到元素列表
        elements = inner_str.split(',')
        if len(elements) >= 2:
            # 去除元素前后的空格
            first_element = elements[0].strip()
            second_element = elements[1].strip()
            return first_element, second_element
    return None, None


def set_tensordump_mode(cell, input_str):
    first_str, second_str = get_tensordump_mode(input_str)
    if first_str and second_str:
        cell.input_dump_mode = first_str
        cell.output_dump_mode = second_str


def create_kbyk_json(dump_path, summary_mode, step):
    if step:
        step_str = ""
        for s in step:
            step_str += (str(s) + '|')
        iteration = step_str[:-1]
    else:
        iteration = "all"

    if summary_mode == "statistics":
        statistic_category = ["max", "min", "avg", "l2norm"]
    elif "mean" in summary_mode:
        mean_index = summary_mode.index("mean")
        summary_mode[mean_index] = "avg"
        statistic_category = summary_mode
    else:
        statistic_category = summary_mode

    config_json = {
        "common_dump_settings": {
            "op_debug_mode": 0,
            "dump_mode": 1,
            "path": dump_path,
            "net_name": "Net",
            "iteration": iteration,
            "saved_data": "statistic",
            "input_output": 0,
            "kernels": ["TensorDump"],
            "support_device": [0, 1, 2, 3, 4, 5, 6, 7],
            "statistic_category": statistic_category
        },
        "e2e_dump_settings": {
            "enable": False,
            "trans_flag": True,
            "stat_calc_mode": "device"
        }
    }

    create_directory(dump_path)
    rank_id = os.environ.get('RANK_ID')
    if rank_id is None:
        rank_id = 0
    config_json_path = os.path.join(dump_path, str(rank_id) + "kernel_kbyk_dump.json")
    save_json(config_json_path, config_json, indent=4)
    logger.info(config_json_path + " has been created.")
    return config_json_path


def start(config: CellDumpConfig):
    global dump_task
    dump_task = config.task
    net = config.net
    dump_path = config.dump_path
    data_mode = config.data_mode
    summary_mode = config.summary_mode
    step = config.step
    if dump_task == CoreConst.STATISTICS:
        # 使能KBK dump
        config_json_path = create_kbyk_json(dump_path, summary_mode, step)
        os.environ["MINDSPORE_DUMP_CONFIG"] = config_json_path

        # 执行过程中跳过TensorDump算子
        os.environ["MS_KERNEL_LAUNCH_SKIP"] = "TensorDump"

        # 初始化静态图KBK dump的step数，从0开始
        if not graph_step_flag:
            raise Exception(
                "Importing _set_init_iter failed, "
                "please use the latest version package of MindSpore."
            )
        _set_init_iter(0)
        remove_path(config_json_path)

    if net is None:
        return

    if isinstance(net, nn.Cell):
        net = (('', net),)

    td_config_path = ""
    try:
        import mindformers
        mindformers_file = mindformers.__file__
        mindformers_dir = os.path.dirname(mindformers_file)
        td_config_path = os.path.join(mindformers_dir, "configuration", "layer_mapping.yaml")
        if not os.path.exists(td_config_path):
            td_config_path = ""
            logger.warning("The configuration file in mindformers was not loaded, the default mode will be used.")
    except ImportError:
        logger.warning("The mindFormers failed to load, the default mode will be used.")

    if td_config_path == "":
        yaml_data = {}
    else:
        yaml_data = load_yaml(td_config_path)
    first_layer_key = get_yaml_keys(yaml_data)

    black_list = ["grad_reducer", ""]

    for name_and_model in net:
        for name, cell in name_and_model[1].cells_and_names(name_prefix=name_and_model[0]):
            class_name = cell.__class__.__name__
            # 跳过黑名单cell
            if name in black_list:
                logger.info(f"Cell {name}.{class_name} is skipped!")
                continue
            # 跳过框架内部的cell
            if class_name.startswith(CoreConst.REPLACEMENT_CHARACTER):
                logger.info(f"Cell {name}.{class_name} is skipped!")
                continue
            else:
                # Format: Cell.{cell_name}.{class_name}
                cell.cell_prefix = CoreConst.SEP.join([CoreConst.CELL, name, cell.__class__.__name__])
                if dump_task == CoreConst.STATISTICS:
                    cell.cell_prefix = cell.cell_prefix.replace(CoreConst.SEP, CoreConst.HYPHEN)

            # 根据yaml配置文件设置cell的TensorDump模式
            if class_name in first_layer_key:
                layer_data = yaml_data.get(class_name)
                if layer_data:
                    for child_name, child_cell in cell.cells_and_names():
                        if child_name in layer_data:
                            set_tensordump_mode(child_cell, layer_data[child_name])
            top_layer_data = yaml_data.get(KEY_TOPLAYER)
            if top_layer_data and name in top_layer_data:
                set_tensordump_mode(cell, top_layer_data[name])

            # 替换construct函数
            cell.construct = cell_construct_wrapper(cell.construct, cell)
            logger.info(f"Cell {name}: construct function is wrapped!")
            cell.dump_path = dump_path
            cell.data_mode = data_mode
            cell.input_clips = []
            cell.output_clips = []
            # It is assumed that each cell has a maximum of 50 outputs and 50 inputs.
            for i in range(50):
                cell.input_clips.append(
                    ops.InsertGradientOf(partial_func(clip_gradient, cell.dump_path, cell.cell_prefix, i, KEY_INPUT))
                )
                cell.output_clips.append(
                    ops.InsertGradientOf(partial_func(clip_gradient, cell.dump_path, cell.cell_prefix, i, KEY_OUTPUT))
                )

    logger.info("==========The cell_dump_process_start phase is Finished!==========")
    if dump_task == CoreConst.TENSOR:
        atexit.register(process, dump_path=dump_path)
    if dump_task == CoreConst.STATISTICS:
        atexit.register(process_statistics, dump_path=dump_path)
