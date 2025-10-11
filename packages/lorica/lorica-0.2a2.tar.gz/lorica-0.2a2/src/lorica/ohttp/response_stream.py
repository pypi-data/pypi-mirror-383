# Copyright (c) 2025 Lorica Cybersecurity, Inc. All rights reserved.
# This software is proprietary and confidential. 
# Unauthorized copying of this file via any means is strictly prohibited.
# Lorica Cybersecurity Inc. support@loricacyber.com, May 2025

import importlib
import sys

MODULE_NAME = "ohttpy.response_stream"

# Dynamically import the external module
try:
    external_module = importlib.import_module(MODULE_NAME)
except ModuleNotFoundError:
    raise ImportError(f"Module '{MODULE_NAME}' is not found.")

# Expose all attributes from the external package
for attr_name in dir(external_module):
    if not attr_name.startswith("_"):  # Avoid private/internal attributes
        setattr(sys.modules[__name__], attr_name, getattr(external_module, attr_name))

# Cleanup namespace
del importlib, sys, attr_name, external_module
