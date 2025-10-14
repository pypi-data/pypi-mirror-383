"""
Payslips resource class for Loket SDK.

This module provides methods for interacting with payslip-related endpoints
in the Loket API, including retrieving payslip information.
"""

from typing import Optional, Tuple, Union
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.payslips import PayslipsGet, PayrollPeriodResultsGet


class Payslips:
    """
    Handles all payslip-related operations for Loket SDK.

    This class provides methods to interact with payslip endpoints,
    including retrieving payslip information for employments.
    """

    def __init__(self, loket_instance):
        """
        Initialize the Payslips resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(
        self,
        employment_id: str,
        year: Optional[int] = None,
        payrollrun_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], Response]:
        """
        Get payslips data for a specific employment or download PDF.

        Args:
            employment_id: The unique identifier of the employment
            year: Optional year to filter payslips (if provided, uses year-specific endpoint)
            payrollrun_id: Optional payroll run ID to download PDF (if provided, downloads PDF file)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated payslips data
                - invalid_data: DataFrame containing data that failed validation
            Response: If payrollrun_id is provided, returns Response object with PDF content

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the employment ID is invalid

        Example:
            # Get all payslips for a specific employment
            valid_df, invalid_df = loket.payslips.get(employment_id="xxx-xxx")

            # Get payslips for a specific year
            valid_df, invalid_df = loket.payslips.get(employment_id="xxx-xxx", year=2024)

            # Download PDF for specific payroll run
            response = loket.payslips.get(employment_id="xxx-xxx", payrollrun_id="yyy-yyy")
            with open("payslip.pdf", "wb") as f:
                f.write(response.content)
        """
        if not employment_id or not employment_id.strip():
            raise ValueError("Employment ID cannot be empty")

        try:
            # If payrollrun_id is provided, download PDF
            if payrollrun_id is not None:
                if not payrollrun_id.strip():
                    raise ValueError("Payroll run ID cannot be empty")

                # Download PDF for specific payroll run
                response = self.loket.session.get(
                    url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/payslips/{payrollrun_id}",
                    timeout=self.loket.timeout,
                )
                response.raise_for_status()
                return response

            # Determine endpoint based on whether year is provided
            if year is not None:
                endpoint = f"providers/employers/employees/employments/{employment_id}/payslips/{year}"
            else:
                endpoint = f"providers/employers/employees/employments/{employment_id}/payslips"

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

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            # Validate data using Pandera schema
            valid_data, invalid_data = BrynQFunctions.validate_data(df, PayslipsGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get payslips for employment {employment_id}: {e}")

    def get_payroll_period_results(
        self,
        employment_id: str,
        year: int,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get payroll period results for a specific employment and year.

        Args:
            employment_id: The unique identifier of the employment
            year: The year to get payroll period results for
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated payroll period results data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the employment ID or year is invalid

        Example:
            # Get payroll period results for 2024
            valid_df, invalid_df = loket.payslips.get_payroll_period_results(
                employment_id="xxx-xxx",
                year=2024
            )

            # Get payroll period results with filter
            valid_df, invalid_df = loket.payslips.get_payroll_period_results(
                employment_id="xxx-xxx",
                year=2024,
                filter_query="payrollPeriod.periodNumber eq 1"
            )
        """
        if not employment_id or not employment_id.strip():
            raise ValueError("Employment ID cannot be empty")
        if not isinstance(year, int) or year < 1900 or year > 2100:
            raise ValueError("Year must be a valid integer between 1900 and 2100")

        try:
            # Get payroll period results for employment and year
            endpoint = f"providers/employers/employees/employments/{employment_id}/payrollperiodresults/year/{year}"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=False  # This endpoint returns single content object
            )

            # Convert to DataFrame for validation
            if not response_data or "content" not in response_data:
                return pd.DataFrame(), pd.DataFrame()

            # Extract content from response
            content = response_data["content"]

            # Normalize nested JSON structure (single content object)
            df = pd.json_normalize([content])

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            # Validate data using Pandera schema
            valid_data, invalid_data = BrynQFunctions.validate_data(df, PayrollPeriodResultsGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get payroll period results for employment {employment_id} and year {year}: {e}")
