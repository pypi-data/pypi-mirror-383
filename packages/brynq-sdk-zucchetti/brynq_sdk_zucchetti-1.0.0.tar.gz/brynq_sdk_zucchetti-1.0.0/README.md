# BrynQ SDK Zucchetti

The BrynQ SDK Zucchetti package provides a comprehensive interface for interacting with the Zucchetti HR system, enabling seamless integration of Zucchetti HR functionality into your applications.

## Features

The Zucchetti SDK can be used for:
- Subject (Employee) data management (creation, updates, and validation)
- Employment data management (contractual information, payment details)
- SOAP-based communication with Zucchetti HR system
- Data validation using Pydantic schemas
- Comprehensive error handling and logging
- Support for both GET and POST operations via separate WSDL endpoints

## Installation

```bash
pip install brynq-sdk-zucchetti
```

## Quick Start

```python
from brynq_sdk_zucchetti import Zucchetti

# Initialize the client
zucchetti = Zucchetti(
    system_type="source",
    debug=False
)

# Create a new subject (employee)
subject_data = {
    "subject_code": "EMP001",
    "effective_date": "20250101",
    "name": "John",
    "surname": "Doe",
    "birth_date": "19900101",
    "tax_code": "DOEJHN90A01H501U",
    "gender": "M",
    "address": "Via Roma 123",
    "zip_code": "00100",
    "city": "Rome",
    "province": "RM",
    "email": "john.doe@example.com"
}
response = zucchetti.subject.create(subject_data)

# Create employment data for the subject
employment_data = {
    "effective_date": "20250101",
    "external_code": "EMP001",
    "hire_date": "20250101",
    "status_code": "ACTIVE",
    "employment_class": "EMPLOYEE",
    "cost_center": "CC001",
    "subsidiary": "MAIN",
    "payment_type": "IT",
    "italian_iban": "IT60X0542811101000000123456",
    "main_credit": "S",
    "reference_det": "1"
}
response = zucchetti.employment.create(employment_data)

# Update subject data
update_data = subject_data.copy()
update_data["email"] = "john.doe.updated@example.com"
response = zucchetti.subject.update(update_data)

# Update employment data
employment_update = employment_data.copy()
employment_update["cost_center"] = "CC002"
response = zucchetti.employment.update(employment_update)
```

## Configuration

To use the Zucchetti HR system, you need to configure the SDK with your credentials:

### Initializing the Zucchetti Client

```python
from brynq_sdk_zucchetti import Zucchetti

# Initialize the Zucchetti client
zucchetti = Zucchetti(
    system_type="source",  # System type identifier
    debug=False  # Set to True for debug mode
)
```

Parameters:
- **system_type** (str): System type identifier (e.g., "source", "target")
- **debug** (bool, optional): Whether to enable debug mode. Defaults to False.

## Basic Usage

### Working with Subjects (Employees)

```python
# Create a new subject (employee)
subject_data = {
    "subject_code": "EMP001",
    "effective_date": "20250101",
    "name": "John",
    "surname": "Doe",
    "birth_date": "19900101",
    "tax_code": "DOEJHN90A01H501U",
    "gender": "M",
    "address": "Via Roma 123",
    "zip_code": "00100",
    "city": "Rome",
    "province": "RM",
    "email": "john.doe@example.com"
}
response = zucchetti.subject.create(subject_data)

# Update subject data
update_data = subject_data.copy()
update_data["email"] = "john.doe.updated@example.com"
response = zucchetti.subject.update(update_data)
```

### Working with Employment Data

```python
# Create employment data for a subject
employment_data = {
    "effective_date": "20250101",
    "external_code": "EMP001",
    "hire_date": "20250101",
    "status_code": "ACTIVE",
    "employment_class": "EMPLOYEE",
    "cost_center": "CC001",
    "subsidiary": "MAIN",
    "payment_type": "IT",
    "italian_iban": "IT60X0542811101000000123456",
    "main_credit": "S",
    "reference_det": "1"
}
response = zucchetti.employment.create(employment_data)

# Update employment data
employment_update = employment_data.copy()
employment_update["cost_center"] = "CC002"
response = zucchetti.employment.update(employment_update)
```

### Advanced Employment Configuration

```python
# Employment with foreign IBAN
employment_foreign = {
    "effective_date": "20250101",
    "external_code": "EMP002",
    "hire_date": "20250101",
    "status_code": "ACTIVE",
    "employment_class": "EMPLOYEE",
    "cost_center": "CC001",
    "subsidiary": "MAIN",
    "payment_type": "EE",  # Foreign payment
    "foreign_iban": "DE89370400440532013000",
    "foreign_account": "1234567890",
    "foreign_bank": "DEUTDEFF",
    "foreign_currency": "EUR",
    "main_credit": "S",
    "reference_det": "1"
}
response = zucchetti.employment.create(employment_foreign)

# Employment with part-time configuration
employment_parttime = {
    "effective_date": "20250101",
    "external_code": "EMP003",
    "hire_date": "20250101",
    "status_code": "ACTIVE",
    "employment_class": "EMPLOYEE",
    "cost_center": "CC001",
    "subsidiary": "MAIN",
    "payment_type": "IT",
    "italian_iban": "IT60X0542811101000000123456",
    "main_credit": "S",
    "reference_det": "1",
    "part_time_percentage": "5000",  # 50% part-time
    "part_time_type": "01",
    "employment_type": "1"
}
response = zucchetti.employment.create(employment_parttime)
```

