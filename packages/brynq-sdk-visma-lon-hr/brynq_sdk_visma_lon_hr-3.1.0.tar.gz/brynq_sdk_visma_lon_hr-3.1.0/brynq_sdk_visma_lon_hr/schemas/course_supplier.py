from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class CourseSupplierGet(BrynQPanderaDataFrameModel):
    """
    Schema for course supplier data from Visma Lon HR.
    Represents course supplier information from the Visma HR table CourseSupplier.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="CourseSupplierRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Organisation", alias="CustomerID")
    id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Supplier number", alias="CourseSupplierID")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Supplier name", alias="CourseSupplierName")
    adress: Series[pd.StringDtype] = pa.Field(coerce=True, description="Address", alias="Adress", nullable=True)
    contact: Series[pd.StringDtype] = pa.Field(coerce=True, description="Contact person", alias="Contact", nullable=True)
    address_web: Series[pd.StringDtype] = pa.Field(coerce=True, description="Website address", alias="AddressWeb", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
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
