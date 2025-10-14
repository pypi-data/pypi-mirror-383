from collections import defaultdict
import json

# ===========================================================================================
# COMPONENT DIRECTORY BUILDER
# ===========================================================================================

def _build_component_directory(exclude_reporters: bool = False, exclude_executors: bool = False) -> str:
    """Build a categorized directory of all available components.

    Args:
        exclude_reporters: If True, filter out components with isReporter=True
        exclude_executors: If True, filter out trade_signal_executor

    Returns:
        Formatted string with components organized by category
    """
    try:
        from epochflow.registry import get_transforms_list
        TRANSFORMS_LIST = get_transforms_list()
    except ImportError:
        return "# Component directory unavailable - import failed"

    if not TRANSFORMS_LIST:
        return "# Component directory unavailable - no transforms loaded"

    # Operators that are handled automatically by the compiler
    OPERATOR_COMPONENTS = {
        'add', 'sub', 'mul', 'div', 'lt', 'gt', 'lte', 'gte', 'eq', 'neq',
        'logical_and', 'logical_or', 'logical_not', 'abs'
    }

    by_category = defaultdict(list)

    for t in TRANSFORMS_LIST:
        component_id = t.get('id', '')

        # Skip operators
        if component_id in OPERATOR_COMPONENTS:
            continue

        # Skip reporters if requested
        if exclude_reporters and t.get('isReporter', False):
            continue

        # Skip trade_signal_executor if requested
        if exclude_executors and component_id == 'trade_signal_executor':
            continue

        category = t.get('category', 'Other')
        by_category[category].append(component_id)

    # Format the directory
    lines = ["# AVAILABLE COMPONENTS BY CATEGORY", ""]
    lines.append("**Use get_multi_component_details() to get exact parameters for any component.**")
    lines.append("**NEVER assume a component has the same options as another - always check!**")
    lines.append("")

    for category in sorted(by_category.keys()):
        ids = sorted(by_category[category])
        lines.append(f"## {category} ({len(ids)} components)")

        # Format as comma-separated list, wrapped at reasonable width
        line = ""
        for component_id in ids:
            if len(line) + len(component_id) + 2 > 80:
                lines.append(line.rstrip(', '))
                line = ""
            line += f"{component_id}, "
        if line:
            lines.append(line.rstrip(', '))
        lines.append("")

    return "\n".join(lines)


def _build_reporter_components_details() -> str:
    """Build detailed documentation for all reporter components.

    Returns:
        Raw JSON for all components where isReporter == True
    """
    try:
        from epochflow.registry import get_transforms_list
        TRANSFORMS_LIST = get_transforms_list()
    except ImportError:
        return "# Reporter components unavailable - import failed"

    if not TRANSFORMS_LIST:
        return "# Reporter components unavailable - no transforms loaded"

    # Find all reporter components using the isReporter flag
    reporters = [
        t for t in TRANSFORMS_LIST
        if t.get('isReporter', False) is True
    ]

    if not reporters:
        return "# No reporter components found"

    lines = ["# REPORTER COMPONENTS - FULL DETAILS", ""]
    lines.append(f"Total reporters available: {len(reporters)}")
    lines.append("")
    lines.append("These are terminal nodes for dashboard visualization. They consume data but produce NO outputs.")
    lines.append("Use these components to build focused research dashboards that answer specific questions.")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(reporters, indent=2))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def _build_datasource_components_details() -> str:
    """Build detailed documentation for all DataSource components.

    Returns:
        Raw JSON for all components where category == 'DataSource'
    """
    try:
        from epochflow.registry import get_transforms_list
        TRANSFORMS_LIST = get_transforms_list()
    except ImportError:
        return "# DataSource components unavailable - import failed"

    if not TRANSFORMS_LIST:
        return "# DataSource components unavailable - no transforms loaded"

    # Find all DataSource components
    datasources = [
        t for t in TRANSFORMS_LIST
        if t.get('category') == 'DataSource'
    ]

    if not datasources:
        return "# No DataSource components found"

    lines = ["# DATA SOURCE COMPONENTS - FULL DETAILS", ""]
    lines.append(f"Total data sources available: {len(datasources)}")
    lines.append("")
    lines.append("Data sources provide market data (OHLCV) to your algorithm.")
    lines.append("Typically you only need ONE market_data_source per algorithm.")
    lines.append("")
    lines.append("**Special Parameters** (not in options list):")
    lines.append("  - `timeframe` (String) [○ Optional]: Pandas offset like '1D', '1H', '5Min', '1W'")
    lines.append("  - `session` (String) [○ Optional]: Sydney, Tokyo, London, NewYork, AsianKillZone, etc.")
    lines.append("")
    lines.append("**Usage Example**:")
    lines.append("```python")
    lines.append("src = market_data_source()  # Basic")
    lines.append('src = market_data_source(timeframe="1H")  # With timeframe')
    lines.append('src = market_data_source(timeframe="15Min", session="NewYork")  # With both')
    lines.append("close_price = src.c  # Access OHLCV via .o .h .l .c .v")
    lines.append("```")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(datasources, indent=2))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def _build_trade_signal_executor_details() -> str:
    """Build detailed documentation for trade_signal_executor component.

    Returns:
        Raw JSON for trade_signal_executor
    """
    try:
        from epochflow.registry import get_transforms_list
        TRANSFORMS_LIST = get_transforms_list()
    except ImportError:
        return "# trade_signal_executor details unavailable - import failed"

    if not TRANSFORMS_LIST:
        return "# trade_signal_executor details unavailable - no transforms loaded"

    # Build transforms dict from list
    TRANSFORMS_DICT = {t.get("id"): t for t in TRANSFORMS_LIST if t.get("id")}

    executor = TRANSFORMS_DICT.get('trade_signal_executor')
    if not executor:
        return "# trade_signal_executor not found in transforms"

    lines = ["# TRADE SIGNAL EXECUTOR - FULL DETAILS", ""]
    lines.append("**REQUIRED** for all trading strategies. This is a terminal node that executes trade signals.")
    lines.append("")
    lines.append("All inputs are **optional** - only specify the signals you need.")
    lines.append("")
    lines.append("**Usage Example**:")
    lines.append("```python")
    lines.append("trade_signal_executor()(")
    lines.append("    enter_long=long_entry_condition,")
    lines.append("    exit_long=long_exit_condition,")
    lines.append("    enter_short=short_entry_condition,")
    lines.append("    exit_short=short_exit_condition")
    lines.append(")")
    lines.append("```")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(executor, indent=2))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ===========================================================================================
