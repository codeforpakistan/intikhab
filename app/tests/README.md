# Intikhab Election System - Test Suite

This directory contains comprehensive tests for the Intikhab electronic voting system models.

## Test Structure

```
app/tests/
├── __init__.py                 # Test package initialization
├── test_base.py               # Base test classes and utilities
├── test_models.py             # Test runner/imports
├── test_election_model.py     # Election model tests
├── test_party_model.py        # Party model tests
├── test_candidate_model.py    # Candidate model tests
├── test_vote_model.py         # Vote model tests
└── README.md                  # This file
```

## Running Tests

### Run All Tests
```bash
python manage.py test app.tests
```

### Run Specific Model Tests
```bash
# Election model tests only
python manage.py test app.tests.test_election_model

# Party model tests only
python manage.py test app.tests.test_party_model

# Candidate model tests only
python manage.py test app.tests.test_candidate_model

# Vote model tests only
python manage.py test app.tests.test_vote_model
```

### Run Specific Test Cases
```bash
# Run a specific test class
python manage.py test app.tests.test_election_model.ElectionModelTest

# Run a specific test method
python manage.py test app.tests.test_election_model.ElectionModelTest.test_election_creation
```

### Run Tests with Verbose Output
```bash
python manage.py test app.tests --verbosity=2
```

## Test Coverage

### Election Model Tests (`test_election_model.py`)
- ✅ Basic election creation
- ✅ String representation
- ✅ Default field values
- ✅ Relationship with candidates and votes
- ✅ Date validation
- ✅ Active status toggle
- ✅ Encryption field storage
- ✅ Name length constraints

### Party Model Tests (`test_party_model.py`)
- ✅ Basic party creation
- ✅ String representation
- ✅ Meta verbose names
- ✅ Symbol file handling
- ✅ Name uniqueness
- ✅ Creation timestamp
- ✅ Field constraints
- ✅ Relationship capabilities

### Candidate Model Tests (`test_candidate_model.py`)
- ✅ Basic candidate creation
- ✅ Creation with party and symbol
- ✅ String representation (user full name)
- ✅ Multiple candidates per election
- ✅ Foreign key relationships
- ✅ Optional fields (null/blank)
- ✅ Creation timestamp
- ✅ Deletion protection (PROTECT)

### Vote Model Tests (`test_vote_model.py`)
- ✅ Basic vote creation
- ✅ String representation
- ✅ Unique constraint (one vote per user per election)
- ✅ Multiple users per election
- ✅ Same user across different elections
- ✅ Default field values
- ✅ Ballot JSON storage
- ✅ Hash storage and validation
- ✅ Foreign key relationships
- ✅ Complex ballot data handling

## Test Data and Utilities

### BaseTestCase (`test_base.py`)
The `BaseTestCase` class provides common setup for all tests including:
- Pre-created users (admin, voter, candidate)
- Test party and election
- Test candidate
- Helper methods for creating additional test data

### TestDataMixin (`test_base.py`)
Provides static methods for generating sample test data:
- Sample encrypted ballots
- Sample public/private keys
- Sample vote hashes

## Test Database

Tests use Django's test database which is automatically created and destroyed for each test run. No manual database setup is required.

## Mock Data and Encryption

Since the tests focus on model behavior rather than actual encryption, they use:
- Sample JSON strings for public/private keys
- Mock encrypted ballot data
- Simplified hash values

For integration tests involving actual encryption, see the separate integration test suite.

## Coverage Goals

These tests aim to achieve:
- **Model Creation**: All models can be created with valid data
- **Field Validation**: All field constraints work correctly
- **Relationships**: Foreign keys and related fields function properly
- **Business Logic**: Model methods and properties work as expected
- **Edge Cases**: Boundary conditions and error cases are handled

## Adding New Tests

When adding new model fields or methods:

1. Add tests to the appropriate `test_*_model.py` file
2. Follow the existing naming convention: `test_description_of_what_is_tested`
3. Use the `BaseTestCase` for common setup
4. Add docstrings explaining what each test verifies
5. Update this README if adding new test files

## Dependencies

Tests require:
- Django test framework
- All app models (`Election`, `Party`, `Candidate`, `Vote`)
- Django's `User` model and authentication system
- Python standard library modules (`json`, `hashlib`, etc.)

## Notes

- Some tests may show linter warnings due to Django's dynamic model relationships
- File upload tests use Django's `SimpleUploadedFile` for mock file handling
- Encryption-related tests use mock data rather than actual encryption
- Tests are designed to be independent and can run in any order