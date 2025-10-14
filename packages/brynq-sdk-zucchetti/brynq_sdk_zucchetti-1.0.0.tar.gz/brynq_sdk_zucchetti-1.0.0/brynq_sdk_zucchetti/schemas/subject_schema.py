from pydantic import BaseModel, Field
from typing import Optional
from .enums import IdStateEnum, IdCityEnum, SubjectTypeEnum, EducationLevelEnum, MaritalStatusEnum


class SubjectUpsert(BaseModel):
    """Unified schema for creating/updating a Subject (Employee) in Zucchetti"""

    # Required keys
    subject_code: str = Field(..., description="Subject/Employee code", alias="IDCODAL", max_length=60)
    effective_date: str = Field(..., description="Effective date (YYYYMMDD)", alias="effectiveDate", min_length=8, max_length=8, pattern=r"^\d{8}$")

    # Subject Definition (codd_subject00)
    flcheckobb: Optional[str] = Field(None, description="Mandatory checks flag (S/N)", alias="FLCHECKOBB", min_length=1, max_length=1)

    # Subject Types (codd_subject03)
    subject_type: Optional[SubjectTypeEnum] = Field(None, description="Subject type", alias="IDTPSUBJ")

    # Subject Personal Data (codd_subject03_m)
    name: Optional[str] = Field(None, description="Name", alias="ANNAME", max_length=40)
    surname: Optional[str] = Field(None, description="Surname", alias="ANSURNAM", max_length=40)
    birth_date: Optional[str] = Field(None, description="Birth date (YYYYMMDD)", alias="DTBIRTH", min_length=8, max_length=8, pattern=r"^\d{8}$")
    flactive: Optional[str] = Field(None, description="Active flag (S or N)", alias="FLACTIVE", min_length=1, max_length=1)
    tax_code: Optional[str] = Field(None, description="Personal Tax code", alias="IDIDENTIFP", max_length=16)
    legal_nature: Optional[str] = Field(None, description="Legal nature code", alias="IDLEGALNAT", max_length=3)
    national_id_type: Optional[str] = Field(None, description="National ID Type", alias="TPIDENTIP", min_length=1, max_length=1)
    gender: Optional[str] = Field(None, description="Gender (M or F)", alias="TPSEX", min_length=1, max_length=1)
    marital_status: Optional[MaritalStatusEnum] = Field(None, description="Marital status (coded)", alias="IDMARITAL")
    birth_country: Optional[IdStateEnum] = Field(None, description="Birth country code", alias="IDSTATEBT")
    birth_city_code: Optional[IdCityEnum] = Field(None, description="Birth city code (coded)", alias="IDCITYBT")
    birth_city: Optional[str] = Field(None, description="Birthplace city", alias="ANCITYBT", max_length=40)
    birth_province: Optional[str] = Field(None, description="Birth province", alias="ANPROVINBT", max_length=10)
    citizenship_country: Optional[IdStateEnum] = Field(None, description="Citizenship country code", alias="IDSTATECTY")
    education_level: Optional[EducationLevelEnum] = Field(None, description="Education level (coded)", alias="IDSTUDY")

    # Addresses (codd_subject04)
    address: Optional[str] = Field(None, description="Residence address (street)", alias="ANADDRESRS", max_length=40)
    street_number: Optional[str] = Field(None, description="Residence street no.", alias="ANCIVICNRS", max_length=8)
    zip_code: Optional[str] = Field(None, description="Residence zip code", alias="ANZIPCODRS", max_length=10)
    province: Optional[str] = Field(None, description="Residence province", alias="ANPROVINRS", max_length=10)
    phone: Optional[str] = Field(None, description="Phone no. (personal)", alias="ANTELEFRS", max_length=20)
    address_country: Optional[IdStateEnum] = Field(None, description="Residence country code", alias="IDSTATERS")
    city: Optional[str] = Field(None, description="Residence city", alias="DSCITYRS", max_length=40)

    # Other addresses (codd_subject07)
    email: Optional[str] = Field(None, description="Email address (business)", alias="ANEMAIL", max_length=70)

    class Config:
        populate_by_name = True
