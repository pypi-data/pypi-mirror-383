from typing import Optional, Union, List
import pandas as pd
from .schemas.pay_type import PayTypeGet

class PayType:
    """
    Handles pay type operations for Visma Lon HR API.
    PayType holds information about wage types from the VISMALØN table LOENART.
    """

    def __init__(self, visma_instance):
        """
        Initialize the PayType class.

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
        Get pay type data from Visma.

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
            entity_type="PayType",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=PayTypeGet
        )

    def get_by_id(self, pay_type_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific pay type record by its ID.

        Args:
            pay_type_id (str): The unique identifier of the pay type record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"PayTypeRID eq '{pay_type_id}'"
        return self.get(filter=filter_expression)
