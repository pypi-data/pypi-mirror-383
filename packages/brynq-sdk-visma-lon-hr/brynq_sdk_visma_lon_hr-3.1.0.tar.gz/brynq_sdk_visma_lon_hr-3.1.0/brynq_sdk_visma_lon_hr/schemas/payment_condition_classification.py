from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class PaymentConditionClassificationGet(BrynQPanderaDataFrameModel):
    """
    Schema for payment condition classification data from Visma Lon HR.
    Represents payment condition classification information from the VISMALØN table STILKATOPLYSNING.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="PaymentConditionClassificationRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Position category", alias="PaymentConditionCode")
    content_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Ex. 100, 200, 350, 400, 600, 610, 620, 700, 800 etc.", alias="ContentTypeCode")
    classification_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Ex. 6 digit Disco-08 code for IP_type 350", alias="ClassificationCode")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    value: Series[pd.StringDtype] = pa.Field(coerce=True, description="For IP_Type 600, 610, og 620 the normtime, holidays or holiday supplement is shown", alias="Value", nullable=True)
    create_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="CreateTime")
    update_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for latest update of the registration", alias="UpdateTime")

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
