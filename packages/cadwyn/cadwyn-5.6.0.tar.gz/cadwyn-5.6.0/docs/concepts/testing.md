# Testing

As Cadwyn allows to keep the same business logic, database schemas, etc -- you should have a single set of **common** tests that test the current latest version. These tests are going to work like the regular tests that you would have if you did not have any API versioning.

Here's a possible structure for test files:

```tree
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── head
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_users.py
    │   ├── test_admins.py
    │   └── test_invoices.py
    ├── v2022_11_16
    │   ├── __init__.py
    │   ├── conftest.py
    │   └── test_invoices.py
    └── v2023_03_11
        ├── __init__.py
        ├── conftest.py
        └── test_users.py

```

The following process is recommended when creating a new version:

1. Before creating a new version, apply the changes you want to your logic and schemas in the latest version (i.e., make the desired breaking changes), and then run the tests in the head directory. The tests that fail indicate the broken contracts
1. Create a new sub-directory in `tests`, name it after the previous version (e.g., v2024_05_04), and copy only the failing tests into it. Ensure these tests invoke the old version of the API
1. Write a `VersionChange` that fixes the tests in this outdated version through converters. In the new version, these same tests should still fail
1. Modify the tests in the head directory so that they test the new API contract and pass successfully

This approach helps to keep the old versions covered by tests and to keep the test code duplication minimal.
