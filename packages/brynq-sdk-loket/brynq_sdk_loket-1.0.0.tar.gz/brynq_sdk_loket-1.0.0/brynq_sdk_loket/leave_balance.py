"""
LeaveBalance resource class for Loket SDK.

This module provides methods for interacting with employment leave balance-related endpoints
in the Loket API, including retrieving leave balance information.
"""

from typing import Optional, Tuple
import pandas as pd

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.leave_balance import LeaveBalanceGet


class LeaveBalance:
    """
    Handles all leave balance-related operations for Loket SDK.

    This class provides methods to interact with employment leave balance endpoints,
    including retrieving leave balance information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the LeaveBalance resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employer_id: str, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get leave balance data for an employer.

        Args:
            employer_id: The unique identifier of the employer
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)

        Example:
            # Get all leave balances for an employer
            valid_df, invalid_df = loket.leave_balance.get(employer_id="xxx-xxx")
        """
        try:
            if not employer_id.strip():
                raise ValueError("Employer ID cannot be empty")

            # Get all leave balances for employer
            endpoint = f"providers/employers/{employer_id}/leavebalances"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=True
            )

            # Convert to DataFrame for validation
            if not response_data:
                return pd.DataFrame(), pd.DataFrame()

            # Handle leaveBalance array - flatten it
            flattened_data = []
            for item in response_data:
                if "leaveBalance" in item and isinstance(item["leaveBalance"], list):
                    for balance in item["leaveBalance"]:
                        # Create a copy of the main item and add balance data
                        flattened_item = item.copy()
                        flattened_item["leaveBalance"] = balance
                        flattened_data.append(flattened_item)
                else:
                    flattened_data.append(item)

            # Normalize nested JSON structure (list of items)
            df = pd.json_normalize(flattened_data)

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            valid_data, invalid_data = BrynQFunctions.validate_data(df, LeaveBalanceGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get leave balances for employer {employer_id}: {e}")
