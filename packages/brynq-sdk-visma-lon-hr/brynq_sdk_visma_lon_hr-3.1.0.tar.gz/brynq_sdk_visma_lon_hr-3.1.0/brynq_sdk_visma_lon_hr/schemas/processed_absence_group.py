from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class ProcessedAbsenceGroupGet(BrynQPanderaDataFrameModel):
    """
    Schema for processed absence group data from Visma Lon HR.
    Represents processed absence group information from the VISMALØN table FRAVAERSPOSTERING.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="ProcessedAbsenceGroupRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment", alias="EmploymentID")
    group_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="ID that refers to a possible registration in the table ProcessedAbsence", alias="GroupID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[datetime] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment", alias="Comment", nullable=True)
    project_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Project ID", alias="ProjectID", nullable=True)
    calendar_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Calendar code", alias="CalendarCode", nullable=True)
    create_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="CreateTime")
    update_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for latest update of the registration", alias="UpdateTime")
    disapproval_comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment for dissapprovals", alias="DisapprovalComment", nullable=True)

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