# SHARED DSL RULES - USED BY BOTH STRATEGY_BUILDER AND QUANT_RESEARCHER
# ===========================================================================================

# Core DSL syntax rules that apply to both delegate
DSL_SYNTAX_RULES = """
# DSL SYNTAX FUNDAMENTALS

## 0. Single-Asset Constraint

⚠️ **CRITICAL LIMITATION**: Each algorithm operates on **ONE asset only**.

**NOT SUPPORTED**: Cross-asset analysis in a single algorithm
```python
# ❌ WRONG - Multiple assets in same algorithm
vix_data = market_data_source(asset="VIX")
spx_data = market_data_source(asset="SPX")
condition = vix_data.c > vix_data.c[1] and spx_data.c > spx_data.c[1]  # REJECTED
```

**SUPPORTED**: Single asset per algorithm
```python
# ✅ CORRECT - One asset
src = market_data_source()  # Asset specified at execution time
rsi_val = rsi(period=14)(src.c)
```

**Alternative for multi-asset comparisons**:
- Run separate analyses on each asset
- Compare results after execution
- This is a **per-execution limitation**, not a platform limitation

## 1. Component Instantiation Pattern
```python
# Standard: component with parameters, then inputs
result = component_name(param1=value1)(input_data)

# NO PARAMETERS: Can omit empty ()
abs_val = abs(src.c)  # Instead of abs()(src.c)

# NO INPUTS: Some components take no inputs
adx_val = adx(period=14)()  # Note: empty () for no inputs
vwap_val = vwap()()  # Both parentheses needed when no params AND no inputs
```

**Rules:**
- Zero parameters → shorthand: `abs(input)` instead of `abs()(input)`
- Zero inputs → empty call: `adx(period=14)()` or `vwap()()`
- Use get_multi_component_details() to check if component needs inputs

## 2. Data Access (Dot Notation)
```python
src.c  # close price
src.o  # open price
src.h  # high price
src.l  # low price
src.v  # volume
```

## 3. Output Handle Access

**Components fall into two categories:**

### A. Components WITH Outputs (Transforms)
These produce data you can use in expressions via output handles.

**Single-output components** (most common):
```python
# EXPLICIT: Use the output handle name
ema20 = ema(period=20)(src.c)
condition = ema20.result > 100  # Explicitly access .result

# INFERRED: Single-output handle is automatic (preferred for cleaner code)
ema20 = ema(period=20)(src.c)
condition = ema20 > 100  # .result inferred automatically

# Both explicit and inferred work
rsi_val = rsi(period=14)(src.c)
buy_signal = rsi_val < 30  # Inferred
sell_signal = rsi_val.result > 70  # Explicit also works
```

**Rule**: For components with exactly ONE output, the handle is inferred when omitted.
- `component_var > 100` ≡ `component_var.result > 100` (if only 1 output)
- Explicit access still works: `component_var.result`
- Choose based on code clarity preference

**Multi-output components via tuple unpacking:**
```python
# Bollinger Bands returns 3 outputs
upper, middle, lower = bbands(period=20, stddev=2)(src.c)
# Each unpacked variable is bound to its output handle
buy_signal = src.c < lower  # Use directly, no .result needed

# SQL query with multiple outputs
out0, out1 = sql_query_2(sql="...")(data)
# Variables are already bound to their respective output handles
condition = out0 > 100  # Use directly
```

**Multi-output components with named handles (MUST use explicit handles):**
```python
# Component with multiple outputs - CANNOT infer, MUST use explicit handle
london = sessions(session_type="London")
is_active = london.active  # MUST use .active handle
session_high = london.high  # MUST use .high handle

# london > 100  # ❌ ERROR: Ambiguous - which of the 5 outputs?
```

**Rule**: Multi-output components require explicit handle names - inference only works for single-output components.
- Discovery: Use search_components() and get_multi_component_details() to find output handle names
- Examples: sessions (5 outputs), hmm (3 outputs), fair_value_gap (4 outputs), bbands (3 outputs)

**Summary of Handle Access Rules:**
1. **Single output** → Handle inferred: `ema20 > 100` ✓
2. **Multiple outputs via tuple unpacking** → Use variables directly: `upper, middle, lower = bbands(...); buy = src.c < lower` ✓
3. **Multiple outputs NOT unpacked** → MUST use explicit handle: `london.active` ✓
4. **Finding handle names** → Use search_components() and get_multi_component_details()

### B. Terminal Nodes (No Outputs)
Some components are **terminal/sink nodes** that consume data but produce no outputs.
They cannot be used in expressions.

**Key distinction:**
- **Transforms**: Have outputs → can use in expressions → `ema20 > 100`
- **Terminal nodes**: NO outputs → cannot use in expressions

**Operator results don't need handles:**
```python
is_higher = src.c > 100  # Comparison returns boolean directly
spread = src.h - src.l   # Arithmetic returns number directly
combined = cond1 and cond2  # Logical returns boolean directly
```

## 4. Lag Operator [n] - Historical Values
```python
src.c[1]  # Previous close (1 period ago)
src.c[2]  # Close 2 periods ago
ema20.result[3]  # EMA value 3 periods ago

# Examples:
momentum = src.c > src.c[1]  # Current > previous
gap_up = src.o > src.c[1]  # Today's open > yesterday's close
three_up = (src.c > src.c[1]) and (src.c[1] > src.c[2])
```

## 5. Lookahead Bias and When to Use Lag

**CRITICAL**: Rolling window indicators (moving averages, `max()`, `min()`, `donchian_channel()`, `bbands()`) include the current bar in their calculation. When comparing current price to these indicators, you MUST use `[1]` lag.

### The Rule

**When comparing current price to rolling window indicators → Use `[1]` lag**

```python
# ❌ WRONG - Lookahead bias
dc = donchian_channel(window=20, timeframe="1D")()
enter_long = src.h > dc.bbands_upper  # Includes current bar

# ✅ CORRECT - Classic Donchian/Turtle breakout
enter_long = src.h > dc.bbands_upper[1]  # Current high breaks previous 20-bar high
exit_long = src.c < dc.bbands_lower[1]   # Close below previous 20-bar low
```

**Why:** Rolling window `max()/min()` includes current bar [t-19...t]. Using `[1]` compares current price to the previous completed window [t-20...t-1], which is the classical breakout definition.

**Critical for Donchian:** Since `bbands_upper` = highest **high** and `bbands_lower` = lowest **low**, use `src.h` for entry (high-based breakout) and `src.c` or `src.l` for exit.

### When Lag is NOT Needed

```python
# ✅ Indicator-to-indicator comparisons
sma_fast = sma(period=10)(src.c)
sma_slow = sma(period=20)(src.c)
cross = sma_fast > sma_slow  # No lag needed

# ✅ Historical price comparisons
momentum = src.c > src.c[1]  # Already lagged
```

**Decision tree:**
- Comparing current price to rolling window indicator? → Use `[1]`
- Comparing two indicators to each other? → No lag needed
- Using historical prices (`src.c[1]`, `src.h[5]`)? → No lag needed

## 6. Literals and Constants
**Numeric Literals:**
```python
threshold = 100  # Numbers used directly
ratio = 0.02
multiplier = -1.5
```

**Boolean Literals:**
```python
always_true = True
always_false = False
is_valid = True  # Boolean constant
```

**Bare Identifiers as Strings:**
```python
# For session parameters, can omit quotes
london = sessions(session_type=London)  # Same as "London"
src = market_data_source(timeframe="1H", session=NewYork)
```

## 6. Supported Python Features
**Operators:**
- Arithmetic: `+`, `-`, `*`, `/`, `-x` (negation)
- Comparison: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Logical: `and`, `or`, `not`
- Conditional: `true_value if condition else false_value` (ternary expression)

**Note:** Tuple unpacking for multi-output components is covered in Section 3 (Output Handle Access).

## 7. Automatic Type Casting
The compiler automatically handles type conversions:
```python
# Boolean to Number (0 or 1)
is_up = src.c > src.o  # Boolean
multiplier = is_up * 2  # Auto-cast to 0 or 1, then multiply

# Number to Boolean (0 = False, non-zero = True)
volume = src.v
has_volume = volume and condition  # volume cast to boolean
```

## 8 Report Example
gaps = gap_classify(
    fill_percent=100,
    timeframe="1Min",
    session="NewYork"
)()

# Generate comprehensive gap report
# Setting fill_time_pivot_hour=12 to analyze fills before/after noon
gap_report(
    fill_time_pivot_hour=12,
    histogram_bins=15
)(gaps.gap_filled, gaps.gap_retrace, gaps.gap_size, gaps.psc, gaps.psc_timestamp)

"""

