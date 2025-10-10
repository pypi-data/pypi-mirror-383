from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class ProcessedAbsenceGet(BrynQPanderaDataFrameModel):
    """
    Schema for processed absence data from Visma Lon HR.
    Represents processed absence information from the VISMALØN table FRAVAERSPOSTERING.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="ProcessedAbsenceRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment", alias="EmploymentID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[datetime] = pa.Field(coerce=True, description="End date", alias="EndDate", nullable=True)
    absence_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Absence code", alias="AbsenceCode")
    processed_absence_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of absence", alias="ProcessedAbsenceName")
    rate: Series[pd.StringDtype] = pa.Field(coerce=True, description="Rate that the absence is paid out by", alias="Rate", nullable=True)
    duration: Series[pd.StringDtype] = pa.Field(coerce=True, description="Length of absence period either in days or hours depending on the type of absence", alias="Duration", nullable=True)
    duration_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Hours or days", alias="DurationType", nullable=True)
    used_date: Series[datetime] = pa.Field(coerce=True, description="Date of payroll processed", alias="UsedDate", nullable=True)
    project_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Project number", alias="ProjectID", nullable=True)
    used_payroll_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Payroll number", alias="UsedPayrollNumber", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    group_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="ID that refers to a possible registration in the table ProcessedAbsence", alias="GroupID", nullable=True)
    start_time: Series[pd.StringDtype] = pa.Field(coerce=True, description="Start time for the absence", alias="StartTime", nullable=True)
    end_time: Series[pd.StringDtype] = pa.Field(coerce=True, description="End time for the absence", alias="EndTime", nullable=True)
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
            },
            "absence_code": {
                "parent_schema": "AbsenceTypeGet",
                "parent_column": "absence_type_code",
                "cardinality": "N:1"
            }
        }
