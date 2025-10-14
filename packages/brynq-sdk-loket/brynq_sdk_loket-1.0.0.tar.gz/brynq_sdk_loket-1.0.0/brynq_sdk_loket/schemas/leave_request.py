"""
Schema definitions for Leave Request data structures in Loket API.
"""

from typing import Optional, Dict, Any, Set
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey


class LeaveRequestGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Leave Request data returned from Loket API.
    """
    id: Series[str] = pa.Field(coerce=True, alias="id")
    number_of_units: Series[pd.Float64Dtype] = pa.Field(coerce=True, alias="numberOfUnits", nullable=True)

    # Unit type
    unit_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, alias="unitType.key", nullable=True)
    unit_type_value: Series[str] = pa.Field(coerce=True, alias="unitType.value", nullable=True)

    is_accrual: Series[bool] = pa.Field(coerce=True, alias="isAccrual", nullable=True)
    start_date: Series[str] = pa.Field(coerce=True, alias="startDate", nullable=True)
    end_date: Series[str] = pa.Field(coerce=True, alias="endDate", nullable=True)

    # Leave type
    leave_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, alias="leaveType.key", nullable=True)
    leave_type_value: Series[str] = pa.Field(coerce=True, alias="leaveType.value", nullable=True)

    # Status
    leave_request_status_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, alias="leaveRequestStatus.key", nullable=True)
    leave_request_status_value: Series[str] = pa.Field(coerce=True, alias="leaveRequestStatus.value", nullable=True)

    submitted_on: Series[str] = pa.Field(coerce=True, alias="submittedOn", nullable=True)

    # Submitted by (employee)
    submitted_by_id: Series[str] = pa.Field(coerce=True, alias="submittedBy.id", nullable=True)
    submitted_by_employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, alias="submittedBy.employeeNumber", nullable=True)
    submitted_by_first_name: Series[str] = pa.Field(coerce=True, alias="submittedBy.firstName", nullable=True)
    submitted_by_initials: Series[str] = pa.Field(coerce=True, alias="submittedBy.initials", nullable=True)
    submitted_by_prefix: Series[str] = pa.Field(coerce=True, alias="submittedBy.prefix", nullable=True)
    submitted_by_last_name: Series[str] = pa.Field(coerce=True, alias="submittedBy.lastName", nullable=True)
    submitted_by_prefix_partner: Series[str] = pa.Field(coerce=True, alias="submittedBy.prefixPartner", nullable=True)
    submitted_by_last_name_partner: Series[str] = pa.Field(coerce=True, alias="submittedBy.lastNamePartner", nullable=True)
    submitted_by_formatted_name: Series[str] = pa.Field(coerce=True, alias="submittedBy.formattedName", nullable=True)
    submitted_by_date_of_birth: Series[str] = pa.Field(coerce=True, alias="submittedBy.dateOfBirth", nullable=True)
    submitted_by_photo: Series[str] = pa.Field(coerce=True, alias="submittedBy.photo", nullable=True)

    handled_time: Series[str] = pa.Field(coerce=True, alias="handledTime", nullable=True)

    # Handled by (approver)
    handled_by_id: Series[str] = pa.Field(coerce=True, alias="handledBy.id", nullable=True)
    handled_by_initials: Series[str] = pa.Field(coerce=True, alias="handledBy.initials", nullable=True)
    handled_by_prefix: Series[str] = pa.Field(coerce=True, alias="handledBy.prefix", nullable=True)
    handled_by_last_name: Series[str] = pa.Field(coerce=True, alias="handledBy.lastName", nullable=True)
    handled_by_formatted_name: Series[str] = pa.Field(coerce=True, alias="handledBy.formattedName", nullable=True)

    comment_employee: Series[str] = pa.Field(coerce=True, alias="commentEmployee", nullable=True)
    comment_handler: Series[str] = pa.Field(coerce=True, alias="commentHandler", nullable=True)

    currently_available_units: Series[pd.Float64Dtype] = pa.Field(coerce=True, alias="currentlyAvailableUnits", nullable=True)
    started_via_workflow: Series[bool] = pa.Field(coerce=True, alias="startedViaWorkflow", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


class LeaveRequestCreate(BaseModel):
    """Schema for creating and updating a leave request."""
    number_of_units: Optional[float] = Field(None, alias="numberOfUnits", description="Number of units", example=8.0)
    is_accrual: Optional[bool] = Field(None, alias="isAccrual", description="Is accrual", example=True)
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date (YYYY-MM-DD)", example="2024-01-15")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date (YYYY-MM-DD)", example="2024-01-22")
    leave_type: Optional[MetadataWithKey] = Field(None, alias="leaveType", description="Leave type information")
    comment_employee: Optional[str] = Field(None, alias="commentEmployee", description="Employee comment", example="Family vacation")
    started_via_workflow: Optional[bool] = Field(None, alias="startedViaWorkflow", description="Started via workflow", example=False)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function.
        Supports keys like leave_type_key → leaveType {"key": ...} and
        auto-converts root snake_case fields to camelCase aliases.
        """
        if not isinstance(values, dict):
            return values

        # Define metadata fields for this schema
        ROOT_METADATA_FIELDS: Set[str] = {
            "leave_type",
        }

        return flat_to_nested_with_metadata(
            values=values,
            prefix_map={},
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields={}
        )
