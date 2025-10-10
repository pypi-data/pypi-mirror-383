from typing import Optional, Union, List
import pandas as pd
from .schemas.organization import OrganizationGet

class Organization:
    """
    Handles organization operations for Visma Lon HR API.
    Organization holds information about the top level in the organizations described in the datamodel
    from the VISMALØN table ARBEJDSGIVER or Visma HR table Company.
    """

    def __init__(self, visma_instance):
        """
        Initialize the Organization class.

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
        Get organization data from Visma.

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
            entity_type="Organization",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=OrganizationGet
        )

    def get_by_id(self, organization_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific organization record by its ID.

        Args:
            organization_id (str): The unique identifier of the organization record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"OrganizationRID eq '{organization_id}'"
        return self.get(filter=filter_expression)
