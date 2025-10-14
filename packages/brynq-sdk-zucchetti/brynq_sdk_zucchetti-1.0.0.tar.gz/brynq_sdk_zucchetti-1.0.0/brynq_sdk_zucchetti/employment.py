from typing import Dict, Any
import pandas as pd
from .schemas.employment_schema import EmploymentUpsert


class Employment:
    """Employment resource for Zucchetti SDK.

    Handles creation and updates of employment data in Zucchetti HR system.
    Provides validation, formatting, and field ordering for employment data.
    Processes employment data using DataFrame for both single and batch operations.

    Usage:
        employment = Employment(zucchetti_instance, reception_employment="HIBOB-EMPL")

        # Single record (DataFrame with 1 row)
        df_single = pd.DataFrame([employment_data])
        response = employment.create(df_single)
        response = employment.update(df_single)

        # Batch processing (DataFrame with multiple rows)
        df_batch = pd.DataFrame([employment_data1, employment_data2, ...])
        response = employment.create(df_batch)
        response = employment.update(df_batch)

    Attributes:
        zucchetti: Zucchetti base instance providing company and formatting helpers
        reception (str): Reception code for employment operations (e.g., "HIBOB-EMPL")
    """

    def __init__(self, zucchetti, reception_employment: str):
        """Initialize Employment resource.

        Sets up the employment resource with Zucchetti instance and reception code.

        Args:
            zucchetti: Zucchetti base instance providing company and formatting helpers
            reception_employment (str): Reception code for employment operations (e.g., "HIBOB-EMPL")
        """
        self.zucchetti = zucchetti
        self.reception = reception_employment

    def _build_core_fields(self, payload: Dict[str, Any]) -> Dict[str, str]:
        order = [
            "DTASSUMPT", "IDNATREL", "IDGRPEM", "TPRELATION", "IDCOSTCNT", "IDDEPENDEN",
            "IDCAUSEASS", "IDCAUSELOF", "DTEXPDT", "DTLAYOFF",
        ]
        return {code: payload[code] for code in order if code in payload}

    def _build_contractual_fields(self, payload: Dict[str, Any]) -> Dict[str, str]:
        order = [
            "IDAGRMNT", "IDLVAGRMNT", "IDQUAGRMNT", "ANEXRIF01",
        ]
        return {code: payload[code] for code in order if code in payload}

    def _build_optional_fields(self, payload: Dict[str, Any]) -> Dict[str, str]:
        order = [
            "PEPARTTIME", "TPPARTTIME", "DTCONVTT", "DTENDPT"
        ]
        return {code: payload[code] for code in order if code in payload}

    def _build_payment_fields(self, payload: Dict[str, Any]) -> Dict[str, str]:
        # Reference: 1 should be used in formatter for these
        order = [
            "IDREFDET", "FLMAIN", "IDPAY", "IDIBANIT", "IDIBANCNTY", "IDIBANDIGT", "IDABI", "IDCAB",
            "IDIBANEE", "IDIBANFG", "IDBANKFG", "IDCURRFG", "FLIBAN", "ANBCODE", "ANCHKACCEM",
        ]
        return {code: payload[code] for code in order if code in payload}

    def _process_dataframe_employment(self, df: pd.DataFrame) -> str:
        """Process DataFrame of employment records and return combined formatted payload.

        Args:
            df (pd.DataFrame): DataFrame containing employment data (1 or multiple rows)

        Returns:
            str: Combined formatted payload string for all employment records
        """
        all_payloads = []

        for _, row in df.iterrows():
            # Convert DataFrame row to dictionary
            employment_data = row.to_dict()
            # Remove NaN values
            employment_data = {k: v for k, v in employment_data.items() if pd.notna(v)}

            try:
                # Process single record
                validated = EmploymentUpsert(**employment_data)
                payload = validated.model_dump(by_alias=True, exclude_none=True)

                employee_code = payload.get("IDCODAL", "")
                start_validation = payload.get("effectiveDate", "")

                # Build ordered sections
                core = self._build_core_fields(payload)
                contractual = self._build_contractual_fields(payload)
                optional = self._build_optional_fields(payload)
                payment = self._build_payment_fields(payload)

                # Assemble in order
                result = []
                if core:
                    result.append(self._format_with_order(employee_code, start_validation, core))
                if contractual:
                    result.append(self._format_with_order(employee_code, start_validation, contractual))
                if optional:
                    result.append(self._format_with_order(employee_code, start_validation, optional))
                if payment:
                    # Ensure IDREFDET appears first without reference value, then others with reference=1
                    pay_ordered = {}
                    if "IDREFDET" in payment:
                        pay_ordered["IDREFDET"] = payment["IDREFDET"]
                    for k, v in payment.items():
                        if k != "IDREFDET":
                            pay_ordered[k] = v
                    if "IDREFDET" in pay_ordered:
                        result.append(self._format_with_order(employee_code, start_validation, {"IDREFDET": pay_ordered["IDREFDET"]}, use_reference=False))
                        del pay_ordered["IDREFDET"]
                    if pay_ordered:
                        result.append(self._format_with_order(employee_code, start_validation, pay_ordered, use_reference=True))

                single_payload = "".join(result)
                all_payloads.append(single_payload)
            except Exception as e:
                raise ValueError(f"Failed to process employment record for employee {employment_data.get('external_code', 'unknown')}: {e}") from e

        return "\n".join(all_payloads)

    def _format_with_order(self, employee_code: str, start_validation: str, fields: Dict[str, str], use_reference: bool = False) -> str:
        references = None
        if use_reference:
            references = {code: "1" for code in fields.keys() if code != "IDREFDET"}
        return self.zucchetti._format_subject_payload(
            company_code=self.zucchetti.company,
            employee_code=employee_code,
            start_validation=start_validation,
            reception_code=self.reception,
            fields=fields,
            references=references,
        )

    def create(self, data: pd.DataFrame) -> str:
        """Create new employment data in Zucchetti HR system.

        Processes employment data from DataFrame and formats it into Zucchetti's
        required semicolon-delimited format with proper field ordering and references.
        All validations are handled by Pydantic model_validators in the schema.

        Args:
            data (pd.DataFrame): Employment data DataFrame containing employment information.
                Required fields: external_code, effective_date
                Optional fields: hire_date, status_code, employment_class, cost_center,
                payment_type, italian_iban, foreign_iban, etc.
                Can contain 1 or multiple rows.

        Returns:
            str: SOAP response from Zucchetti HR system

        Raises:
            ValidationError: If input data fails Pydantic validation
            ValueError: If SOAP request fails or DataFrame is empty

        Examples:
            # Employment records
            df = pd.DataFrame([
                {"external_code": "EMP001", "effective_date": "20250101", "hire_date": "20250101", ...},
                {"external_code": "EMP002", "effective_date": "20250101", "hire_date": "20250101", ...}
            ])
            response = employment.create(df)
        """
        try:
            if data.empty:
                raise ValueError("DataFrame cannot be empty")

            payload = self._process_dataframe_employment(data)

            try:
                response = self.zucchetti.post(payload)
                return response
            except Exception as e:
                raise ValueError(f"Request failed: {e}") from e

        except Exception as exc:
            raise ValueError(f"Employment.create failed: {exc}") from exc

    def update(self, data: pd.DataFrame) -> str:
        """Update existing employment data in Zucchetti HR system.

        Processes employment data from DataFrame and uses the same validation and formatting logic as create() method.
        In Zucchetti, create and update operations are identical.

        Args:
            data (pd.DataFrame): Employment data DataFrame containing employment information.
                Can contain 1 or multiple rows.

        Returns:
            str: SOAP response from Zucchetti HR system

        Raises:
            ValidationError: If input data fails Pydantic validation
            ValueError: If SOAP request fails or DataFrame is empty

        Examples:
            # Employment records
            df = pd.DataFrame([
                {"external_code": "EMP001", "effective_date": "20250101", "cost_center": "CC002"},
                {"external_code": "EMP002", "effective_date": "20250101", "cost_center": "CC003"}
            ])
            response = employment.update(df)
        """
        try:
            return self.create(data)
        except Exception as exc:
            raise ValueError(f"Employment.update failed: {exc}") from exc
