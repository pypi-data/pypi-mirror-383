from pandera.typing import Series
import pandera as pa
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from datetime import datetime


class AdministrationGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Administration data returned from Loket API.
    An Administration represents a payroll administration in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the administration", alias="id")
    client_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The client number", alias="clientNumber")
    employer_id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employer", alias="employerId")
    wage_tax_number: Series[str] = pa.Field(coerce=True, description="The wage tax number", alias="wageTaxNumber", nullable=True)
    description: Series[str] = pa.Field(coerce=True, description="The description of the administration", alias="description")
    start_date: Series[str] = pa.Field(coerce=True, description="The start date of the administration", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="The end date of the administration", alias="endDate", nullable=True)
    is_payroll_administration: Series[bool] = pa.Field(coerce=True, description="Indicates if this is a payroll administration", alias="isPayrollAdministration")

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
