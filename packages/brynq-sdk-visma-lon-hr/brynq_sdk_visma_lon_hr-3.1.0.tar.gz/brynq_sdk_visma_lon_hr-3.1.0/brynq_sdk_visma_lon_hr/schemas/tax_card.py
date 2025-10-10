from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class TaxCardGet(BrynQPanderaDataFrameModel):
    """
    Schema for tax card data from Visma Lon HR.
    Represents tax card information from the VISMALØN table SKATTEKORT.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="TaxCardRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    tax_card_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Type of tax card ex. hovedkort (main) or bikort (secondary)", alias="TaxCardType")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Valid from", alias="StartDate")
    end_date: Series[datetime] = pa.Field(coerce=True, description="Valid to", alias="EndDate", nullable=True)
    tax_free_amount: Series[pd.StringDtype] = pa.Field(coerce=True, description="Tax free amount", alias="TaxFreeAmount", nullable=True)
    income_tax_rate: Series[pd.StringDtype] = pa.Field(coerce=True, description="Tax rate", alias="IncomeTaxRate", nullable=True)
    deduction_pr_day: Series[pd.StringDtype] = pa.Field(coerce=True, description="Daily deduction", alias="DeductionPrDay", nullable=True)
    deduction_pr_week: Series[pd.StringDtype] = pa.Field(coerce=True, description="Weekly deduction", alias="DeductionPrWeek", nullable=True)
    deduction_pr_14_day: Series[pd.StringDtype] = pa.Field(coerce=True, description="Bi weekly deduction", alias="DeductionPr14Day", nullable=True)
    deduction_pr_month: Series[pd.StringDtype] = pa.Field(coerce=True, description="Monthly deduction", alias="DeductionPrMonth", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    additional_income_tax_rate: Series[pd.StringDtype] = pa.Field(coerce=True, description="Extra additional tax rate", alias="AdditionalIncomeTaxRate", nullable=True)
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
            }
        }
