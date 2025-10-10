from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmployerGet(BrynQPanderaDataFrameModel):
    """
    Schema for employer data from Visma Lon HR.
    Represents employer information from the VISMALØN table ARBEJDSGIVER.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="EmployerRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Employer start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date for closing down the employer", alias="EndDate", nullable=True)
    from_date: Series[datetime] = pa.Field(coerce=True, description="Active start date", alias="FromDate", nullable=True)
    to_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Active end date", alias="ToDate", nullable=True)
    cvr_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="CVR number", alias="CVRNumber", nullable=True)
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of employer", alias="Name")
    address_line1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer address", alias="AddressLine1", nullable=True)
    address_line2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Supplementary address information", alias="AddressLine2", nullable=True)
    postal_code_dk: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer postal code", alias="PostalCodeDK", nullable=True)
    postal_district_dk: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer city name", alias="PostalDistrictDK", nullable=True)
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
