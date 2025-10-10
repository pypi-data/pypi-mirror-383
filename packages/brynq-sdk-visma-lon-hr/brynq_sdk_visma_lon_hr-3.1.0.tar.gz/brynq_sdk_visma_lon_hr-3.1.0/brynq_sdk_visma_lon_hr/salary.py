from typing import Optional, Union, List
import pandas as pd
import xmltodict
from .utils import parse_xml_to_df
from .schemas.salary import SalaryGet

class Salary:
    """
    Handles salary operations for Visma Lon HR API.
    """

    def __init__(self, visma_instance):
        """
        Initialize the Salary class.

        Args:
            visma_instance: The Visma class instance.
        """
        self.visma = visma_instance

    def get(self,
            filter: Optional[str] = None,
            orderby: Optional[Union[List[str], str]] = None,
            top: Optional[int] = None,
            skip: Optional[int] = None,
            skiptoken: Optional[str] = None,
            max_pages: Optional[int] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get salary data from Visma.

        Args:
            filter (str, optional): OData filter expression. Defaults to None.
            orderby (Union[List[str], str], optional): Columns to order by. Defaults to None.
            top (int, optional): Number of records to return. Defaults to None.
            skip (int, optional): Number of records to skip. Defaults to None.
            skiptoken (str, optional): Token for continuing a paged request. Defaults to None.
            max_pages (int, optional): Maximum number of pages to fetch. Defaults to None (all pages).

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        return self.visma.get(
            entity_type="CalculatedSalary",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=SalaryGet
        )

    def get_by_id(self, salary_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific salary record by its ID.

        Args:
            salary_id (str): The unique identifier of the salary record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"CalculatedSalaryRID eq '{salary_id}'"
        return self.get(filter=filter_expression)
