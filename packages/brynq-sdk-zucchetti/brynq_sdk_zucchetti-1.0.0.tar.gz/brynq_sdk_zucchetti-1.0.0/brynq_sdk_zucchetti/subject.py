import pandas as pd
from .schemas.subject_schema import SubjectUpsert


class Subject:
    """Subject (Employee Master Data) resource for Zucchetti SDK.

    Handles creation and updates of employee master data in Zucchetti HR system.
    Provides validation and formatting for subject data.
    Processes subject data using DataFrame for both single and batch operations.

    Usage:
        subject = Subject(zucchetti_instance, reception_subject="HIBOB-ANAGR")

        # Single record (DataFrame with 1 row)
        df_single = pd.DataFrame([subject_data])
        response = subject.create(df_single)
        response = subject.update(df_single)

        # Batch processing (DataFrame with multiple rows)
        df_batch = pd.DataFrame([subject_data1, subject_data2, ...])
        response = subject.create(df_batch)
        response = subject.update(df_batch)

    Attributes:
        zucchetti: Zucchetti base instance providing company and formatting helpers
        reception (str): Reception code for subject operations (e.g., "HIBOB-ANAGR")
    """

    def __init__(self, zucchetti, reception_subject: str):
        """Initialize Subject resource.

        Sets up the subject resource with Zucchetti instance and reception code.

        Args:
            zucchetti: Zucchetti base instance providing company and formatting helpers
            reception_subject (str): Reception code for subject operations (e.g., "HIBOB-ANAGR")
        """
        self.zucchetti = zucchetti
        self.reception = reception_subject

    def _process_dataframe_subject(self, df: pd.DataFrame) -> str:
        """Process DataFrame of subject records and return combined formatted payload.

        Args:
            df (pd.DataFrame): DataFrame containing subject data (1 or multiple rows)

        Returns:
            str: Combined formatted payload string for all subject records
        """
        all_payloads = []

        for _, row in df.iterrows():
            # Convert DataFrame row to dictionary
            subject_data = row.to_dict()
            # Remove NaN values
            subject_data = {k: v for k, v in subject_data.items() if pd.notna(v)}

            try:
                # Process single record
                validated = SubjectUpsert(**subject_data)
                payload = validated.model_dump(by_alias=True, exclude_none=True)

                company_code = self.zucchetti.company
                employee_code = payload.get("IDCODAL", "")
                # StartValidation: for Subject use birth date if provided, else effectiveDate
                start_validation = payload.get("DTBIRTH") or payload.get("effectiveDate", "")
                reception_code = self.reception

                # Remove header fields from field list
                for header_key in ("IDCODAL", "effectiveDate"):
                    payload.pop(header_key, None)

                references = None
                if "IDTPSUBJ" in payload and payload["IDTPSUBJ"]:
                    val = payload["IDTPSUBJ"]
                    if hasattr(val, "value"):
                        val = val.value
                    references = {"IDTPSUBJ": str(val)}

                # Build lines (no references by default)
                single_payload = self.zucchetti._format_subject_payload(
                    company_code=company_code,
                    employee_code=employee_code,
                    start_validation=start_validation,
                    reception_code=reception_code,
                    fields=payload,
                    references=references,
                )
                all_payloads.append(single_payload)
            except Exception as e:
                raise ValueError(f"Failed to process subject record for employee {subject_data.get('subject_code', 'unknown')}: {e}") from e

        return "\n".join(all_payloads)

    def create(self, data: pd.DataFrame) -> str:
        """Create a new subject (employee) in Zucchetti HR system.

        Processes subject data from DataFrame and formats it into Zucchetti's
        required semicolon-delimited format with || terminators.

        Args:
            data (pd.DataFrame): Subject data DataFrame containing employee information.
                Required fields: subject_code, effective_date
                Optional fields: name, surname, birth_date, tax_code, gender, address, etc.
                Can contain 1 or multiple rows.

        Returns:
            str: SOAP response from Zucchetti HR system

        Raises:
            ValidationError: If input data fails Pydantic validation
            ValueError: If SOAP request fails or DataFrame is empty

        Examples:
            # Subject records
            df = pd.DataFrame([
                {"subject_code": "EMP001", "effective_date": "20250101", "name": "John", ...},
                {"subject_code": "EMP002", "effective_date": "20250101", "name": "Jane", ...}
            ])
            response = subject.create(df)
        """
        try:
            if data.empty:
                raise ValueError("DataFrame cannot be empty")

            payload = self._process_dataframe_subject(data)

            try:
                response = self.zucchetti.post(payload)
                return response
            except Exception as e:
                raise ValueError(f"Subject.create failed: {e}") from e

        except Exception as exc:
            raise ValueError(f"Subject.create failed: {exc}") from exc

    def update(self, data: pd.DataFrame) -> str:
        """Update an existing subject (employee) in Zucchetti HR system.

        Processes subject data from DataFrame and uses the same validation and formatting logic as create() method.
        In Zucchetti, create and update operations are identical.

        Args:
            data (pd.DataFrame): Subject data DataFrame containing employee information.
                Can contain 1 or multiple rows.

        Returns:
            str: SOAP response from Zucchetti HR system

        Raises:
            ValidationError: If input data fails Pydantic validation
            ValueError: If SOAP request fails or DataFrame is empty

        Examples:
            # Subject records
            df = pd.DataFrame([
                {"subject_code": "EMP001", "effective_date": "20250101", "email": "john.updated@example.com"},
                {"subject_code": "EMP002", "effective_date": "20250101", "email": "jane.updated@example.com"}
            ])
            response = subject.update(df)
        """
        try:
            return self.create(data)
        except Exception as exc:
            raise ValueError(f"Subject.update failed: {exc}") from exc
