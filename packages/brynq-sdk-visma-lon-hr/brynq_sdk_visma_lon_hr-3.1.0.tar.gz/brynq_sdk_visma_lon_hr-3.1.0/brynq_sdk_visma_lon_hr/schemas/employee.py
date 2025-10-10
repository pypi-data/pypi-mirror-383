from datetime import datetime
from typing import Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmployeeGet(BrynQPanderaDataFrameModel):
    """Schema for employee data from Visma Lon HR"""

    rid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Unique key for use of OData", alias="EmployeeRID")
    customer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Customer ID", alias="CustomerID")
    employer_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employer number", alias="EmployerID")
    employee_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee number", alias="EmployeeID")
    first_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="First name of employee", alias="FirstName", nullable=True)
    last_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Last name of employee", alias="LastName", nullable=True)
    address_line1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee address", alias="AddressLine1", nullable=True)
    address_line2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Supplementary address information for employee", alias="AddressLine2", nullable=True)
    postal_code_dk: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee postal code", alias="PostalCodeDK", nullable=True)
    postal_district_dk: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee city name", alias="PostalDistrictDK", nullable=True)
    private_phone_number1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Private phone number", alias="PrivatePhoneNumber1", nullable=True)
    private_phone_number2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Alternative private phone number", alias="PrivatePhoneNumber2", nullable=True)
    company_phone_number1: Series[pd.StringDtype] = pa.Field(coerce=True, description="Direct company phone number", alias="CompanyPhoneNumber1", nullable=True)
    company_phone_number2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Mobile company phone number", alias="CompanyPhoneNumber2", nullable=True)
    company_email: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee work e-mail address", alias="CompanyEmail", nullable=True)
    private_email: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee private e-mail address", alias="PrivateEmail", nullable=True)
    initials: Series[pd.StringDtype] = pa.Field(coerce=True, description="Initials", alias="Initials", nullable=True)
    social_security_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="CPR-number", alias="SocialSecurityNumber", nullable=True)
    postal_code_int: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee foreign postal code", alias="PostalCodeInt", nullable=True)
    postal_district_int: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee foreign city name", alias="PostalDistrictInt", nullable=True)
    country_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Country code for tax registration", alias="CountryCode", nullable=True)
    country: Series[pd.StringDtype] = pa.Field(coerce=True, description="Country name", alias="Country", nullable=True)
    first_hired_date: Series[datetime] = pa.Field(coerce=True, description="Date of first employment", alias="FirstHiredDate", nullable=True)
    seniority: Series[pd.StringDtype] = pa.Field(coerce=True, description="Number of years, months and days employed (Format YYMMDD)", alias="Seniority", nullable=True)
    eboks: Series[pd.StringDtype] = pa.Field(coerce=True, description="Defines whether the employee receives the payslip in eBoks", alias="Eboks", nullable=True)
    registration_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee bank registration number", alias="RegistrationNumber", nullable=True)
    account_number: Series[pd.StringDtype] = pa.Field(coerce=True, description="Employee bank account number", alias="AccountNumber", nullable=True)
    email2: Series[pd.StringDtype] = pa.Field(coerce=True, description="Email (Private)", alias="Email2", nullable=True)
    birth_date: Series[datetime] = pa.Field(coerce=True, description="Date of birth", alias="BirthDate", nullable=True)
    gender: Series[pd.StringDtype] = pa.Field(coerce=True, description="Gender", alias="Gender", nullable=True)
    state_country_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Citizenship", alias="StateCountryCode", nullable=True)
    birth_country_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Country of birth", alias="BirthCountryCode", nullable=True)
    default_calendar_code: Series[pd.StringDtype] = pa.Field(coerce=True, description="Default Calendar code", alias="DefaultCalendarCode", nullable=True)
    comment: Series[pd.StringDtype] = pa.Field(coerce=True, description="Comment", alias="Comment", nullable=True)
    calling_name: Series[pd.StringDtype] = pa.Field(coerce=True, description="Nickname", alias="CallingName", nullable=True)
    social_security_number_abroad: Series[pd.StringDtype] = pa.Field(coerce=True, description="Foreign CPR-Number", alias="SocialSecurityNumberAbroad", nullable=True)
    verification_date: Series[datetime] = pa.Field(coerce=True, description="Date for validation of Registration/account number", alias="VerificationDate", nullable=True)
    nem_account: Series[pd.StringDtype] = pa.Field(coerce=True, description="Code for NemKonto", alias="NemAccount", nullable=True)
    salary_seniority_from: Series[datetime] = pa.Field(coerce=True, description="Salary seniority date", alias="SalarySeniorityFrom", nullable=True)
    salary_computed: Series[pd.StringDtype] = pa.Field(coerce=True, description="Part of payroll", alias="SalaryComputed", nullable=True)
    social_security_number_validated: Series[pd.StringDtype] = pa.Field(coerce=True, description="CPR number validation", alias="SocialSecurityNumberValidated", nullable=True)
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
            }
        }