MISSING_COMPONENT_HANDLING = """
# HANDLING MISSING COMPONENTS

## Critical Rule: Never Approximate Without Approval

**IF YOU CANNOT IMPLEMENT THE USER'S EXACT REQUEST:**
1. **Stop immediately** - Do not generate approximated/modified code
2. **Return to orchestrator** explaining what's missing/unsupported
3. **Let the orchestrator ask_approval()** with options:
   - Option A: Build approximation (explain limitations)
   - Option B: Remove unsupported feature
   - Option C: Report as feature request
   - Option D: Suggest alternative approach

**NEVER make these decisions yourself:**
- ❌ "I'll approximate this with X" → ASK FIRST
- ❌ "I'll skip this feature" → ASK FIRST
- ❌ "This is close enough" → ASK FIRST
- ✅ "Cannot implement exact request - return to orchestrator for approval"

## When Components Don't Exist

If a required transform/component does not exist in the catalog:
1. **Stop immediately** - Do not attempt to generate code
2. **Return to the orchestrator** with a clear message
3. **Provide implementation details** to help the backend team:
   - Algorithm or calculation method
   - GitHub implementations (TA-Lib, pandas-ta, technical libraries)
   - Research papers or academic references
   - Books or authoritative sources
   - Similar existing transforms that could be adapted

## When Requirements Are Ambiguous or Unsupported

If a user requirement CANNOT be implemented exactly (even with available components):
1. **Stop immediately** - Do not generate flawed approximations
2. **Return to orchestrator** with explanation of the issue
3. **Explain why exact implementation isn't possible**
4. **Suggest concrete alternatives** for the orchestrator to present

Example: User requests "hold for 2 days after entering"
- Issue: Requires position state tracking (not signal tracking)
- Available: Only lag operators (track signals, not positions)
- Return: "Cannot implement exact request. Lag operators track signal history, not position state. Need bars_in_position component. Alternatives: (A) Remove time exit, (B) Report feature request, (C) Use signal-based approximation with known limitations."

## Implementation Details Template

**BE CONCISE** - Provide only essential information:

**Algorithm:** [Brief formula or key steps only]
**Outputs:** [List expected output handles]
**References:** [URLs to GitHub, libraries, books - links only]
**Alternative:** [Existing transforms that could approximate, if any]

## Example Response

User requests: "Screen for bull flag patterns"
Missing: `bull_flag_pattern` transform

Return message:
"Cannot complete - `bull_flag_pattern` transform doesn't exist.

**Implementation Details:**

Algorithm: Detect uptrend pole (20-40% gain) → consolidation flag (range < 40% of pole, declining volume) → quality score (0-100)

Outputs: pattern_quality, pattern_high, pattern_low, pole_high

References:
- https://github.com/cinar/indicator
- https://github.com/bukosabino/ta
- Thomas Bulkowski - Encyclopedia of Chart Patterns

Alternative: Build from roc() + max()/min() + volume sma()

Would you like me to build an approximation?"
"""

