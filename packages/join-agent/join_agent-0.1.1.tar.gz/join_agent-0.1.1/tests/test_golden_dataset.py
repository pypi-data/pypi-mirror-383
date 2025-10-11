# tests/test_join_agent.py

import pytest
from join_agent.agent import JoinAgent
from join_agent.models import JoinInput, OperationEnum

# Sample input for golden_dataset operation with 5 tables
sample_col_metadata = {
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
    "products": {
        "product_id": {
            "data_type": "int",
            "row_count": 100,
            "null_count": 0,
            "unique_count": 100,
            "sample_values": [11, 12],
            "description": "Unique product identifier",
        },
        "name": {
            "data_type": "str",
            "row_count": 100,
            "null_count": 0,
            "unique_count": 100,
            "sample_values": ["Laptop"],
            "description": "Product name",
        },
        "category": {
            "data_type": "str",
            "row_count": 100,
            "null_count": 0,
            "unique_count": 10,
            "sample_values": ["Electronics"],
            "description": "Product category",
        },
        "price": {
            "data_type": "float",
            "row_count": 100,
            "null_count": 0,
            "unique_count": 95,
            "sample_values": [999.99],
            "description": "Product price",
        },
        "stock": {
            "data_type": "int",
            "row_count": 100,
            "null_count": 0,
            "unique_count": 50,
            "sample_values": [10, 20],
            "description": "Available stock",
        },
    },
    "payments": {
        "payment_id": {
            "data_type": "int",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 5000,
            "sample_values": [1001, 1002],
            "description": "Unique payment identifier",
        },
        "order_id": {
            "data_type": "int",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 5000,
            "sample_values": [101, 102],
            "description": "FK to orders table",
        },
        "amount": {
            "data_type": "float",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 2000,
            "sample_values": [100.5, 200.0],
            "description": "Payment amount",
        },
        "payment_date": {
            "data_type": "date",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 365,
            "sample_values": ["2025-01-01"],
            "description": "Date of payment",
        },
        "method": {
            "data_type": "str",
            "row_count": 5000,
            "null_count": 0,
            "unique_count": 5,
            "sample_values": ["Credit Card"],
            "description": "Payment method",
        },
    },
    "reviews": {
        "review_id": {
            "data_type": "int",
            "row_count": 2000,
            "null_count": 0,
            "unique_count": 2000,
            "sample_values": [1, 2],
            "description": "Unique review identifier",
        },
        "customer_id": {
            "data_type": "int",
            "row_count": 2000,
            "null_count": 0,
            "unique_count": 1000,
            "sample_values": [1, 2],
            "description": "FK to customers table",
        },
        "product_id": {
            "data_type": "int",
            "row_count": 2000,
            "null_count": 0,
            "unique_count": 100,
            "sample_values": [11, 12],
            "description": "FK to products table",
        },
        "rating": {
            "data_type": "int",
            "row_count": 2000,
            "null_count": 0,
            "unique_count": 5,
            "sample_values": [5, 4],
            "description": "Rating given by customer",
        },
        "review_date": {
            "data_type": "date",
            "row_count": 2000,
            "null_count": 0,
            "unique_count": 365,
            "sample_values": ["2025-01-01"],
            "description": "Date of review",
        },
    },
}

sample_input = JoinInput(
    operation=OperationEnum.golden_dataset,
    tables=list(sample_col_metadata.keys()),
    col_metadata=sample_col_metadata,
    primary_table=None,
    groupby_fields=None,
    use_case=None,
    ml_approach=None,
    domain_metadata=None,
)


@pytest.fixture
def agent():
    return JoinAgent()


def test_golden_dataset_real(agent):
    output, cost = agent(sample_input)
    
    # Assertions
    assert output is not None
    assert hasattr(output, "joins")
    assert hasattr(output, "unjoinable_tables")
    print("Golden dataset analysis completed. Output:")
    print(output.model_dump_json(indent=2))
