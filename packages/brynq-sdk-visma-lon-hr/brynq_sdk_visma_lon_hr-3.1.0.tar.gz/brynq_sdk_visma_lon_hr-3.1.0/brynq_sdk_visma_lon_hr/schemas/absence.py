from datetime import datetime, time
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class AbsenceGet(BrynQPanderaDataFrameModel):
    """Schema for absence data from Visma Lon HR"""

    code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Code identifying the type of absence", alias="AbsenceCode")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of the absence type", alias="AbsenceName")
    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Resource identifier for the absence", alias="AbsenceRID")
    approve_item_status: Series[pd.StringDtype] = pa.Field(coerce=True, description="Status of approval for the absence", alias="ApproveItemStatus")
    create_time: Series[datetime] = pa.Field(coerce=True, description="Time when the record was created", alias="CreateTime")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID associated with this absence", alias="CustomerID")
    duration: Series[pd.StringDtype] = pa.Field(coerce=True, description="Duration of the absence", alias="Duration")
    duration_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Type of duration measurement", alias="DurationType")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee ID for whom the absence is recorded", alias="EmployeeID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer ID associated with this absence", alias="EmployerID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment ID associated with this absence", alias="EmploymentID")
    end_date: Series[datetime] = pa.Field(coerce=True, description="End date of the absence period", alias="EndDate")
    end_time: Series[pd.StringDtype] = pa.Field(coerce=True, description="End time of the absence on the end date", alias="EndTime", nullable=True)
    group_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Group identifier for the absence", alias="GroupID", nullable=True)
    project_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Project identifier if applicable", alias="ProjectID", nullable=True)
    rate: Series[pd.StringDtype] = pa.Field(coerce=True, description="Rate associated with the absence", alias="Rate", nullable=True)
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date of the absence period", alias="StartDate")
    start_time: Series[pd.StringDtype] = pa.Field(coerce=True, description="Start time of the absence on the start date", alias="StartTime", nullable=True)
    update_time: Series[datetime] = pa.Field(coerce=True, description="Last update time of the record", alias="UpdateTime")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Version number of the record", alias="VersionNumber")

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
