from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class OrganizationGet(BrynQPanderaDataFrameModel):
    """
    Schema for organization data from Visma Lon HR.
    Represents organization information from the VISMALØN table ARBEJDSGIVER or Visma HR table Company.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="OrganizationRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Organisation", alias="OrganizationID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    from_date: Series[datetime] = pa.Field(coerce=True, description="From date", alias="FromDate", nullable=True)
    to_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="To date", alias="ToDate", nullable=True)
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name", alias="Name")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    parent_organization_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Parent Company", alias="ParentOrganizationId", nullable=True)
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
            "parent_organization_id": {
                "parent_schema": "OrganizationGet",
                "parent_column": "organization_id",
                "cardinality": "N:1"
            }
        }
