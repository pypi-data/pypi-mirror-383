"""
Schema definitions for Functions-related data structures in Loket API.

This module contains Pandera schemas for GET operations and Pydantic schemas for CREATE/UPDATE operations
related to employer functions.
"""

from typing import Optional, Dict, Any
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel


class FunctionGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Function data returned from Loket API.
    A Function represents a function/position of an employer in the Loket system.
    """
    key: Series[str] = pa.Field(coerce=True, description="The unique identifier of the function", alias="key")
    description: Series[str] = pa.Field(coerce=True, description="The description of the function", alias="description")
    group: Series[str] = pa.Field(coerce=True, description="The group of the function", alias="group", nullable=True)

    class _Annotation:
        primary_key = "key"

    class Config:
        coerce = True
        strict = False


class FunctionCreate(BaseModel):
    """Schema for creating/updating a function."""
    description: str = Field(..., description="Description of the function", example="Software Developer", max_length=200)
    group: str = Field(..., description="Group of the function", example="IT", max_length=100)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
