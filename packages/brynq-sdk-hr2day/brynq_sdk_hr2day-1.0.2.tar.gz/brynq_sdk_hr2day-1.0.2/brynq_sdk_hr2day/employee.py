from typing import Optional, Union, List, Dict, Any, Tuple
import pandas as pd
import requests
from .schemas.employee import EmployeeGet, EmployeeUpdate
from .sick_leave import SickLeave
from .leave import Leave

# Entity type constant
ENTITY_TYPE = "hr2d__Employee__c"


class Employee:
    """
    Handles employee operations for HR2Day API.
    Employee holds information about employees in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the Employee class.

        Args:
            hr2day_instance: The HR2Day class instance.
        """
        self.hr2day = hr2day_instance
        self.sick_leave = SickLeave(hr2day_instance)
        self.leave = Leave(hr2day_instance)
        self.available_fields = []  # Will be populated dynamically on first call

    def get(self,
            filter: Optional[str] = None,
            select_fields: Optional[Union[List[str], str]] = None,
            related: Optional[Dict[str, List[str]]] = None,
            orderby: Optional[Union[List[str], str]] = None,
            limit: Optional[int] = None,
            skip: Optional[int] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employee data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "Id = 'a08P500000USWDPIA5'"
            select_fields (Union[List[str], str], optional): Fields to select. If None, all available fields will be used.
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

        Raises:
            ValueError: If the data validation fails
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
            schema=EmployeeGet
        )


    def update(self, employees: List[Dict[str, Any]]) -> requests.Response:
        """
        Sends a PUT request to the HR2Day API to update employee information.

        Args:
            employees (List[Dict[str, Any]]): List of employees to update. Each employee must include at least one of
                                             the following parameters:
                - employee_id: 18 characters, case sensitive (e.g., a05A00000ZKQj3IAH)
                - employee_key: 22 characters, case sensitive (e.g., 000000000L01-012345678)
                - employee_emplnr: Max 10 characters, numeric (e.g., 123)
                - employee_emplnr_alternative: Max 10 characters, case sensitive (e.g., 0123-A)

                If employee_emplnr or employee_emplnr_alternative is used, one of the following is required:
                - employer_id: 18 characters, case sensitive (e.g., a04A000004eQcJIAU)
                - employer_name: Max 80 characters, case sensitive
                - employer_tax_id: 12 characters, case sensitive

                Fields that can be updated:
                - email: Private email (in email format)
                - email_work: Work email (in email format)
                - phone: Phone number (max 20 characters)
                - phone2: Second phone number (max 20 characters)
                - phone3: Third phone number (max 20 characters)
                - workplace: Workplace/room number (max 25 characters)
                - default_username: Default username (max 80 characters)
                - bundel_id: SAML Bundle Id (max 60 characters)
                - empl_nr_alt: Alternative personnel number (max 20 characters)

        Returns:
            requests.Response: API response

        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """

        try:
            # Validate each employee update data using Schema(**data) pattern
            validated_employees = []
            for i, employee_data in enumerate(employees):
                try:
                    validated_employee = EmployeeUpdate(**employee_data)
                    validated_employees.append(validated_employee.model_dump(by_alias=True, exclude_none=True))
                except Exception as e:
                    raise ValueError(f"Employee {i+1} validation failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"Employee data validation failed:\n{str(e)}")

        # Create request body
        request_body = {
            "request": {
                "requesterId": self.hr2day.requester_id,
                "employees": validated_employees
            }
        }

        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/apexrest/hr2d/employee"

        # Send PUT request
        response = self.hr2day.session.put(
            url=url,
            json=request_body
        )

        response.raise_for_status()

        return response
