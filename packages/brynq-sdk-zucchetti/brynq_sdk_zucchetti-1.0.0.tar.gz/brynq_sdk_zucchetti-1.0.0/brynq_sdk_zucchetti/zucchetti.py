from typing import Dict, Optional, Literal
from .client import ZucchettiClient, ZucchettiConfig
from .subject import Subject
from .employment import Employment
from brynq_sdk_brynq import BrynQ



class Zucchetti(BrynQ):
    """Base entrypoint for BrynQ Zucchetti SDK.

    Provides configured SOAP client and exposes resource helpers for
    Subject and Employment data management in Zucchetti HR system.

    Usage:
        zucchetti = Zucchetti(system_type="source", debug=False)
    Args:

        system_type (str, optional): BrynQ system type. Defaults to None.
        debug (bool, optional): Debug mode. Defaults to False.

    Attributes:
        subject: Subject resource for employee master data management
        employment: Employment resource for employment data management

    Raises:
        ValueError: If required credentials are missing or invalid
        ConnectionError: If SOAP service connection fails
    """

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        """Initialize the Zucchetti SDK client.

        Sets up SOAP clients for both GET and POST operations, configures
        authentication credentials, and initializes resource helpers.

        Args:
            system_type (str, optional): BrynQ system type identifier.
                Used to retrieve credentials from BrynQ interfaces.
            debug (bool, optional): Enable debug mode for detailed logging.

        Raises:
            ValueError: If required credentials are missing from interfaces
            ConnectionError: If SOAP service connection fails during initialization
        """
        super().__init__()
        self.debug = debug
        self.timeout = 60

        # Get credentials from interfaces
        credentials = self.interfaces.credentials.get(system="zucchetti", system_type=system_type)
        self.timeout = 60
        self.base_url = "https://saas.hrzucchetti.it"
        self.get_wsdl_link = None
        self.post_wsdl_link = None
        if credentials["data"]["get_wsdl_uri"]:
            self.get_wsdl_link = f"{self.base_url}/{credentials["data"]["domain"]}/{credentials["data"]["get_wsdl_uri"]}/?wsdl"
        if credentials["data"]["post_wsdl_uri"]:
            self.post_wsdl_link = f"{self.base_url}/{credentials["data"]["domain"]}/{credentials["data"]["post_wsdl_uri"]}/?wsdl"
        self.username = credentials["data"]["username"]
        self.password = credentials["data"]["password"]
        self.company = credentials["data"]["company"]
        reception_employment = credentials["data"]["reception_employment"]
        reception_subject = credentials["data"]["reception_subject"]



        # Initialize resources
        self.subject = Subject(self, reception_subject=reception_subject)
        self.employment = Employment(self, reception_employment=reception_employment)

        # Initialize clients based on available WSDL links
        self.get_client = None
        self.post_client = None

        # Create GET client if get_wsdl_link is available
        if self.get_wsdl_link:
            get_config = ZucchettiConfig(
                wsdl_link=self.get_wsdl_link,
                username=self.username,
                password=self.password,
                company=self.company,
                timeout=self.timeout
            )
            self.get_client = ZucchettiClient(get_config)

        # Create POST client if post_wsdl_link is available
        if self.post_wsdl_link:
            post_config = ZucchettiConfig(
                wsdl_link=self.post_wsdl_link,
                username=self.username,
                password=self.password,
                company=self.company,
                timeout=self.timeout
            )
            self.post_client = ZucchettiClient(post_config)


    def post(self, pfile: str):
        """Perform POST operation using SOAP client.

        Sends formatted payload to Zucchetti HR system via SOAP service.

        Args:
            pfile (str): Formatted payload string in Zucchetti's required format.
                Format: CompanyCode;EmployeeCode;StartValidation;ReceptionCode;FieldCode;Reference;Value||

        Returns:
            tuple: Response tuple containing (status, request_xml, response_xml)

        Raises:
            ValueError: If POST client is not available or configured
            ConnectionError: If SOAP service connection fails
        """
        if not self.post_client:
            raise ValueError("POST client not available. Check if post_wsdl_link is configured.")
        return self.post_client.run_import(pfile)


    def _format_subject_line(self, company_code: str, employee_code: str, start_validation: str, reception_code: str, field_code: str, value: str, reference: str = "") -> str:
        """Format a single Subject/Employment line in Zucchetti's required format.

        Creates a semicolon-delimited line with || terminator for Zucchetti HR system.

        Args:
            company_code (str): Company identifier code
            employee_code (str): Employee identifier code
            start_validation (str): Start validation date (YYYYMMDD)
            reception_code (str): Reception code (e.g., "HIBOB-ANAGR", "HIBOB-EMPL")
            field_code (str): Field code identifier
            value (str): Field value
            reference (str, optional): Reference value. Defaults to empty string.

        Returns:
            str: Formatted line in format: CompanyCode;EmployeeCode;StartValidation;ReceptionCode;FieldCode;Reference;Value||

        """
        parts = [
            company_code or "",
            employee_code or "",
            start_validation or "",
            reception_code or "",
            field_code or "",
            reference or "",
            value or "",
        ]
        return ";".join(parts) + "||"

    def _format_subject_payload(self, company_code: str, employee_code: str, start_validation: str, reception_code: str, fields: Dict[str, str], references: Optional[Dict[str, str]] = None) -> str:
        """Build multi-line payload from field mappings.

        Creates a complete payload string with multiple lines for Zucchetti HR system.

        Args:
            company_code (str): Company identifier code
            employee_code (str): Employee identifier code
            start_validation (str): Start validation date (YYYYMMDD)
            reception_code (str): Reception code (e.g., "HIBOB-ANAGR", "HIBOB-EMPL")
            fields (Dict[str, str]): Mapping of field codes to values
            references (Dict[str, str], optional): Mapping of field codes to reference values.
                Defaults to None.

        Returns:
            str: Multi-line payload string with || terminators

        """
        lines = []
        for field_code, field_value in fields.items():
            ref = (references or {}).get(field_code, "")
            # Handle enum values properly - get the actual value, not the enum representation
            if hasattr(field_value, 'value'):
                str_value = str(field_value.value)
            else:
                str_value = str(field_value)
            lines.append(self._format_subject_line(company_code, employee_code, start_validation, reception_code, field_code, str_value, ref))
        return "\n".join(lines)