### Working with Enums

The SDK provides enums for better type safety and validation:

```python
from brynq_sdk_zucchetti.schemas.enums import (
    SubjectTypeEnum,
    MaritalStatusEnum,
    EducationLevelEnum,
    StatusCodeEnum,
    EmploymentClassEnum
)

# Using enums in subject data
subject_with_enums = {
    "subject_code": "EMP004",
    "effective_date": "20250101",
    "name": "Jane",
    "surname": "Smith",
    "birth_date": "19850101",
    "tax_code": "SMTHJN85A41H501U",
    "gender": "F",
    "subject_type": SubjectTypeEnum.EMPLOYEE,
    "marital_status": MaritalStatusEnum.SINGLE,
    "education_level": EducationLevelEnum.UNIVERSITY,
    "address": "Via Milano 456",
    "zip_code": "20100",
    "city": "Milan",
    "province": "MI",
    "email": "jane.smith@example.com"
}
response = zucchetti.subject.create(subject_with_enums)

# Using enums in employment data
employment_with_enums = {
    "effective_date": "20250101",
    "external_code": "EMP004",
    "hire_date": "20250101",
    "status_code": StatusCodeEnum.ACTIVE,
    "employment_class": EmploymentClassEnum.EMPLOYEE,
    "cost_center": "CC001",
    "subsidiary": "MAIN",
    "payment_type": "IT",
    "italian_iban": "IT60X0542811101000000123456",
    "main_credit": "S",
    "reference_det": "1"
}
response = zucchetti.employment.create(employment_with_enums)
```

## Error Handling

The SDK provides comprehensive error handling for API requests:

```python
from requests.exceptions import HTTPError
from pydantic import ValidationError

try:
    response = zucchetti.subject.create(subject_data)
    print(f"Success: {response.status_code}")
except ValidationError as e:
    print(f"Validation error: {e}")
except HTTPError as e:
    print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Data Validation

The SDK uses Pydantic models for data validation:

```python
# Invalid data will raise ValidationError
invalid_subject = {
    "subject_code": "EMP001",
    "effective_date": "invalid-date",  # Should be YYYYMMDD format
    "name": "John",
    "surname": "Doe"
}

try:
    response = zucchetti.subject.create(invalid_subject)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## SOAP Communication

The SDK handles SOAP communication automatically:

- **GET Operations**: Uses the configured GET WSDL endpoint
- **POST Operations**: Uses the configured POST WSDL endpoint
- **Authentication**: Handles SOAP authentication automatically
- **Timeout**: Configurable timeout (default: 60 seconds)

## Advanced Usage

### Validation Features

The SDK includes comprehensive validation:

- **Date Format Validation**: All dates must be in YYYYMMDD format
- **Field Length Validation**: Automatic validation of field lengths
- **Required Field Validation**: Ensures all required fields are present
- **Enum Validation**: Validates enum values against allowed options
- **Cross-field Validation**: Validates relationships between fields (e.g., effective_date must match hire_date)
- **Payment Type Consistency**: Ensures Italian vs Foreign IBAN fields are used correctly
- **Auto-injection**: Automatically injects required fields like IDREFDET when needed

### Payload Format

The SDK automatically formats data into Zucchetti's required semicolon-delimited format:

```
CompanyCode;EmployeeCode;StartValidation;ReceptionCode;FieldCode;Reference;Value||
```

Example:
```
001;EMP001;20241201;HIBOB-EMPL;DTASSUMPT;;20241201||
001;EMP001;20241201;HIBOB-EMPL;IDREFDET;;1||
001;EMP001;20241201;HIBOB-EMPL;FLMAIN;1;S||
```

## Testing

The package includes comprehensive test suites:

```bash
# Run basic tests
python test_comprehensive.py

# Run comprehensive validation tests
python test_validation_comprehensive.py
```

## Documentation

For detailed documentation, please visit our [API Reference](docs/api/zucchetti/zucchetti.md).

### Key Documentation Sections
- [Subject Management](docs/api/zucchetti/subject.md) - Complete subject (employee) operations
- [Employment Management](docs/api/zucchetti/employment.md) - Employment data operations
- [Schema Documentation](docs/api/schemas) - Detailed schema information
- [Getting Started Guide](docs/getting-started.md) - Installation and setup instructions

## Contributing

This package follows BrynQ SDK standards and conventions. When contributing:

1. Follow the established naming conventions (`<Subject><Type>`)
2. Use Pydantic models for validation
3. Include comprehensive error handling
4. Add appropriate documentation
5. Include tests for new functionality

## License

This package is licensed under the BrynQ License.

## Support

For support and questions, please contact support@brynq.com.
