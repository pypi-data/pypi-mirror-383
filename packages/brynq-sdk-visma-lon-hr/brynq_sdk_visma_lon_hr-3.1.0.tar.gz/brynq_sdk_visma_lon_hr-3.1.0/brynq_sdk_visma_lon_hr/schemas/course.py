from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class CourseGet(BrynQPanderaDataFrameModel):
    """
    Schema for course data from Visma Lon HR.
    Represents course information from the Visma HR table Course.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="CourseRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Organisation", alias="CustomerID")
    id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Course ID", alias="CourseID")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of course", alias="CourseName")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Valid from", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Valid to", alias="EndDate")
    course_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Type of course", alias="CourseTypeCode", nullable=True)
    instructor: Series[pd.StringDtype] = pa.Field(coerce=True, description="Instructor", alias="Instructor", nullable=True)
    phone_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Phone number", alias="PhoneNumber", nullable=True)
    price: Series[pd.StringDtype] = pa.Field(coerce=True, description="Price", alias="CoursePrice", nullable=True)
    duration: Series[pd.StringDtype] = pa.Field(coerce=True, description="Duration", alias="Duration", nullable=True)
    duration_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Hours or days", alias="DurationType", nullable=True)
    description: Series[pd.StringDtype] = pa.Field(coerce=True, description="Description", alias="Description", nullable=True)
    course_supplier_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Supplier number", alias="CourseSupplierID", nullable=True)
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
            "course_supplier_id": {
                "parent_schema": "CourseSupplierGet",
                "parent_column": "course_supplier_id",
                "cardinality": "N:1"
            }
        }
