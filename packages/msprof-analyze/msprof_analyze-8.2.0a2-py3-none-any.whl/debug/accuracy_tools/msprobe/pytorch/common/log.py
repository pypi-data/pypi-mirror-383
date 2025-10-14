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

from msprobe.core.common.exceptions import DistributedNotInitializedError
from msprobe.core.common.log import BaseLogger
from msprobe.pytorch.common.utils import get_rank_if_initialized


class PyTorchLogger(BaseLogger):
    def __init__(self):
        super().__init__()

    def get_rank(self):
        try:
            current_rank = get_rank_if_initialized()
        except DistributedNotInitializedError:
            current_rank = None
        return current_rank


logger = PyTorchLogger()
