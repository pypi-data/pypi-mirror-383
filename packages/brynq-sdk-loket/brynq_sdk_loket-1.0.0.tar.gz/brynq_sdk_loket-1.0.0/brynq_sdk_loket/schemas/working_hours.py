"""
Schema definitions for WorkingHours-related data structures in Loket API.

This module contains Pandera schemas for GET operations related to employment working hours.
"""

from typing import Optional, Dict, Any
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel
from .base import MetadataWithKey, MetadataWithStringKey


class WorkingHoursGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating WorkingHours data returned from Loket API.
    WorkingHours represents working hours information for an employment in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the working hours", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="The start date of the working hours", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="The end date of the working hours", alias="endDate", nullable=True)
    shift_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Shift number", alias="shift.shiftNumber", nullable=True)
    full_time_hours_per_week: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Full time hours per week", alias="shift.fullTimeHoursPerWeek", nullable=True)
    bonus_percentage: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Bonus percentage", alias="shift.bonusPercentage", nullable=True)
    deviating_hours_per_week: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Deviating hours per week", alias="deviatingHoursPerWeek", nullable=True)
    average_hours_per_week: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Average hours per week", alias="averageHoursPerWeek", nullable=True)
    deviating_sv_days_per_period: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deviating SV days per period", alias="deviatingSvDaysPerPeriod", nullable=True)
    average_parttime_factor: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Average parttime factor", alias="averageParttimeFactor", nullable=True)
    regular_work_pattern: Series[bool] = pa.Field(coerce=True, description="Regular work pattern", alias="regularWorkPattern", nullable=True)
    shift_rate_sick_leave_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Shift rate sick leave number", alias="shiftRateSickLeave.shiftNumber", nullable=True)
    shift_rate_sick_leave_hours: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Shift rate sick leave hours", alias="shiftRateSickLeave.fullTimeHoursPerWeek", nullable=True)
    shift_rate_sick_leave_bonus: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Shift rate sick leave bonus", alias="shiftRateSickLeave.bonusPercentage", nullable=True)
    calculate_leave_hours: Series[bool] = pa.Field(coerce=True, description="Calculate using work pattern leave hours", alias="calculateUsingWorkPattern.leaveHours", nullable=True)
    calculate_hours_broken_period: Series[bool] = pa.Field(coerce=True, description="Calculate using work pattern hours broken period", alias="calculateUsingWorkPattern.hoursBrokenPeriod", nullable=True)
    calculate_hours_regular_period: Series[bool] = pa.Field(coerce=True, description="Calculate using work pattern hours regular period", alias="calculateUsingWorkPattern.hoursRegularPeriod", nullable=True)
    calculate_days_daily_rate: Series[bool] = pa.Field(coerce=True, description="Calculate using work pattern days daily rate", alias="calculateUsingWorkPattern.daysDailyRate", nullable=True)
    calculate_deviating_days_hours: Series[bool] = pa.Field(coerce=True, description="Calculate using work pattern deviating days and hours", alias="calculateUsingWorkPattern.deviatingDaysAndHours", nullable=True)
    flexible_hours_contract: Series[str] = pa.Field(coerce=True, description="Flexible hours contract object", alias="flexibleHoursContract", nullable=True)
    work_pattern: Series[str] = pa.Field(coerce=True, description="Work pattern object", alias="workPattern", nullable=True)
    contract_code: Series[str] = pa.Field(coerce=True, description="Contract code object", alias="contractCode", nullable=True)
    aggregated_hours_per_week: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Aggregated hours per week", alias="aggregatedHoursPerWeek", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False



