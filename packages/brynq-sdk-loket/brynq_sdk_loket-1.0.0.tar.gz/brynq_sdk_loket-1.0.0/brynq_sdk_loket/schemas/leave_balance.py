"""
Schema definitions for LeaveBalance-related data structures in Loket API.

This module contains Pandera schemas for GET operations related to employment leave balance.
"""

from typing import Optional, Dict, Any
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel
from .base import MetadataWithKey, MetadataWithStringKey


class LeaveBalanceGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating LeaveBalance data returned from Loket API.
    A LeaveBalance represents leave balance information for an employment in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the leave balance", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="Start date", alias="startDate", nullable=True)
    historical_start_date: Series[str] = pa.Field(coerce=True, description="Historical start date", alias="historicalStartDate", nullable=True)
    end_date: Series[str] = pa.Field(coerce=True, description="End date", alias="endDate", nullable=True)

    # Payroll administration fields
    payroll_administration_id: Series[str] = pa.Field(coerce=True, description="Payroll administration ID", alias="payrollAdministration.id", nullable=True)
    payroll_administration_name: Series[str] = pa.Field(coerce=True, description="Payroll administration name", alias="payrollAdministration.name", nullable=True)
    payroll_administration_client_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll administration client number", alias="payrollAdministration.clientNumber", nullable=True)
    payroll_administration_description: Series[str] = pa.Field(coerce=True, description="Payroll administration description", alias="payrollAdministration.description", nullable=True)

    # Non-payroll administration fields
    non_payroll_administration_id: Series[str] = pa.Field(coerce=True, description="Non-payroll administration ID", alias="nonPayrollAdministration.id", nullable=True)
    non_payroll_administration_name: Series[str] = pa.Field(coerce=True, description="Non-payroll administration name", alias="nonPayrollAdministration.name", nullable=True)
    non_payroll_administration_description: Series[str] = pa.Field(coerce=True, description="Non-payroll administration description", alias="nonPayrollAdministration.description", nullable=True)

    # Income relationship fields
    income_relationship_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Income relationship number", alias="incomeRelationshipNumber", nullable=True)

    # Employee fields
    employee_id: Series[str] = pa.Field(coerce=True, description="Employee ID", alias="employee.id", nullable=True)
    employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee number", alias="employee.employeeNumber", nullable=True)
    employee_first_name: Series[str] = pa.Field(coerce=True, description="Employee first name", alias="employee.firstName", nullable=True)
    employee_initials: Series[str] = pa.Field(coerce=True, description="Employee initials", alias="employee.initials", nullable=True)
    employee_prefix: Series[str] = pa.Field(coerce=True, description="Employee prefix", alias="employee.prefix", nullable=True)
    employee_last_name: Series[str] = pa.Field(coerce=True, description="Employee last name", alias="employee.lastName", nullable=True)
    employee_prefix_partner: Series[str] = pa.Field(coerce=True, description="Employee prefix partner", alias="employee.prefixPartner", nullable=True)
    employee_last_name_partner: Series[str] = pa.Field(coerce=True, description="Employee last name partner", alias="employee.lastNamePartner", nullable=True)
    employee_formatted_name: Series[str] = pa.Field(coerce=True, description="Employee formatted name", alias="employee.formattedName", nullable=True)
    employee_date_of_birth: Series[str] = pa.Field(coerce=True, description="Employee date of birth", alias="employee.dateOfBirth", nullable=True)
    employee_photo: Series[str] = pa.Field(coerce=True, description="Employee photo URL", alias="employee.photo", nullable=True)

    # Organizational entity fields
    organizational_entity_start_date: Series[str] = pa.Field(coerce=True, description="Organizational entity start date", alias="organizationalEntity.startDate", nullable=True)
    organizational_entity_end_date: Series[str] = pa.Field(coerce=True, description="Organizational entity end date", alias="organizationalEntity.endDate", nullable=True)

    # Department fields
    department_key: Series[str] = pa.Field(coerce=True, description="Department key", alias="organizationalEntity.department.key", nullable=True)
    department_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Department code", alias="organizationalEntity.department.code", nullable=True)
    department_description: Series[str] = pa.Field(coerce=True, description="Department description", alias="organizationalEntity.department.description", nullable=True)

    # Function fields
    function_key: Series[str] = pa.Field(coerce=True, description="Function key", alias="organizationalEntity.function.key", nullable=True)
    function_description: Series[str] = pa.Field(coerce=True, description="Function description", alias="organizationalEntity.function.description", nullable=True)
    function_group: Series[str] = pa.Field(coerce=True, description="Function group", alias="organizationalEntity.function.group", nullable=True)

    # Standard function fields
    standard_function_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Standard function key", alias="organizationalEntity.standardFunction.key", nullable=True)
    standard_function_value: Series[str] = pa.Field(coerce=True, description="Standard function value", alias="organizationalEntity.standardFunction.value", nullable=True)
    standard_function_code: Series[str] = pa.Field(coerce=True, description="Standard function code", alias="organizationalEntity.standardFunction.code", nullable=True)
    standard_function_category: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Standard function category", alias="organizationalEntity.standardFunction.category", nullable=True)

    # Deviating function fields
    deviating_function_group: Series[str] = pa.Field(coerce=True, description="Deviating function group", alias="organizationalEntity.deviatingFunctionGroup", nullable=True)
    deviating_function_description: Series[str] = pa.Field(coerce=True, description="Deviating function description", alias="organizationalEntity.deviatingFunctionDescription", nullable=True)

    # Place of employment
    place_of_employment: Series[str] = pa.Field(coerce=True, description="Place of employment", alias="organizationalEntity.placeOfEmployment", nullable=True)

    # Leave balance fields (will be flattened from array)
    leave_balance_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Leave balance year", alias="leaveBalance.year", nullable=True)
    leave_balance_leave_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Leave balance leave type key", alias="leaveBalance.leaveType.key", nullable=True)
    leave_balance_leave_type_value: Series[str] = pa.Field(coerce=True, description="Leave balance leave type value", alias="leaveBalance.leaveType.value", nullable=True)
    leave_balance_leave_type_balance_exceeds_year: Series[bool] = pa.Field(coerce=True, description="Leave balance leave type balance exceeds year", alias="leaveBalance.leaveType.balanceExceedsYear", nullable=True)
    leave_balance_balance_previous_year: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance previous year", alias="leaveBalance.balancePreviousYear", nullable=True)
    leave_balance_accrual: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance accrual", alias="leaveBalance.accrual", nullable=True)
    leave_balance_usage_total: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance usage total", alias="leaveBalance.usageTotal", nullable=True)
    leave_balance_usage_through_reference_date: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance usage through reference date", alias="leaveBalance.usageThroughReferenceDate", nullable=True)
    leave_balance_usage_after_reference_date: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance usage after reference date", alias="leaveBalance.usageAfterReferenceDate", nullable=True)
    leave_balance_usage_first_half_year: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance usage first half year", alias="leaveBalance.usageFirstHalfYear", nullable=True)
    leave_balance_balance: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance", alias="leaveBalance.balance", nullable=True)
    leave_balance_expires: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Leave balance expires", alias="leaveBalance.expires", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
