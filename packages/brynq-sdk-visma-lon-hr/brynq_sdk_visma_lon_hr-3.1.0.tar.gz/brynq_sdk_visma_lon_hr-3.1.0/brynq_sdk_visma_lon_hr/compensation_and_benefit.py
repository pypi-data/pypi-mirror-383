from typing import Optional, Union, List
import pandas as pd
from .schemas.compensation_and_benefit import CompensationAndBenefitGet

class CompensationAndBenefit:
    """
    Handles compensation and benefit operations for Visma Lon HR API.
    CompensationAndBenefit holds information about wage types that will be a part of a future payroll,
    from the VISMALØN tables ANSLOENOPLYSNING and ANSLOENOPLPARAM.
    """

    def __init__(self, visma_instance):
        """
        Initialize the CompensationAndBenefit class.

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
        Get compensation and benefit data from Visma.

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
            entity_type="CompensationAndBenefit",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=CompensationAndBenefitGet
        )

    def get_by_id(self, compensation_and_benefit_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific compensation and benefit record by its ID.

        Args:
            compensation_and_benefit_id (str): The unique identifier of the compensation and benefit record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"CompensationAndBenefitRID eq '{compensation_and_benefit_id}'"
        return self.get(filter=filter_expression)
