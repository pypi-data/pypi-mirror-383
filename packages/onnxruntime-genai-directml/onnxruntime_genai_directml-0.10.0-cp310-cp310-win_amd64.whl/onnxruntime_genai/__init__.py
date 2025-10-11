# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License

from onnxruntime_genai import _dll_directory

__version__ = "0.10.0"
__id__ = "onnxruntime-genai-directml"

_dll_directory.add_onnxruntime_dependency(__id__)

try:
    from onnxruntime_genai.onnxruntime_genai import *
except ImportError as e:
    if __id__ == "onnxruntime-genai-cuda":
        # Try importing onnxruntime_genai. If an ImportError is raised,
        # it could be because the cuda dlls could not be found on windows.
        # Try adding the cuda dlls path to the dll search directory
        # and import onnxruntime_genai again.
        _dll_directory.add_cuda_dependency()
        from onnxruntime_genai.onnxruntime_genai import *
    else:
        raise e
