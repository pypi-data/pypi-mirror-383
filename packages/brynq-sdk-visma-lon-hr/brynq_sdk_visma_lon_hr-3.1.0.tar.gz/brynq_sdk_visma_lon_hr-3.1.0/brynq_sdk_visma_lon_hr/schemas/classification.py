from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class ClassificationGet(BrynQPanderaDataFrameModel):
    """
    Schema for classification data from Visma Lon HR.
    Represents classification information from the VISMALØN table IP_KODE.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="ClassificationRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    content_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Ex. 350", alias="ContentTypeCode")
    classification_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Ex. 6 digit Disco-08 code", alias="ClassificationCode")
    start_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    classification_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of IP_kode", alias="ClassificationName")
    create_time: Series[pd.StringDtype] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="CreateTime")
    update_time: Series[pd.StringDtype] = pa.Field(coerce=True, description="Timestamp for latest update of the registration", alias="UpdateTime")

    class _Annotation:
        primary_key = "rid"
        foreign_keys = {
            "customer_id": {
                "parent_schema": "CustomerGet",
                "parent_column": "customer_id",
                "cardinality": "N:1"
            },
            "content_type_code": {
                "parent_schema": "ContentTypeGet",
                "parent_column": "content_type_code",
                "cardinality": "N:1"
            }
        }
