from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class PostedAccountingGet(BrynQPanderaDataFrameModel):
    """
    Schema for posted accounting data from Visma Lon HR.
    Represents posted accounting information from the VISMALØN table KOERSELSSELEKTION.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="PostedAccountingRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment", alias="EmploymentID")
    accounting_serial_number1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Accounting serial number", alias="AccountingSerialNumber1")
    accounting_serial_number2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Secondary accounting number", alias="AccountingSerialNumber2", nullable=True)
    breakdown_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Break down number", alias="BreakdownNumber", nullable=True)
    calculated_salary_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Calculated salary number", alias="CalculatedSalaryNumber", nullable=True)
    pay_period_start: Series[datetime] = pa.Field(coerce=True, description="Start date of the payroll period", alias="PayPeriodStart")
    pay_period_end: Series[datetime] = pa.Field(coerce=True, description="End date of the payroll period", alias="PayPeriodEnd")
    payroll_run_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Payroll run number", alias="PayrollRunNumber")
    account_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Account number for bookkeeping", alias="AccountNumber", nullable=True)
    account_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Account name for bookkeeping", alias="AccountName", nullable=True)
    amount: Series[pd.StringDtype] = pa.Field(coerce=True, description="Amount", alias="Amount", nullable=True)
    rate: Series[pd.StringDtype] = pa.Field(coerce=True, description="Rate for payout", alias="Rate", nullable=True)
    debit_credit_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="D=Debet/K=Credit", alias="DebitCreditCode", nullable=True)
    organizational_unit_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Organisation ID", alias="OrganizationalUnitID", nullable=True)
    udbetalings_sted_nr: Series[pd.StringDtype] = pa.Field(coerce=True, description="Subsection number", alias="UdbetalingsStedNr", nullable=True)
    payment_condition_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Position category", alias="PaymentConditionCode", nullable=True)
    wage_group_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Pay group", alias="WageGroupNumber", nullable=True)
    salary_scale: Series[pd.StringDtype] = pa.Field(coerce=True, description="Pay scale", alias="SalaryScale", nullable=True)
    salary_step: Series[pd.StringDtype] = pa.Field(coerce=True, description="Salary step", alias="SalaryStep", nullable=True)
    customized_information1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional1", alias="CustomizedInformation1", nullable=True)
    customized_information2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional2", alias="CustomizedInformation2", nullable=True)
    customized_information3: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional3", alias="CustomizedInformation3", nullable=True)
    customized_information4: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional4", alias="CustomizedInformation4", nullable=True)
    customized_information5: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional5", alias="CustomizedInformation5", nullable=True)
    customized_information6: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional6", alias="CustomizedInformation6", nullable=True)
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    pay_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Wage type number", alias="PayTypeCode", nullable=True)
    wage_condition_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Paid in arrear, paid in advance, hourly or forthnightly paid", alias="WageConditionNumber", nullable=True)
    value: Series[pd.StringDtype] = pa.Field(coerce=True, description="Value", alias="Value", nullable=True)
    created_by_payroll: Series[pd.StringDtype] = pa.Field(coerce=True, description="Created by payroll", alias="CreatedByPayroll", nullable=True)
    coa_organizational_unit_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Department or input constant from account plan", alias="COA_OrganizationalUnitID", nullable=True)
    coa_udbetalingsstednr: Series[pd.StringDtype] = pa.Field(coerce=True, description="Subsection if Finans is marked with a udbetalingskode", alias="COA_UDBETALINGSSTEDNR", nullable=True)
    coa_input_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Inputvalue if this is chosen to be shown in the account plan", alias="COA_InputCode", nullable=True)
    coa_employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employeenumber if this is chosen to be shown in the account plan", alias="COA_EmployeeID", nullable=True)
    chart_of_accounts: Series[pd.StringDtype] = pa.Field(coerce=True, description="Account plan number / name", alias="ChartOfAccounts", nullable=True)
    salary_distributed: Series[pd.StringDtype] = pa.Field(coerce=True, description="If values are distributet between ex. department / pct", alias="SalaryDistributed", nullable=True)
    settlement_method: Series[pd.StringDtype] = pa.Field(coerce=True, description="Only deduction wage types with reg/bank accountnumber can have the code BC", alias="SettlementMethod", nullable=True)
    use_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="How the wage type must be shown in connection to output", alias="UseCode", nullable=True)
    printed_on_payslip: Series[pd.StringDtype] = pa.Field(coerce=True, description="Wage type show on the payslip", alias="PrintedOnPayslip", nullable=True)
    pension_year_mark: Series[pd.StringDtype] = pa.Field(coerce=True, description="Value = 1 moves the settlement from current year to first bank day in the new year", alias="PensionYearMark", nullable=True)
    selected_date: Series[datetime] = pa.Field(coerce=True, description="Accounting date", alias="SelectedDate", nullable=True)
    visma_loen_department: Series[pd.StringDtype] = pa.Field(coerce=True, description="Department", alias="VismaLoenDepartment", nullable=True)

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
            "organizational_unit_id": {
                "parent_schema": "OrganizationalUnitGet",
                "parent_column": "organizational_unit_rid",
                "cardinality": "N:1"
            },
            "pay_type_code": {
                "parent_schema": "PayTypeGet",
                "parent_column": "pay_type_code",
                "cardinality": "N:1"
            }
        }
