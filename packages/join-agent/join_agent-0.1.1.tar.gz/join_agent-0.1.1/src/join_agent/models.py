"""
Data models for Join Agent operations.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class Join(BaseModel):
    left_table: str
    right_table: str
    join_type: str
    join_fields: List[Tuple[str, str]] = Field(
        ..., description="Pairs of columns used as join keys"
    )


class JoinOutput(BaseModel):
    joins: List[Join]
    unjoinable_tables: List[str]


class OperationEnum(str, Enum):
    golden_dataset = "golden_dataset"
    manual_data_prep = "manual_data_prep"


class JoinInput(BaseModel):
    operation: OperationEnum
    tables: List[str]
    col_metadata: Dict[str, Dict[str, Dict[str, Any]]]
    primary_table: Optional[str] = None
    groupby_fields: Optional[Dict[str, List[str]]] = None
    use_case: Optional[str] = None
    ml_approach: Optional[str] = None
    domain_metadata: Optional[Dict[str, Any]] = None
