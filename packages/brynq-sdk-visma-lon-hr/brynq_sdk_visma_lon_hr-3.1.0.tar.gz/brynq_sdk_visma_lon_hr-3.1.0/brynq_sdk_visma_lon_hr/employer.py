from typing import Optional, Union, List
import pandas as pd
from .schemas.employer import EmployerGet

class Employer:
    """
    Handles employer operations for Visma Lon HR API.
    Employer holds information about employers registered under the CustomerID.
    """

    def __init__(self, visma_instance):
        """
        Initialize the Employer class.

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
        Get employer data from Visma.

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
            entity_type="Employer",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=EmployerGet
        )

    def get_by_id(self, employer_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific employer record by its ID.

        Args:
            employer_id (str): The unique identifier of the employer record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"EmployerRID eq '{employer_id}'"
        return self.get(filter=filter_expression)
