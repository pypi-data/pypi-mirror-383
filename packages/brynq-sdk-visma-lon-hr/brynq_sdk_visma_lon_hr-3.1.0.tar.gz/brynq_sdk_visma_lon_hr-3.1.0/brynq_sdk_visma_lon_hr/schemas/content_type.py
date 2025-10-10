from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class ContentTypeGet(BrynQPanderaDataFrameModel):
    """
    Schema for content type data from Visma Lon HR.
    Represents content type information from the VISMALØN table INDHOLDSTYPE.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="ContentTypeRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    content_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Ex. 100, 200, 350, 400, 600, 610, 620, 700, 800 etc.", alias="ContentTypeCode")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    from_date: Series[datetime] = pa.Field(coerce=True, description="Period From date", alias="FromDate", nullable=True)
    to_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Period To date", alias="ToDate", nullable=True)
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Description of personal information", alias="ContentTypeName")
    reciever: Series[pd.StringDtype] = pa.Field(coerce=True, description="Receiver of statistics ex. DA, DS, FA", alias="Reciever", nullable=True)
    create_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="CreateTime")
    update_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for latest update of the registration", alias="UpdateTime")

    class _Annotation:
        primary_key = "rid"
        foreign_keys = {
            "customer_id": {
                "parent_schema": "CustomerGet",
                "parent_column": "customer_id",
                "cardinality": "N:1"
            }
        }
