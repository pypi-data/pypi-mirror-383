from typing import Optional, Union, List, Dict, Tuple
import pandas as pd
from .schemas.employment_conditions_cluster import EmploymentConditionsClusterGet

# Entity type constant
ENTITY_TYPE = "hr2d__ArbVoorwCluster__c"


class EmploymentConditionsCluster:
    """
    Handles employment conditions cluster operations for HR2Day API.
    EmploymentConditionsCluster holds information about employment conditions clusters in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the EmploymentConditionsCluster class.

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
        Get employment conditions cluster data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "Id = 'a08P500000USWDPIA5'"
            select_fields (Union[List[str], str], optional): Fields to select. If None, all available fields will be used.
                            Example (list): ["Id", "Name", "Description"]
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                            Example: {"Department": ["Name"]} will include department name.
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
                            Example (list): ["Name ASC", "CreatedDate DESC"]
            limit (int, optional): Number of records to return (LIMIT clause). Max 200 when all_fields is True. Defaults to 200.
                            Example: 100
            skip (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
                            Example: 0

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple containing (valid_data, invalid_data)
        """
        # Determine fields to use
        if select_fields is not None:
            # Use only the specified fields
            fields_to_use = select_fields
        else:
            # If available fields not cached yet, discover them
            if not self.available_fields:
                self.available_fields = self.hr2day.discover_fields(ENTITY_TYPE)

            # Use available fields
            fields_to_use = self.available_fields.copy()

        return self.hr2day.get(
            entity_type=ENTITY_TYPE,
            select_fields=fields_to_use,
            related_fields=related,
            filter=filter,
            order_by=orderby,
            limit=limit,
            offset=skip,
            schema=EmploymentConditionsClusterGet
        )
