from typing import Optional, Union, List
import pandas as pd
from .schemas.course import CourseGet
from .course_supplier import CourseSupplier
from .course_calendar import CourseCalendar

class Course:
    """
    Handles course operations for Visma Lon HR API.
    Course holds information about courses from the Visma HR table Course.
    """

    def __init__(self, visma_instance):
        """
        Initialize the Course class.

        Args:
            visma_instance: The Visma class instance.
        """
        self.visma = visma_instance
        self.supplier = CourseSupplier(visma_instance)
        self.calendar = CourseCalendar(visma_instance)

    def get(self,
            filter: Optional[str] = None,
            orderby: Optional[Union[List[str], str]] = None,
            top: Optional[int] = None,
            skip: Optional[int] = None,
            skiptoken: Optional[str] = None,
            max_pages: Optional[int] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get course data from Visma.

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
            entity_type="Course",
            filter=filter,
            orderby=orderby,
            top=top,
            skip=skip,
            skiptoken=skiptoken,
            max_pages=max_pages,
            schema=CourseGet
        )

    def get_by_id(self, course_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a specific course record by its ID.

        Args:
            course_id (str): The unique identifier of the course record.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing (valid_data, invalid_data).
        """
        filter_expression = f"CourseRID eq '{course_id}'"
        return self.get(filter=filter_expression)
