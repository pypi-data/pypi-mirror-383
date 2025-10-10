from typing import Optional, Union, List
import pandas as pd
from .schemas.salary_comment import SalaryCommentGet

class SalaryComment:
    """
    Handles salary comment operations for Visma Lon HR API.
    SalaryComment holds information about comments for Employment.
    """

    def __init__(self, visma_instance):
        """
        Initialize the SalaryComment class.

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
        Get salary comment data from Visma.

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
            entity_type="SalaryComment",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=SalaryCommentGet
        )

    def get_by_id(self, salary_comment_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific salary comment record by its ID.

        Args:
            salary_comment_id (str): The unique identifier of the salary comment record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"SalaryCommentRID eq '{salary_comment_id}'"
        return self.get(filter=filter_expression)
