# Copyright (c) 2024 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys
from typing import TYPE_CHECKING

from ..utils.lazy_import import _LazyModule

import_structure = {
    "merge_model": ["save_file", "device_guard", "divide_lora_key_list", "divide_positions", "MergeModel"],
    "merge_method": ["MergeMethod"],
    "sparsify_method": ["SparsifyMethod"],
    "merge_utils": ["divide_positions", "divide_lora_key_list", "divide_safetensor_key_list"],
    "merge_config": ["MergeConfig"],
}

if TYPE_CHECKING:
    from .merge_config import *
    from .merge_method import *
    from .merge_model import *
    from .merge_utils import *
    from .sparsify_method import *
else:
    sys.modules[__name__] = _LazyModule(
        __name__,
        globals()["__file__"],
        import_structure,
        module_spec=__spec__,
    )