COMPONENT_DISCOVERY_RULES = """
# COMPONENT USAGE RULES

## Critical Rules - READ CAREFULLY
- Component names MUST match exactly (case-sensitive)
- Parameters MUST match exactly ('period' not 'lookback', 'timeframe' not 'tf')
- **ALWAYS specify ALL parameters**, even if `isRequired: false`
  - `isRequired` is a FRONTEND/UI flag indicating if the UI requires user input
  - Backend validation expects ALL parameters to be explicitly specified
  - Missing parameters cause validation errors even if marked isRequired=false
- **NEVER assume parameter names or values** - Similar components have DIFFERENT parameters
  - Example: lines_chart_report uses different options than bar_chart_report
  - Example: ema(period=20) and sma(period=20) - always check component details for parameter names!
  - Example: rsi(period=14) not rsi(length=14) - check component details!
- Each component has its own specific inputs, outputs, and options
- See COMPONENT DIRECTORY below for all available components organized by category

## Mandatory Component Discovery Workflow
Before generating ANY code, you MUST:
1. Identify ONLY components needed to answer user's question directly
   - Don't fetch components for "nice to have" analysis
   - Start minimal - fetch only what's explicitly requested
2. Call get_multi_component_details() or get_transform_details() for those components
3. Review returned JSON carefully for:
   - Exact parameter names
   - Parameter types (number, string, boolean, etc.)
   - All available parameters (include all, not just isRequired=true)
   - Input requirements
   - Output handles

**Never guess or assume** - Always load component details first. Parameter names and options are NOT standardized across components.

## Example: WRONG vs RIGHT
❌ WRONG (assuming from examples):
```python
rsi = rsi(length=14)(src.c)  # ERROR: rsi uses 'period', not 'length'
```

✅ RIGHT (loaded from get_multi_component_details):
```python
# First: get_multi_component_details(["rsi"])
# Returns: {"id": "rsi", "options": [{"name": "period", "type": "number", ...}]}
rsi = rsi(period=14)(src.c)  # Correct parameter name
```
"""

TIMEFRAME_RULES = """
# TIMEFRAME RULES
1. **Must be string literals**: `"1D"`, `"1H"`, `"5Min"`
2. **Format exactly**: `"1D"` not `"1 day"` or `"1d"`
3. **Common timeframes**: "1Min", "5Min", "15Min", "30Min", "1H", "4H", "1D", "1W", "1ME"
4. **CRITICAL**: All components in an algorithm should use consistent timeframes
5. **INTRADAY_ONLY components**: Must use intraday timeframes (1Min through 12H)

"""

SESSION_RULES = """
# SESSION HANDLING

Sessions can be specified in three ways:

## 1. Session Parameter in Components
```python
component_id = component_name(session="London")(input)
```

## 2. Session Node (Multiple Outputs)
```python
london = sessions(session_type="London")
# Outputs: .active, .high, .low, .opened, .closed
condition = london.active  # Use explicit output handles
```

## 3. Market Data Source Filter
```python
src = market_data_source(timeframe="1H", session="London")
# Filters all OHLCV data to session hours
```

**Available Sessions**: Sydney, Tokyo, London, NewYork, AsianKillZone, LondonOpenKillZone, NewYorkKillZone, LondonCloseKillZone
"""

# ===========================================================================================
# COMPONENT-SPECIFIC RULES
# ===========================================================================================

TRANSFORM_COMPONENTS_RULES = """
# TRANSFORM COMPONENTS

Transforms process data and produce outputs for use in expressions.
See COMPONENT DIRECTORY for all available transforms organized by category.

## Self-Contained Data Source Components

**CRITICAL RULE**: Components with `requiredDataSources` (e.g., `["o", "h", "l", "c"]`) ARE data sources themselves.

**When a component has non-empty `requiredDataSources`:**
1. ✅ DO NOT create or connect `market_data_source()` - it accesses OHLC data directly
2. ✅ DO add `timeframe` and `session` parameters directly to the component
3. ✅ Call with no inputs: `component(params)()`

```python
# ❌ WRONG - unnecessary market_data_source
src = market_data_source(timeframe="1H", session="NewYork")
gaps = gap_classify(fill_percent=100)(src)  # gap_classify doesn't need inputs!

# ✅ CORRECT - gap_classify has requiredDataSources, so it's self-contained
gaps = gap_classify(fill_percent=100, timeframe="1H", session="NewYork")()

# Another example: sessions component
# ❌ WRONG
src = market_data_source(timeframe="1H")
london = sessions(session_type="London")(src)

# ✅ CORRECT
london = sessions(session_type="London", timeframe="1H")()
```

**How to identify**: Use `get_transform_details()` and check for `requiredDataSources` field.

## SQL Query Components (sql_query_1 through sql_query_4)

**CRITICAL: sql_query components use different table name than table_report**
- `sql_query_*` transforms: Use `FROM input`
- `table_report` reporter: Use `FROM table` (see REPORT COMPONENTS section)

**Critical SQL Syntax Rules for sql_query_1/2/3/4:**
- Multi-output: MUST alias columns as `output0`, `output1`, `output2`, `output3` exactly
- MUST include `timestamp` column in SELECT for timeseries continuity
- Input DataFrame is referenced as `input` table (NOT `table`)
- Column names with `#` become `_` (e.g., `market_data#c` → `market_data_c`)

```python
# Multi-output example
out0, out1 = sql_query_2(
    sql="SELECT close AS output0, volume AS output1, timestamp FROM input"
)(src.c)
```
"""

