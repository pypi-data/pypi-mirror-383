from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class WorkCalendarGet(BrynQPanderaDataFrameModel):
    """
    Schema for work calendar data from Visma Lon HR.
    Represents work calendar information from the VISMALØN table ARBEJDSTIDSKALENDER.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="VismaLoenWorkCalendarRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment", alias="EmploymentID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    ical: Series[pd.StringDtype] = pa.Field(coerce=True, description="Calendar in the format ICAL", alias="ICAL", nullable=True)
    working_hours_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Working hour type", alias="WorkingHoursType", nullable=True)
    ignore_holidays: Series[pd.StringDtype] = pa.Field(coerce=True, description="Ignore holidays", alias="IgnoreHolidays", nullable=True)
    include_saturdays: Series[pd.StringDtype] = pa.Field(coerce=True, description="Include Saturdays", alias="IncludeSaturdays", nullable=True)
    include_sundays: Series[pd.StringDtype] = pa.Field(coerce=True, description="Include Sundays", alias="IncludeSundays", nullable=True)
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
            "employee_id": {
                "parent_schema": "EmployeeGet",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            },
            "employment_id": {
                "parent_schema": "EmploymentGet",
                "parent_column": "employment_id",
                "cardinality": "N:1"
            }
        }