class WorkingHoursCreate(BaseModel):
    """Schema for creating working hours."""
    start_date: str = Field(..., alias="startDate", description="Start date of the working hours (YYYY-MM-DD)", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the working hours (YYYY-MM-DD)", example="2024-12-31")
    shift: Optional[Dict[str, Any]] = Field(None, description="Shift information")
    deviating_hours_per_week: Optional[float] = Field(None, alias="deviatingHoursPerWeek", description="Deviating hours per week", example=40.0)
    average_hours_per_week: Optional[float] = Field(None, alias="averageHoursPerWeek", description="Average hours per week", example=40.0)
    deviating_sv_days_per_period: Optional[int] = Field(None, alias="deviatingSvDaysPerPeriod", description="Deviating SV days per period", example=5)
    average_parttime_factor: Optional[float] = Field(None, alias="averageParttimeFactor", description="Average parttime factor", example=1.0)
    regular_work_pattern: Optional[bool] = Field(None, alias="regularWorkPattern", description="Regular work pattern", example=True)
    shift_rate_sick_leave: Optional[Dict[str, Any]] = Field(None, alias="shiftRateSickLeave", description="Shift rate sick leave information")
    flexible_hours_contract: Optional[MetadataWithKey] = Field(None, alias="flexibleHoursContract", description="Flexible hours contract information")
    work_pattern: Optional[Dict[str, Any]] = Field(None, alias="workPattern", description="Work pattern information")
    calculate_using_work_pattern: Optional[Dict[str, Any]] = Field(None, alias="calculateUsingWorkPattern", description="Calculate using work pattern information")
    contract_code: Optional[MetadataWithStringKey] = Field(None, alias="contractCode", description="Contract code information")

    class Config:
        validate_by_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def fold_flat_keys(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle flat keys conversion to nested structure for working hours creation.
        Maps flat fields to their proper nested locations.
        """
        if not isinstance(values, dict):
            return values

        values = values.copy()

        # Initialize nested structures
        shift: Dict[str, Any] = {}
        shift_rate_sick_leave: Dict[str, Any] = {}
        flexible_hours_contract: Dict[str, Any] = {}
        work_pattern: Dict[str, Any] = {}
        calculate_using_work_pattern: Dict[str, Any] = {}
        contract_code: Dict[str, Any] = {}

        # Process shift fields
        shift_map = {
            "shift_number": "shiftNumber",
        }

        for flat_key, nested_key in shift_map.items():
            if flat_key in values and values[flat_key] is not None:
                shift[nested_key] = values.pop(flat_key)

        # Process shift rate sick leave fields
        shift_rate_sick_leave_map = {
            "shift_rate_sick_leave_number": "shiftNumber",
        }

        for flat_key, nested_key in shift_rate_sick_leave_map.items():
            if flat_key in values and values[flat_key] is not None:
                shift_rate_sick_leave[nested_key] = values.pop(flat_key)

        # Process flexible hours contract fields
        flexible_hours_contract_map = {
            "flexible_hours_contract_key": "key",
        }

        for flat_key, nested_key in flexible_hours_contract_map.items():
            if flat_key in values and values[flat_key] is not None:
                flexible_hours_contract[nested_key] = values.pop(flat_key)

        # Process work pattern fields
        work_pattern_map = {
            "work_pattern_odd_monday": "oddWeeks.monday",
            "work_pattern_odd_tuesday": "oddWeeks.tuesday",
            "work_pattern_odd_wednesday": "oddWeeks.wednesday",
            "work_pattern_odd_thursday": "oddWeeks.thursday",
            "work_pattern_odd_friday": "oddWeeks.friday",
            "work_pattern_odd_saturday": "oddWeeks.saturday",
            "work_pattern_odd_sunday": "oddWeeks.sunday",
            "work_pattern_even_monday": "evenWeeks.monday",
            "work_pattern_even_tuesday": "evenWeeks.tuesday",
            "work_pattern_even_wednesday": "evenWeeks.wednesday",
            "work_pattern_even_thursday": "evenWeeks.thursday",
            "work_pattern_even_friday": "evenWeeks.friday",
            "work_pattern_even_saturday": "evenWeeks.saturday",
            "work_pattern_even_sunday": "evenWeeks.sunday",
        }

        for flat_key, nested_key in work_pattern_map.items():
            if flat_key in values and values[flat_key] is not None:
                # Handle nested keys like "oddWeeks.monday"
                if "." in nested_key:
                    parent_key, child_key = nested_key.split(".", 1)
                    if parent_key not in work_pattern:
                        work_pattern[parent_key] = {}
                    work_pattern[parent_key][child_key] = values.pop(flat_key)
                else:
                    work_pattern[nested_key] = values.pop(flat_key)

        # Process calculate using work pattern fields
        calculate_using_work_pattern_map = {
            "calculate_leave_hours": "leaveHours",
            "calculate_hours_broken_period": "hoursBrokenPeriod",
            "calculate_hours_regular_period": "hoursRegularPeriod",
            "calculate_days_daily_rate": "daysDailyRate",
            "calculate_deviating_days_hours": "deviatingDaysAndHours",
        }

        for flat_key, nested_key in calculate_using_work_pattern_map.items():
            if flat_key in values and values[flat_key] is not None:
                calculate_using_work_pattern[nested_key] = values.pop(flat_key)

        # Process contract code fields
        contract_code_map = {
            "contract_code_key": "key",
        }

        for flat_key, nested_key in contract_code_map.items():
            if flat_key in values and values[flat_key] is not None:
                contract_code[nested_key] = values.pop(flat_key)

        # Add nested structures to values if they have content
        if shift:
            values["shift"] = shift
        if shift_rate_sick_leave:
            values["shift_rate_sick_leave"] = shift_rate_sick_leave
        if flexible_hours_contract:
            values["flexible_hours_contract"] = flexible_hours_contract
        if work_pattern:
            values["work_pattern"] = work_pattern
        if calculate_using_work_pattern:
            values["calculate_using_work_pattern"] = calculate_using_work_pattern
        if contract_code:
            values["contract_code"] = contract_code

        return values
