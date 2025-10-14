"""
Schema definitions for Departments-related data structures in Loket API.

This module contains Pandera schemas for GET operations and Pydantic schemas for CREATE/UPDATE operations
related to employer departments.
"""

from typing import Optional, Dict, Any, Set
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithStringKey


class DepartmentGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Department data returned from Loket API.
    A Department represents a department of an employer in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the department", alias="id")
    code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The code of the department", alias="code")
    description: Series[str] = pa.Field(coerce=True, description="The description of the department", alias="description")
    sub_department_of: Optional[Series[str]] = pa.Field(coerce=True, description="Sub department object", alias="subDepartmentOf", nullable=True)
    sub_department_of_key: Optional[Series[str]] = pa.Field(coerce=True, description="Sub department key", alias="subDepartmentOf.key", nullable=True)
    sub_department_of_code: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, description="Sub department code", alias="subDepartmentOf.code", nullable=True)
    sub_department_of_description: Optional[Series[str]] = pa.Field(coerce=True, description="Sub department description", alias="subDepartmentOf.description", nullable=True)
    email_leave_request: Series[str] = pa.Field(coerce=True, description="Email for leave requests", alias="emailLeaveRequest", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


# Prefix → target alias (nested object name)
PREFIX_MAP: Dict[str, str] = {
    # No prefixes for departments, only root level metadata fields
}

# Root level fields expecting MetadataWithStringKey (snake_case)
ROOT_METADATA_FIELDS: Set[str] = {
    "sub_department_of",
}

# Nested level fields expecting MetadataWithStringKey (prefix → field set)
NESTED_METADATA_FIELDS: Dict[str, Set[str]] = {
    # No nested metadata fields for departments
}


class DepartmentCreate(BaseModel):
    """Schema for creating/updating a department."""
    code: int = Field(..., description="Code of the department", example=1001)
    description: str = Field(..., description="Description of the department", example="Engineering", max_length=200)
    sub_department_of: Optional[MetadataWithStringKey] = Field(None, alias="subDepartmentOf", description="Sub department information")
    email_leave_request: Optional[str] = Field(None, alias="emailLeaveRequest", description="Email for leave requests", max_length=100)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function from brynq_sdk_functions.
        """
        return flat_to_nested_with_metadata(
            values=values,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )


class DepartmentUpdate(BaseModel):
    """Schema for updating a department (without code field)."""
    description: str = Field(..., description="Description of the department", example="Engineering", max_length=200)
    sub_department_of: Optional[MetadataWithStringKey] = Field(None, alias="subDepartmentOf", description="Sub department information")
    email_leave_request: Optional[str] = Field(None, alias="emailLeaveRequest", description="Email for leave requests", example="hr@company.com", max_length=100)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function from brynq_sdk_functions.
        """
        return flat_to_nested_with_metadata(
            values=values,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )
