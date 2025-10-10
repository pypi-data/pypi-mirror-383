from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class AbsenceTypeGet(BrynQPanderaDataFrameModel):
    """
    Schema for absence type data from Visma Lon HR.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="AbsenceTypeRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    absence_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Absence type code", alias="AbsenceTypeCode")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of absence type", alias="Name")
    absence_group: Series[pd.StringDtype] = pa.Field(coerce=True, description="Absence group", alias="AbsenceGroup", nullable=True)
    il_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="IL type", alias="ILType", nullable=True)
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    from_date: Series[datetime] = pa.Field(coerce=True, description="From date", alias="FromDate", nullable=True)
    to_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="To date", alias="ToDate", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Version number", alias="VersionNumber")
    create_time: Series[datetime] = pa.Field(coerce=True, description="Creation timestamp", alias="CreateTime")
    update_time: Series[datetime] = pa.Field(coerce=True, description="Update timestamp", alias="UpdateTime")

    class _Annotation:
        primary_key = "rid"
        foreign_keys = {
            "customer_id": {
                "parent_schema": "CustomerGet",
                "parent_column": "customer_id",
                "cardinality": "N:1"
            }
        }
