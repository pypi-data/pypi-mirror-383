from datetime import datetime
from typing import Union, Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class SalaryGet(BrynQPanderaDataFrameModel):
    """Schema for salary data from Visma Lon HR"""

    account_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Account number associated with the salary", alias="AccountNumber", nullable=True)
    amount: Series[pd.StringDtype] = pa.Field(coerce=True, description="Salary amount", alias="Amount")
    calculated_salary_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of the calculated salary", alias="CalculatedSalaryName")
    calculated_salary_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Number identifying the calculated salary", alias="CalculatedSalaryNumber")
    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Resource identifier for the calculated salary", alias="CalculatedSalaryRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID associated with this salary", alias="CustomerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee ID for whom the salary is recorded", alias="EmployeeID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer ID associated with this salary", alias="EmployerID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment ID associated with this salary", alias="EmploymentID")
    made_by_adjustment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Indicator if the salary was made by adjustment", alias="MadeByAdjustment")
    original_payroll_run_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Original payroll run number", alias="OriginalPayrollRunNumber")
    original_payroll_selection_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Original payroll selection number", alias="OriginalPayrollSelectionNumber")
    pay_period_end: Series[datetime] = pa.Field(coerce=True, description="End date of the pay period", alias="PayPeriodEnd")
    pay_period_start: Series[datetime] = pa.Field(coerce=True, description="Start date of the pay period", alias="PayPeriodStart")
    pay_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Code for the type of pay", alias="PayTypeCode")
    payroll_run_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Payroll run number", alias="PayrollRunNumber")
    payroll_selection_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Payroll selection number", alias="PayrollSelectionNumber")
    registration_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Registration number", alias="RegistrationNumber")
    transaction_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Type of transaction", alias="TransactionType")
    value1: Series[pd.StringDtype] = pa.Field(coerce=True, description="First value associated with the salary", alias="Value1", nullable=True)
    value2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Second value associated with the salary", alias="Value2", nullable=True)
    value3: Series[pd.StringDtype] = pa.Field(coerce=True, description="Third value associated with the salary", alias="Value3", nullable=True)
    value4: Series[pd.StringDtype] = pa.Field(coerce=True, description="Fourth value associated with the salary", alias="Value4", nullable=True)
    value5: Series[pd.StringDtype] = pa.Field(coerce=True, description="Fifth value associated with the salary", alias="Value5", nullable=True)
    value6: Series[pd.StringDtype] = pa.Field(coerce=True, description="Sixth value associated with the salary", alias="Value6", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Version number of the record", alias="VersionNumber")

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
            "pay_type_code": {
                "parent_schema": "PayTypeGet",
                "parent_column": "pay_type_code",
                "cardinality": "N:1"
            }
        }