ANTI_OVERENGINEERING_RULES = """
# ANTI-OVER-ENGINEERING PRINCIPLES

## Core Philosophy: Answer ONLY What's Asked

**Start Minimal, Expand Only If Requested**

1. **One Question = One Metric (Default)**
   - User asks "What's the RSI?" → Show ONLY current RSI value (1 card)
   - User asks "How often is RSI overbought?" → Show ONLY overbought count (1 card)
   - User asks "Analyze RSI" → Show 2-3 key metrics max (current value, overbought count, oversold count)

2. **Default to Single Group**
   - Most analyses need ONLY 1 group
   - Use multiple groups ONLY when user explicitly asks for comparison or contrasting themes
   - Example: "Compare overbought vs oversold" → 2 groups
   - Example: "Show gap fill rate" → 1 group (no comparison needed)

3. **Avoid SQL Unless Necessary**
   - Use component outputs directly when possible
   - SQL is for complex aggregations NOT available via components
   - ❌ Don't: sql_query to extract/filter a single value from component output
   - ✅ Do: Use component output handle directly (e.g., `gaps.gap_filled`)

4. **No Intermediate Calculations Unless Required for Display**
   - Don't calculate metrics user didn't ask for
   - Don't create "supporting" variables "for context"
   - Only calculate what will be directly displayed or reported

## Examples: Minimal vs Over-Engineered

**User Query: "What's the gap fill rate for EUR/USD?"**

❌ OVER-ENGINEERED (Bad - Don't do this):
```python
# Calculating things gap_report already provides
gaps = gap_classify(fill_percent=100, timeframe="1Min", session="NewYork")()
sql_total = sql_query_1(sql="SELECT COUNT(*) FROM input WHERE input0 IS NOT NULL ...")(gaps.gap_size)
sql_filled = sql_query_1(sql="SELECT SUM(CASE WHEN input0=true THEN 1 ...")(gaps.gap_filled)
sql_percent = sql_query_1(sql="SELECT (input0/input1*100) ...")(sql_filled.output0, sql_total.output0)

numeric_cards_report(title="Fill Rate %", group=0, group_size=3)(sql_percent.output0)
numeric_cards_report(title="Total Gaps", group=0, group_size=3)(sql_total.output0)
numeric_cards_report(title="Filled Count", group=0, group_size=3)(sql_filled.output0)
# Extra cards user didn't ask for:
numeric_cards_report(title="Avg Gap Size", group=1, group_size=3)(gaps.gap_size)
numeric_cards_report(title="Retrace %", group=1, group_size=3)(gaps.gap_retrace)
```

✅ MINIMAL (Good - Do this):
```python
# gap_report already shows everything including fill rate
gaps = gap_classify(fill_percent=100, timeframe="1Min", session="NewYork")()
gap_report(fill_time_pivot_hour=12, histogram_bins=15)(
    gaps.gap_filled, gaps.gap_retrace, gaps.gap_size, gaps.psc, gaps.psc_timestamp
)
```

**User Query: "Show me RSI overbought conditions for SPX"**

❌ OVER-ENGINEERED:
```python
src = market_data_source(timeframe="1D")
rsi_val = rsi(period=14)(src.c)
overbought = rsi_val > 70
oversold = rsi_val < 30  # ❌ User didn't ask for oversold!
ob_count = count(lookback=252)(overbought)
os_count = count(lookback=252)(oversold)  # ❌ User didn't ask for this!
ob_duration = avg_consecutive_true()(overbought)  # ❌ User didn't ask for duration!
current_rsi = rsi_val  # ❌ User didn't ask for current value!

# Then 6 cards in 2 groups...
```

✅ MINIMAL:
```python
src = market_data_source(timeframe="1D")
rsi_val = rsi(period=14)(src.c)
overbought = rsi_val > 70
ob_count = count(lookback=252)(overbought)

numeric_cards_report(
    title="Overbought Days",
    category="RSI",
    group=0,
    group_size=1  # Just 1 group!
)(ob_count)
```

## Decision Framework

Before writing code, ask yourself:

1. **Did the user explicitly ask for this metric?**
   - Yes → Include it
   - No → Remove it

2. **Is this comparison user requested?**
   - Yes → Create separate group
   - No → Use single group

3. **Can I use a specialized report instead?**
   - Yes → Use ONLY specialized report
   - No → Build minimal custom dashboard

4. **Is this SQL query necessary?**
   - Can I use component output directly? → Yes, use component output
   - Do I need complex aggregation not available? → Yes, use SQL
   - Am I just extracting/filtering a value? → No SQL needed

**When in doubt, build less. Users can always ask for more.**
"""

