from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class PayTypeGet(BrynQPanderaDataFrameModel):
    """
    Schema for pay type data from Visma Lon HR.
    Represents wage type information from the VISMALØN table LOENART.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="PayTypeRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of Wage type", alias="Name")
    benefit_deduction: Series[pd.StringDtype] = pa.Field(coerce=True, description="Benefit deduction", alias="BenefitDeduction", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    pay_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Number of Wage type", alias="PayTypeCode")
    create_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="CreateTime")
    update_time: Series[pd.StringDtype] = pa.Field(coerce=True, description="Timestamp for latest update of the registration", alias="UpdateTime")

    class _Annotation:
        primary_key = "rid"
        foreign_keys = {
            "customer_id": {
                "parent_schema": "CustomerGet",
                "parent_column": "customer_id",
                "cardinality": "N:1"
            }
        }
