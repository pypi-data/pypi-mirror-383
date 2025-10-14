"""
Schema definitions for Leave Type data structures in Loket API.
"""

from typing import Optional, Dict, Any
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field

from brynq_sdk_functions import BrynQPanderaDataFrameModel


class LeaveTypeGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Leave Type data returned from Loket API.
    """
    id: Series[str] = pa.Field(coerce=True, alias="id")

    # Leave type fields
    leave_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, alias="leaveType.key", nullable=True)
    leave_type_value: Series[str] = pa.Field(coerce=True, alias="leaveType.value", nullable=True)
    leave_type_balance_exceeds_year: Series[bool] = pa.Field(coerce=True, alias="leaveType.balanceExceedsYear", nullable=True)
    leave_type_enabled: Series[bool] = pa.Field(coerce=True, alias="leaveType.enabled", nullable=True)
    leave_type_employee_can_request_increase: Series[bool] = pa.Field(coerce=True, alias="leaveType.employeeCanRequestIncrease", nullable=True)

    # Deviations fields - Optional since deviations can be null
    deviations_value: Optional[Series[str]] = pa.Field(coerce=True, alias="deviations.value", nullable=True)
    deviations_balance_exceeds_year: Optional[Series[bool]] = pa.Field(coerce=True, alias="deviations.balanceExceedsYear", nullable=True)
    deviations_enabled: Optional[Series[bool]] = pa.Field(coerce=True, alias="deviations.enabled", nullable=True)
    deviations_employee_can_request_increase: Optional[Series[bool]] = pa.Field(coerce=True, alias="deviations.employeeCanRequestIncrease", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


class LeaveTypeUpdate(BaseModel):
    """Schema for updating a leave type."""
    value: Optional[str] = Field(None, description="Deviations value", example="Annual Leave", alias="value")
    balance_exceeds_year: Optional[bool] = Field(None, description="Deviations balance exceeds year", example=False, alias="balanceExceedsYear")
    enabled: Optional[bool] = Field(None, description="Deviations enabled", example=True, alias="enabled")
    employee_can_request_increase: Optional[bool] = Field(None, description="Deviations employee can request increase", example=True, alias="employeeCanRequestIncrease")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
