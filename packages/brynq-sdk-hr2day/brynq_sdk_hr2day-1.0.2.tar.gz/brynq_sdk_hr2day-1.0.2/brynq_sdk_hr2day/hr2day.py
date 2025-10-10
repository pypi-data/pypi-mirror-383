import requests
import pandas as pd
from typing import Union, Optional, List, Dict, Type, Literal, Tuple
from datetime import datetime, date
from brynq_sdk_brynq import BrynQ
from brynq_sdk_functions import Functions, BrynQPanderaDataFrameModel
from .employee import Employee
from .cost_center import CostCenter
from .job import Job
from .file import File
from .department import Department
from .employer import Employer
from .employment_conditions_cluster import EmploymentConditionsCluster
from .employment_relationship import EmploymentRelationship
from .sick_classification import SickClassification
from .substitution import Substitution
from .wage_component_definition import WageComponentDefinition
from .work_history import WorkHistory
class HR2Day(BrynQ):
    """
    A class to interact with HR2Day API.
    """


    def __init__(self, requester_id: str, debug: bool = False, api_version: str = "v63.0", system_type: Optional[Literal['source', 'target']] = None):
        """
        Initialize the HR2Day class.

        Args:
            system_type (str): System type identifier.
            debug (bool, optional): Whether to enable debug mode. Defaults to False.
        """

        super().__init__()
        self.timeout = 3600
        self.debug = debug
        self.API_VERSION = api_version
        self.requester_id = requester_id

        # Get authentication token
        credentials = self.interfaces.credentials.get(system='hr2day', system_type=system_type)
        self.access_token, self.base_url = self._get_access_token(credentials)

        # Initialize session with headers and retry strategy
        self.session = requests.Session()

        # Set default headers for all requests
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'X-PrettyPrint': '1'
        })

        # Initialize components
        self.employee = Employee(self)
        self.cost_center = CostCenter(self)
        self.file = File(self)
        self.department = Department(self)
        self.employer = Employer(self)
        self.employment_conditions_cluster = EmploymentConditionsCluster(self)
        self.employment_relationship = EmploymentRelationship(self)
        self.job = Job(self)
        self.sick_classification = SickClassification(self)
        self.substitution = Substitution(self)
        self.wage_component_definition = WageComponentDefinition(self)
        self.work_history = WorkHistory(self)

    def _get_access_token(self, credentials):
        payload = {
            "grant_type": "password",
            "client_id": credentials["data"]["client_id"],
            "client_secret": credentials["data"]["client_secret"],
            "username": credentials["data"]["username"],
            "password": credentials["data"]["password"]
        }
        resp = requests.post(url='https://login.salesforce.com/services/oauth2/token',
                             data=payload)
        resp.raise_for_status()
        data = resp.json()

        return data.get('access_token'), data.get('instance_url')


    def _build_soql_query(self,
                         entity_type: str,
                         select_fields: Optional[Union[List[str], str]] = None,
                         related_fields: Optional[Dict[str, List[str]]] = None,
                         filter: Optional[str] = None,
                         order_by: Optional[Union[List[str], str]] = None,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None,
                         schema: Optional[Type[BrynQPanderaDataFrameModel]] = None) -> tuple[str, int]:
        """
        Builds a SOQL query.

        Args:
            entity_type (str): The entity type to query (e.g., "hr2d__Employee__c")
            select_fields (Union[List[str], str], optional): Fields to select.
            related_fields (Dict[str, List[str]], optional): Dictionary of fields to select from related objects.
            filter (str, optional): WHERE clause.
            order_by (Union[List[str], str], optional): Sorting criteria.
            limit (int, optional): Number of records to return.
            offset (int, optional): Number of records to skip.
            schema (Type[BrynQPanderaDataFrameModel], optional): Pandera schema class for validation.

        Returns:
            tuple[str, int]: The generated SOQL query and limit value
        """
        # Create SELECT part
        if select_fields:
            if isinstance(select_fields, str):
                select_fields = [select_fields]

            query = f"SELECT {','.join(select_fields)}"
        else:
            if schema:
                try:
                    all_fields = []


                    schema_fields = list(schema.to_schema().columns.keys())

                    for field in schema_fields:
                        if not any(hasattr(getattr(schema, field, None), attr)
                                  for attr in ["model_fields", "__fields__"]):
                            all_fields.append(field)

                    if not all_fields:
                        query = "SELECT FIELDS(ALL)"
                        limit = 1
                    else:
                        query = f"SELECT {','.join(all_fields)}"
                except Exception as e:
                    query = "SELECT FIELDS(ALL)"
                    limit = 1
            else:
                query = "SELECT FIELDS(ALL)"
                limit = 1

        # Add related fields
        if related_fields:
            related_query_parts = []
            for relation, fields in related_fields.items():
                for field in fields:
                    related_query_parts.append(f"hr2d__{relation}__r.{field}")
            if related_query_parts:
                query += "," + ",".join(related_query_parts)

        # Add FROM part
        query += f" FROM {entity_type}"

        # Add WHERE clause
        if filter:
            query += f" WHERE {filter}"

        # Add ORDER BY part
        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]
            processed_order = []
            for field in order_by:
                processed_order.append(field)
            query += f" ORDER BY {','.join(processed_order)}"

        # Add LIMIT part
        if limit:
            query += f" LIMIT {limit}"

        # Add OFFSET part
        if offset:
            if offset > 2000:
                raise ValueError("OFFSET cannot exceed 2000")
            query += f" OFFSET {offset}"

        return query, limit

    def get(self,
            entity_type: str,
            select_fields: Optional[Union[List[str], str]] = None,
            related_fields: Optional[Dict[str, List[str]]] = None,
            filter: Optional[str] = None,
            order_by: Optional[Union[List[str], str]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            schema: Optional[Type[BrynQPanderaDataFrameModel]] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get data from HR2Day using Salesforce SOQL query.

        Args:
            entity_type (str): The full entity type name (e.g., "hr2d__Employee__c")
            select_fields (Union[List[str], str], optional): Fields to select. If None, FIELDS(ALL) will be used (requires limit <= 200).
            related_fields (Dict[str, List[str]], optional): Dictionary of related fields to select.
                                                           Key is the relation field, value is list of fields to select from related object.
                                                           Example: {"DepartmentToday": ["Name", "Code"]} will add "hr2d__DepartmentToday__r.Name, hr2d__DepartmentToday__r.Code"
            filter (str, optional): WHERE clause for the query. Defaults to None.
            order_by (Union[List[str], str], optional): Fields to order by. Defaults to None.
            limit (int): Number of records to return (LIMIT clause). Defaults to 200. Must be <= 200 when select_fields is None.
            offset (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
            schema (Type[BrynQPanderaDataFrameModel], optional): Pandera schema class for validation. Defaults to None.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple containing (valid_data, invalid_data)

        Raises:
            ValueError: If the data validation fails
        """
        # Build SOQL query
        query, limit = self._build_soql_query(
            entity_type=entity_type,
            select_fields=select_fields,
            related_fields=related_fields,
            filter=filter,
            order_by=order_by,
            limit=limit,
            offset=offset,
            schema=schema
        )

        # URL encode the query (only convert spaces to +)
        encoded_query = query.replace(" ", "+")

        # Make the request
        response = self.session.get(f"{self.base_url}/services/data/{self.API_VERSION}/query?q={encoded_query}")
        response.raise_for_status()

        # Convert response to DataFrame
        data = response.json()

        # Check if pagination is needed
        all_records = []
        while True:
            if not data.get("records"):
                break

            # Remove "attributes" field from records
            records = data["records"]
            for record in records:
                record.pop("attributes", None)

            all_records.extend(records)

            # Check if there are more records
            if data.get("nextRecordsUrl"):
                response = self.session.get(f"{self.base_url}{data['nextRecordsUrl']}")
                response.raise_for_status()
                data = response.json()
            else:
                break

        if not all_records:
            return pd.DataFrame(), pd.DataFrame()

        # Create DataFrame from all records
        df = pd.DataFrame(all_records)

        # Skip validation if related_fields is provided
        if related_fields:
            return df, pd.DataFrame()

        try:
            # If select_fields parameter is used, only validate those fields
            if select_fields:
                # Create a list of selected fields
                if isinstance(select_fields, str):
                    selected_fields_list = [field.strip() for field in select_fields.split(',')]
                else:
                    selected_fields_list = select_fields

                # Remove "attributes" field if present
                if "attributes" in selected_fields_list:
                    selected_fields_list.remove("attributes")

                # Add fields from related objects
                if related_fields:
                    for relation, fields in related_fields.items():
                        for field in fields:
                            related_field = f"hr2d__{relation}__r.{field}"
                            if related_field not in selected_fields_list:
                                selected_fields_list.append(related_field)

                # Filter DataFrame to only include selected fields
                df = df[selected_fields_list]

                # If schema is provided, validate with the original schema
                if schema:
                    try:
                        valid_data, invalid_data = Functions.validate_data(df, schema)
                        return valid_data, invalid_data
                    except Exception as e:
                        raise ValueError(f"Data validation failed: {str(e)}")

            # Validate DataFrame with original schema if no select_fields or if select_fields but no schema
            if schema:
                # Check schema type and validate accordingly
                try:
                    valid_data, invalid_data = Functions.validate_data(df, schema)
                    return valid_data, invalid_data
                except Exception as e:
                    raise ValueError(f"Data validation failed: {str(e)}")

        except Exception as e:
            raise e

        return df, pd.DataFrame()

    @staticmethod
    def datetime_converter(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def discover_fields(self, entity_type: str) -> List[str]:
        """
        Discover all available fields for an entity type by making a FIELDS(ALL) query.

        Args:
            entity_type (str): The full entity type name (e.g., "hr2d__Department__c")

        Returns:
            List[str]: List of available field names
        """
        # Make a call with FIELDS(ALL) to get all available fields
        discovery_df = self.get(
            entity_type=entity_type,
            limit=1
        )

        # Extract field names from the first record
        if not discovery_df[0].empty:
            available_fields = [field for field in discovery_df[0].columns if field != 'attributes']
            return available_fields
        else:
            return []

    def close(self):
        """Close the session"""
        self.session.close()
