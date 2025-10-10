from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class OrganizationalUnitGet(BrynQPanderaDataFrameModel):
    """
    Schema for organizational unit data from Visma Lon HR.
    Represents organizational unit information from Visma Løn or Visma HR.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="OrganizationalUnitRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    organization_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Organisation ID", alias="OrganizationID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of organisational unit", alias="Name")
    address_line1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Address line 1", alias="AddressLine1", nullable=True)
    address_line2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Address line 2", alias="AddressLine2", nullable=True)
    postal_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Postal code", alias="PostalCode", nullable=True)
    postal_district: Series[pd.StringDtype] = pa.Field(coerce=True, description="City name", alias="PostalDistrict", nullable=True)
    country_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Country code for tax registration", alias="CountryCode", nullable=True)
    country: Series[pd.StringDtype] = pa.Field(coerce=True, description="Country name", alias="Country", nullable=True)
    responsible_employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Department manager", alias="ResponsibleEmployeeId", nullable=True)
    id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Department ID", alias="OrganizationalUnitID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    parent_organizational_unit_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Identification of parent organisation unit (if any)", alias="ParentOrganizationalUnitID", nullable=True)
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
            "employer_id": {
                "parent_schema": "EmployerGet",
                "parent_column": "employer_id",
                "cardinality": "N:1"
            },
            "organization_id": {
                "parent_schema": "OrganizationGet",
                "parent_column": "organization_id",
                "cardinality": "N:1"
            },
            "responsible_employee_id": {
                "parent_schema": "EmployeeGet",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            },
            "parent_organizational_unit_id": {
                "parent_schema": "OrganizationalUnitGet",
                "parent_column": "organizational_unit_id",
                "cardinality": "N:1"
            }
        }
