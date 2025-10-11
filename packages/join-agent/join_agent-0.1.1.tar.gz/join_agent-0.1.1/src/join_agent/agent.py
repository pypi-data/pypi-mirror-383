"""
Join Agent - LLM-driven intelligent data joining and relationship analysis.

This agent analyzes data tables and suggests optimal join strategies using LLM reasoning.
"""

import logging
import sys
from typing import Optional

from pydantic import ValidationError
from sfn_blueprint import SFNAIHandler

from .config import JoinAgentConfig
from .constants import PromptsClass
from .models import JoinInput, JoinOutput

DEFAULT_CONFIG = {
    "model": "gpt-4.1-mini",
    "temperature": 0.1,
    "max_retries": 3,
    "timeout": 300,
    "max_tokens": 4000,
}


class JoinAgent:
    """
    LLM-driven agent for intelligent data joining and relationship analysis.

    This agent uses LLM reasoning to identify potential join keys
    """

    def __init__(self, config: Optional[JoinAgentConfig] = None):
        """Initialize the Join Agent.
        Args:config: Optional FeatureCreationConfig instance. If not provided, a default will be used.
        """
        # Initialize configuration
        self.config = config or JoinAgentConfig()
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:  # Only add handlers if none exist
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize sfn_blueprint components
        self.ai_handler = SFNAIHandler()

        # Load configuration from sfn_blueprint config manager
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from sfn_blueprint config manager."""
        # Ensure logger is properly initialized
        if not hasattr(self, "logger") or not isinstance(self.logger, logging.Logger):
            self.logger = logging.getLogger(__name__)

        # Set default config
        self.llm_config = DEFAULT_CONFIG.copy()

        self.logger.info("Join Agent initialized successfully")

    def __call__(self, inputs: JoinInput):
        return self.analyze_join_key(inputs)

    def analyze_join_key(self, inputs: JoinInput):
        """operation : enum["golden_dataset","manual_data_prep"]"""
        operation = inputs.operation
        table_names = inputs.tables
        col_metadata = inputs.col_metadata
        primary_table = inputs.primary_table
        groupby_fields = inputs.groupby_fields
        use_case = inputs.use_case
        ml_approach = inputs.ml_approach
        domain_metadata = inputs.domain_metadata

        if operation not in {"golden_dataset", "manual_data_prep"}:
            raise ValueError("operation must be 'golden_dataset' or 'manual_data_prep'")

        # if operation == "manual_data_prep" and not primary_table:
        #     raise ValueError("primary_table is required when operation = 'manual_data_prep'")

        if operation == "manual_data_prep" and len(table_names) > 2:
            raise ValueError(
                "Only two tables can be analyzed when operation = 'manual_data_prep'"
            )

        self.logger.info(f"Analyzing join keys between :{', '.join(table_names)}")

        # Generate LLM prompt for join analysis
        system_prompt, user_prompt = PromptsClass().operation_prompt(
            operation,
            table_names,
            col_metadata,
            primary_table,
            groupby_fields,
            use_case,
            ml_approach,
            domain_metadata,
        )

        # print("system prompt",system_prompt,"user prompt",user_prompt)
        # Call LLM for join suggestions
        response, cost = self.call_llm(system_prompt, user_prompt)
        # Get LLM response
        # print(f"llm response {response}")
        print(f"llm cost: {cost}")

        # Parse LLM response
        parsed_output = self._parse_llm_output(response)
        # print(f"parsed output {parsed_output}")

        return parsed_output, cost

    def call_llm(self, system_prompt, user_prompt):
        try:
            response, cost = self.ai_handler.route_to(
                llm_provider=self.config.ai_provider,
                configuration={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "model": self.config.model_name,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "api_key": self.config.api_key,
                },
                model=self.llm_config["model"],
            )

            return response, cost

        except Exception as e:
            self.logger.error(f"Error in response: {str(e)}")
            return {
                "status": "response error",
                "message": f"Error in producing LLM response: {str(e)}",
            }

    def _parse_llm_output(self, llm_response):
        # Parse LLM response
        try:
            parsed_output = JoinOutput.model_validate_json(llm_response)
            return parsed_output
        except ValidationError as e:
            print("Parsing failed with validation error:")
            print(e.json(indent=2))
            self.logger.error(f"Parsing failed with validation error: {e}")

    # def validate_joins(
    #     self, join_plan: Dict[str, Any], tables, confidence_threshold: float = 0.6
    # ) -> Dict[str, Any]:
    #     """
    #     Validate a structured join plan with multiple joins and optional unjoinable tables.
    #     Returns updated plan with statuses for each join.
    #     """
    #     table_dict = dict(tables)
    #     valid_joins = []

    #     table_dict = dict(tables)
    #     # valid_joins = []

    #     # Extract joins and unjoinable tables from dict or object
    #     join_suggestions = getattr(join_plan, "joins", [])
    #     unjoinable_tables = set(getattr(join_plan, "unjoinable_tables", []))
    #     validated_joins = []

    #     for join in join_suggestions:
    #         # Read join properties safely
    #         left_table = getattr(join, "left_table", None)
    #         right_table = getattr(join, "right_table", None)
    #         join_fields = getattr(join, "join_fields", None)
    #         reason = getattr(join, "reason", None)
    #         confidence_score = getattr(join, "confidence_score", 0)

    #         if confidence_score < confidence_threshold:
    #             status = "invalid_low_confidence"
    #             overlap_percent = 0.0
    #         elif left_table in unjoinable_tables or right_table in unjoinable_tables:
    #             status = "invalid_unjoinable"
    #             overlap_percent = 0.0
    #         elif left_table not in table_dict or right_table not in table_dict:
    #             status = "invalid_missing_table"
    #             overlap_percent = 0.0
    #         else:
    #             df_left, df_right = table_dict[left_table], table_dict[right_table]

    #             if not self._validate_schema(df_left, df_right, join_fields):
    #                 status = "invalid_schema"
    #                 overlap_percent = 0.0
    #             else:
    #                 overlap_percent = self._validate_data(
    #                     df_left, df_right, join_fields
    #                 )
    #                 status = "valid"

    #         validated_join = JoinStrategy(
    #             table1_name=left_table,
    #             table2_name=right_table,
    #             join_keys=join_fields,
    #             suggested_join_type=JoinType.INNER,  # or whatever type
    #             confidence_score=confidence_score,
    #             reasoning=reason,
    #             overlap_percent=overlap_percent,
    #             status=status,
    #             # newly added
    #         )

    #         validated_joins.append(validated_join)

    #     return validated_joins

    # def _validate_schema(
    #     self,
    #     df_left: pd.DataFrame,
    #     df_right: pd.DataFrame,
    #     join_fields: List[List[str]],
    # ) -> bool:
    #     """Check if columns exist and datatypes are compatible."""
    #     for left_col, right_col in join_fields:
    #         if left_col not in df_left.columns or right_col not in df_right.columns:
    #             return False
    #         if df_left[left_col].dtype != df_right[right_col].dtype:
    #             return False
    #     return True

    # def _validate_data(
    #     self,
    #     df_left: pd.DataFrame,
    #     df_right: pd.DataFrame,
    #     join_fields: List[List[str]],
    # ) -> bool:
    #     """Check overlap of join keys and return overlap percentage (0-100)."""
    #     left_keys = df_left[[lf for lf, _ in join_fields]].dropna()
    #     right_keys = df_right[[rf for _, rf in join_fields]].dropna()

    #     if left_keys.empty or right_keys.empty:
    #         return 0.0

    #     # Perform inner join to find matching rows
    #     merged = pd.merge(
    #         left_keys,
    #         right_keys,
    #         left_on=[lf for lf, _ in join_fields],
    #         right_on=[rf for _, rf in join_fields],
    #         how="inner",
    #     )

    #     if merged.empty:
    #         return 0.0

    #     # Overlap percentage relative to the smaller table
    #     overlap_count = len(merged)
    #     min_rows = min(len(left_keys), len(right_keys))
    #     overlap_pct = (overlap_count / min_rows) * 100

    #     return overlap_pct

    # def _analyze_table_structure(
    #     self, df: pd.DataFrame, table_name: str
    # ) -> Dict[str, Any]:
    #     # Analyze table structure for join analysis.
    #     analysis = {
    #         "table_name": table_name,
    #         "columns": list(df.columns),
    #         "data_types": df.dtypes.to_dict(),
    #         "row_count": len(df),
    #         "null_counts": df.isnull().sum().to_dict(),
    #         "unique_counts": df.nunique().to_dict(),
    #         "sample_values": {},
    #     }

    #     # Get sample values for each column (for LLM analysis)
    #     for col in df.columns:
    #         sample_values = df[col].dropna().head(5).tolist()
    #         analysis["sample_values"][col] = sample_values

    #     return analysis
