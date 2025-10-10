from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class PayrollGet(BrynQPanderaDataFrameModel):
    """
    Schema for payroll data from Visma Lon HR.
    Represents payroll information from the VISMALØN table KOERSELSSELEKTION.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="PayrollRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    payroll_run_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Payroll run number", alias="PayrollRunNumber")
    selection_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Selection number", alias="SelectionNumber")
    pay_period_start: Series[datetime] = pa.Field(coerce=True, description="Payroll period start", alias="PayPeriodStart")
    pay_period_end: Series[datetime] = pa.Field(coerce=True, description="Payroll period end", alias="PayPeriodEnd")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Payroll name", alias="Name")
    accounting_date: Series[datetime] = pa.Field(coerce=True, description="Accounting date", alias="AccountingDate", nullable=True)
    availability_date: Series[datetime] = pa.Field(coerce=True, description="Availability date", alias="AvailabilityDate", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    payroll_used_date: Series[datetime] = pa.Field(coerce=True, description="Payroll used date", alias="PayrollUsedDate", nullable=True)
    create_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="CreateTime")
    update_time: Series[datetime] = pa.Field(coerce=True, description="Timestamp for latest update of the registration", alias="UpdateTime")

    class _Annotation:
        primary_key = "rid"
        foreign_keys = {
            "customer_id": {
                "parent_schema": "CustomerGet",
                "parent_column": "customer_id",
                "cardinality": "N:1"
            }
        }
