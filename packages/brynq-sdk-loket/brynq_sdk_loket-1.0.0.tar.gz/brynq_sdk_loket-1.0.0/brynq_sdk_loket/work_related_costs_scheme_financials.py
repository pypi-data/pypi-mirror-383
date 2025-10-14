from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.work_related_costs_scheme_financials import WorkRelatedCostsSchemeFinancialsGet, WorkRelatedCostsSchemeFinancialsCreate, WorkRelatedCostsSchemeFinancialsUpdate, WorkRelatedCostsSchemeMatrixGet


class WorkRelatedCostsSchemeFinancials:
    """
    Handles all work related costs scheme financials-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize WorkRelatedCostsSchemeFinancials manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        payroll_administration_id: Optional[str] = None,
        work_related_costs_scheme_financial_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get work related costs scheme financials data. Can retrieve either a list of work related costs scheme financials for a payroll administration or a specific work related costs scheme financial by ID.

        Args:
            payroll_administration_id: The unique identifier of the payroll administration (for getting all work related costs scheme financials)
            work_related_costs_scheme_financial_id: The unique identifier of the work related costs scheme financial (for getting specific work related costs scheme financial)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated work related costs scheme financials data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all work related costs scheme financials for a payroll administration
            valid_df, invalid_df = loket.work_related_costs_scheme_financials.get(payroll_administration_id="xxx-xxx")

            # Get specific work related costs scheme financial by ID
            valid_df, invalid_df = loket.work_related_costs_scheme_financials.get(work_related_costs_scheme_financial_id="yyy-yyy")

            # Get work related costs scheme financials with filter (year equals 2023)
            valid_df, invalid_df = loket.work_related_costs_scheme_financials.get(payroll_administration_id="xxx-xxx", filter_query="year eq 2023")
        """
        try:
            # Determine endpoint and parameters based on input
            if work_related_costs_scheme_financial_id:
                # Get specific work related costs scheme financial by ID
                endpoint = f"providers/employers/payrolladministrations/workRelatedCostsSchemeFinancials/{work_related_costs_scheme_financial_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([response_data.get("content")])

            elif payroll_administration_id:
                # Get all work related costs scheme financials for payroll administration
                endpoint = f"providers/employers/payrolladministrations/{payroll_administration_id}/workRelatedCostsSchemeFinancials"
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
                raise ValueError("Either payroll_administration_id or work_related_costs_scheme_financial_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, WorkRelatedCostsSchemeFinancialsGet)

            return valid_data, invalid_data

        except Exception as e:
            if work_related_costs_scheme_financial_id:
                raise ValueError(f"Failed to get work related costs scheme financial {work_related_costs_scheme_financial_id}: {e}")
            else:
                raise ValueError(f"Failed to get work related costs scheme financials for payroll administration {payroll_administration_id}: {e}")

    def create(
        self,
        payroll_administration_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new work related costs scheme financial for a specific payroll administration.

        Args:
            payroll_administration_id: The unique identifier of the payroll administration
            data: Dictionary containing work related costs scheme financial data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "year": 2023,
                "period": 1,
                "identification": "Company bike",
                "description": "Sparta d-RULE ULTRA",
                "amount": 3500
            }
            response = loket.work_related_costs_scheme_financials.create(payroll_administration_id="xxx-xxx", data=data)
        """
        try:
            # Validate input data using Pydantic schema
            validated_data = WorkRelatedCostsSchemeFinancialsCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate work related costs scheme financials create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/payrolladministrations/{payroll_administration_id}/workRelatedCostsSchemeFinancials",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        work_related_costs_scheme_financial_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing work related costs scheme financial.

        Args:
            work_related_costs_scheme_financial_id: The unique identifier of the work related costs scheme financial
            data: Dictionary containing work related costs scheme financial data to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "year": 2023,
                "period": 1,
                "identification": "Company bike",
                "description": "Sparta d-RULE ULTRA",
                "amount": 3500
            }
            response = loket.work_related_costs_scheme_financials.update(
                work_related_costs_scheme_financial_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Validate input data using Pydantic schema
            validated_data = WorkRelatedCostsSchemeFinancialsUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate work related costs scheme financials update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/payrolladministrations/workRelatedCostsSchemeFinancials/{work_related_costs_scheme_financial_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        work_related_costs_scheme_financial_id: str,
    ) -> Response:
        """
        Delete an existing work related costs scheme financial.

        Args:
            work_related_costs_scheme_financial_id: The unique identifier of the work related costs scheme financial

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.work_related_costs_scheme_financials.delete(work_related_costs_scheme_financial_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/payrolladministrations/workRelatedCostsSchemeFinancials/{work_related_costs_scheme_financial_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete work related costs scheme financial {work_related_costs_scheme_financial_id}: {e}")

    def get_matrix(
        self,
        payroll_administration_id: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get work related costs scheme matrix for a specific payroll administration.

        Args:
            payroll_administration_id: The unique identifier of the payroll administration
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated work related costs scheme matrix data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            valid_df, invalid_df = loket.work_related_costs_scheme_financials.get_matrix(payroll_administration_id="xxx-xxx")
        """
        try:
            # Get all pages automatically
            endpoint = f"providers/employers/payrolladministrations/{payroll_administration_id}/workRelatedCostsSchemeMatrix"
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
            valid_data, invalid_data = Functions.validate_data(df, WorkRelatedCostsSchemeMatrixGet)

            return valid_data, invalid_data

        except Exception as e:
            raise ValueError(f"Failed to get work related costs scheme matrix for payroll administration {payroll_administration_id}: {e}")

    def download_report(
        self,
        payroll_administration_id: str,
        report_year: int,
    ) -> Response:
        """
        Download work related costs scheme report as PDF for a specific payroll administration.

        Args:
            payroll_administration_id: The unique identifier of the payroll administration
            report_year: The year for which to generate the report

        Returns:
            Response: API response containing the PDF file

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.work_related_costs_scheme_financials.download_report(payroll_administration_id="xxx-xxx", report_year=2023)
            # Save PDF content
            with open("work_related_costs_report.pdf", "wb") as f:
                f.write(response.content)
        """
        try:
            response = self.loket.session.get(
                url=f"{self.loket.base_url}/providers/employers/payrolladministrations/{payroll_administration_id}/workRelatedCostsSchemeReport",
                params={"reportYear": report_year},
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to download work related costs scheme report for payroll administration {payroll_administration_id}: {e}")
