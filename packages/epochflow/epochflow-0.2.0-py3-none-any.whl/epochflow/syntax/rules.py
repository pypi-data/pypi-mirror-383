"""
EpochFlow Syntax Rules

This module now imports rules from the EpochAI parent project.
Rules have been moved to EpochAI/common/dsl_rules for better separation of concerns.
"""

try:
    # Import from EpochAI if available
    from common.dsl_rules import (
        ANTI_OVERENGINEERING_RULES,
        COMPONENT_DISCOVERY_RULES,
        COMPOSITIONAL_LOGIC_RULES,
        DSL_SYNTAX_RULES,
        EXECUTION_COMPONENTS_RULES,
        MISSING_COMPONENT_HANDLING,
        QUANT_RESEARCHER_RULE,
        REPORT_COMPONENTS_RULES,
        SESSION_RULES,
        STRATEGY_BUILDER_RULE,
        STRATEGY_EXIT_PATTERNS,
        TIMEFRAME_RULES,
        TRANSFORM_COMPONENTS_RULES,
    )
except ImportError:
    # Fallback for when epochflow is used standalone
    # In this case, rules should be provided externally
    ANTI_OVERENGINEERING_RULES = "# Rules not available - please install from EpochAI context"
    COMPONENT_DISCOVERY_RULES = "# Rules not available - please install from EpochAI context"
    COMPOSITIONAL_LOGIC_RULES = "# Rules not available - please install from EpochAI context"
    DSL_SYNTAX_RULES = "# Rules not available - please install from EpochAI context"
    EXECUTION_COMPONENTS_RULES = "# Rules not available - please install from EpochAI context"
    MISSING_COMPONENT_HANDLING = "# Rules not available - please install from EpochAI context"
    QUANT_RESEARCHER_RULE = "# Rules not available - please install from EpochAI context"
    REPORT_COMPONENTS_RULES = "# Rules not available - please install from EpochAI context"
    SESSION_RULES = "# Rules not available - please install from EpochAI context"
    STRATEGY_BUILDER_RULE = "# Rules not available - please install from EpochAI context"
    STRATEGY_EXIT_PATTERNS = "# Rules not available - please install from EpochAI context"
    TIMEFRAME_RULES = "# Rules not available - please install from EpochAI context"
    TRANSFORM_COMPONENTS_RULES = "# Rules not available - please install from EpochAI context"

__all__ = [
    "ANTI_OVERENGINEERING_RULES",
    "COMPONENT_DISCOVERY_RULES",
    "COMPOSITIONAL_LOGIC_RULES",
    "DSL_SYNTAX_RULES",
    "EXECUTION_COMPONENTS_RULES",
    "MISSING_COMPONENT_HANDLING",
    "QUANT_RESEARCHER_RULE",
    "REPORT_COMPONENTS_RULES",
    "SESSION_RULES",
    "STRATEGY_BUILDER_RULE",
    "STRATEGY_EXIT_PATTERNS",
    "TIMEFRAME_RULES",
    "TRANSFORM_COMPONENTS_RULES",
]