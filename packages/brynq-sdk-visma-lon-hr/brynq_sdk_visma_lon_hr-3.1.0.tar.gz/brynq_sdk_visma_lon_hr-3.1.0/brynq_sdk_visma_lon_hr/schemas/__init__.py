"""Schema definitions for Visma Lon HR package"""

# Import schemas
from .absence import AbsenceGet
from .absence_group import AbsenceGroupGet
from .absence_type import AbsenceTypeGet
from .classification import ClassificationGet
from .compensation_and_benefit import CompensationAndBenefitGet
from .content_type import ContentTypeGet
from .course import CourseGet
from .course_calendar import CourseCalendarGet
from .course_supplier import CourseSupplierGet
from .customer import CustomerGet
from .employee import EmployeeGet
from .employee_qualification import EmployeeQualificationGet
from .employer import EmployerGet
from .employment import EmploymentGet
from .employment_classification import EmploymentClassificationGet
from .organization import OrganizationGet
from .organizational_unit import OrganizationalUnitGet
from .pay_type import PayTypeGet
from .payment_condition_classification import PaymentConditionClassificationGet
from .payroll import PayrollGet
from .phone_number import PhoneNumberGet
from .posted_accounting import PostedAccountingGet
from .processed_absence import ProcessedAbsenceGet
from .processed_absence_group import ProcessedAbsenceGroupGet
from .salary import SalaryGet
from .salary_comment import SalaryCommentGet
from .tax_card import TaxCardGet
from .work_calendar import WorkCalendarGet

__all__ = [
    'AbsenceGet',
    'AbsenceGroupGet',
    'AbsenceTypeGet',
    'ClassificationGet',
    'CompensationAndBenefitGet',
    'ContentTypeGet',
    'CourseGet',
    'CourseCalendarGet',
    'CourseSupplierGet',
    'CustomerGet',
    'EmployeeGet',
    'EmployeeQualificationGet',
    'EmployerGet',
    'EmploymentGet',
    'EmploymentClassificationGet',
    'OrganizationGet',
    'OrganizationalUnitGet',
    'PayTypeGet',
    'PaymentConditionClassificationGet',
    'PayrollGet',
    'PhoneNumberGet',
    'PostedAccountingGet',
    'ProcessedAbsenceGet',
    'ProcessedAbsenceGroupGet',
    'SalaryGet',
    'SalaryCommentGet',
    'TaxCardGet',
    'WorkCalendarGet',
]
