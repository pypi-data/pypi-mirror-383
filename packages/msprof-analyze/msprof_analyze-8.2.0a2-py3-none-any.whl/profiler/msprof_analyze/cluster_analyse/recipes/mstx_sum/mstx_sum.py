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
from collections import namedtuple

import os
import pandas as pd

from msprof_analyze.cluster_analyse.common_func.utils import describe_duration
from msprof_analyze.cluster_analyse.recipes.base_recipe_analysis import BaseRecipeAnalysis
from msprof_analyze.prof_common.constant import Constant
from msprof_analyze.prof_common.logger import get_logger
from msprof_analyze.prof_exports.mstx_event_export import MstxMarkExport, MstxRangeExport
from msprof_analyze.prof_exports.mstx_step_export import MstxStepExport

logger = get_logger()

MarkInfo = namedtuple("MarkInfo", ["name", "framework_duration", "cann_duration", "device_duration",
                                   "tid", "start_ns"])


def format_mark_info(df: pd.DataFrame, start_idx, stop_idx, name) -> MarkInfo:
    start_series = df.iloc[start_idx]
    stop_series = df.iloc[stop_idx]
    return MarkInfo(
        name=name,
        framework_duration=float(stop_series["framework_ts"] - start_series["framework_ts"]),
        cann_duration=float(stop_series["cann_ts"] - start_series["cann_ts"]),
        device_duration=float(stop_series["device_ts"] - start_series["device_ts"]),
        tid=start_series["tid"],
        start_ns=start_series["cann_ts"]
    )


def format_range_info(df: pd.DataFrame, idx, name) -> MarkInfo:
    range_series = df.iloc[idx]
    return MarkInfo(
        name=name,
        framework_duration=float(0),
        cann_duration=float(range_series["cann_end_ts"] - range_series["cann_start_ts"]),
        device_duration=float(range_series["device_end_ts"] - range_series["device_start_ts"]),
        tid=range_series["tid"],
        start_ns=range_series["cann_start_ts"]
    )


def rename_mark_msg_name(mstx_stats_df: pd.DataFrame):
    msg_idx_counter = {}
    for idx, mark_info in enumerate(mstx_stats_df.itertuples(index=False)):
        msg_idx_counter.setdefault(mark_info.step_id, {}).setdefault(mark_info.name, []).append(idx)
    for msg_dict in msg_idx_counter.values():
        for msg, idx_list in msg_dict.items():
            if len(idx_list) <= 1:
                continue
            for i, idx in enumerate(idx_list):
                mstx_stats_df.loc[idx, 'name'] = f"{msg}_{i}"


def compute_step_id(mark_stat, step_stats_df: pd.DataFrame):
    for step_info in step_stats_df.itertuples(index=False):
        if step_info.start_ns <= mark_stat.start_ns <= step_info.end_ns:
            return step_info.step_id
    logger.warning(f"{mark_stat.name} is not in any step.")
    return 0


def format_columns(df: pd.DataFrame):
    formatted_df = df.rename(
        {
            "framework_duration": "FrameworkDurationNs",
            "cann_duration": "CannDurationNs",
            "device_duration": "DeviceDurationNs",
            "duration": "DurationNs",
            "step_id": "StepId",
            "tid": "Tid",
            "name": "Name"
        },
        axis="columns"
    )
    cols = [col for col in formatted_df.columns if not col.endswith("_ns") and col not in {"Tid"}]
    return formatted_df[cols]


def handle_mark_data(mark_df: pd.DataFrame, rank_id: int) -> list:
    res = []
    mark_df["framework_ts"] = mark_df["framework_ts"].astype("int64")
    mark_info = {}
    mismatch_msg = []
    for idx, row in enumerate(mark_df.itertuples(index=False)):
        if row.msg.endswith(MstxSum.START_SUFFIX):
            msg = row.msg[:-len(MstxSum.START_SUFFIX)]
            mark_info.setdefault(row.tid, {}).setdefault(msg, []).append(idx)
        elif row.msg.endswith(MstxSum.STOP_SUFFIX):
            msg = row.msg[:-len(MstxSum.STOP_SUFFIX)]
            idx_list = mark_info.get(row.tid, {}).get(msg, [])
            if not idx_list:
                mismatch_msg.append((row.msg, idx))
                continue
            start_idx = idx_list.pop()
            res.append(format_mark_info(mark_df, start_idx, idx, msg))

    # 统计未匹配上的mark信息
    for msg_info in mark_info.values():
        for msg, idx_list in msg_info.items():
            if not idx_list:
                continue
            mismatch_msg.extend((msg + MstxSum.START_SUFFIX, idx) for idx in idx_list)
    if mismatch_msg:
        mismatch_msg.sort(key=lambda msg: msg[1])
        logger.warning(f"The following mark messages do not match anyone in "
                       f"rank {rank_id}: {','.join(msg[0] for msg in mismatch_msg)}.")

    return res


