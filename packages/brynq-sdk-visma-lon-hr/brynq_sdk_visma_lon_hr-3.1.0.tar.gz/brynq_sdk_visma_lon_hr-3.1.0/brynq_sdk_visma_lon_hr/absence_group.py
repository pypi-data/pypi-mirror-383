from typing import Optional, Union, List
import pandas as pd
from .schemas.absence_group import AbsenceGroupGet

class AbsenceGroup:
    """
    Handles absence group operations for Visma Lon HR API.
    AbsenceGroup holds information about absence that is not yet processed in a payroll,
    from the VISMALØN table FRAVAERSPOSTERING.
    """

    def __init__(self, visma_instance):
        """
        Initialize the AbsenceGroup class.

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
        Get absence group data from Visma.

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
            entity_type="AbsenceGroup",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=AbsenceGroupGet
        )

    def get_by_id(self, absence_group_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific absence group record by its ID.

        Args:
            absence_group_id (str): The unique identifier of the absence group record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"AbsenceGroupRID eq '{absence_group_id}'"
        return self.get(filter=filter_expression)
