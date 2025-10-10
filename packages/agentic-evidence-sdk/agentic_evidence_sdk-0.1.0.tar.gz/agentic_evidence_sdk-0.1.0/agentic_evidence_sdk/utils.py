# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rajeshwar Dhayalan and Contributors

from __future__ import annotations
from typing import Any, Dict

def _headers(api_key: str) -> Dict[str, str]:
    return {"X-API-Key": api_key, "Content-Type": "application/json"}