from typing import Optional, Union, List, Dict, Any, Tuple
import pandas as pd
from datetime import date
from .schemas.leave import LeaveGet, LeaveCreate, LeaveUpdate
from .schemas.leave_entitlement import LeaveEntitlementGet

# Entity type constant
ENTITY_TYPE = "hr2d__Leave__c"
IMPORT_ENTITY_TYPE = "hr2d__LeaveImport__c"
ENTITLEMENT_ENTITY_TYPE = "hr2d__LeaveEntitlement__c"


class Leave:
    """
    Handles leave operations for HR2Day API.
    Leave holds information about leave requests in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the Leave class.

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
        Get leave data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "Id = 'a08P500000USWDPIA5'"
            select_fields (Union[List[str], str], optional): Fields to select. If None, all available fields will be used.
                            Example (list): ["Id", "Name", "hr2d__StartDate__c"]
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                            Example: {"Employee": ["Name"]} will include employee name.
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
            schema=LeaveGet
        )

    def _process(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to process leave records (insert, update, or delete) using the LeaveImport object.

        Args:
            leaves (List[Dict[str, Any]]): List of leave records to process. Each leave must include:
                - hr2d__Operation__c: Operation type ("insert", "update", or "delete")

                For insert:
                - One of hr2d__EmployeeId__c or hr2d__EmployeeNr__c
                - One of hr2d__EmployerId__c, hr2d__EmployerTaxId__c, or hr2d__EmployerName__c
                - One of hr2d__LeaveCode__c or hr2d__Leave__c
                - Required leave fields: hr2d__Hours__c, hr2d__StartDate__c,
                  hr2d__EndDate__c, hr2d__ArbrelVolgnr__c, hr2d__Workflowstatus__c

                For update/delete:
                - One of hr2d__ExternalKey__c or hr2d__InternalId__c

        Returns:
            Dict[str, Any]: API response

        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        try:
            # Validate each leave record against the appropriate schema based on operation
            valid_leaves = []
            for i, leave in enumerate(leaves):
                operation = leave.get("operation")

                if operation == "insert":
                    validated_leave = LeaveCreate(**leave)
                elif operation in ["update", "delete"]:
                    validated_leave = LeaveUpdate(**leave)
                else:
                    raise ValueError(f"Leave {i+1}: Invalid operation '{operation}'. Must be 'insert', 'update', or 'delete'")

                # Convert to dict with aliases
                valid_leaves.append(validated_leave.model_dump(by_alias=True, exclude_none=True))

        except Exception as e:
            raise ValueError(f"Leave data validation failed:\n{str(e)}")

        # Additional validation for required fields based on operation
        for i, leave in enumerate(valid_leaves):
            operation = leave.get("hr2d__Operation__c")

            if operation == "insert":
                # Check employee identification
                if not (leave.get("hr2d__EmployeeId__c") or leave.get("hr2d__EmployeeNr__c")):
                    raise ValueError(f"Leave {i+1}: For insert operation, either hr2d__EmployeeId__c or hr2d__EmployeeNr__c is required")

                # Check employer identification
                if not (leave.get("hr2d__EmployerId__c") or leave.get("hr2d__EmployerTaxId__c") or leave.get("hr2d__EmployerName__c")):
                    raise ValueError(f"Leave {i+1}: For insert operation, one of hr2d__EmployerId__c, hr2d__EmployerTaxId__c, or hr2d__EmployerName__c is required")

                # Check leave identification
                if not (leave.get("hr2d__LeaveCode__c") or leave.get("hr2d__Leave__c")):
                    raise ValueError(f"Leave {i+1}: For insert operation, either hr2d__LeaveCode__c or hr2d__Leave__c is required")

                # Check required fields
                required_fields = ["hr2d__Hours__c", "hr2d__StartDate__c", "hr2d__EndDate__c",
                                 "hr2d__ArbrelVolgnr__c", "hr2d__Workflowstatus__c"]
                missing_fields = [field for field in required_fields if not leave.get(field)]
                if missing_fields:
                    raise ValueError(f"Leave {i+1}: For insert operation, the following fields are required: {', '.join(missing_fields)}")

            elif operation in ["update", "delete"]:
                # Check identification
                if not (leave.get("hr2d__ExternalKey__c") or leave.get("hr2d__InternalId__c")):
                    raise ValueError(f"Leave {i+1}: For {operation} operation, either hr2d__ExternalKey__c or hr2d__InternalId__c is required")

        # Create request body for composite API
        records = []
        for leave in valid_leaves:
            # Create a flat record structure for the API
            record = {
                "attributes": {"type": IMPORT_ENTITY_TYPE}
            }

            # Add API fields
            for field in [
                "hr2d__ExternalKey__c", "hr2d__InternalId__c", "hr2d__EmployeeId__c",
                "hr2d__EmployeeNr__c", "hr2d__Mode__c", "hr2d__Operation__c",
                "hr2d__EmployerId__c", "hr2d__EmployerTaxId__c", "hr2d__EmployerName__c"
            ]:
                if field in leave and leave[field] is not None:
                    record[field] = leave[field]

            # Add leave fields
            for field in [
                "hr2d__Hours__c", "hr2d__StartDate__c", "hr2d__EndDate__c",
                "hr2d__ArbrelVolgnr__c", "hr2d__Reason__c", "hr2d__Details__c",
                "hr2d__TvtType__c", "hr2d__Description__c", "hr2d__LeaveCode__c",
                "hr2d__Leave__c", "hr2d__Changes__c", "hr2d__Workflowstatus__c"
            ]:
                if field in leave and leave[field] is not None:
                    # Convert date objects to string format
                    if isinstance(leave[field], date):
                        record[field] = leave[field].isoformat()
                    else:
                        record[field] = leave[field]

            records.append(record)

        # Create the final request body
        request_body = {
            "allOrNone": False,
            "records": records
        }

        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/data/{self.hr2day.API_VERSION}/composite/sobjects/"

        # Send POST request
        response = self.hr2day.session.post(
            url=url,
            json=request_body
        )

        # Error handling
        response.raise_for_status()

        # Return response as JSON
        return response.json()

    def create(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to insert leave records using the LeaveImport object.
        This is a convenience method that sets the operation type to "insert".

        Args:
            leaves (List[Dict[str, Any]]): List of leave records to insert. Each leave must include:
                - One of employee_id or employee_number
                - One of employer_id, employer_tax_id, or employer_name
                - One of leave_code or leave_type
                - Required leave fields: hours, start_date, end_date, employment_sequence_number, workflow_status

        Returns:
            Dict[str, Any]: API response

        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        # Set operation type to "insert" for all records
        for leave in leaves:
            leave["operation"] = "insert"
            leave["mode"] = "online"

        return self._process(leaves)

    def update(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to update leave records using the LeaveImport object.
        This is a convenience method that sets the operation type to "update".

        Args:
            leaves (List[Dict[str, Any]]): List of leave records to update. Each leave must include:
                - One of external_key or internal_id to identify the leave record
                - The leave fields to update

        Returns:
            Dict[str, Any]: API response

        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        # Set operation type to "update" for all records
        for leave in leaves:
            leave["operation"] = "update"
            leave["mode"] = "online"

        return self._process(leaves)

    def delete(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to delete leave records using the LeaveImport object.
        This is a convenience method that sets the operation type to "delete".

        Args:
            leaves (List[Dict[str, Any]]): List of leave records to delete. Each leave must include:
                - One of external_key or internal_id to identify the leave record

        Returns:
            Dict[str, Any]: API response

        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        # Set operation type to "delete" for all records
        for leave in leaves:
            leave["operation"] = "delete"
            leave["mode"] = "online"

        return self._process(leaves)

    def get_entitlements(self,
                        filter: Optional[str] = None,
                        select_fields: Optional[Union[List[str], str]] = None,
                        related: Optional[Dict[str, List[str]]] = None,
                        orderby: Optional[Union[List[str], str]] = None,
                        limit: Optional[int] = None,
                        skip: Optional[int] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get leave entitlement data from HR2Day API.

        Leave entitlements represent the balance, taken, and entitlement amounts
        for different leave types (L1-L5, L11-L15, TVT) for employees.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "hr2d__Employee__c = 'a087Q000015iQp4QAE'"
            select_fields (Union[List[str], str], optional): Fields to select. If None, all available fields will be used.
                            Example (list): ["Id", "Name", "hr2d__Employee__c", "hr2d__L1_Balance__c"]
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                            Example: {"Employee": ["Name", "FirstName", "LastName"]}
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
                            Example (list): ["Name DESC", "hr2d__StartDate__c ASC"]
            limit (int, optional): Number of records to return (LIMIT clause). Max 200. Defaults to 200.
                            Example: 50
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
            if not hasattr(self, 'available_entitlement_fields'):
                self.available_entitlement_fields = self.hr2day.discover_fields(ENTITLEMENT_ENTITY_TYPE)

            # Use available fields
            fields_to_use = self.available_entitlement_fields.copy()

        return self.hr2day.get(
            entity_type=ENTITLEMENT_ENTITY_TYPE,
            select_fields=fields_to_use,
            related_fields=related,
            filter=filter,
            order_by=orderby,
            limit=limit,
            offset=skip,
            schema=LeaveEntitlementGet
        )