def handle_range_data(range_df: pd.DataFrame) -> list:
    res = []
    for idx, row in enumerate(range_df.itertuples(index=False)):
        res.append(format_range_info(range_df, idx, row.msg))
    return res


class MstxSum(BaseRecipeAnalysis):
    TABLE_FRAMEWORK_STATS = "MSTXAllFrameworkStats"
    TABLE_CANN_STATS = "MSTXAllCannStats"
    TABLE_DEVICE_STATS = "MSTXAllDeviceStats"
    TABLE_MARK_STATS = "MSTXMarkStats"

    START_SUFFIX = "_start"
    STOP_SUFFIX = "_stop"

    def __init__(self, params):
        super().__init__(params)
        logger.info("MstxSum init.")
        self.mark_stats = None
        self.all_fwk_stats = None
        self.all_cann_stats = None
        self.all_device_stats = None

    @property
    def base_dir(self):
        return os.path.basename(os.path.dirname(__file__))

    def reducer_func(self, mapper_res):
        mapper_res = list(filter(lambda df: df is not None, mapper_res))
        if not mapper_res:
            logger.error("Mapper data is None.")
            return
        self.mark_stats = pd.concat(mapper_res)
        all_fwk_stats = []
        all_cann_stats = []
        all_device_stats = []
        mark_step_df = self.mark_stats.groupby("StepId")
        for step_id, df in mark_step_df:
            name_gdf = df.groupby("Name")
            fwk_stats = describe_duration(name_gdf["FrameworkDurationNs"]).assign(StepId=step_id)
            fwk_stats.sort_values(by=["SumNs"], inplace=True, ascending=False)
            all_fwk_stats.append(fwk_stats)
            cann_stats = describe_duration(name_gdf["CannDurationNs"]).assign(StepId=step_id)
            cann_stats.sort_values(by=["SumNs"], inplace=True, ascending=False)
            all_cann_stats.append(cann_stats)
            device_stats = describe_duration(name_gdf["DeviceDurationNs"]).assign(StepId=step_id)
            device_stats.sort_values(by=["SumNs"], inplace=True, ascending=False)
            all_device_stats.append(device_stats)
        self.all_fwk_stats = pd.concat(all_fwk_stats)
        self.all_cann_stats = pd.concat(all_cann_stats)
        self.all_device_stats = pd.concat(all_device_stats)

    def run(self, context):
        mapper_res = self.mapper_func(context)
        self.reducer_func(mapper_res)

        if self._export_type == "db":
            self.save_db()
        elif self._export_type == "notebook":
            self.save_notebook()
        else:
            logger.error("Unknown export type.")

    def save_notebook(self):
        self.dump_data(self.mark_stats, "mark_stats.csv")
        self.dump_data(self.all_fwk_stats, "all_fwk_stats.csv")
        self.dump_data(self.all_cann_stats, "all_cann_stats.csv")
        self.dump_data(self.all_device_stats, "all_device_stats.csv")
        self.create_notebook("stats.ipynb")
        self.add_helper_file("cluster_display.py")

    def save_db(self):
        self.dump_data(self.mark_stats, Constant.DB_CLUSTER_COMMUNICATION_ANALYZER, self.TABLE_MARK_STATS)
        self.dump_data(self.all_fwk_stats, Constant.DB_CLUSTER_COMMUNICATION_ANALYZER, self.TABLE_FRAMEWORK_STATS)
        self.dump_data(self.all_cann_stats, Constant.DB_CLUSTER_COMMUNICATION_ANALYZER, self.TABLE_CANN_STATS)
        self.dump_data(self.all_device_stats, Constant.DB_CLUSTER_COMMUNICATION_ANALYZER, self.TABLE_DEVICE_STATS)

    def _mapper_func(self, data_map, analysis_class):
        profiler_db_path = data_map.get(Constant.PROFILER_DB_PATH)
        rank_id = data_map.get(Constant.RANK_ID)
        step_range = data_map.get(Constant.STEP_RANGE)
        step_df = MstxStepExport(profiler_db_path, analysis_class, step_range).read_export_db()
        if step_df is None or step_df.empty:
            step_df = pd.DataFrame({"start_ns": [0], "end_ns": [float("inf")], "step_id": [0]})
        mark_df = MstxMarkExport(profiler_db_path, analysis_class, step_range).read_export_db()
        range_df = MstxRangeExport(profiler_db_path, analysis_class, step_range).read_export_db()
        mstx_res = []
        if not mark_df.empty:
            mstx_res += handle_mark_data(mark_df, rank_id)
        if not range_df.empty:
            mstx_res += handle_range_data(range_df)
        if not mstx_res:
            logger.warning(f"There is no mstx data in {profiler_db_path}.")
            return None

        mstx_stats_df = pd.DataFrame(mstx_res).assign(Rank=rank_id)
        mstx_stats_df["step_id"] = mstx_stats_df.apply(compute_step_id, axis=1, step_stats_df=step_df)
        rename_mark_msg_name(mstx_stats_df)
        mstx_stats_df = format_columns(mstx_stats_df).set_index("Name", drop=True)
        return mstx_stats_df
