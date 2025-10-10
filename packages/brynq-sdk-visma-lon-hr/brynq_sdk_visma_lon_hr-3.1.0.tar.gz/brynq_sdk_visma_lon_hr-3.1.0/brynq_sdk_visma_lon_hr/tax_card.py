from typing import Optional, Union, List
import pandas as pd
from .schemas.tax_card import TaxCardGet

class TaxCard:
    """
    Handles tax card operations for Visma Lon HR API.
    TaxCard holds information about the tax information for the employee.
    """

    def __init__(self, visma_instance):
        """
        Initialize the TaxCard class.

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
        Get tax card data from Visma.

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
            entity_type="TaxCard",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=TaxCardGet
        )

    def get_by_id(self, tax_card_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific tax card record by its ID.

        Args:
            tax_card_id (str): The unique identifier of the tax card record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"TaxCardRID eq '{tax_card_id}'"
        return self.get(filter=filter_expression)
