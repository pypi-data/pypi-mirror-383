from typing import Union, List, Optional, Literal
import requests
from requests import session
import pandas as pd
import xmltodict
import asyncio
import aiohttp
import urllib.parse

from brynq_sdk_brynq import BrynQ
from .absence import Absence
from .customer import Customer
from .employer import Employer
from .employment import Employment
from .salary import Salary
from .tables import Tables
from .employee import Employee
import os
from brynq_sdk_functions import Functions
from .utils import parse_xml_to_df
from .compensation_and_benefit import CompensationAndBenefit
from .course import Course
from .course_supplier import CourseSupplier
from .employee_qualification import EmployeeQualification
from .organization import Organization
from .organizational_unit import OrganizationalUnit
from .payroll import Payroll
from .pay_type import PayType
from .course_calendar import CourseCalendar
from .employment_classification import EmploymentClassification
from .payment_condition_classification import PaymentConditionClassification
from .content_type import ContentType
from .classification import Classification
from .tax_card import TaxCard
from .processed_absence import ProcessedAbsence
from .processed_absence_group import ProcessedAbsenceGroup
from .posted_accounting import PostedAccounting
from .phone_number import PhoneNumber
from .salary_comment import SalaryComment
from .work_calendar import WorkCalendar



class Visma(BrynQ):
    """
    A class to interact with Visma Lon HR API.
    """

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        """
        Initialize the Visma class.

        Args:
            subdomain (str, optional): BrynQ subdomain. Defaults to None (will use environment variable).
            api_token (str, optional): BrynQ API token. Defaults to None (will use environment variable).
            staging (str, optional): BrynQ environment. Defaults to 'prod'.
        """

        super().__init__()
        self.debug = debug
        self.base_url = "https://datahub.vismaenterprise.dk/datahub/V2/mainservice.svc/"
        credentials = self.interfaces.credentials.get(system="visma-lon-hr", system_type=system_type)
        self.api_key = credentials["data"]["api_key"]
        self.session = requests.Session()

        # Initialize components
        self.tables = Tables(self)
        self.employees = Employee(self)
        self.absences = Absence(self)
        self.customers = Customer(self)
        self.employer = Employer(self)
        self.employment = Employment(self)
        self.salary = Salary(self)
        self.compensation_and_benefit = CompensationAndBenefit(self)
        self.course = Course(self)
        self.course_supplier = CourseSupplier(self)
        self.employee_qualification = EmployeeQualification(self)
        self.organization = Organization(self)
        self.organizational_unit = OrganizationalUnit(self)
        self.payroll = Payroll(self)
        self.pay_type = PayType(self)
        self.course_calendar = CourseCalendar(self)
        self.employment_classification = EmploymentClassification(self)
        self.payment_condition_classification = PaymentConditionClassification(self)
        self.content_type = ContentType(self)
        self.classification = Classification(self)
        self.tax_card = TaxCard(self)
        self.processed_absence = ProcessedAbsence(self)
        self.processed_absence_group = ProcessedAbsenceGroup(self)
        self.posted_accounting = PostedAccounting(self)
        self.phone_number = PhoneNumber(self)
        self.salary_comment = SalaryComment(self)
        self.work_calendar = WorkCalendar(self)

    def get_url(self,
                entity_type: str,
                filter: Optional[str] = None,
                orderby: Optional[Union[List[str], str]] = None,
                top: Optional[int] = None,
                skip: Optional[int] = None,
                skiptoken: Optional[str] = None) -> str:
        """
        Get the full URL for an entity type with all supported query options.
        Ensures the subscription key is always the last parameter.

        Args:
            entity_type (str): The entity type to get the URL for.
            filter (str, optional): OData filter expression. Defaults to None.
            orderby (Union[List[str], str], optional): Columns to order by. Can be a comma-separated string or list of strings. Defaults to None.
            top (int, optional): Number of records to return. Defaults to None.
            skip (int, optional): Number of records to skip. Defaults to None.
            skiptoken (str, optional): Token for continuing a paged request. Defaults to None.

        Returns:
            str: The full URL with all query parameters.
        """
        # Start with base URL
        base_url = f"{self.base_url}{entity_type}"

        # Build query parameters (without subscription key)
        query_params = []

        # Add filter if provided
        if filter:
            encoded_filter = urllib.parse.quote(filter)
            query_params.append(f"$filter={encoded_filter}")

        # Add orderby if provided
        if orderby:
            if isinstance(orderby, list):
                orderby = ",".join(orderby)
            query_params.append(f"$orderby={orderby}")

        # Add top if provided
        if top is not None:
            query_params.append(f"$top={top}")

        # Add skip if provided
        if skip is not None:
            query_params.append(f"$skip={skip}")

        # Add skiptoken if provided
        if skiptoken:
            query_params.append(f"$skiptoken={skiptoken}")

        # Add subscription key as the last parameter
        if query_params:
            return f"{base_url}?{'&'.join(query_params)}"
        else:
            return base_url

    async def _fetch_all_pages(self,
                              entity_type: str,
                              filter: Optional[str] = None,
                              orderby: Optional[Union[List[str], str]] = None,
                              top: Optional[int] = None,
                              skip: Optional[int] = None,
                              skiptoken: Optional[str] = None,
                              max_pages: Optional[int] = None) -> list:
        """
        Asynchronously fetch all pages of data for an entity type.

        Args:
            entity_type (str): The entity type to fetch.
            filter (str, optional): OData filter expression. Defaults to None.
            orderby (Union[List[str], str], optional): Columns to order by. Defaults to None.
            top (int, optional): Number of records to return. Defaults to None.
            skip (int, optional): Number of records to skip. Defaults to None.
            skiptoken (str, optional): Token for continuing a paged request. Defaults to None.
            max_pages (int, optional): Maximum number of pages to fetch. Defaults to None (all pages).

        Returns:
            list: A list of all entries.
        """
        all_entries = []
        page_count = 0
        next_url = self.get_url(entity_type, filter, orderby, top, skip, skiptoken)

        async with aiohttp.ClientSession() as session:
            while True:
                # Check if we've reached the maximum number of pages
                if max_pages is not None and page_count >= max_pages:
                    break

                # Fetch the current page
                headers = {'subscription-key': self.api_key}
                async with session.get(next_url, headers=headers) as response:

                    response.raise_for_status()
                    content = await response.text()
                    data_dict = xmltodict.parse(content)

                # Check if there are entries
                if 'feed' not in data_dict or 'entry' not in data_dict['feed']:
                    break

                # Process entries
                entries = data_dict['feed']['entry']
                if not isinstance(entries, list):
                    entries = [entries]  # Convert single entry to list
                all_entries.extend(entries)
                page_count += 1

                # Find the next page link
                next_link = None
                if 'link' in data_dict['feed']:
                    links = data_dict['feed']['link']
                    if isinstance(links, list):
                        for link in links:
                            if link.get('@rel') == 'next':
                                next_link = link.get('@href')
                                break
                    elif isinstance(links, dict) and links.get('@rel') == 'next':
                        next_link = links.get('@href')

                if not next_link:
                    break  # No more pages

                next_url = next_link

        return all_entries

    def get(self,
            entity_type: str,
            filter: Optional[str] = None,
            orderby: Optional[Union[List[str], str]] = None,
            top: Optional[int] = None,
            skip: Optional[int] = None,
            skiptoken: Optional[str] = None,
            max_pages: Optional[int] = None,
            schema = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetch all data from a specified entity type with pagination and filtering support.

        Args:
            entity_type (str): The entity type to fetch (e.g., "Employee").
            filter (str, optional): Data filter expression. Defaults to None.
            orderby (Union[List[str], str], optional): Columns to order by. Defaults to None.
            top (int, optional): Number of records to return. Defaults to None.
            skip (int, optional): Number of records to skip. Defaults to None.
            skiptoken (str, optional): Token for continuing a paged request. Defaults to None.
            max_pages (int, optional): Maximum number of pages to fetch. Defaults to None (all pages).
            schema (BrynQPanderaDataFrameModel, optional): Schema to validate the data against. Defaults to None.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        # Run the async function in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            all_entries = loop.run_until_complete(
                self._fetch_all_pages(entity_type=entity_type, filter=filter, orderby=orderby, top=top, skip=skip, skiptoken=skiptoken, max_pages=max_pages)
            )
        finally:
            loop.close()

        if not all_entries:
            return pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames if no entries

        # Convert entries to DataFrame
        df_data = pd.DataFrame(parse_xml_to_df(all_entries))

        # Validate with schema if provided
        if schema:
            # Use brynq_sdk_functions.validate_data for Pandera validation
            valid_data, invalid_data = Functions.validate_data(df=df_data, schema=schema)
            return valid_data, invalid_data

        return df_data, pd.DataFrame()
