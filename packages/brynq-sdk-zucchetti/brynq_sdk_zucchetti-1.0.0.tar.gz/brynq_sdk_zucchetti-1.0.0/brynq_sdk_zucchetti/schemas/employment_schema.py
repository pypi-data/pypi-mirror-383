from pydantic import BaseModel, Field, model_validator
from typing import Optional

from .enums import EmploymentClassEnum, StatusCodeEnum

class EmploymentUpsert(BaseModel):
    """Unified schema for creating/updating Employment data in Zucchetti"""

    # Required keys
    effective_date: str = Field(..., description="Effective date (YYYYMMDD)", alias="effectiveDate", min_length=8, max_length=8, pattern=r"^\d{8}$")
    external_code: str = Field(..., description="External report code / Integration key", alias="IDCODAL", max_length=60)

    # Employment/Credit (hrdd_employee02) - Data Reference IDREFDET required
    payment_type: Optional[str] = Field(None, description="Payment type code", alias="IDPAY", max_length=2)
    italian_iban: Optional[str] = Field(None, description="Italian IBAN", alias="IDIBANIT", max_length=27)
    foreign_iban: Optional[str] = Field(None, description="Foreign IBAN", alias="IDIBANEE", max_length=34)
    main_credit: Optional[str] = Field(None, description="Main Credit (S or N)", alias="FLMAIN", min_length=1, max_length=1)
    reference_det: Optional[str] = Field(None, description="Reference code for data retrieval", alias="IDREFDET", max_length=4)

    # Additional credit fields
    bank_code: Optional[str] = Field(None, description="CIN employee credit", alias="ANBCODE", max_length=27)
    bank_account: Optional[str] = Field(None, description="Employee credit bank account", alias="ANCHKACCEM", max_length=27)
    abi_code: Optional[str] = Field(None, description="Employee credit bank code (ABI)", alias="IDABI", max_length=27)
    cab_code: Optional[str] = Field(None, description="Employee credit branch code (CAB)", alias="IDCAB", max_length=27)
    iban_country: Optional[str] = Field(None, description="IBAN country code", alias="IDIBANCNTY", max_length=27)
    iban_digit: Optional[str] = Field(None, description="IBAN check digit", alias="IDIBANDIGT", max_length=27)
    foreign_account: Optional[str] = Field(None, description="Foreign account number", alias="IDIBANFG", max_length=34)
    foreign_bank: Optional[str] = Field(None, description="Foreign bank code", alias="IDBANKFG", max_length=34)
    foreign_currency: Optional[str] = Field(None, description="Foreign account currency", alias="IDCURRFG", max_length=34)
    is_iban: Optional[str] = Field(None, description="IBAN flag (S/N)", alias="FLIBAN", min_length=1, max_length=1)

    # Contractual (hrdd_employee06)
    agreement_code: Optional[str] = Field(None, description="Collective agreement code", alias="IDAGRMNT")
    contractual_level: Optional[str] = Field(None, description="Contractual level", alias="IDLVAGRMNT", max_length=3)
    contractual_qualification: Optional[str] = Field(None, description="Contractual qualification code", alias="IDQUAGRMNT", max_length=3)
    external_reference: Optional[str] = Field(None, description="External reference 1 (Profit Center)", alias="ANEXRIF01", max_length=20)

    # Employment/Organic (hrdd_employee11)
    hire_date: Optional[str] = Field(None, description="Hire date (YYYYMMDD)", alias="DTASSUMPT", min_length=8, max_length=8, pattern=r"^\d{8}$")
    end_date: Optional[str] = Field(None, description="Part-time end date (YYYYMMDD)", alias="DTENDPT", min_length=8, max_length=8, pattern=r"^\d{8}$")
    fiscal_end_date: Optional[str] = Field(None, description="Fixed-term end date (fiscal) (YYYYMMDD)", alias="DTEXPDT", min_length=8, max_length=8, pattern=r"^\d{8}$")
    termination_date: Optional[str] = Field(None, description="Termination date (YYYYMMDD)", alias="DTLAYOFF", min_length=8, max_length=8, pattern=r"^\d{8}$")
    status_code: Optional[StatusCodeEnum] = Field(None, description="Status code (employment state)", alias="IDGRPEM")
    hire_reason: Optional[str] = Field(None, description="Hire reason (type)", alias="IDCAUSEASS", max_length=3)
    cost_center: Optional[str] = Field(None, description="Cost center code", alias="IDCOSTCNT", max_length=40)
    subsidiary: Optional[str] = Field(None, description="Subsidiary/branch code/location", alias="IDDEPENDEN", max_length=10)
    termination_type: Optional[str] = Field(None, description="Termination type", alias="IDCAUSELOF", max_length=3)
    employment_class: Optional[EmploymentClassEnum] = Field(None, description="Employment class", alias="IDNATREL")
    part_time_percentage: Optional[str] = Field(None, description="Part-time percentage (0..10000 basis)", alias="PEPARTTIME", max_length=7)
    part_time_type: Optional[str] = Field(None, description="Part-time type", alias="TPPARTTIME", max_length=2)
    employment_type: Optional[str] = Field(None, description="Employment type", alias="TPRELATION", max_length=1)

    # Seniority (hrdd_employee05)
    seniority_start_date: Optional[str] = Field(None, description="Seniority start date (YYYYMMDD)", alias="DTCONVTT", min_length=8, max_length=8, pattern=r"^\d{8}$")

    @model_validator(mode="after")
    def validate_effective_matches_hire(self):
        if self.effective_date and self.hire_date and self.effective_date != self.hire_date:
            raise ValueError("effectiveDate must match DTASSUMPT (Hire Date)")
        return self

    @model_validator(mode="after")
    def ensure_payment_reference_and_consistency(self):
        payment_present = any([
            self.main_credit, self.payment_type, self.italian_iban, self.iban_country, self.iban_digit,
            self.abi_code, self.cab_code, self.foreign_iban, self.foreign_account, self.foreign_bank, self.foreign_currency
        ])
        if payment_present and not self.reference_det:
            self.reference_det = "1"
        if self.payment_type in {"IT", "EE"}:
            has_italian = any([self.italian_iban, self.iban_country, self.iban_digit, self.abi_code, self.cab_code])
            has_foreign = any([self.foreign_iban, self.foreign_account, self.foreign_bank, self.foreign_currency])
            if self.payment_type == "IT" and has_foreign:
                raise ValueError("IDPAY=IT requires only Italian IBAN fields; foreign IBAN fields present")
            if self.payment_type == "EE" and has_italian:
                raise ValueError("IDPAY=EE requires only foreign IBAN fields; Italian IBAN fields present")
        return self

    class Config:
        populate_by_name = True
