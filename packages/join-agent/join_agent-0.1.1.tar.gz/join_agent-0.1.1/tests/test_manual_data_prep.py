# tests/test_join_agent_manual.py

import pytest
from join_agent.agent import JoinAgent
from join_agent.models import JoinInput, OperationEnum

# Sample input for manual_data_prep with 2 tables
sample_col_metadata_manual = {
    "customers": {
        "customer_id": {
            "data_type": "int",
            "row_count": 1000,
            "null_count": 0,
            "unique_count": 1000,
            "sample_values": [1, 2, 3],
            "description": "Unique identifier for each customer",
        },
        "name": {
            "data_type": "str",
            "row_count": 1000,
            "null_count": 0,
            "unique_count": 950,
            "sample_values": ["Alice", "Bob"],
            "description": "Customer name",
        },
        "email": {
            "data_type": "str",
            "row_count": 1000,
            "null_count": 5,
            "unique_count": 995,
            "sample_values": ["a@example.com"],
            "description": "Customer email address",
        },
        "signup_date": {
            "data_type": "date",
            "row_count": 1000,
            "null_count": 0,
            "unique_count": 1000,
            "sample_values": ["2025-01-01"],
            "description": "Date when customer signed up",
        },
        "region": {
            "data_type": "str",
            "row_count": 1000,
            "null_count": 10,
            "unique_count": 5,
            "sample_values": ["US", "EU"],
            "description": "Customer region",
        },
    },
    "orders": {
        "order_id": {
            "data_type": "int",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 5000,
            "sample_values": [101, 102],
            "description": "Unique order identifier",
        },
        "customer_id": {
            "data_type": "int",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 1000,
            "sample_values": [1, 2],
            "description": "FK to customers table",
        },
        "product_id": {
            "data_type": "int",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 100,
            "sample_values": [11, 12],
            "description": "Product identifier",
        },
        "quantity": {
            "data_type": "int",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 50,
            "sample_values": [1, 2],
            "description": "Quantity ordered",
        },
        "order_date": {
            "data_type": "date",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 365,
            "sample_values": ["2025-01-01"],
            "description": "Date of order",
        },
    },
}

sample_groupby_fields = {"customers": ["customer_id"], "orders": ["customer_id"]}

sample_input_manual = JoinInput(
    operation=OperationEnum.manual_data_prep,
    tables=list(sample_col_metadata_manual.keys()),
    col_metadata=sample_col_metadata_manual,
    primary_table="customers",
    groupby_fields=sample_groupby_fields,
    use_case="customer_order_analysis",
    ml_approach="regression",
    domain_metadata={"domain": "ecommerce", "description": "Online retail data"},
)


@pytest.fixture
def agent():
    return JoinAgent()


def test_manual_data_prep_real(agent):
    # Run analyze_join_key without mocking
    output, cost = agent.analyze_join_key(sample_input_manual)
    
    # Assertions
    assert output is not None
    assert hasattr(output, "joins")
    assert hasattr(output, "unjoinable_tables")
    print("Manual data prep analysis completed. Output:")
    print(output.model_dump_json(indent=2))