REPORT_COMPONENTS_RULES = """
# REPORT COMPONENTS

## CRITICAL: table_report SQL Syntax (DIFFERENT from sql_query)

**WARNING: table_report uses DIFFERENT table name than sql_query components**

```python
# ✅ CORRECT: table_report uses FROM table
table_report(
    sql="SELECT input0, COUNT(*) FROM table WHERE input0 > 0 GROUP BY input0",
    add_index=True,
    title="Statistics"
)(daily_return)

# ❌ WRONG: Do NOT use FROM input (that's for sql_query_*)
table_report(
    sql="SELECT input0 FROM input ...",  # ❌ Error: Table 'input' does not exist!
    ...
)(data)
```

**Key Differences:**
- `sql_query_1/2/3/4` (transforms): Use `FROM input`
- `table_report` (reporter): Use `FROM table`

**Why Different?**
- sql_query components are pipeline transforms that process data
- table_report is a visualization reporter that consumes final data
- They operate in different execution contexts with different table names

## CRITICAL: Check for Specialized Reports FIRST

**Before building manual dashboards with numeric_cards_report or custom SQL queries:**

1. **Check if specialized report components exist for your analysis type**
2. **Specialized reports provide COMPLETE analysis - use them ALONE**
3. **DO NOT add extra cards, queries, or charts when specialized report exists**

**Specialized Report Components:**
- `gap_report`: Comprehensive gap analysis (fill rates, distributions, size analysis, pivot hour analysis)
  - Includes all gap metrics: fill percentages, retrace rates, size distributions, timing analysis
  - Has `fill_time_pivot_hour` parameter for before/after hour analysis (e.g., fills before 12:00 ET)
  - Provides histograms and comprehensive statistics

- `histogram_report`: Distribution analysis with configurable binning
  - Use for any distribution/frequency analysis

- `correlation_matrix`: Multi-metric correlation analysis
  - Use for studying relationships between multiple indicators

**Decision Rule:**
- ✅ IF specialized report exists → Use ONLY that report
- ✅ IF NO specialized report → Build custom dashboard with card/chart reports
- ❌ NEVER mix specialized reports with additional manual cards for the same analysis

**Example - Gap Analysis:**
```python
# ✅ CORRECT: Use only gap_report for gap analysis
gaps = gap_classify(fill_percent=100, timeframe="1Min", session="NewYork")()
gap_report(fill_time_pivot_hour=12, histogram_bins=15)(
    gaps.gap_filled, gaps.gap_retrace, gaps.gap_size, gaps.psc, gaps.psc_timestamp
)

# ❌ WRONG: Don't add extra queries/cards when gap_report exists
# gaps = gap_classify(...)()
# sql_query_1(...)  # ❌ Unnecessary - gap_report has this
# numeric_cards_report(...)  # ❌ Unnecessary - gap_report has this
# gap_report(...)()  # ✅ Only this is needed
```

Reports are terminal nodes for visualization. They consume data but produce NO outputs.
Reports CANNOT be used in expressions.

## Report Syntax
```python
# Direct call syntax - single input
numeric_cards_report(title="Win Rate", subtitle="Percentage")(win_rate_value)

# Multiple series on one chart (SLOT accepts multiple connections)
lines_chart_report(title="Comparison")(series1, series2, series3)
bar_chart_report(title="Distribution")(category_data)
```

**Multiple Inputs**: Chart reports accept multiple inputs to the same SLOT (all series rendered on one chart).

**Report Purpose**: Focus on insights/analytics (counts, aggregations, distributions).
Technical indicators auto-render on candlestick charts - no need to chart them manually.

## Card Organization & Grouping (CRITICAL for Dashboard Structure)

**All card report components support organizational parameters**:
- `category` (string, required): High-level category for filtering/navigation
  - Keep CONCISE: 2-3 words maximum
  - Example: "RSI Analysis", "Gap Stats", "Volume Profile"
  - Use SAME category across all related groups

- `group` (integer, required): Group number for related cards (starts at 0)
  - Cards with same `group` value appear together in UI
  - Use sequential numbers: 0, 1, 2, 3, ...
  - Each group represents one cohesive set of insights

- `group_size` (integer, required): **TOTAL number of groups in entire dashboard**
  - This is what actually creates the card grouping structure
  - ALL cards must have the SAME group_size value
  - Example: If you have 4 groups total, set group_size=4 for EVERY card
  - Range: 1-10 groups maximum

**Planning Workflow** (Do this BEFORE writing Python code):

**DEFAULT: Start with 1 group** - Most analyses need only a single group of related metrics.

1. **Count Groups Needed**: How many distinct themes/sections?
   - **Default**: 1 group (most common - user asks about ONE thing)
   - Example: "Show RSI overbought" → 1 group (just overbought stats)
   - Example: "Gap fill rate" → 1 group (gap stats)
   - **Multiple groups ONLY if user explicitly compares/contrasts**:
     * "Compare overbought vs oversold" → 2 groups (explicit comparison)
     * "Gaps vs breakouts" → 2 groups (explicit comparison)
   - **This number becomes your group_size for ALL cards**

2. **Plan Cards Per Group**: What metrics did user explicitly ask for?
   - Include ONLY metrics user mentioned or directly implied
   - Example: "Show overbought count" → 1 card (just count)
   - Don't add "context" metrics user didn't request

3. **Assign Group Numbers**: Start at 0, increment sequentially
   - Single group = group=0
   - Multiple groups = group=0, group=1, group=2, etc.

4. **Set group_size for ALL cards**: Use the total group count from step 1
   - If you have 1 group: group_size=1 for EVERY card (most common)
   - If you have 2 groups: group_size=2 for EVERY card

**Complete Example - Minimal RSI Analysis**:
```python
# User query: "Show me RSI overbought conditions"
# Plan: 1 group, 1 card (user asked ONLY about overbought)

src = market_data_source(timeframe="1D")
rsi_val = rsi(period=14)(src.c)
overbought = rsi_val > 70
ob_count = count(lookback=252)(overbought)

numeric_cards_report(
    title="Overbought Days",
    category="RSI",
    group=0,
    group_size=1  # Just 1 group
)(ob_count)
```

**Example - Comparison (when user explicitly requests it)**:
```python
# User query: "Compare RSI overbought vs oversold frequency"
# Plan: 2 groups (user explicitly asked for comparison)

src = market_data_source(timeframe="1D")
rsi_val = rsi(period=14)(src.c)
overbought = rsi_val > 70
oversold = rsi_val < 30
ob_count = count(lookback=252)(overbought)
os_count = count(lookback=252)(oversold)

# Group 0: Overbought
numeric_cards_report(
    title="Overbought Days",
    category="RSI",
    group=0,
    group_size=2  # 2 groups for comparison
)(ob_count)

# Group 1: Oversold
numeric_cards_report(
    title="Oversold Days",
    category="RSI",
    group=1,
    group_size=2
)(os_count)
```

**CRITICAL Rules**:
- Plan structure BEFORE generating code
- Count total groups first - this becomes group_size for ALL cards
- ALL cards MUST have the SAME group_size value (total groups in dashboard)
- Keep categories consistent (same name for all groups)
- Use sequential group numbers (no gaps: 0, 1, 2...)
- Cards with same `group` value = logically related metrics that appear together

See COMPONENT DIRECTORY for all available report types organized by category.
"""

