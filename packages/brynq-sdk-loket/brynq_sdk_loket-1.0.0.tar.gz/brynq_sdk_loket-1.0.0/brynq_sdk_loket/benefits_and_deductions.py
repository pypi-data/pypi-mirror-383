from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
import base64
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.benefits_and_deductions import BenefitsAndDeductionsGet, BenefitsAndDeductionsCreate, BenefitsAndDeductionsUpdate, BenefitsAndDeductionsImportGet, BenefitsAndDeductionsCsvImport, BenefitsAndDeductionsBatchCreate, BenefitsAndDeductionsBatchUpdate


class BenefitsAndDeductions:
    """
    Handles all benefits and deductions-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize BenefitsAndDeductions manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        employment_id: Optional[str] = None,
        benefits_and_deductions_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get benefits and deductions data. Can retrieve either a list of benefits and deductions for an employment or a specific benefits and deductions by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all benefits and deductions)
            benefits_and_deductions_id: The unique identifier of the benefits and deductions (for getting specific benefits and deductions)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated benefits and deductions data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all benefits and deductions for an employment
            valid_df, invalid_df = loket.benefits_and_deductions.get(employment_id="xxx-xxx")

            # Get specific benefits and deductions by ID
            valid_df, invalid_df = loket.benefits_and_deductions.get(benefits_and_deductions_id="yyy-yyy")

            # Get benefits and deductions with filter (active only)
            valid_df, invalid_df = loket.benefits_and_deductions.get(employment_id="xxx-xxx", filter_query="isActive eq true")
        """
        try:
            # Determine endpoint and parameters based on input
            if benefits_and_deductions_id:
                # Get specific benefits and deductions by ID
                endpoint = f"providers/employers/employees/employments/benefitsAndDeductions/{benefits_and_deductions_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([response_data.get("content")])

            elif employment_id:
                # Get all benefits and deductions for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/benefitsanddeductions"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    filter_query=filter_query,
                    order_by=order_by,
                    get_all_pages=True
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (list of items)
                df = pd.json_normalize(response_data)

            else:
                raise ValueError("Either employment_id or benefits_and_deductions_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, BenefitsAndDeductionsGet)

            return valid_data, invalid_data

        except Exception as e:
            if benefits_and_deductions_id:
                raise ValueError(f"Failed to get benefits and deductions {benefits_and_deductions_id}: {e}")
            else:
                raise ValueError(f"Failed to get benefits and deductions for employment {employment_id}: {e}")

    def create(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new benefits and deductions for a specific employment.

        Args:
            employment_id: The unique identifier of the employment
            data: Dictionary containing benefits and deductions data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "start_date": "1995-05-21",
                "end_date": "2019-08-24",
                "payroll_component": {"key": 1},
                "value": 50.87
            }
            response = loket.benefits_and_deductions.create(employment_id="xxx-xxx", data=data)
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, BenefitsAndDeductionsCreate)
            # Validate input data using Pydantic schema
            validated_data = BenefitsAndDeductionsCreate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate benefits and deductions create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/benefitsanddeductions",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        benefits_and_deductions_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing benefits and deductions.

        Args:
            benefits_and_deductions_id: The unique identifier of the benefits and deductions
            data: Dictionary containing benefits and deductions data to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "start_date": "1995-05-21",
                "end_date": "2019-08-24",
                "value": 50.87
            }
            response = loket.benefits_and_deductions.update(
                benefits_and_deductions_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, BenefitsAndDeductionsUpdate)
            # Validate input data using Pydantic schema
            validated_data = BenefitsAndDeductionsUpdate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate benefits and deductions update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/benefitsAndDeductions/{benefits_and_deductions_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        benefits_and_deductions_id: str,
    ) -> Response:
        """
        Delete an existing benefits and deductions.

        Args:
            benefits_and_deductions_id: The unique identifier of the benefits and deductions

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.benefits_and_deductions.delete(benefits_and_deductions_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/benefitsAndDeductions/{benefits_and_deductions_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete benefits and deductions {benefits_and_deductions_id}: {e}")

    def get_import_data(
        self,
        payroll_administration_id: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get import data for benefits and deductions from a specific payroll administration.

        Args:
            payroll_administration_id: The unique identifier of the payroll administration
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated import data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            valid_df, invalid_df = loket.benefits_and_deductions.get_import_data(
                payroll_administration_id="xxx-xxx"
            )
        """
        try:
            # Get all pages automatically
            endpoint = f"providers/employers/payrolladministrations/{payroll_administration_id}/import/benefitsanddeductions"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=True
            )

            # Convert to DataFrame for validation
            if not response_data:
                # Return empty DataFrames if no data
                return pd.DataFrame(), pd.DataFrame()

            # Normalize nested JSON structure
            df = pd.json_normalize(response_data)

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, BenefitsAndDeductionsImportGet)

            return valid_data, invalid_data

        except Exception as e:
            raise ValueError(f"Failed to get import data for payroll administration {payroll_administration_id}: {e}")

    def import_csv(
        self,
        payroll_administration_id: str,
        csv_data: str,
    ) -> Response:
        """
        Import benefits and deductions data via CSV string data.

        Args:
            payroll_administration_id: The unique identifier of the payroll administration
            csv_data: CSV data as string

        Returns:
            Response: API response from the import request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            csv_content = "clientNumber,payrollEmployeeNumber,employeeNumber,formattedName,startDate,payrollComponentKey,payrollComponentDescription,value\n20720,202,156,Jong I,2023-11-01,1,Uren gewerkt,3500"
            response = loket.benefits_and_deductions.import_csv(
                payroll_administration_id="xxx-xxx",
                csv_data=csv_content
            )
        """
        try:
            # Encode CSV string to base64
            base64_data = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')

            # Create request data
            request_data = {
                "mimeType": "text/csv",
                "data": base64_data
            }

            # Validate input data using Pydantic schema
            validated_data = BenefitsAndDeductionsCsvImport(**request_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate CSV import data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/payrolladministrations/{payroll_administration_id}/import/benefitsanddeductions",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def create_batch(
        self,
        employer_id: str,
        data: List[Dict[str, Any]],
    ) -> Response:
        """
        Create benefits and deductions for multiple employments in batch.

        Args:
            employer_id: The unique identifier of the employer
            data: List of dictionaries containing benefits and deductions data for multiple employments

        Returns:
            Response: API response from the batch create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = [
                {
                    "employment_id": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "start_date": "1995-05-21",
                    "value": 80,
                    "payroll_component": {"key": 1}
                }
            ]
            response = loket.benefits_and_deductions.create_batch(employer_id="xxx-xxx", data=data)
        """
        try:
            # Validate each item in the batch
            validated_data = []
            for item in data:
                nested_data = self.loket.flat_dict_to_nested_dict(item, BenefitsAndDeductionsBatchCreate)
                validated_item = BenefitsAndDeductionsBatchCreate(**nested_data)
                validated_data.append(validated_item.model_dump(by_alias=True, mode="json", exclude_none=True))


        except Exception as exc:
            raise ValueError(f"Failed to validate benefits and deductions batch create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/{employer_id}/employees/employments/benefitsanddeductions",
            json=validated_data,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update_batch(
        self,
        employer_id: str,
        data: List[Dict[str, Any]],
    ) -> Response:
        """
        Update benefits and deductions for multiple employments in batch.

        Args:
            employer_id: The unique identifier of the employer
            data: List of dictionaries containing benefits and deductions data to update for multiple employments

        Returns:
            Response: API response from the batch update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = [
                {
                    "employment_id": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "benefit_and_deduction_id": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "end_date": "1995-05-21"
                }
            ]
            response = loket.benefits_and_deductions.update_batch(employer_id="xxx-xxx", data=data)
        """
        try:
            # Validate each item in the batch
            validated_data = []
            for item in data:
                nested_data = self.loket.flat_dict_to_nested_dict(item, BenefitsAndDeductionsBatchUpdate)
                validated_item = BenefitsAndDeductionsBatchUpdate(**nested_data)
                validated_data.append(validated_item.model_dump(by_alias=True, mode="json", exclude_none=True))


        except Exception as exc:
            raise ValueError(f"Failed to validate benefits and deductions batch update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/{employer_id}/employees/employments/benefitsanddeductions",
            json=validated_data,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response
