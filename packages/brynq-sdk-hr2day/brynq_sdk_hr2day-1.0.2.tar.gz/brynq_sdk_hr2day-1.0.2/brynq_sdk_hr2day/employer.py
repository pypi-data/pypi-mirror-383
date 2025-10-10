from typing import Optional, Union, List, Dict, Tuple
import pandas as pd
from .schemas.employer import EmployerGet

# Entity type constant
ENTITY_TYPE = "hr2d__Employer__c"


class Employer:
    """
    Handles employer operations for HR2Day API.
    Employer holds information about employers in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the Employer class.

        Args:
            hr2day_instance: The HR2Day class instance.
        """
        self.hr2day = hr2day_instance
        self.available_fields = []  # Will be populated dynamically on first call

    def get(self,
            filter: Optional[str] = None,
            select_fields: Optional[Union[List[str], str]] = None,
            related: Optional[Dict[str, List[str]]] = None,
            orderby: Optional[Union[List[str], str]] = None,
            limit: Optional[int] = None,
            skip: Optional[int] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employer data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "Id = 'a08P500000USWDPIA5'"
            select_fields (Union[List[str], str], optional): Fields to select. If None, default fields will be used.
                            Example (list): ["Id", "FirstName", "LastName"]
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                            Example: {"DepartmentToday": ["Name"]} will include department name.
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
                            Example (list): ["LastName ASC", "FirstName DESC"]
            limit (int, optional): Number of records to return (LIMIT clause). Max 200 when all_fields is True. Defaults to 200.
                            Example: 100
            skip (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
                            Example: 0

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple containing (valid_data, invalid_data)
        """
        # Use available fields if no specific fields are requested
        if select_fields is None:
            # If available fields not cached yet, discover them
            if not self.available_fields:
                self.available_fields = self.hr2day.discover_fields(ENTITY_TYPE)
            select_fields = self.available_fields

        return self.hr2day.get(
            entity_type=ENTITY_TYPE,
            select_fields=select_fields,
            related_fields=related,
            filter=filter,
            order_by=orderby,
            limit=limit,
            offset=skip,
            schema=EmployerGet
        )
