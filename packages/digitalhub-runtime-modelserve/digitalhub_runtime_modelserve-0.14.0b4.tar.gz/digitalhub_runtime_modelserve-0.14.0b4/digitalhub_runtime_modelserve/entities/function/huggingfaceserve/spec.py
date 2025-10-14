# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from pydantic import Field

from digitalhub_runtime_modelserve.entities.function.modelserve.spec import (
    FunctionSpecModelserve,
    FunctionValidatorModelserve,
)

path_regex = (
    r"^(store://([^/]+)/model/huggingface/.*)"
    + r"|"
    + r".*\\/$"
    + r"|"
    + r".*\\.zip$"
    + r"|"
    + r"^huggingface?://.*$"
    + r"|"
    + r"^hf?://.*$"
)

image_regex = r"^kserve\\/huggingfaceserver?:"


class FunctionSpecHuggingfaceserve(FunctionSpecModelserve):
    """
    FunctionSpecHuggingfaceserve specifications.
    """


class FunctionValidatorHuggingfaceserve(FunctionValidatorModelserve):
    """
    FunctionValidatorHuggingfaceserve validator.
    """

    path: Optional[str] = Field(default=None, pattern=path_regex)
    "Path to the model files"

    image: Optional[str] = Field(default=None, pattern=image_regex)
    "Function image"
