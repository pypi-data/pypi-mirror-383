"""
Schema definitions for Leave-related data structures in Loket API.

This module contains Pandera schemas for GET operations related to employment leave.
"""

from typing import Optional, Dict, Any, Set
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey


class LeaveGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Leave data returned from Loket API.
    A Leave represents leave information for an employment in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the leave", alias="id")
    number_of_units: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Number of units", alias="numberOfUnits", nullable=True)

    # Unit type fields
    unit_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Unit type key", alias="unitType.key", nullable=True)
    unit_type_value: Series[str] = pa.Field(coerce=True, description="Unit type value", alias="unitType.value", nullable=True)

    # Leave type fields
    is_accrual: Series[bool] = pa.Field(coerce=True, description="Is accrual", alias="isAccrual", nullable=True)
    start_date: Series[str] = pa.Field(coerce=True, description="Start date", alias="startDate", nullable=True)
    end_date: Series[str] = pa.Field(coerce=True, description="End date", alias="endDate", nullable=True)

    # Leave type fields
    leave_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Leave type key", alias="leaveType.key", nullable=True)
    leave_type_value: Series[str] = pa.Field(coerce=True, description="Leave type value", alias="leaveType.value", nullable=True)
    leave_type_balance_exceeds_year: Series[bool] = pa.Field(coerce=True, description="Leave type balance exceeds year", alias="leaveType.balanceExceedsYear", nullable=True)

    # Origin fields
    origin_leave_policy_id: Series[str] = pa.Field(coerce=True, description="Origin leave policy ID", alias="origin.leavePolicy.id", nullable=True)
    origin_leave_policy_value: Series[str] = pa.Field(coerce=True, description="Origin leave policy value", alias="origin.leavePolicy.value", nullable=True)
    origin_leave_policy_leave_unit_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Origin leave policy leave unit type key", alias="origin.leavePolicy.leaveUnitType.key", nullable=True)
    origin_leave_policy_leave_unit_type_value: Series[str] = pa.Field(coerce=True, description="Origin leave policy leave unit type value", alias="origin.leavePolicy.leaveUnitType.value", nullable=True)
    origin_leave_policy_accrual_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Origin leave policy accrual type key", alias="origin.leavePolicy.accrualType.key", nullable=True)
    origin_leave_policy_accrual_type_value: Series[str] = pa.Field(coerce=True, description="Origin leave policy accrual type value", alias="origin.leavePolicy.accrualType.value", nullable=True)

    # Means of creation fields
    means_of_creation_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Means of creation key", alias="meansOfCreation.key", nullable=True)
    means_of_creation_value: Series[str] = pa.Field(coerce=True, description="Means of creation value", alias="meansOfCreation.value", nullable=True)

    # Additional fields
    comment: Series[str] = pa.Field(coerce=True, description="Comment", alias="comment", nullable=True)
    related_leave_request_id: Series[str] = pa.Field(coerce=True, description="Related leave request ID", alias="relatedLeaveRequest.id", nullable=True)
    related_leave_id: Series[str] = pa.Field(coerce=True, description="Related leave ID", alias="relatedLeave.id", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


class LeaveUpdate(BaseModel):
    """Schema for updating a leave."""
    number_of_units: Optional[float] = Field(None, alias="numberOfUnits", description="Number of units", example=8.0)
    is_accrual: Optional[bool] = Field(None, alias="isAccrual", description="Is accrual", example=True)
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date (YYYY-MM-DD)", example="2024-01-15")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date (YYYY-MM-DD)", example="2024-01-22")
    leave_type: Optional[MetadataWithKey] = Field(None, alias="leaveType", description="Leave type information")
    comment: Optional[str] = Field(None, description="Comment", example="Annual leave")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the shared helper.
        Supports leave_type_key → leaveType {"key": ...} and camelCase aliasing.
        """
        if not isinstance(values, dict):
            return values

        root_metadata_fields: Set[str] = {"leave_type"}

        return flat_to_nested_with_metadata(
            values=values,
            prefix_map={},
            root_metadata_fields=root_metadata_fields,
            nested_metadata_fields={}
        )


class LeaveImportDataGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Leave Import Data returned from Loket API.
    Leave Import Data represents leave data for import purposes.
    """
    employer_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employer number", alias="employerNumber", nullable=True)
    payroll_employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll employee number", alias="payrollEmployeeNumber", nullable=True)
    employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee number", alias="employeeNumber", nullable=True)
    formatted_name: Series[str] = pa.Field(coerce=True, description="Formatted name", alias="formattedName", nullable=True)
    start_date: Series[str] = pa.Field(coerce=True, description="Start date", alias="startDate", nullable=True)
    end_date: Series[str] = pa.Field(coerce=True, description="End date", alias="endDate", nullable=True)
    leave_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Leave type key", alias="leavetypekey", nullable=True)
    is_accrual: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Is accrual", alias="isAccrual", nullable=True)
    number_of_units: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Number of units", alias="numberOfUnits", nullable=True)
    batch_line_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Batch line number", alias="batchLineNumber", nullable=True)

    class _Annotation:
        primary_key = "employee_number"

    class Config:
        coerce = True
        strict = False


# ==================== BATCH LEAVE SCHEMAS ====================

class LeaveBatchCreate(BaseModel):
    """Schema for creating leave in batch for multiple employments."""
    employment_id: str = Field(..., alias="employmentId", description="The unique identifier of the employment", example="emp_123456")
    start_date: str = Field(..., alias="startDate", description="Start date of the leave (YYYY-MM-DD)", example="2024-01-15")
    end_date: str = Field(..., alias="endDate", description="End date of the leave (YYYY-MM-DD)", example="2024-01-22")
    leave_type_key: int = Field(..., alias="leaveTypeKey", description="Leave type key", example=1)
    is_accrual: bool = Field(..., alias="isAccrual", description="Whether this is an accrual leave", example=True)
    number_of_units: float = Field(..., alias="numberOfUnits", description="Number of units for the leave", example=8.0)
    comments: Optional[str] = Field(None, description="Comments for the leave", example="Annual leave request")

    class Config:
        validate_by_name = True
        validate_assignment = True
        extra = "ignore"
