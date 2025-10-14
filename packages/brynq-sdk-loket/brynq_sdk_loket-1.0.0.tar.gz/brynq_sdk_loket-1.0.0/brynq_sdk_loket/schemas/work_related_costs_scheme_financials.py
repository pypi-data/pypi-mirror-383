from pandera.typing import Series
import pandera as pa
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class WorkRelatedCostsSchemeFinancialsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Work Related Costs Scheme Financials data returned from Loket API.
    Represents work related costs scheme financials for a payroll administration.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the work related costs scheme financial", alias="id")
    year: Series[int] = pa.Field(coerce=True, description="Year of the work related costs scheme financial", alias="year")
    period: Series[int] = pa.Field(coerce=True, description="Period of the work related costs scheme financial", alias="period")
    identification: Series[str] = pa.Field(coerce=True, description="Identification of the work related costs scheme financial", alias="identification")
    description: Series[str] = pa.Field(coerce=True, description="Description of the work related costs scheme financial", alias="description")
    amount: Series[float] = pa.Field(coerce=True, description="Amount of the work related costs scheme financial", alias="amount")

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE WORK RELATED COSTS SCHEME FINANCIALS SCHEMAS ====================

class WorkRelatedCostsSchemeFinancialsCreate(BaseModel):
    """Schema for creating work related costs scheme financials."""
    year: int = Field(..., description="Year of the work related costs scheme financial", example=2024)
    period: int = Field(..., description="Period of the work related costs scheme financial", example=1)
    identification: str = Field(..., description="Identification of the work related costs scheme financial", example="WRK001")
    description: str = Field(..., description="Description of the work related costs scheme financial", example="Travel expenses")
    amount: float = Field(..., description="Amount of the work related costs scheme financial", example=500.00)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class WorkRelatedCostsSchemeFinancialsUpdate(BaseModel):
    """Schema for updating work related costs scheme financials."""
    year: Optional[int] = Field(None, description="Year of the work related costs scheme financial", example=2024)
    period: Optional[int] = Field(None, description="Period of the work related costs scheme financial", example=1)
    identification: Optional[str] = Field(None, description="Identification of the work related costs scheme financial", example="WRK001")
    description: Optional[str] = Field(None, description="Description of the work related costs scheme financial", example="Travel expenses")
    amount: Optional[float] = Field(None, description="Amount of the work related costs scheme financial", example=500.00)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


# ==================== WORK RELATED COSTS SCHEME MATRIX SCHEMAS ====================

class WorkRelatedCostsSchemeMatrixGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Work Related Costs Scheme Matrix data returned from Loket API.
    Represents work related costs scheme matrix for a payroll administration.
    """
    # Payroll period fields
    payroll_period_year: Series[int] = pa.Field(coerce=True, description="Year of the payroll period", alias="payrollPeriod.year")
    payroll_period_number: Series[int] = pa.Field(coerce=True, description="Period number of the payroll period", alias="payrollPeriod.periodNumber")
    payroll_period_start_date: Series[str] = pa.Field(coerce=True, description="Start date of the payroll period", alias="payrollPeriod.periodStartDate")
    payroll_period_end_date: Series[str] = pa.Field(coerce=True, description="End date of the payroll period", alias="payrollPeriod.periodEndDate")

    # Matrix fields
    discretionary_scope_cumulative: Series[float] = pa.Field(coerce=True, description="Discretionary scope cumulative", alias="discretionaryScopeCumulative")
    work_related_costs_cumulative: Series[float] = pa.Field(coerce=True, description="Work related costs cumulative", alias="workRelatedCostsCumulative")

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    payroll_period: Series[str] = pa.Field(coerce=True, description="Payroll period object", alias="payrollPeriod", nullable=True)

    class _Annotation:
        primary_key = "payroll_period_year"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True
