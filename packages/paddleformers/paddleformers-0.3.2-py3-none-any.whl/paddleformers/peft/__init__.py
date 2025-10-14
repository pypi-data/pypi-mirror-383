# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
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
    "lokr": ["LoKrConfig", "LoKrModel"],
    "lora": ["LoRAAutoConfig", "LoRAAutoModel", "LoRAConfig", "LoRAModel"],
    "prefix": ["PrefixConfig", "PrefixModelForCausalLM"],
    "reft": ["ReFTModel"],
    "vera": ["VeRAConfig", "VeRAModel"],
}

if TYPE_CHECKING:
    from .lokr import LoKrConfig, LoKrModel
    from .lora import LoRAAutoConfig, LoRAAutoModel, LoRAConfig, LoRAModel
    from .prefix import PrefixConfig, PrefixModelForCausalLM
    from .reft import ReFTModel
    from .vera import VeRAConfig, VeRAModel
else:
    sys.modules[__name__] = _LazyModule(
        __name__,
        globals()["__file__"],
        import_structure,
        module_spec=__spec__,
    )
