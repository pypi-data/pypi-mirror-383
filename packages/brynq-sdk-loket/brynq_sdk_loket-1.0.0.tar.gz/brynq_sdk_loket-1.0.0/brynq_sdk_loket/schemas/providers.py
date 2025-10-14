from pandera.typing import Series
import pandera as pa
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class ProviderGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Provider data returned from Loket API.
    A Provider represents an accountant or service provider in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the provider", alias="id")
    name: Series[str] = pa.Field(coerce=True, description="The name of the provider", alias="name")

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
