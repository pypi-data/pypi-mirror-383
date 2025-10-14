"""
Schema definitions for Year End Statements data structures in Loket API.

This module contains Pandera schemas for GET operations related to year end statements.
"""

import pandas as pd
import pandera as pa
from pandera.typing import Series

from brynq_sdk_functions import BrynQPanderaDataFrameModel


class YearEndStatementsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Year End Statements data returned from Loket API.
    A Year End Statements represents year end statement information for an employment.
    """
    # Main year field
    year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The year of the year end statement")

    class _Annotation:
        primary_key = "year"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True