COMPOSITIONAL_LOGIC_RULES = """
# COMPOSITIONAL LOGIC - COMBINING TRANSFORMS

## Core Principle: Full Composability

**The EpochFlow DSL is fully compositional** - ANY transform output can be combined with ANY other using operators.

You do NOT need special components for complex logic. The operators ARE the integration layer.

### What You CAN Compose

**ANY transform output can be:**
- Combined with arithmetic operators: `+`, `-`, `*`, `/`
- Compared with operators: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Combined with logical operators: `and`, `or`, `not`
- Used in ternary expressions: `value_if_true if condition else value_if_false`
- Passed to cross-sectional transforms: `top_k(k=N)(any_numeric_output)`

### When NOT to Use Special Components

**You do NOT need special components for:**

❌ **Breakout triggers** → Use: `src.c > resistance_level`
```python
# No special "breakout_trigger" component needed
high_20 = max(period=20)(src.h)
breakout = src.c > high_20  # This IS the trigger
```

❌ **Dynamic stops** → Use: `src.c < (entry_price - offset)`
```python
# No special "dynamic_stop" component needed
atr_val = atr(period=14)(src.h, src.l, src.c)
stop_distance = atr_val * 1.5
stop_hit = src.c < (entry_price - stop_distance)  # Dynamic stop logic
```

❌ **Custom scoring/ranking** → Use: `(metric1 * w1) + (metric2 * w2)`
```python
# No special "scoring" component needed
momentum_score = roc(period=20)(src.c) * 0.6
volume_score = (src.v / sma(period=20)(src.v)) * 0.4
composite_score = momentum_score + volume_score  # Composite metric

# Works with cross-sectional ranking
top_20 = top_k(k=20)(composite_score)
```

❌ **Pattern quality ranking** → Use: `top_k(k=N)(pattern.quality_score)`
```python
# No special "pattern_ranker" component needed
# HYPOTHETICAL EXAMPLE (pattern transforms may not exist - check component catalog):
# IF a pattern transform existed with quality score output:
# pattern = hypothetical_pattern(...)(src.o, src.h, src.l, src.c)
# top_patterns = top_k(k=20)(pattern.quality)  # Would rank by pattern quality
#
# Always verify component existence with get_multi_component_details() before use
```

### Cross-Sectional Transforms Work on ANY Output

**`top_k()`, `bottom_k()`, and related cross-sectional transforms accept ANY numeric series:**

✅ Works on **technical indicators**:
```python
top_k(k=20)(rsi(period=14)(src.c))
```

✅ Works on **custom calculations**:
```python
volatility = stddev(period=20)(src.c)
normalized_vol = volatility / src.c  # Coefficient of variation
top_volatile = top_k(k=50)(normalized_vol)
```

✅ Works on **pattern outputs** (if transform has numeric output):
```python
# HYPOTHETICAL EXAMPLE (verify component exists first):
# pattern = hypothetical_pattern(lookback=126)(src.o, src.h, src.l, src.c, src.v)
# cleanest_flags = top_k(k=20)(pattern.quality)
# Always check component catalog before using
```

✅ Works on **composite metrics**:
```python
# Combine multiple factors
momentum_rank = cs_momentum()(roc(period=20)(src.c))  # Momentum ranking
volume_ratio = src.v / sma(period=50)(src.v)
combined = momentum_rank * volume_ratio
top_movers = top_k(k=30)(combined)
```

### Examples: Composition in Action

**Example 1 - Dynamic Entry/Exit Based on Multiple Conditions:**
```python
src = market_data_source(timeframe="1D")

# Combine multiple indicators
rsi_val = rsi(period=14)(src.c)
ema_20 = ema(period=20)(src.c)
ema_50 = ema(period=50)(src.c)
atr_val = atr(period=14)(src.h, src.l, src.c)

# Entry: Multiple conditions composed with AND
rsi_oversold = rsi_val < 30
ema_bullish = ema_20 > ema_50
above_ema = src.c > ema_20
enter_long = rsi_oversold and ema_bullish and above_ema

# Exit: Dynamic stop/target based on ATR
entry_price = src.c  # Simplified
stop_hit = src.c < (entry_price - (atr_val * 1.5))
target_hit = src.c > (entry_price + (atr_val * 3.0))
exit_long = stop_hit or target_hit
```

**Example 2 - Breakout Strategy Using Price Levels (Real Components):**
```python
src = market_data_source(timeframe="1D")

# Use actual components to find breakout levels
high_20 = max(period=20)(src.h)  # 20-day high
low_20 = min(period=20)(src.l)   # 20-day low
atr_val = atr(period=14)(src.h, src.l, src.c)

# Entry: Breakout above 20-day high
enter_long = src.c > high_20

# Exit: Stop below 20-day low minus 1 ATR, target at high plus 2 ATR
stop_level = low_20 - (atr_val * 1.0)
target_level = high_20 + (atr_val * 2.0)
exit_long = (src.c < stop_level) or (src.c > target_level)
```

**Example 3 - Multi-Factor Ranking for Stock Screening:**
```python
# Rank 500 stocks by custom composite score
src = market_data_source(timeframe="1D")

# Factor 1: Momentum
momentum = roc(period=60)(src.c)

# Factor 2: Relative strength vs moving average
ma_200 = sma(period=200)(src.c)
rel_strength = (src.c - ma_200) / ma_200

# Factor 3: Volume surge
vol_ma = sma(period=20)(src.v)
vol_surge = src.v / vol_ma

# Composite score (weighted combination)
composite = (momentum * 0.5) + (rel_strength * 0.3) + (vol_surge * 0.2)

# Get top 20 stocks by composite score
top_20 = top_k(k=20)(composite)

# Report
numeric_cards_report(title="Composite Score", category="Screening", group=0, group_size=1)(composite)
```

### Key Takeaway

**The DSL is a composition language, not a component library.**

When you need complex logic:
1. ✅ Compose primitives using operators
2. ✅ Build intermediate calculations
3. ✅ Use cross-sectional transforms on ANY result
4. ❌ Don't search for specialized components that don't exist
"""

