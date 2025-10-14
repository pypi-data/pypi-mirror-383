# Copyright (c) 2025 PaddlePaddle Authors. All Rights Reserved.
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
from contextlib import suppress
from typing import TYPE_CHECKING

from ...utils.lazy_import import _LazyModule

import_structure = {
    "eager_attention": ["eager_attention_forward"],
    "flashmask_attention": ["flashmask_attention_forward"],
    "interface": ["AttentionInterface", "ALL_ATTENTION_FUNCTIONS"],
    "sdpa_attention": ["sdpa_attention_forward"],
    "utils": ["repeat_kv"],
    "sink_impl": ["sink_attention_forward"],
}

if TYPE_CHECKING:
    from .eager_attention import *
    from .flashmask_attention import *
    from .interface import *
    from .sdpa_attention import *
    from .sink_impl import *
    from .utils import *
else:
    sys.modules[__name__] = _LazyModule(
        __name__,
        globals()["__file__"],
        import_structure,
        module_spec=__spec__,
    )
