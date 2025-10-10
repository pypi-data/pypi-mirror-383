from typing import Optional, Union, List, Dict, Any, Tuple
import json
import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.cost_center import CostCenterUpdate, CostCenterGet

# Entity type constant
ENTITY_TYPE = "hr2d__CostCenter__c"


class CostCenter:
    """
    Handles cost center operations for HR2Day API.
    Cost center holds information about cost centers in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the CostCenter class.

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
        Get cost center data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "Id = 'a08P500000USWDPIA5'"
            select_fields (Union[List[str], str], optional): Fields to select. If provided, only these fields are used.
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
            schema=CostCenterGet
        )

    def update(self, cost_centers: List[Dict[str, Any]]) -> requests.Response:
        """
        Sends a PUT request to the HR2Day API to update or create cost center information.

        Args:
            cost_centers (List[Dict[str, Any]]): List of cost centers to update/create. Each cost center must include:
                For update:
                - costcenterId: 18 characters, case sensitive (e.g., a0M2G00011iDU9IAH)

                For create (insert):
                One of the following is required:
                - employerId: 18 characters, case sensitive (e.g., a04A000004eQcJIAU)
                - employerName: Max 80 characters, case sensitive
                - employerTaxId: 12 characters, case sensitive

                Fields that can be updated/created:
                - Name: Name of the cost center (max 80 characters, mandatory for insert)
                - hr2d__StartDate__c: Start date (format: yyyy-mm-dd)
                - hr2d__EndDate__c: End date (format: yyyy-mm-dd)
                - hr2d__Description__c: Description (max 75 characters)
                - hr2d__Dimension__c: Dimension (1 character: 1, 2, 3 or 9)
                - hr2d__Classification__c: Classification (max 20 characters)
                - hr2d__RecapChar__c: Verdichtings-kenmerk (max 20 characters)

        Returns:
            requests.Response: API response object

        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """

        try:
            validated_cost_centers = []
            for i, cost_center_data in enumerate(cost_centers):
                try:
                    nested_data = Functions.flat_dict_to_nested_dict(cost_center_data, CostCenterUpdate)
                    validated_cost_center = CostCenterUpdate(**nested_data)
                    validated_cost_center = validated_cost_center.model_dump(by_alias=True, exclude_none=True)
                    if "errors" not in validated_cost_center:
                        validated_cost_center["errors"] = ""
                    validated_cost_centers.append(validated_cost_center)
                except Exception as e:
                    raise ValueError(f"Cost center {i+1} validation failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"Cost center data validation failed:\n{str(e)}")

        # Check if there are valid cost centers
        if not validated_cost_centers:
            raise ValueError("No valid cost centers to update/create")

        # Create request body
        request_body = {
            "request": {
                "requesterId": self.hr2day.requester_id,
                "costcenters": validated_cost_centers
            }
        }

        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/apexrest/hr2d/costcenter"
        json_body = json.dumps(request_body, default=self.hr2day.datetime_converter)

        # Send PUT request
        response = self.hr2day.session.put(
            url=url,
            data=json_body
        )

        response.raise_for_status()

        return response