STRATEGY_EXIT_PATTERNS = """
# STRATEGY EXIT PATTERNS

## Two Approaches to Exit Logic

Strategies can define exits in two ways. Choose based on your needs.

### Approach 1: Inline Boolean Expressions (Most Flexible)

**Use `exit_long` parameter with boolean expressions** for dynamic, condition-based exits:

```python
# Dynamic ATR-based stops/targets
atr_val = atr(period=14)(src.h, src.l, src.c)

# Track entry price (simplified - actual implementations vary)
entry_price = src.c

# Define exit conditions using composition
stop_hit = src.c < (entry_price - (atr_val * 1.5))  # 1.5 ATR stop
target_hit = src.c > (entry_price + (atr_val * 3.0))  # 3 ATR target

# Exit on either condition
exit_long = stop_hit or target_hit

trade_signal_executor()(
    enter_long=entry_condition,
    exit_long=exit_long
)
```

**When to use inline expressions:**
- ✅ Dynamic stops based on ATR, pattern levels, or volatility
- ✅ Multiple exit conditions (stop OR target OR time-based)
- ✅ Pattern-aware exits (e.g., exit below pattern support)
- ✅ Trailing stops or conditional exits
- ✅ Complex exit logic combining multiple indicators

**Inline Exit Examples:**

```python
# Example 1: ATR Trailing Stop
atr_val = atr(period=14)(src.h, src.l, src.c)
highest_since_entry = max(period=10)(src.c)  # Simplified
trailing_stop = highest_since_entry - (atr_val * 2.0)
exit_long = src.c < trailing_stop

# Example 2: Support/Resistance + Time-Based Exit
low_20 = min(period=20)(src.l)  # 20-day support
below_support = src.c < low_20
bars_held = 20  # Simplified bar counter
time_exit = bars_held > 50
exit_long = below_support or time_exit

# Example 3: Indicator Reversal Exit
rsi_val = rsi(period=14)(src.c)
macd_val, signal_val = macd(short_period=12, long_period=26, signal_period=9)(src.c)
rsi_overbought = rsi_val > 70
macd_bearish_cross = macd_val < signal_val
exit_long = rsi_overbought and macd_bearish_cross
```

### Approach 2: stop_loss/take_profit Components (Pre-built Logic)

**Use separate components** for standard percentage or ATR-based exits:

```python
# User must explicitly request these components
# Example: "Use 2% stop loss and 5% take profit"

# In strategy configuration (NOT in algorithm code):
strategy_config = {
    "stop_loss": {
        "type": "percentage",
        "percentage": 2.0
    },
    "take_profit": {
        "type": "percentage",
        "percentage": 5.0
    }
}

# Algorithm still uses trade_signal_executor
trade_signal_executor()(
    enter_long=entry_condition,
    exit_long=exit_condition_if_any
)
```

**When to use components:**
- ✅ User explicitly requests "X% stop" or "Y ATR stop"
- ✅ Simple, standard risk management
- ✅ Strategy metadata/config (not algorithm logic)

**Important: These are OPTIONAL strategy components, NOT algorithm transforms.**

### Combining Both Approaches

You CAN use both inline exits AND stop/take profit components:

```python
# Inline exit for strategy-specific logic
rsi_val = rsi(period=14)(src.c)
exit_long = rsi_val > 80  # Exit on extreme overbought

trade_signal_executor()(
    enter_long=entry_condition,
    exit_long=exit_long  # Strategy exits
)

# PLUS stop_loss component for risk management (in strategy config)
# These work together - whichever triggers first
```

### Price Level Breakout Example (Full Strategy with Real Components)

```python
# Breakout strategy using actual price levels
src = market_data_source(timeframe="1D")

# Identify breakout levels using real components
high_20 = max(period=20)(src.h)  # 20-day resistance
low_20 = min(period=20)(src.l)    # 20-day support
atr_val = atr(period=14)(src.h, src.l, src.c)

# Entry: Breakout above resistance
enter_long = src.c > high_20

# Exit: Multiple conditions
below_support = src.c < low_20  # Break below support
atr_stop = src.c < (high_20 - (atr_val * 1.0))  # ATR-based stop
atr_target = src.c > (high_20 + (atr_val * 2.0))  # ATR-based target

# Exit on any condition
exit_long = below_support or atr_stop or atr_target

trade_signal_executor()(
    enter_long=enter_long,
    exit_long=exit_long
)
```

### Key Rules

1. **Inline `exit_long` boolean expressions** → For dynamic, complex exit logic
2. **stop_loss/take_profit components** → For standard risk management (optional)
3. **Can combine both** → Strategy exits + risk management
4. **Use composition** → Build exits from ANY transform outputs + operators
5. **No special components needed** → Operators handle all exit logic
"""

EXECUTION_COMPONENTS_RULES = """
# EXECUTION COMPONENTS (Trading Signals)

## Trade Signal Executor (REQUIRED for trading strategies)
```python
# Direct call with keyword arguments for named inputs
trade_signal_executor()(
    enter_long=entry_condition,
    exit_long=exit_condition,
    enter_short=short_entry,
    exit_short=short_exit
)
```

**All inputs are optional** - only specify the signals you need.
"""


# ===========================================================================================
# STRATEGY BUILDER AGENT RULE - TRADING STRATEGY GENERATION
# ===========================================================================================

STRATEGY_BUILDER_RULE = f"""
# PYTHON DSL SYNTAX REFERENCE FOR TRADING STRATEGIES

{COMPOSITIONAL_LOGIC_RULES}

{STRATEGY_EXIT_PATTERNS}

{MISSING_COMPONENT_HANDLING}

{DSL_SYNTAX_RULES}

{COMPONENT_DISCOVERY_RULES}

{TIMEFRAME_RULES}

{SESSION_RULES}

{_build_datasource_components_details()}

{TRANSFORM_COMPONENTS_RULES}

{EXECUTION_COMPONENTS_RULES}

{_build_trade_signal_executor_details()}

{_build_component_directory(exclude_reporters=True, exclude_executors=False)}
"""

# ===========================================================================================
# QUANT RESEARCHER AGENT RULE - DATA ANALYSIS & INSIGHTS
# ===========================================================================================

QUANT_RESEARCHER_RULE = f"""
# PYTHON DSL SYNTAX REFERENCE FOR QUANTITATIVE RESEARCH

{ANTI_OVERENGINEERING_RULES}

{COMPOSITIONAL_LOGIC_RULES}

{MISSING_COMPONENT_HANDLING}

{DSL_SYNTAX_RULES}

{COMPONENT_DISCOVERY_RULES}

{TIMEFRAME_RULES}

{SESSION_RULES}

{_build_datasource_components_details()}

{TRANSFORM_COMPONENTS_RULES}

{REPORT_COMPONENTS_RULES}

{_build_reporter_components_details()}

{_build_component_directory(exclude_reporters=False, exclude_executors=True)}
"""

with open("quant.txt", "w") as f:
    f.write(QUANT_RESEARCHER_RULE)