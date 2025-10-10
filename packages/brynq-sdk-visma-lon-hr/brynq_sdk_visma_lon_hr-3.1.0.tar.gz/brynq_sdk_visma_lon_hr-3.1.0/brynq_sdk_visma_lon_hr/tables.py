from typing import Union, Optional, List
import pandas as pd
import requests
import xmltodict
from .utils import clean_column_names, handle_duplicate_columns

class Tables:
    """
    Handles table operations for Visma Lon HR API.

    The Tables class provides a generic interface to access any table in the Visma Lon HR system.
    Unlike specific resource classes (like Employee, Absence, etc.), this class allows you to query
    any table by name without needing a predefined schema or resource class.

    Key Features:
    - Generic table access: Query any table by name
    - Flexible filtering: Use OData filter expressions
    - Pagination support: Handle large datasets with top/skip parameters
    - Ordering: Sort results by any column(s)
    - No schema validation: Returns raw data without Pandera validation
    - Direct API access: Bypasses the standard resource class structure

    Use Cases:
    - Accessing tables not covered by specific resource classes
    - Quick data exploration and testing
    - Custom queries that don't fit standard patterns
    - Administrative tasks requiring direct table access

    Note: This class returns raw DataFrames without validation. For production use,
    consider using specific resource classes with proper schema validation.
    """

    def __init__(self, visma_instance):
        """
        Initialize the Tables class.

        Args:
            visma_instance: The Visma class instance for API access.
        """
        self.visma = visma_instance

    def get(self,
            table_name: str,
            filter: Optional[str] = None,
            orderby: Optional[Union[List[str], str]] = None,
            top: Optional[int] = None,
            skip: Optional[int] = None,
            skiptoken: Optional[str] = None,
            max_pages: Optional[int] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get data from a specified table in Visma Lon HR.

        This method provides direct access to any table in the Visma Lon HR system.
        It bypasses the standard resource class structure and allows you to query
        tables that may not have dedicated resource classes.

        Args:
            table_name (str): Name of the table to query. Examples:
                - "Employee" - Employee table
                - "Absence" - Absence table
                - "Payroll" - Payroll table
                - "Customer" - Customer table
                - Any other table name in the Visma system

            filter (str, optional): OData filter expression for filtering results.
                Examples:
                - "EmployeeID eq '123'"
                - "StartDate gt 2024-01-01"
                - "FirstName eq 'John' and LastName eq 'Doe'"
                Defaults to None (no filtering).

            orderby (Union[List[str], str], optional): Column(s) to order results by.
                Examples:
                - "EmployeeID" (single column)
                - ["LastName", "FirstName"] (multiple columns)
                - "CreateTime desc" (descending order)
                Defaults to None (no ordering).

            top (int, optional): Maximum number of records to return.
                Useful for limiting results and improving performance.
                Defaults to None (return all records).

            skip (int, optional): Number of records to skip from the beginning.
                Used with 'top' for pagination.
                Defaults to None (start from beginning).

            skiptoken (str, optional): Token for continuing a paged request.
                Used when the previous request was truncated due to 'top' limit.
                Defaults to None (start fresh request).

            max_pages (int, optional): Maximum number of pages to fetch in a single call.
                Helps prevent excessive API calls for very large datasets.
                Defaults to None (fetch all pages).

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
                - valid_data: DataFrame with successfully processed records
                - invalid_data: DataFrame with records that failed validation

        Raises:
            ValueError: If table_name is empty or invalid
            ConnectionError: If unable to connect to Visma API
            Exception: For other API-related errors

        Examples:
            # Get all employees
            valid_data, invalid_data = visma.tables.get("Employee")

            # Get employees with specific filter
            valid_data, invalid_data = visma.tables.get(
                "Employee",
                filter="FirstName eq 'John'"
            )

            # Get first 100 employees ordered by last name
            valid_data, invalid_data = visma.tables.get(
                "Employee",
                orderby="LastName",
                top=100
            )

            # Get employees with pagination
            valid_data, invalid_data = visma.tables.get(
                "Employee",
                top=50,
                skip=100
            )
        """
        return self.visma.get(
            entity_type=f'{table_name}',
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages
        )
