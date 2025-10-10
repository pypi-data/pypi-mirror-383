from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmployeeQualificationGet(BrynQPanderaDataFrameModel):
    """
    Schema for employee qualification data from Visma Lon HR.
    Represents course and education information for employees from the Visma HR table EmployeeQualification.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="EmployeeQualificationRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Organisation", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    course_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Course ID", alias="CourseID")
    course_calendar_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Calendar for course", alias="CourseCalendarID", nullable=True)
    course_state_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Status", alias="CourseStateCode", nullable=True)
    text: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of course", alias="Text", nullable=True)
    course_start_date: Series[datetime] = pa.Field(coerce=True, description="Course start date", alias="CourseStartDate", nullable=True)
    course_price: Series[pd.StringDtype] = pa.Field(coerce=True, description="Price", alias="CoursePrice", nullable=True)
    duration: Series[pd.StringDtype] = pa.Field(coerce=True, description="Duration", alias="Duration", nullable=True)
    duration_is_default_value: Series[pd.StringDtype] = pa.Field(coerce=True, description="Absence text", alias="DurationIsDefaultValue", nullable=True)
    duration_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Units for duration", alias="DurationTypeCode", nullable=True)
    grade: Series[pd.StringDtype] = pa.Field(coerce=True, description="Grade/Level", alias="Grade", nullable=True)
    deadline_date: Series[datetime] = pa.Field(coerce=True, description="Obsolescence/expiration date", alias="DeadlineDate", nullable=True)
    description: Series[pd.StringDtype] = pa.Field(coerce=True, description="Remark", alias="Description", nullable=True)
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
            "course_id": {
                "parent_schema": "CourseGet",
                "parent_column": "course_id",
                "cardinality": "N:1"
            },
            "course_calendar_id": {
                "parent_schema": "CourseCalendarGet",
                "parent_column": "course_calendar_id",
                "cardinality": "N:1"
            }
        }
