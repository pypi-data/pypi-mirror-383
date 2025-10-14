from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from .base import MetadataWithKey


class BenefitsAndDeductionsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Benefits and Deductions data returned from Loket API.
    A Benefits and Deductions represents payroll components for an employment.
    """
    # Main benefits and deductions fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the benefits and deductions", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="Start date of the benefits and deductions", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="End date of the benefits and deductions", alias="endDate", nullable=True)
    value: Series[float] = pa.Field(coerce=True, description="Value of the benefits and deductions", alias="value")

    # Payroll component fields
    payroll_component_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the payroll component", alias="payrollComponent.key", nullable=True)
    payroll_component_description: Series[str] = pa.Field(coerce=True, description="Description of the payroll component", alias="payrollComponent.description", nullable=True)

    # Category fields
    category_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the category", alias="payrollComponent.category.key", nullable=True)
    category_value: Series[str] = pa.Field(coerce=True, description="Value of the category", alias="payrollComponent.category.value", nullable=True)

    # Deduction or payment fields
    deduction_or_payment_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of deduction or payment", alias="payrollComponent.deductionOrPayment.key", nullable=True)
    deduction_or_payment_value: Series[str] = pa.Field(coerce=True, description="Value of deduction or payment", alias="payrollComponent.deductionOrPayment.value", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    payroll_component: Series[str] = pa.Field(coerce=True, description="Payroll component object", alias="payrollComponent", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE BENEFITS AND DEDUCTIONS SCHEMAS ====================

class PayrollComponentCreate(BaseModel):
    """Payroll component for creating benefits and deductions."""
    key: int = Field(..., description="The key of the payroll component")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class BenefitsAndDeductionsCreate(BaseModel):
    """Schema for creating benefits and deductions."""
    start_date: str = Field(..., alias="startDate", description="Start date of the benefits and deductions", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the benefits and deductions", example="2024-12-31")
    payroll_component: PayrollComponentCreate = Field(..., alias="payrollComponent", description="Payroll component")
    value: float = Field(..., description="Value of the benefits and deductions", example=100.00)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class BenefitsAndDeductionsUpdate(BaseModel):
    """Schema for updating benefits and deductions."""
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date of the benefits and deductions", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the benefits and deductions", example="2024-12-31")
    value: Optional[float] = Field(None, description="Value of the benefits and deductions", example=100.00)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


# ==================== IMPORT BENEFITS AND DEDUCTIONS SCHEMAS ====================

class BenefitsAndDeductionsImportGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Benefits and Deductions Import data returned from Loket API.
    This represents data that can be imported for benefits and deductions.
    """
    # Main import fields
    client_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Client number", alias="clientNumber")
    payroll_employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll employee number", alias="payrollEmployeeNumber")
    employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee number", alias="employeeNumber")
    formatted_name: Series[str] = pa.Field(coerce=True, description="Formatted employee name", alias="formattedName")
    start_date: Series[str] = pa.Field(coerce=True, description="Start date", alias="startDate")
    payroll_component_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll component key", alias="payrollComponentKey")
    payroll_component_description: Series[str] = pa.Field(coerce=True, description="Payroll component description", alias="payrollComponentDescription")
    value: Series[float] = pa.Field(coerce=True, description="Value", alias="value")

    class _Annotation:
        primary_key = "client_number"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CSV IMPORT BENEFITS AND DEDUCTIONS SCHEMAS ====================

class BenefitsAndDeductionsCsvImport(BaseModel):
    """Schema for importing benefits and deductions via CSV."""
    mime_type: str = Field(default="text/csv", alias="mimeType", description="The type of file to import. Currently only csv is supported")
    data: str = Field(..., description="Base64 encoded file content")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


# ==================== BATCH BENEFITS AND DEDUCTIONS SCHEMAS ====================

class BenefitsAndDeductionsBatchCreate(BaseModel):
    """Schema for creating benefits and deductions in batch."""
    employment_id: str = Field(..., alias="employmentId", description="The unique identifier of the employment")
    start_date: str = Field(..., alias="startDate", description="Start date of the benefits and deductions")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the benefits and deductions")
    payroll_component: PayrollComponentCreate = Field(..., alias="payrollComponent", description="Payroll component")
    value: float = Field(..., description="Value of the benefits and deductions")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class BenefitsAndDeductionsBatchUpdate(BaseModel):
    """Schema for updating benefits and deductions in batch."""
    employment_id: str = Field(..., alias="employmentId", description="The unique identifier of the employment")
    benefit_and_deduction_id: str = Field(..., alias="benefitAndDeductionId", description="The unique identifier of the benefits and deductions")
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date of the benefits and deductions")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the benefits and deductions")
    payroll_component: Optional[PayrollComponentCreate] = Field(None, alias="payrollComponent", description="Payroll component")
    value: Optional[float] = Field(None, description="Value of the benefits and deductions")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
