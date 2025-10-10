from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class CourseCalendarGet(BrynQPanderaDataFrameModel):
    """
    Schema for course calendar data from Visma Lon HR.
    Represents course calendar information from the Visma HR table CourseCalendar.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="CourseCalendarRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Organisation", alias="CustomerID")
    course_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Key to the specific course", alias="CourseID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Course calendar", alias="CourseCalendarID")
    end_date: Series[datetime] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    max_participants: Series[pd.StringDtype] = pa.Field(coerce=True, description="Max number of participants", alias="MaxParticipants", nullable=True)
    note: Series[pd.StringDtype] = pa.Field(coerce=True, description="Note", alias="Note", nullable=True)
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
            "course_id": {
                "parent_schema": "CourseGet",
                "parent_column": "course_id",
                "cardinality": "N:1"
            }
        }
