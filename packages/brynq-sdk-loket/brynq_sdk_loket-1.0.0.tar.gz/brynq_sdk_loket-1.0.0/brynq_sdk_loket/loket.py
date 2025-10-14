from brynq_sdk_brynq import BrynQ
import requests
from typing import Optional, Literal, Dict, Any, List, Union, get_args
from pydantic import BaseModel
from .providers import Providers
from .employers import Employers
from .administrations import Administrations
from .employments import Employments
from .employees import Employees
from .absence_progress import AbsenceProgress
from .benefit_inkind_types import BenefitInKindTypes
from .benefits_and_deductions import BenefitsAndDeductions
from .benefits_inkind import BenefitsInKind
from .social_security_benefits import SocialSecurityBenefits
from .pension_benefits import PensionBenefits
from .work_related_costs_scheme_financials import WorkRelatedCostsSchemeFinancials
from .declarations import Declarations
from .contacts import Contacts
from .children import Children
from .partners import Partners
from .departments import Departments
from .functions import Functions
from .working_hours import WorkingHours
from .organizational_entities import OrganizationalEntities
from .leave import Leave
from .leave_balance import LeaveBalance
from .leave_request import LeaveRequest
from .leave_types import LeaveTypes
from .payslips import Payslips
from .year_end_statements import YearEndStatements


class Loket(BrynQ):
    """
    This class is meant to be a simple wrapper around the Loket API. In order to start using it, authorize your application in BrynQ.
    You will need to provide a token for the authorization, which can be set up in BrynQ and referred to with a label.
    """

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        super().__init__()
        self.timeout = 3600
        if debug:
            self.base_url = "https://api.loket-acc.nl/v2"
        else:
            self.base_url = "https://api.loket.nl/v2/"

        credentials = self.interfaces.credentials.get(
            system="loket",
            system_type=system_type
        )

        api_token = credentials["data"]["api_token"]
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Initialize session
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Initialize resource components
        self.providers = Providers(self)
        self.employers = Employers(self)
        self.administrations = Administrations(self)
        self.employments = Employments(self)
        self.employees = Employees(self)
        self.absence_progress = AbsenceProgress(self)
        self.benefit_inkind_types = BenefitInKindTypes(self)
        self.benefits_and_deductions = BenefitsAndDeductions(self)
        self.benefits_inkind = BenefitsInKind(self)
        self.social_security_benefits = SocialSecurityBenefits(self)
        self.pension_benefits = PensionBenefits(self)
        self.work_related_costs_scheme_financials = WorkRelatedCostsSchemeFinancials(self)
        self.declarations = Declarations(self)
        self.contacts = Contacts(self)
        self.children = Children(self)
        self.partners = Partners(self)
        self.departments = Departments(self)
        self.functions = Functions(self)
        self.working_hours = WorkingHours(self)
        self.organizational_entities = OrganizationalEntities(self)
        self.leave = Leave(self)
        self.leave_balance = LeaveBalance(self)
        self.leave_request = LeaveRequest(self)
        self.leave_types = LeaveTypes(self)
        self.payslips = Payslips(self)
        self.year_end_statements = YearEndStatements(self)


    def get(
        self,
        endpoint: str,
        page_number: Optional[int] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
        get_all_pages: bool = True,
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Private method to make GET requests to Loket API with pagination, filtering and ordering support.

        Args:
            endpoint: API endpoint path (e.g., 'providers/employers/{employerId}/employees')
            page_number: Page number to retrieve (default: 1, ignored if get_all_pages=True)
            filter_query: OData-style filter query (e.g., "city eq 'Redmond'")
            order_by: Field(s) to order by (e.g., "companyName" or "-companyName,address.houseNumber")
            get_all_pages: If True, automatically fetches all pages and returns combined results
            **kwargs: Additional query parameters

        Returns:
            If get_all_pages=True: List of all entities from all pages
            If get_all_pages=False: Dict containing the API response data

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        if get_all_pages:
            return self._get_all_pages(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                **kwargs
            )
        else:
            return self._get_single_page(
                endpoint=endpoint,
                page_number=page_number,
                filter_query=filter_query,
                order_by=order_by,
                **kwargs
            )

    def _get_single_page(
        self,
        endpoint: str,
        page_number: Optional[int] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a single page from the API.
        """
        # Build query parameters
        params = {}

        # Add pagination parameters
        if page_number is not None:
            params['pageNumber'] = page_number

        # Add filtering
        if filter_query:
            params['filter'] = filter_query

        # Add ordering
        if order_by:
            params['orderBy'] = order_by

        # Add any additional parameters
        params.update(kwargs)

        # Construct full URL
        url = f"{self.base_url}/{endpoint}"

        # Make the request
        response = self.session.get(
            url=url,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()

        return response.json()

    def _get_all_pages(
        self,
        endpoint: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get all pages from the API and combine the results.
        """
        all_entities = []
        current_page = 1
        total_pages = None

        while True:
            # Get current page
            response_data = self._get_single_page(
                endpoint=endpoint,
                page_number=current_page,
                filter_query=filter_query,
                order_by=order_by,
                **kwargs
            )

            # Extract entities from current page
            if "_embedded" in response_data and response_data["_embedded"]:
                all_entities.extend(response_data["_embedded"])

            # Get pagination info
            if total_pages is None:
                total_pages = response_data.get("totalPages", 1)

            # Check if we've reached the last page
            if current_page >= total_pages:
                break

            current_page += 1

        return all_entities

    @staticmethod
    def flat_dict_to_nested_dict(flat_dict: dict, model: BaseModel) -> dict:
        """
        Convert a flat dictionary to a nested dictionary based on a Pydantic model structure.

        This utility function helps transform flat key-value pairs into nested structures
        that match the expected format of Pydantic models with nested BaseModel fields.

        Args:
            flat_dict: The flat dictionary to convert
            model: The Pydantic model to use as a template for the nested structure

        Returns:
            A nested dictionary matching the model structure

        Example:
            flat_data = {
                "value": "Verlof",
                "balance_exceeds_year": True,
                "enabled": True
            }
            nested = Loket.flat_dict_to_nested_dict(flat_data, LeaveTypeUpdate)
        """
        nested = {}
        for name, field in model.model_fields.items():
            key_in_input = name
            alias = field.alias or name
            ann = field.annotation

            # 1) If the user already provided a nested dict (using name or alias)
            if key_in_input in flat_dict and isinstance(flat_dict[key_in_input], dict):
                nested[alias] = flat_dict[key_in_input]
                continue
            if alias in flat_dict and isinstance(flat_dict[alias], dict):
                nested[alias] = flat_dict[alias]
                continue

            # 2) If the field itself is a BaseModel → recurse
            if isinstance(ann, type) and issubclass(ann, BaseModel):
                nested_candidate = Loket.flat_dict_to_nested_dict(flat_dict, ann)
                if nested_candidate:  # only add if not empty
                    nested[alias] = nested_candidate
                continue

            # 3) Handle Union/Optional[BaseModel] cases
            args = get_args(ann)
            if any(isinstance(item, type) and issubclass(item, BaseModel) for item in args):
                nested_model = next(
                    item for item in args if isinstance(item, type) and issubclass(item, BaseModel)
                )
                nested_candidate = Loket.flat_dict_to_nested_dict(flat_dict, nested_model)
                if nested_candidate:
                    nested[alias] = nested_candidate
                continue

            # 4) Primitive fields (string/int/bool etc.)
            if key_in_input in flat_dict:
                nested[alias] = flat_dict[key_in_input]

        return nested
