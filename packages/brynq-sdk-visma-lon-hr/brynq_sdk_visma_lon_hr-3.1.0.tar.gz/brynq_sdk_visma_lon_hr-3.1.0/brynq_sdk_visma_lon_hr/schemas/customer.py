from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class CustomerGet(BrynQPanderaDataFrameModel):
    """Schema for customer data from Visma Lon HR"""

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="CustomerRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    parent_customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Parent customer ID", alias="ParentCustomerID", nullable=True)
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of employer", alias="Name")
    address_line1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Address for employer", alias="AddressLine1", nullable=True)
    address_line2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Supplementary address information", alias="AddressLine2", nullable=True)
    postal_code_dk: Series[pd.StringDtype] = pa.Field(coerce=True, description="Postal code for employer", alias="PostalCodeDK", nullable=True)
    postal_district_dk: Series[pd.StringDtype] = pa.Field(coerce=True, description="City name for employer", alias="PostalDistrictDK", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    create_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="CreateTime")
    update_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for latest update of the registration", alias="UpdateTime")

    class _Annotation:
        primary_key = "rid"
        foreign_keys = {
            "parent_customer_id": {
                "parent_schema": "CustomerGet",
                "parent_column": "customer_id",
                "cardinality": "N:1"
            }
        }
