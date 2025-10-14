"""
Schema definitions for Payslips and Payroll Period Results data structures in Loket API.

This module contains Pandera schemas for GET operations related to payslips and payroll period results.
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series

from brynq_sdk_functions import BrynQPanderaDataFrameModel


class PayslipsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Payslips data returned from Loket API.
    A Payslips represents payslip information for an employment in the Loket system.
    """
    # Main payslip fields
    payroll_run_id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the payroll run", alias="payrollrunId")
    number_of_payslips: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of payslips in this payroll run", alias="numberOfPayslips")
    approval_time: Series[str] = pa.Field(coerce=True, description="Approval time of the payroll run", alias="approvalTime", nullable=True)

    # Payroll period fields
    payroll_period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year of the payroll period", alias="payrollPeriod.year")
    payroll_period_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period number within the year", alias="payrollPeriod.periodNumber")
    payroll_period_start_date: Series[str] = pa.Field(coerce=True, description="Start date of the payroll period", alias="payrollPeriod.periodStartDate")
    payroll_period_end_date: Series[str] = pa.Field(coerce=True, description="End date of the payroll period", alias="payrollPeriod.periodEndDate")
    payroll_period_test_year: Series[bool] = pa.Field(coerce=True, description="Whether this is a test year", alias="payrollPeriod.testYear", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    payroll_period: Series[str] = pa.Field(coerce=True, description="Payroll period object", alias="payrollPeriod", nullable=True)

    class _Annotation:
        primary_key = "payroll_run_id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


class PayrollPeriodResultsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Payroll Period Results data returned from Loket API.
    A Payroll Period Results represents detailed payroll period information for an employment.
    """
    # Main employment field
    employment_id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employment", alias="employmentId")

    # Payroll period fields
    payroll_period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year of the payroll period", alias="payrollPeriods.payrollPeriod.year", nullable=True)
    payroll_period_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period number within the year", alias="payrollPeriods.payrollPeriod.periodNumber", nullable=True)
    payroll_period_start_date: Series[str] = pa.Field(coerce=True, description="Start date of the payroll period", alias="payrollPeriods.payrollPeriod.periodStartDate", nullable=True)
    payroll_period_end_date: Series[str] = pa.Field(coerce=True, description="End date of the payroll period", alias="payrollPeriods.payrollPeriod.periodEndDate", nullable=True)
    payroll_period_test_year: Series[bool] = pa.Field(coerce=True, description="Whether this is a test year", alias="payrollPeriods.payrollPeriod.testYear", nullable=True)
    payroll_period_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll period type key", alias="payrollPeriods.payrollPeriod.payrollPeriodType.key", nullable=True)
    payroll_period_type_value: Series[str] = pa.Field(coerce=True, description="Payroll period type value", alias="payrollPeriods.payrollPeriod.payrollPeriodType.value", nullable=True)

    # Payslip type fields
    payslip_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payslip type key", alias="payrollPeriods.payslipTypes.payslipType.key", nullable=True)
    payslip_type_value: Series[str] = pa.Field(coerce=True, description="Payslip type value", alias="payrollPeriods.payslipTypes.payslipType.value", nullable=True)

    # Payroll component fields
    payroll_component_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll component key", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.key", nullable=True)
    payroll_component_value: Series[str] = pa.Field(coerce=True, description="Payroll component value", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.value", nullable=True)
    payroll_component_category_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll component category key", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.category.key", nullable=True)
    payroll_component_category_value: Series[str] = pa.Field(coerce=True, description="Payroll component category value", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.category.value", nullable=True)
    payroll_component_column_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll component column key", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.column.key", nullable=True)
    payroll_component_column_value: Series[str] = pa.Field(coerce=True, description="Payroll component column value", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.column.value", nullable=True)
    payroll_component_costs_employer_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll component costs employer key", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.costsEmployer.key", nullable=True)
    payroll_component_costs_employer_value: Series[str] = pa.Field(coerce=True, description="Payroll component costs employer value", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.costsEmployer.value", nullable=True)
    payroll_component_hours_indication: Series[bool] = pa.Field(coerce=True, description="Payroll component hours indication", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.hoursIndication", nullable=True)
    payroll_component_count_as_norm_hours: Series[bool] = pa.Field(coerce=True, description="Payroll component count as norm hours", alias="payrollPeriods.payslipTypes.payrollComponentResults.payrollComponent.countAsNormHours", nullable=True)

    # Value fields
    payroll_component_value_amount: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Payroll component value amount", alias="payrollPeriods.payslipTypes.payrollComponentResults.value", nullable=True)
    payroll_component_value_special_tariff: Series[pd.Float64Dtype] = pa.Field(coerce=True, description="Payroll component value special tariff", alias="payrollPeriods.payslipTypes.payrollComponentResults.valueSpecialTariff", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    payroll_periods: Series[str] = pa.Field(coerce=True, description="Payroll periods object", alias="payrollPeriods", nullable=True)
    payslip_types: Series[str] = pa.Field(coerce=True, description="Payslip types object", alias="payrollPeriods.payslipTypes", nullable=True)
    payroll_component_results: Series[str] = pa.Field(coerce=True, description="Payroll component results object", alias="payrollPeriods.payslipTypes.payrollComponentResults", nullable=True)

    class _Annotation:
        primary_key = "employment_id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True
