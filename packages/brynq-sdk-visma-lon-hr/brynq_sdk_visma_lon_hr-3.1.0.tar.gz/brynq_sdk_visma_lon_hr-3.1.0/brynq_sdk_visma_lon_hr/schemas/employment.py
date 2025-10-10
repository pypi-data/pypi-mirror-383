from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmploymentGet(BrynQPanderaDataFrameModel):
    """
    Schema for employment data from Visma Lon HR.
    Represents employment information from the VISMALØN table ANSFORHOLD.
    """

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="EmploymentRID")
    version_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Used to control the update of data (internal Datahub field)", alias="VersionNumber")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    employment_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment", alias="EmploymentID")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start date in Visma Løn", alias="StartDate")
    end_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Change or termination of Employment", alias="EndDate", nullable=True)
    from_date: Series[datetime] = pa.Field(coerce=True, description="From date", alias="FromDate", nullable=True)
    to_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="To date", alias="ToDate", nullable=True)
    organizational_unit_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Department ID", alias="OrganizationalUnitID", nullable=True)
    organizational_unit_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Department name", alias="OrganizationalUnitName", nullable=True)
    place_of_work_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="P-nummer if it deviates from the p-number registered on the employer", alias="PlaceOfWorkNumber", nullable=True)
    employment_designation: Series[pd.StringDtype] = pa.Field(coerce=True, description="Title", alias="EmploymentDesignation", nullable=True)
    payment_condition_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Position category", alias="PaymentConditionCode", nullable=True)
    wage_condition_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Prepaid, paid in arrears, hourly- or forthnightly paid", alias="WageConditionNumber", nullable=True)
    working_hour_numerator: Series[pd.StringDtype] = pa.Field(coerce=True, description="Number of employee working hours per month", alias="WorkingHourNumerator", nullable=True)
    working_hour_denominator: Series[pd.StringDtype] = pa.Field(coerce=True, description="Number of full time working hours per month or per forthnightly period", alias="WorkingHourDenominator", nullable=True)
    vacation_week: Series[pd.StringDtype] = pa.Field(coerce=True, description="Vacation week", alias="VacationWeek", nullable=True)
    salary_scale: Series[pd.StringDtype] = pa.Field(coerce=True, description="Pay scale", alias="SalaryScale", nullable=True)
    salary_step: Series[pd.StringDtype] = pa.Field(coerce=True, description="Salary step", alias="SalaryStep", nullable=True)
    wage_group_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Pay group", alias="WageGroupNumber", nullable=True)
    date_of_employment: Series[datetime] = pa.Field(coerce=True, description="Hire date", alias="DateOfEmployment", nullable=True)
    termination_date: Series[pd.StringDtype] = pa.Field(coerce=True, description="Termination date", alias="TerminationDate", nullable=True)
    customized_information1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional1", alias="CustomizedInformation1", nullable=True)
    customized_information2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional2", alias="CustomizedInformation2", nullable=True)
    customized_information3: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional3", alias="CustomizedInformation3", nullable=True)
    customized_information4: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional4", alias="CustomizedInformation4", nullable=True)
    customized_information5: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional5", alias="CustomizedInformation5", nullable=True)
    customized_information6: Series[pd.StringDtype] = pa.Field(coerce=True, description="Optional6", alias="CustomizedInformation6", nullable=True)
    auto_movement: Series[pd.StringDtype] = pa.Field(coerce=True, description="Auto movement", alias="AutoMovement", nullable=True)
    movement_code1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of table for movement in relation to use of Pay scale/salary step", alias="MovementCode1", nullable=True)
    movement_code2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of table for movement in relation to use of Pay scale/salary step", alias="MovementCode2", nullable=True)
    movement_code3: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of table for movement in relation to use of Pay scale/salary step", alias="MovementCode3", nullable=True)
    last_movement_date1: Series[datetime] = pa.Field(coerce=True, description="Date of last movement in relation to use of Pay scale/salary step", alias="LastMovementDate1", nullable=True)
    last_movement_date2: Series[datetime] = pa.Field(coerce=True, description="Date of last movement in relation to use of Pay scale/salary step", alias="LastMovementDate2", nullable=True)
    last_movement_date3: Series[datetime] = pa.Field(coerce=True, description="Date of last movement in relation to use of Pay scale/salary step", alias="LastMovementDate3", nullable=True)
    next_movement_date1: Series[datetime] = pa.Field(coerce=True, description="Date of next movement in relation to use of Pay scale/salary step", alias="NextMovementDate1", nullable=True)
    next_movement_date2: Series[datetime] = pa.Field(coerce=True, description="Date of next movement in relation to use of Pay scale/salary step", alias="NextMovementDate2", nullable=True)
    next_movement_date3: Series[datetime] = pa.Field(coerce=True, description="Date of next movement in relation to use of Pay scale/salary step", alias="NextMovementDate3", nullable=True)
    auto_movement_code1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Must the movement in relation to use of Pay scale/salary step be automatic? Ja (yes) or Nej (no)", alias="AutoMovementCode1", nullable=True)
    auto_movement_code2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Must the movement in relation to use of Pay scale/salary step be automatic? Ja (yes) or Nej (no)", alias="AutoMovementCode2", nullable=True)
    auto_movement_code3: Series[pd.StringDtype] = pa.Field(coerce=True, description="Must the movement in relation to use of Pay scale/salary step be automatic? Ja (yes) or Nej (no)", alias="AutoMovementCode3", nullable=True)
    job_function_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Job function number", alias="JobFunctionNumber", nullable=True)
    job_function_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Name of job function number", alias="JobFunctionName", nullable=True)
    occupation: Series[pd.StringDtype] = pa.Field(coerce=True, description="Position", alias="Occupation", nullable=True)
    internal_occupation_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Internal position code", alias="InternalOccupationCode", nullable=True)
    occupation_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Position type code", alias="OccupationTypeCode", nullable=True)
    change_reason_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Code for change reason", alias="ChangeReasonCode", nullable=True)
    internal_title_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Internal title code", alias="InternalTitleCode", nullable=True)
    work_plan_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Work plan code", alias="WorkPlanCode", nullable=True)
    skill_requirement_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Education requirement code", alias="SkillRequirementCode", nullable=True)
    extra_notice_person_month: Series[pd.StringDtype] = pa.Field(coerce=True, description="Extra termination notice employee", alias="ExtraNoticePersonMonth", nullable=True)
    extra_notice_company_month: Series[pd.StringDtype] = pa.Field(coerce=True, description="Extra termination notice company", alias="ExtraNoticeCompanyMonth", nullable=True)
    comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment", alias="Comment", nullable=True)
    payroll_run_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Payroll run number", alias="PayrollRunNumber", nullable=True)
    seniority2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Seniority date 2", alias="Seniority2", nullable=True)
    anniversary2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Anniversary date 2", alias="Anniversary2", nullable=True)
    resignation_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Termination reason code", alias="ResignationCode", nullable=True)
    employment_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employment type code", alias="EmploymentTypeCode", nullable=True)
    visma_loen_department: Series[pd.StringDtype] = pa.Field(coerce=True, description="Cost center", alias="VismaLoenDepartment", nullable=True)
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
            "organizational_unit_id": {
                "parent_schema": "OrganizationalUnitGet",
                "parent_column": "organizational_unit_id",
                "cardinality": "N:1"
            }
        }
