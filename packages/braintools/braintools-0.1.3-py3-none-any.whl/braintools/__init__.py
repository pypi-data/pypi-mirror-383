# Copyright 2024 BrainX Ecosystem Limited. All Rights Reserved.
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
# ==============================================================================


__version__ = "0.1.3"
__version_info__ = (0, 1, 3)

from . import conn
from . import file
from . import init
from . import input
from . import metric
from . import optim
from . import quad
from . import surrogate
from . import tree
from . import visualize
from ._spike_encoder import *
from ._spike_encoder import __all__ as encoder_all
from ._spike_operation import *
from ._spike_operation import __all__ as operation_all
from ._transform import *
from ._transform import __all__ as transform_all

__all__ = [
    'conn', 'input', 'init',
    'file', 'metric', 'visualize',
    'optim', 'tree', 'quad',
    'surrogate',
]
__all__ = __all__ + encoder_all + transform_all + operation_all

del encoder_all, transform_all, operation_all
