from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class CompensationAndBenefitGet(BrynQPanderaDataFrameModel):
    """
    Schema for compensation and benefit data from Visma Lon HR.
    Represents wage types that will be a part of a future payroll from ANSLOENOPLYSNING and ANSLOENOPLPARAM tables.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="CompensationAndBenefitRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment ID", alias="EmploymentID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="End date", alias="EndDate")
    pay_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Wage type number", alias="PayTypeCode")
    name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Text that describes the wage type", alias="CompensationAndBenefitName", nullable=True)
    pay_type_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Type of wage type", alias="PayTypeType", nullable=True)
    frequency: Series[pd.StringDtype] = pa.Field(coerce=True, description="Frequency", alias="Frequency", nullable=True)
    use_after: Series[pd.StringDtype] = pa.Field(coerce=True, description="To be paid out after a specific date", alias="UseAfter", nullable=True)
    units: Series[pd.StringDtype] = pa.Field(coerce=True, description="Units, number of units to be paid out", alias="Units", nullable=True)
    rate: Series[pd.StringDtype] = pa.Field(coerce=True, description="The rate to calculate the payout", alias="Rate", nullable=True)
    amount: Series[pd.StringDtype] = pa.Field(coerce=True, description="The amount to pay out", alias="Amount", nullable=True)
    pension_own_percent: Series[pd.StringDtype] = pa.Field(coerce=True, description="Pension own percentage", alias="PensionOwnPercent", nullable=True)
    do_not_reduce: Series[pd.StringDtype] = pa.Field(coerce=True, description="If the amount on the wage type is to be reduced if the employee is on paid leave", alias="DoNotReduce", nullable=True)
    pension_company_amount: Series[pd.StringDtype] = pa.Field(coerce=True, description="Pension company amount", alias="PensionCompanyAmount", nullable=True)
    pension_company_percent: Series[pd.StringDtype] = pa.Field(coerce=True, description="Pension company percent", alias="PensionCompanyPercent", nullable=True)
    pension_basis: Series[pd.StringDtype] = pa.Field(coerce=True, description="Basis to calculate the pension", alias="PensionBasis", nullable=True)
    balance: Series[pd.StringDtype] = pa.Field(coerce=True, description="Balance", alias="Balance", nullable=True)
    year: Series[pd.StringDtype] = pa.Field(coerce=True, description="Year", alias="Year", nullable=True)
    input_value: Series[pd.StringDtype] = pa.Field(coerce=True, description="Input value", alias="InputValue", nullable=True)
    registration_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Registration number", alias="RegistrationNumber", nullable=True)
    account_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Account number", alias="AccountNumber", nullable=True)
    settling_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Transaction code for pension company", alias="SettlingType", nullable=True)
    approve_item_status: Series[pd.StringDtype] = pa.Field(coerce=True, description="Status for approval", alias="ApproveItemStatus", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    historik: Series[pd.StringDtype] = pa.Field(coerce=True, description="Timestamp for creating the registration", alias="Historik", nullable=True)
    used: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used", alias="Used", nullable=True)
    settlement_method: Series[pd.StringDtype] = pa.Field(coerce=True, description="Method of settlement", alias="SettlementMethod", nullable=True)
    settlement_type: Series[pd.StringDtype] = pa.Field(coerce=True, description="Number for settlement type", alias="SettlementType", nullable=True)
    disapproval_comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment for rejection", alias="DisapprovalComment", nullable=True)
    change_reason_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Code for change reason", alias="ChangeReasonCode", nullable=True)
    comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment", alias="Comment", nullable=True)

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
