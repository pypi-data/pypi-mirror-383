from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class AbsenceGroupGet(BrynQPanderaDataFrameModel):
    """
    Schema for absence group data from Visma Lon HR.
    Represents absence that is not yet processed in a payroll from FRAVAERSPOSTERING table.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="AbsenceGroupRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment ID", alias="EmploymentID")
    group_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="ID that refers to a potential occurrence in the table Absence", alias="GroupID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date of absence period", alias="StartDate")
    end_date: Series[datetime] = pa.Field(coerce=True, description="End date of absence period", alias="EndDate")
    comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment about the absence", alias="Comment", nullable=True)
    disapproval_comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment if absence is rejected", alias="DisapprovalComment", nullable=True)
    project_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Project ID", alias="ProjectID", nullable=True)
    calendar_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Calendar code", alias="CalendarCode", nullable=True)
    create_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for creating the absence registration", alias="CreateTime")
    update_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for latest update of the absence registration", alias="UpdateTime")

    class _Annotation:
        primary_key = "rid"
        foreign_keys = {
            "customer_id": {
                "parent_schema": "CustomerGet",
                "parent_column": "customer_id",
                "cardinality": "N:1"
            },
            "employee_id": {
                "parent_schema": "EmployeeGet",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            },
            "employer_id": {
                "parent_schema": "EmployerGet",
                "parent_column": "employer_id",
                "cardinality": "N:1"
            },
            "employment_id": {
                "parent_schema": "EmploymentGet",
                "parent_column": "employment_id",
                "cardinality": "N:1"
            }
        }
