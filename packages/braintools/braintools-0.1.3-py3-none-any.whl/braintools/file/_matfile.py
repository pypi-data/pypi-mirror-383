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

from typing import Any, Dict

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab import mio5_params

__all__ = [
    'load_matfile',
]


def load_matfile(
    filename: str,
    header_info: bool = True,
    struct_as_record=False,
    squeeze_me=True,
    **kwargs
) -> Dict:
    """
    A simple function to load a .mat file using scipy from Python.
    It uses a recursive approach for parsing properly Matlab' objects.

    Parameters
    ----------
    filename : str
        The path to the .mat file to be loaded.
    header_info : bool, optional
        Whether to include the header information, by default True.
    struct_as_record : bool, optional
        Whether to load Matlab structs as numpy record arrays, by default False.
    squeeze_me : bool, optional
        Whether to squeeze unit matrix dimensions, by default True.

    Returns
    -------
    dict
        A dictionary with the content of the .mat file.
    """

    def parse_mat(element: Any):
        # lists (1D cell arrays usually) or numpy arrays as well
        if element.__class__ == np.ndarray and element.dtype == np.object_ and len(element.shape) > 0:
            return [parse_mat(entry) for entry in element]

        # matlab struct
        if element.__class__ == mio5_params.mat_struct:
            return {fn: parse_mat(getattr(element, fn)) for fn in element._fieldnames}

        # regular numeric matrix, or a scalar
        return element

    mat = loadmat(filename, struct_as_record=struct_as_record, squeeze_me=squeeze_me, **kwargs)
    dict_output = dict()

    for key, value in mat.items():
        if header_info:
            # not considering the '__header__', '__version__', '__globals__'
            if not key.startswith('__'):
                dict_output[key] = parse_mat(mat[key])
        else:
            dict_output[key] = parse_mat(mat[key])
    return dict_output
