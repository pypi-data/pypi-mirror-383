"""
Pythonic algorithm AST compiler.

Parses a constrained subset of Python expressions for the algorithm section and
lowers to a nodes/edges IR using a transforms registry. No imports or general
Python execution are allowed.

Supported constructs:
  - Assign to names or tuple of names: x = ema(period=20)(src.c)
  - Nested calls to represent input application: ctor(...)(input0, input1, ...)
  - Direct calls to sinks (no outputs): numeric_cards_report(title="X")(data)
  - Keyword args for named inputs: trade_signal_executor()(enter_long=cond)
  - Attribute access for handles: src.c, cross.result

Disallowed:
  - imports, control flow, function defs, attribute assignment on LHS.

Timeframe:
  - If provided in params, it must be a pandas offset string (e.g., "1H", "15min", "W-FRI").
    We validate via pandas if available, but do not rewrite or uppercase the value.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Import at module level to avoid blocking during function execution
from epochflow.registry.transform_registry import build_core_transform_registry_or_none


# Optional pandas-based offset validation
try:  # pragma: no cover - optional dependency
    from pandas.tseries.frequencies import to_offset as _to_offset  # type: ignore
    import warnings

    def _is_valid_pandas_offset(value: str) -> bool:
        try:
            with warnings.catch_warnings():  # Suppress FutureWarnings from pandas offset codes
                warnings.simplefilter("ignore")
                _to_offset(value)
            return True
        except Exception:
            return False
except Exception:  # pragma: no cover - pandas not installed
    def _is_valid_pandas_offset(value: str) -> bool:
        # Fallback: accept any non-empty string
        return isinstance(value, str) and len(value) > 0


@dataclass
class Edge:
    source: str
    source_handle: str
    target: str
    target_handle: str


class AlgorithmAstCompiler(ast.NodeVisitor):
    def __init__(self, registry: Dict[str, Any], transforms_list: Optional[List[Dict[str, Any]]] = None):
        self.registry = registry
        self.components: Dict[str, Any] = (registry or {}).get("manifest", {}).get("components", {})
        self.transforms_list = transforms_list
        self.var_to_binding: Dict[str, str] = {}
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Edge] = []

        # Track node output types for type checking/casting
        self.node_output_types: Dict[str, Dict[str, str]] = {}

        # Operator mappings
        self._binary_op_map = {
            ast.Add: "add",
            ast.Sub: "sub",
            ast.Mult: "mul",
            ast.Div: "div",
            # ast.Mod: "modulo",  # Not available in transforms
            # ast.Pow: "power",   # Not available in transforms
            ast.Lt: "lt",
            ast.Gt: "gt",
            ast.LtE: "lte",
            ast.GtE: "gte",
            ast.Eq: "eq",
            ast.NotEq: "neq",
            ast.And: "logical_and",
            ast.Or: "logical_or",
        }

        self._unary_op_map = {
            ast.Not: "logical_not",
            ast.USub: "sub",  # Will use 0 - operand for negation
        }

    # Public API
    def compile(self, source: str) -> Dict[str, Any]:
        module = ast.parse(source)
        self.visit(module)
        self._verify_session_dependencies()
        return {
            "nodes": self.nodes,
            "edges": [e.__dict__ for e in self.edges],
        }

    def _verify_session_dependencies(self) -> None:
        """Verify that all nodes with session parameters have corresponding sessions nodes.

        For each node with a session field, ensures a sessions node exists with:
        - Matching session parameter value
        - Same timeframe (if the dependent node has a timeframe)

        If a matching sessions node doesn't exist, creates one automatically.
        """
        # Track required sessions: {(session_val, timeframe): [node_ids]}
        required_sessions: Dict[Tuple[str, Optional[str]], List[str]] = {}

        # Scan all nodes for session fields
        for node in self.nodes:
            session = node.get("session")
            node_type = node.get("type")

            # Skip if no session or if this is already a sessions node
            if not session or node_type == "sessions":
                continue

            # Get the timeframe for this node (if any)
            timeframe = node.get("timeframe")

            # Track this requirement
            key = (session, timeframe)
            if key not in required_sessions:
                required_sessions[key] = []
            required_sessions[key].append(node.get("id", "unknown"))

        # For each required session, ensure a sessions node exists
        for (session_val, timeframe), node_ids in required_sessions.items():
            if not self._has_sessions_node(session_val, timeframe):
                # Create the missing sessions node
                self._create_sessions_node(session_val, timeframe)

    # Helpers
    def _error(self, node: ast.AST, msg: str) -> None:
        line = getattr(node, "lineno", "?")
        col = getattr(node, "col_offset", "?")
        raise SyntaxError(f"{msg} (line {line}, col {col})")

    def _ensure_new_binding(self, name: str, node: ast.AST) -> None:
        # Allow '_' to be reused (Python convention for throwaway variables)
        if name != "_" and name in self.var_to_binding:
            self._error(node, f"Variable '{name}' already bound")

    def _require_component(self, comp_name: str, node: ast.AST) -> Dict[str, Any]:
        meta = self.components.get(comp_name)
        if not meta:
            self._error(node, f"Unknown component '{comp_name}'")
        return meta

    def _allows_multiple_connections(self, comp_name: str) -> bool:
        """Check if component has single input with allowMultipleConnections flag."""
        if not self.transforms_list:
            return False
        for t in self.transforms_list:
            if t.get("id") == comp_name:
                inputs = t.get("inputs", [])
                if len(inputs) == 1 and isinstance(inputs[0], dict):
                    return inputs[0].get("allowMultipleConnections", False)
        return False

    def _canonicalize_timeframe(self, params: Dict[str, Any], node: ast.AST) -> None:
        """Validate timeframe is a pandas offset string if provided; do not mutate.

        For the compiler, enforce that timeframe is a string and, when pandas
        is available, parseable by pandas to_offset.

        Empty strings are ignored (removed from params).
        """
        if "timeframe" in params:
            tf_val = params["timeframe"]
            # Skip empty strings - treat as "not specified"
            if tf_val == "":
                del params["timeframe"]
                return
            if not isinstance(tf_val, str):
                self._error(node, "Parameter 'timeframe' must be a string (pandas offset)")
            if not _is_valid_pandas_offset(tf_val):
                self._error(node, f"Invalid pandas offset timeframe '{tf_val}'")
    
    def _canonicalize_session(self, params: Dict[str, Any], node: ast.AST) -> None:
        """Validate session parameter if provided - must be a string literal.

        Session must be a string representing a predefined session type.
        Valid values: Sydney, Tokyo, London, NewYork, AsianKillZone,
                     LondonOpenKillZone, NewYorkKillZone, LondonCloseKillZone

        Empty strings are ignored (removed from params).
        """
        if "session" in params:
            session_val = params["session"]
            # Skip empty strings - treat as "not specified"
            if session_val == "":
                del params["session"]
                return
            if not isinstance(session_val, str):
                self._error(node, "Parameter 'session' must be a string literal")
            # Validate against predefined sessions
            valid_sessions = {
                'Sydney', 'Tokyo', 'London', 'NewYork',
                'AsianKillZone', 'LondonOpenKillZone', 'NewYorkKillZone', 'LondonCloseKillZone'
            }
            if session_val not in valid_sessions:
                self._error(node, f"Invalid session '{session_val}'. Must be one of: {', '.join(sorted(valid_sessions))}")

    def _has_sessions_node(self, session_val: str, timeframe: Optional[str]) -> bool:
        """Check if a sessions node exists with matching session_type and timeframe.

        Args:
            session_val: The session value to match (e.g., "NewYork")
            timeframe: The timeframe to match (optional)

        Returns:
            True if a matching sessions node exists, False otherwise
        """
        for node in self.nodes:
            if node.get("type") == "sessions":
                # Session can be in params OR at top level (moved by _create_ui_node)
                params = node.get("params", {})
                node_session = node.get("session") or params.get("session")

                if node_session == session_val:
                    # If timeframe is specified, it must match
                    if timeframe is not None:
                        node_timeframe = node.get("timeframe")
                        if node_timeframe == timeframe:
                            return True
                    else:
                        # No timeframe requirement, any matching session is fine
                        return True
        return False

    def _create_sessions_node(self, session_val: str, timeframe: Optional[str]) -> None:
        """Create a sessions node with the specified session_type and timeframe.

        Args:
            session_val: The session value (e.g., "NewYork")
            timeframe: The timeframe (optional)
        """
        # Generate unique ID for the sessions node
        node_id = self._unique_node_id("sessions")

        # Build params with session (the parameter name for sessions component)
        params = {"session": session_val}

        # Create the sessions node
        ui_node = {"id": node_id, "type": "sessions", "params": params}

        # Add timeframe if specified
        if timeframe is not None:
            ui_node["timeframe"] = timeframe

        # Track output types for sessions node (has multiple outputs)
        output_types = self._get_output_types("sessions")
        if output_types:
            self.node_output_types[node_id] = output_types

        # Add to nodes list
        self.nodes.append(ui_node)

        # Register in var_to_binding
        self.var_to_binding[node_id] = "sessions"
    
    def _get_input_types(self, comp_name: str) -> Dict[str, str]:
        """Get input types for a component from transforms_list if available."""
        try:
            if not self.transforms_list:
                return {}
            for transform in self.transforms_list:
                if transform.get("id") == comp_name:
                    input_types = {}
                    for inp in transform.get("inputs", []):
                        input_id = inp.get("id", "")
                        # Handle SLOT naming
                        if input_id.startswith("*"):
                            suffix = input_id[1:]
                            input_id = "SLOT" if suffix == "" else f"SLOT{suffix}"
                        # Map type to single letter
                        type_str = inp.get("type", "Any")
                        if type_str == "Boolean":
                            input_types[input_id] = "B"
                        elif type_str == "Integer":
                            input_types[input_id] = "I"
                        elif type_str == "Decimal":
                            input_types[input_id] = "D"
                        elif type_str == "Number":
                            input_types[input_id] = "N"
                        else:
                            input_types[input_id] = "A"  # Any
                    return input_types
        except:
            pass
        return {}

    def _get_output_types(self, comp_name: str) -> Dict[str, str]:
        """Get output types for a component from transforms_list if available."""
        try:
            if not self.transforms_list:
                return {}
            for transform in self.transforms_list:
                if transform.get("id") == comp_name:
                    output_types = {}
                    for out in transform.get("outputs", []):
                        output_id = out.get("id", "")
                        # Map type to single letter
                        type_str = out.get("type", "Any")
                        if type_str == "Boolean":
                            output_types[output_id] = "B"
                        elif type_str == "Integer":
                            output_types[output_id] = "I"
                        elif type_str == "Decimal":
                            output_types[output_id] = "D"
                        elif type_str == "Number":
                            output_types[output_id] = "N"
                        else:
                            output_types[output_id] = "A"  # Any
                    return output_types
        except:
            pass
        return {}

    def _is_type_compatible(self, source_type: str, target_type: str) -> bool:
        """Check if source type is compatible with target type."""
        # Any type accepts all
        if target_type == "A" or source_type == "A":
            return True
        # Exact match
        if source_type == target_type:
            return True
        # Number accepts Integer and Decimal
        if target_type == "N" and source_type in ("I", "D"):
            return True
        # Otherwise incompatible
        return False

    def _needs_type_cast(self, source_type: str, target_type: str) -> Optional[str]:
        """Determine if type casting is needed and return the cast method.

        Returns:
            None if compatible, "bool_to_num" or "num_to_bool" if casting needed
        """
        if self._is_type_compatible(source_type, target_type):
            return None

        # Boolean to Number/Decimal/Integer
        if source_type == "B" and target_type in ("N", "D", "I"):
            return "bool_to_num"

        # Number/Decimal/Integer to Boolean
        if source_type in ("N", "D", "I") and target_type == "B":
            return "num_to_bool"

        return "incompatible"  # Can't cast

    def _insert_type_cast(
        self,
        src_node: str,
        src_handle: str,
        src_type: str,
        target_type: str,
        ctx_node: ast.AST
    ) -> Tuple[str, str]:
        """Insert a type casting node if needed.

        Returns:
            (node_id, handle) of either the original source or the casting node
        """
        cast_method = self._needs_type_cast(src_type, target_type)

        if cast_method is None:
            # No casting needed
            return src_node, src_handle

        if cast_method == "bool_to_num":
            # Use boolean_select to convert boolean to number
            cast_node_id = self._unique_node_id("bool_to_num_cast")
            self.nodes.append({"id": cast_node_id, "type": "boolean_select", "params": {}})

            # Wire the boolean to condition
            self.edges.append(Edge(src_node, src_handle, cast_node_id, "condition"))

            # Create number nodes for true (1) and false (0)
            true_node = self._unique_node_id("number")
            self.nodes.append({"id": true_node, "type": "number", "params": {"value": 1}})
            false_node = self._unique_node_id("number")
            self.nodes.append({"id": false_node, "type": "number", "params": {"value": 0}})

            # Track output types for number nodes
            self.node_output_types[true_node] = {"result": "D"}
            self.node_output_types[false_node] = {"result": "D"}

            # Wire the numbers to true and false inputs
            self.edges.append(Edge(true_node, "result", cast_node_id, "true"))
            self.edges.append(Edge(false_node, "result", cast_node_id, "false"))

            # Track output type
            self.node_output_types[cast_node_id] = {"result": "N"}

            return cast_node_id, "result"

        elif cast_method == "num_to_bool":
            # Use neq (not equal) to convert number to boolean (num != 0)
            cast_node_id = self._unique_node_id("num_to_bool_cast")
            self.nodes.append({"id": cast_node_id, "type": "neq", "params": {}})

            # Wire the number to SLOT0
            self.edges.append(Edge(src_node, src_handle, cast_node_id, "SLOT0"))

            # Create zero node
            zero_node = self._unique_node_id("number")
            self.nodes.append({"id": zero_node, "type": "number", "params": {"value": 0}})
            # Track output type for zero node
            self.node_output_types[zero_node] = {"result": "D"}

            # Wire zero to SLOT1
            self.edges.append(Edge(zero_node, "result", cast_node_id, "SLOT1"))

            # Track output type
            self.node_output_types[cast_node_id] = {"result": "B"}

            return cast_node_id, "result"

        else:
            # Incompatible types that can't be cast
            self._error(
                ctx_node,
                f"Type mismatch: Cannot convert {src_type} to {target_type}"
            )

    def _create_ui_node(self, node_id: str, ctor_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a UINode dictionary with special handling for timeframe and session parameters.

        Extracts timeframe and session from params and sets them as separate fields,
        similar to how the UI expects them.
        """
        # Extract timeframe if present
        timeframe = params.pop("timeframe", None)
        # Extract session if present
        session = params.pop("session", None)

        # Build the node dictionary
        ui_node = {"id": node_id, "type": ctor_name, "params": params}

        # Add timeframe as a separate field if it exists
        if timeframe is not None:
            ui_node["timeframe"] = timeframe

        # Add session as a separate field if it exists
        if session is not None:
            ui_node["session"] = session

        # Track output types for this node
        output_types = self._get_output_types(ctor_name)
        if output_types:
            self.node_output_types[node_id] = output_types

        return ui_node

    # AST visitors
    def visit_Module(self, node: ast.Module) -> Any:
        for stmt in node.body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.With, ast.For, ast.While, ast.If, ast.Try, ast.Lambda)):
                self._error(stmt, "Disallowed construct in algorithm section")
            self.visit(stmt)
        return None

    def visit_Expr(self, node: ast.Expr) -> Any:
        v = node.value

        # Allow direct calls to sink components (components with no outputs)
        if self._is_constructor_call(v):
            ctor_name, ctor_kwargs, feed_steps = self._parse_constructor_and_feeds(v)
            comp_meta = self._require_component(ctor_name, node)

            # Check if component has no outputs (is a sink)
            outputs = comp_meta.get("outputs", [])
            if not outputs:
                # Create sink node with synthetic ID
                synthetic_id = f"node_{len(self.nodes)}"
                params = dict(ctor_kwargs)
                self._canonicalize_timeframe(params, node)
                self._canonicalize_session(params, node)
                ui_node = self._create_ui_node(synthetic_id, ctor_name, params)
                self.nodes.append(ui_node)

                # Wire inputs
                for args, kwargs in feed_steps:
                    self._wire_inputs(synthetic_id, comp_meta, args, kwargs, node)
                return None
            else:
                self._error(node, "Direct call to component with outputs must be assigned to a variable")

        self._error(node, "Unsupported expression statement")

    def visit_Assign(self, node: ast.Assign) -> Any:
        if len(node.targets) != 1:
            self._error(node, "Only single assignment supported")
        target = node.targets[0]
        if isinstance(target, ast.Attribute):
            self._error(node, "Assignment to attributes/handles is not allowed")

        # Check if value is a constructor call or something else
        if self._is_constructor_call(node.value):
            ctor_name, ctor_kwargs, feed_steps = self._parse_constructor_and_feeds(node.value)
            comp_meta = self._require_component(ctor_name, node)

            if isinstance(target, ast.Name):
                node_id = target.id
                self._ensure_new_binding(node_id, node)
                params = dict(ctor_kwargs)
                self._canonicalize_timeframe(params, node)
                self._canonicalize_session(params, node)
                ui_node = self._create_ui_node(node_id, ctor_name, params)
                self.nodes.append(ui_node)
                self.var_to_binding[node_id] = ctor_name
                for args, kwargs in feed_steps:
                    self._wire_inputs(node_id, comp_meta, args, kwargs, node)
                return None

            if isinstance(target, ast.Tuple):
                names: List[str] = []
                for elt in target.elts:
                    if not isinstance(elt, ast.Name):
                        self._error(node, "Tuple targets must be simple names")
                    names.append(elt.id)
                for n in names:
                    self._ensure_new_binding(n, node)

                synthetic_id = f"node_{len(self.nodes)}"
                params = dict(ctor_kwargs)
                self._canonicalize_timeframe(params, node)
                self._canonicalize_session(params, node)
                ui_node = self._create_ui_node(synthetic_id, ctor_name, params)
                self.nodes.append(ui_node)
                self.var_to_binding[synthetic_id] = ctor_name
                for args, kwargs in feed_steps:
                    self._wire_inputs(synthetic_id, comp_meta, args, kwargs, node)

                out_handles = comp_meta.get("outputs", [])
                if len(out_handles) != len(names):
                    self._error(node, f"Expected {len(out_handles)} outputs, got {len(names)}")
                for name, handle in zip(names, out_handles):
                    # Bind variable to an alias "node.handle" so it can be used as a value
                    self.var_to_binding[name] = f"{synthetic_id}.{handle}"
                return None
        else:
            # Handle non-constructor assignments (operators, name references, etc.)
            if isinstance(target, ast.Name):
                node_id = target.id
                self._ensure_new_binding(node_id, node)
                # Parse the value and resolve to a handle
                parsed_value = self._parse_value(node.value)
                src_node, src_handle = self._resolve_value_handle(parsed_value, node)
                # Bind the variable to the source node.handle
                self.var_to_binding[node_id] = f"{src_node}.{src_handle}"
                return None

            if isinstance(target, ast.Tuple):
                # Support deferred tuple unpacking: a, b = variable_name
                # where variable_name is bound to a multi-output node
                if not isinstance(node.value, ast.Name):
                    self._error(node, "Tuple unpacking only supports name references or direct constructor calls")

                var_name = node.value.id
                ref = self.var_to_binding.get(var_name)

                if not ref:
                    self._error(node, f"Unknown variable '{var_name}'")

                # Check if ref is a node.handle or just a component name
                if "." in ref:
                    # It's already bound to a specific handle, can't unpack
                    self._error(node, f"Cannot unpack '{var_name}' - already bound to single output '{ref}'")

                # var_name is bound to a component name, look up its outputs
                comp_name = ref
                comp_meta = self.components.get(comp_name)
                if not comp_meta:
                    self._error(node, f"Unknown component '{comp_name}' for variable '{var_name}'")

                # Extract tuple target names
                names: List[str] = []
                for elt in target.elts:
                    if not isinstance(elt, ast.Name):
                        self._error(node, "Tuple targets must be simple names")
                    names.append(elt.id)

                for n in names:
                    self._ensure_new_binding(n, node)

                # Get output handles
                out_handles = comp_meta.get("outputs", [])
                if len(out_handles) != len(names):
                    self._error(node, f"Expected {len(out_handles)} outputs from '{var_name}', got {len(names)} names in tuple")

                # Bind each name to the corresponding output handle
                for name, handle in zip(names, out_handles):
                    # Extract handle ID if it's a dict
                    if isinstance(handle, dict):
                        handle_id = handle.get("id", "result")
                    else:
                        handle_id = handle
                    self.var_to_binding[name] = f"{var_name}.{handle_id}"

                return None

        self._error(node, "Unsupported assignment target")

    def _is_constructor_call(self, value: ast.AST) -> bool:
        """Check if the value is a constructor call (possibly chained)."""
        # Must have at least one Call in the chain
        if not isinstance(value, ast.Call):
            return False
        cur = value
        while isinstance(cur, ast.Call):
            cur = cur.func
        return isinstance(cur, ast.Name)

    # Parsing helpers
    def _parse_constructor_and_feeds(self, value: ast.AST) -> Tuple[str, Dict[str, Any], List[Tuple[List[Any], Dict[str, Any]]]]:
        calls: List[ast.Call] = []
        cur = value
        while isinstance(cur, ast.Call):
            calls.append(cur)
            cur = cur.func
        if not isinstance(cur, ast.Name):
            self._error(value, "Right-hand side must be a constructor call (e.g., ema(...)(...))")
        ctor_name = cur.id
        calls.reverse()
        # Reject positional constructor args for options; constructor kwargs only.
        # If the first call includes positional ARGS and there are NO constructor options,
        # interpret them as feed inputs in a single-call form: comp(a,b) == comp()(a,b)
        ctor_kwargs = self._keywords_to_dict(calls[0].keywords)
        feed_steps: List[Tuple[List[Any], Dict[str, Any]]] = []
        if calls[0].args:
            comp_meta = self._require_component(ctor_name, value)
            options = comp_meta.get("options", [])
            # Extract option IDs from option metadata if they're dicts
            if options and isinstance(options[0], dict):
                option_ids = [opt.get("id", "") for opt in options]
            else:
                option_ids = options
            if not option_ids and len(calls) == 1:
                # Treat as a feed step on the constructor
                args = [self._parse_value(a) for a in calls[0].args]
                kwargs: Dict[str, Any] = {}
                feed_steps.append((args, kwargs))
            else:
                if len(calls[0].args) > len(option_ids):
                    self._error(calls[0], "Too many positional constructor arguments")
                for idx, arg_node in enumerate(calls[0].args):
                    opt_name = option_ids[idx]
                    if opt_name in ctor_kwargs:
                        self._error(calls[0], f"Duplicate value for parameter '{opt_name}'")
                    ctor_kwargs[opt_name] = self._parse_literal_or_primitive(arg_node)
        for c in calls[1:]:
            args = [self._parse_value(a) for a in c.args]
            kwargs = {kw.arg: self._parse_value(kw.value) for kw in c.keywords}
            feed_steps.append((args, kwargs))
        return ctor_name, ctor_kwargs, feed_steps

    def _keywords_to_dict(self, keywords: List[ast.keyword]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for kw in keywords:
            if kw.arg is None:
                self._error(kw, "**kwargs not supported")
            out[kw.arg] = self._parse_literal_or_primitive(kw.value)
        return out

    def _parse_literal_or_primitive(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Str):
            return node.s
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Name):
            # Check if this name is bound to a constant value (number, bool)
            # This resolves variables like: lookback = 20, then max(period=lookback)
            ref = self.var_to_binding.get(node.id)
            if ref and "." in ref:
                # ref is in form "node_id.handle" - extract the node_id
                node_id, handle = ref.split(".", 1)
                # Check if it's bound to a literal node (number, bool_true, bool_false)
                for n in self.nodes:
                    if n.get("id") == node_id and n.get("type") in ("number", "bool_true", "bool_false"):
                        params = n.get("params", {})
                        if n.get("type") == "number":
                            return params.get("value")
                        elif n.get("type") == "bool_true":
                            return True
                        elif n.get("type") == "bool_false":
                            return False
            # Fallback: Accept bare identifiers and convert them to strings
            # This allows syntax like sessions(session=London) instead of sessions(session="London")
            return node.id
        self._error(node, "Only literal keyword values supported")

    def _parse_value(self, node: ast.AST) -> Tuple[str, Any]:
        if isinstance(node, ast.Attribute):
            return ("attr", self._attribute_to_tuple(node))
        if isinstance(node, ast.Name):
            return ("name", node.id)
        if isinstance(node, ast.Call):
            # Materialize inline call into a node and refer to its single/default output
            node_id = self._materialize_inline_call(node, node)
            return ("name", node_id)
        if isinstance(node, ast.Constant):
            # Treat boolean constants as bool_true or bool_false nodes
            # MUST check bool BEFORE int/float since bool is a subtype of int in Python
            if isinstance(node.value, bool):
                node_id, handle = self._materialize_boolean(node.value, node)
                return ("name", node_id)  # name resolves to single-output 'result'
            # Treat numeric constants as number(value=...) nodes
            if isinstance(node.value, (int, float)):
                # Materialize immediately so downstream sees a handle-producing value
                node_id, handle = self._materialize_number(node.value, node)
                return ("name", node_id)  # name resolves to single-output 'result'
            # Treat string constants as text(value=...) nodes
            if isinstance(node.value, str):
                node_id, handle = self._materialize_text(node.value, node)
                return ("name", node_id)  # name resolves to single-output 'result'
            # Treat None as null node
            if node.value is None:
                node_id, handle = self._materialize_null(node)
                return ("name", node_id)  # name resolves to single-output 'result'
            return ("const", node.value)
        if isinstance(node, ast.List):
            return ("list", [self._parse_value(elt) for elt in node.elts])
        if isinstance(node, ast.IfExp):
            # Ternary expression: a if cond else b
            return (
                "ifexp",
                (
                    self._parse_value(node.test),
                    self._parse_value(node.body),
                    self._parse_value(node.orelse),
                ),
            )
        if isinstance(node, ast.BinOp):
            # Binary operation: left op right
            return (
                "binop",
                (
                    type(node.op),
                    self._parse_value(node.left),
                    self._parse_value(node.right),
                ),
            )
        if isinstance(node, ast.UnaryOp):
            # Unary operation: op operand
            if isinstance(node.op, ast.UAdd):
                self._error(node, "Unary plus is not supported; use an explicit transform if needed")
            return (
                "unaryop",
                (
                    type(node.op),
                    self._parse_value(node.operand),
                ),
            )
        if isinstance(node, ast.Compare):
            # Comparison: left op right (only single comparison supported)
            if len(node.ops) != 1 or len(node.comparators) != 1:
                self._error(node, "Only single comparisons supported")
            return (
                "binop",
                (
                    type(node.ops[0]),
                    self._parse_value(node.left),
                    self._parse_value(node.comparators[0]),
                ),
            )
        if isinstance(node, ast.BoolOp):
            # Boolean operation: values[0] op values[1] op ...
            # We'll convert to nested binary operations
            if len(node.values) < 2:
                self._error(node, "Boolean operation needs at least 2 operands")
            return self._parse_bool_op(node)
        if isinstance(node, ast.Subscript):
            # Subscript notation interpreted as lag operator
            # e.g., src.c[1] becomes lag(period=1)(src.c)
            return self._parse_subscript_as_lag(node)
        self._error(node, "Unsupported value in inputs")

    def _parse_bool_op(self, node: ast.BoolOp) -> Tuple[str, Any]:
        """Convert multi-value boolean operation to nested binary operations."""
        op_type = type(node.op)
        values = [self._parse_value(v) for v in node.values]

        # Build nested structure: (a and b and c) -> (a and (b and c))
        result = values[-1]
        for i in range(len(values) - 2, -1, -1):
            result = ("binop", (op_type, values[i], result))
        return result

    def _parse_subscript_as_lag(self, node: ast.Subscript) -> Tuple[str, Any]:
        """Parse subscript notation as lag operator.

        Example:
        - src.c[1] becomes lag(period=1)(src.c) - look back 1 period
        - src.c[-5] becomes lag(period=-5)(src.c) - look forward 5 periods
        """
        # Extract the lag period from the index
        lag_period = None

        if isinstance(node.slice, ast.Constant):
            lag_period = node.slice.value
        elif isinstance(node.slice, ast.Index) and isinstance(node.slice.value, ast.Constant):
            # Python 3.8 compatibility
            lag_period = node.slice.value.value
        elif isinstance(node.slice, ast.UnaryOp) and isinstance(node.slice.op, ast.USub):
            # Handle negative indices: -N is UnaryOp(USub, Constant(N))
            if isinstance(node.slice.operand, ast.Constant):
                lag_period = -node.slice.operand.value
            else:
                self._error(node, "Subscript index must be a constant integer for lag operator")
        else:
            self._error(node, "Subscript index must be a constant integer for lag operator")

        # Validate lag period is a non-zero integer (positive for backward, negative for forward)
        if not isinstance(lag_period, int) or lag_period == 0:
            self._error(node, "Lag period must be a non-zero integer")

        # Create a lag node
        lag_node_id = self._unique_node_id("lag")
        self.nodes.append({
            "id": lag_node_id,
            "type": "lag",
            "params": {"period": lag_period}
        })

        # Register the lag node in var_to_binding
        self.var_to_binding[lag_node_id] = "lag"

        # Parse the value being lagged
        value_v = self._parse_value(node.value)
        value_node, value_handle = self._resolve_value_handle(value_v, node)

        # Wire the value to the lag input
        self.edges.append(Edge(value_node, value_handle, lag_node_id, "SLOT"))

        # Track output type (lag always returns Decimal)
        # Note: lag converts any input to Decimal output
        self.node_output_types[lag_node_id] = {"result": "D"}

        # Return reference to the lag node
        return ("name", lag_node_id)

    def _attribute_to_tuple(self, attr: ast.Attribute) -> Tuple[str, str]:
        parts: List[str] = []
        cur: ast.AST = attr
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Call):
            # Materialize inline call into a synthetic node, then attach attribute to it
            node_id = self._materialize_inline_call(cur, attr)
            parts.append(node_id)
        elif isinstance(cur, ast.Name):
            parts.append(cur.id)
        else:
            self._error(attr, "Invalid attribute base")
        parts.reverse()
        return parts[0], ".".join(parts[1:])

    def _materialize_inline_call(self, call: ast.Call, ctx_node: ast.AST) -> str:
        # Parse constructor and feed steps from a value-position call and emit a node
        calls: List[ast.Call] = []
        cur = call
        while isinstance(cur, ast.Call):
            calls.append(cur)
            cur = cur.func
        if not isinstance(cur, ast.Name):
            self._error(ctx_node, "Inline call must start with a component name")
        ctor_name = cur.id
        calls.reverse()

        # Handle shorthand syntax: component(inputs) instead of component()(inputs)
        # If first call has args and component has no options, treat args as feed inputs
        comp_meta = self._require_component(ctor_name, ctx_node)
        options = comp_meta.get("options", [])
        if options and isinstance(options[0], dict):
            option_ids = [opt.get("id", "") for opt in options]
        else:
            option_ids = options

        ctor_kwargs = self._keywords_to_dict(calls[0].keywords)
        feed_steps: List[Tuple[List[Any], Dict[str, Any]]] = []

        if calls[0].args:
            if not option_ids and len(calls) == 1:
                # Shorthand: treat as feed step
                args = [self._parse_value(a) for a in calls[0].args]
                feed_steps.append((args, {}))
            else:
                self._error(calls[0], "Positional constructor arguments are not supported; use keyword args")

        node_id = self._unique_node_id(ctor_name)
        params = dict(ctor_kwargs)
        self._canonicalize_timeframe(params, ctx_node)
        self._canonicalize_session(params, ctx_node)
        ui_node = self._create_ui_node(node_id, ctor_name, params)
        self.nodes.append(ui_node)
        self.var_to_binding[node_id] = ctor_name
        # Track output types
        output_types = self._get_output_types(ctor_name)
        if output_types:
            self.node_output_types[node_id] = output_types

        # Wire feed steps (from shorthand or explicit chained calls)
        for args, kwargs in feed_steps:
            self._wire_inputs(node_id, comp_meta, args, kwargs, ctx_node)

        for c in calls[1:]:
            args = [self._parse_value(a) for a in c.args]
            kwargs = {kw.arg: self._parse_value(kw.value) for kw in c.keywords}
            self._wire_inputs(node_id, comp_meta, args, kwargs, ctx_node)
        return node_id

    def _resolve_value_handle(self, v: Tuple[str, Any], ctx_node: ast.AST) -> Tuple[str, str]:
        kind, val = v
        if kind == "attr":
            var, handle = val
            return self._resolve_handle(var, handle, ctx_node)
        if kind == "name":
            ref = self.var_to_binding.get(val)
            if ref and "." in ref:
                node_id, handle = ref.split(".", 1)
                return node_id, handle
            # If no binding or no dot, it must be a node name
            if val not in self.var_to_binding:
                self._error(ctx_node, f"Unknown variable '{val}'")
            comp_name = self.var_to_binding[val]
            comp_meta = self.components.get(comp_name)
            # Allow synthetic nodes even if not present in registry
            if comp_meta is None:
                if comp_name in ("number", "bool_true", "bool_false", "text", "null"):
                    return val, "result"
                self._error(ctx_node, f"Unknown component '{comp_name}'")
            outs = comp_meta.get("outputs", [])
            if len(outs) == 1:
                # Handle both string and dict outputs
                if isinstance(outs[0], dict):
                    return val, outs[0].get("id", "result")
                else:
                    return val, outs[0]
            self._error(ctx_node, f"Ambiguous output for '{val}'")
        if kind == "ifexp":
            test_v, true_v, false_v = val
            return self._materialize_ifexp(test_v, true_v, false_v, ctx_node)
        if kind == "binop":
            op_type, left_v, right_v = val
            return self._materialize_binop(op_type, left_v, right_v, ctx_node)
        if kind == "unaryop":
            op_type, operand_v = val
            return self._materialize_unaryop(op_type, operand_v, ctx_node)
        self._error(ctx_node, "Value must be a handle or bound name")

    def _unique_node_id(self, base: str) -> str:
        idx = 0
        existing = {n.get("id") for n in self.nodes}
        candidate = f"{base}_{idx}"
        while candidate in existing:
            idx += 1
            candidate = f"{base}_{idx}"
        return candidate

    def _materialize_ifexp(
        self,
        test_v: Tuple[str, Any],
        true_v: Tuple[str, Any],
        false_v: Tuple[str, Any],
        ctx_node: ast.AST,
    ) -> Tuple[str, str]:
        # Lower to boolean_select(condition, true, false).result
        comp_meta = self._require_component("boolean_select", ctx_node)
        node_id = self._unique_node_id("ifexp")
        self.nodes.append({"id": node_id, "type": "boolean_select", "params": {}})
        # Resolve inputs
        cond_node, cond_handle = self._resolve_value_handle(test_v, ctx_node)
        t_node, t_handle = self._resolve_value_handle(true_v, ctx_node)
        f_node, f_handle = self._resolve_value_handle(false_v, ctx_node)
        # Wire edges to named inputs
        self.edges.append(Edge(cond_node, cond_handle, node_id, "condition"))
        self.edges.append(Edge(t_node, t_handle, node_id, "true"))
        self.edges.append(Edge(f_node, f_handle, node_id, "false"))
        # Output is 'result'
        outs = comp_meta.get("outputs", [])
        # Extract IDs if outputs are dicts
        if outs and isinstance(outs[0], dict):
            out_ids = set(o.get("id", "") for o in outs)
        else:
            out_ids = set(outs)

        if "result" not in out_ids:
            # Fallback: if meta lists outputs but not named, choose first
            if outs and isinstance(outs[0], dict):
                out_handle = outs[0].get("id", "result")
            elif outs:
                out_handle = outs[0]
            else:
                out_handle = "result"
        else:
            out_handle = "result"
        return node_id, out_handle

    def _materialize_binop(
        self,
        op_type: type,
        left_v: Tuple[str, Any],
        right_v: Tuple[str, Any],
        ctx_node: ast.AST,
    ) -> Tuple[str, str]:
        """Materialize a binary operation node."""
        # Look up the operator component name
        comp_name = self._binary_op_map.get(op_type)
        if not comp_name:
            self._error(ctx_node, f"Unsupported binary operator: {op_type.__name__}")

        comp_meta = self._require_component(comp_name, ctx_node)
        node_id = self._unique_node_id(comp_name)
        self.nodes.append({"id": node_id, "type": comp_name, "params": {}})

        # Resolve inputs
        left_node, left_handle = self._resolve_value_handle(left_v, ctx_node)
        right_node, right_handle = self._resolve_value_handle(right_v, ctx_node)

        # Get input types for this operator
        input_types = self._get_input_types(comp_name)

        # Check type compatibility and insert casts if needed
        if "SLOT0" in input_types:
            src_type = self._get_node_output_type(left_node, left_handle)
            target_type = input_types["SLOT0"]
            left_node, left_handle = self._insert_type_cast(left_node, left_handle, src_type, target_type, ctx_node)

        if "SLOT1" in input_types:
            src_type = self._get_node_output_type(right_node, right_handle)
            target_type = input_types["SLOT1"]
            right_node, right_handle = self._insert_type_cast(right_node, right_handle, src_type, target_type, ctx_node)

        # Wire edges to inputs (SLOT0 and SLOT1 for binary operators)
        self.edges.append(Edge(left_node, left_handle, node_id, "SLOT0"))
        self.edges.append(Edge(right_node, right_handle, node_id, "SLOT1"))

        # Track output type for operators
        if comp_name in ("lt", "gt", "lte", "gte", "eq", "neq", "logical_and", "logical_or"):
            self.node_output_types[node_id] = {"result": "B"}
        elif comp_name in ("add", "sub", "mul", "div"):
            self.node_output_types[node_id] = {"result": "D"}

        # Output is typically 'result'
        outs = comp_meta.get("outputs", [])
        # Handle both string and dict outputs
        if outs and isinstance(outs[0], dict):
            out_handle = outs[0].get("id", "result")
        elif outs:
            out_handle = outs[0]
        else:
            out_handle = "result"
        return node_id, out_handle

    def _materialize_unaryop(
        self,
        op_type: type,
        operand_v: Tuple[str, Any],
        ctx_node: ast.AST,
    ) -> Tuple[str, str]:
        """Materialize a unary operation node."""
        # Look up the operator component name
        comp_name = self._unary_op_map.get(op_type)
        if not comp_name:
            self._error(ctx_node, f"Unsupported unary operator: {op_type.__name__}")

        if op_type == ast.USub:
            # Special case for negation: use (-1) * operand
            comp_meta = self._require_component("mul", ctx_node)
            node_id = self._unique_node_id("mul")
            self.nodes.append({"id": node_id, "type": "mul", "params": {}})

            # Create a number node with value -1
            minus_one_id = self._unique_node_id("number")
            self.nodes.append({"id": minus_one_id, "type": "number", "params": {"value": -1}})
            self.node_output_types[minus_one_id] = {"result": "D"}

            # Resolve operand
            operand_node, operand_handle = self._resolve_value_handle(operand_v, ctx_node)

            # Wire edges: (-1) * operand
            self.edges.append(Edge(minus_one_id, "result", node_id, "SLOT0"))
            self.edges.append(Edge(operand_node, operand_handle, node_id, "SLOT1"))

            # Track output type
            self.node_output_types[node_id] = {"result": "D"}
        else:
            comp_meta = self._require_component(comp_name, ctx_node)
            node_id = self._unique_node_id(comp_name)
            self.nodes.append({"id": node_id, "type": comp_name, "params": {}})

            # Resolve input
            operand_node, operand_handle = self._resolve_value_handle(operand_v, ctx_node)

            # Wire edge to input (SLOT for unary operators)
            self.edges.append(Edge(operand_node, operand_handle, node_id, "SLOT"))

            # Track output type
            if comp_name == "logical_not":
                self.node_output_types[node_id] = {"result": "B"}

        # Output is typically 'result'
        outs = comp_meta.get("outputs", [])
        # Handle both string and dict outputs
        if outs and isinstance(outs[0], dict):
            out_handle = outs[0].get("id", "result")
        elif outs:
            out_handle = outs[0]
        else:
            out_handle = "result"
        return node_id, out_handle

    def _materialize_number(self, value: Any, ctx_node: ast.AST) -> Tuple[str, str]:
        """Create a number(value=...) node for numeric literals used as inputs.

        Does not require 'number' to exist in the registry; assumes a single
        output handle named 'result'.
        """
        node_id = self._unique_node_id("number")
        self.nodes.append({"id": node_id, "type": "number", "params": {"value": value}})
        # Bind node id to its component type so it can be resolved by name
        self.var_to_binding[node_id] = "number"
        # Track output type
        self.node_output_types[node_id] = {"result": "D"}
        return node_id, "result"

    def _materialize_boolean(self, value: bool, ctx_node: ast.AST) -> Tuple[str, str]:
        """Create a bool_true or bool_false node for boolean literals used as inputs.

        Does not require these nodes to exist in the registry; assumes a single
        output handle named 'result'.
        """
        node_type = "bool_true" if value else "bool_false"
        node_id = self._unique_node_id(node_type)
        self.nodes.append({"id": node_id, "type": node_type, "params": {}})
        # Bind node id to its component type so it can be resolved by name
        self.var_to_binding[node_id] = node_type
        # Track output type
        self.node_output_types[node_id] = {"result": "B"}
        return node_id, "result"

    def _materialize_text(self, value: str, ctx_node: ast.AST) -> Tuple[str, str]:
        """Create a text(value=...) node for string literals used as inputs.

        Does not require 'text' to exist in the registry; assumes a single
        output handle named 'result'.
        """
        node_id = self._unique_node_id("text")
        self.nodes.append({"id": node_id, "type": "text", "params": {"value": value}})
        # Bind node id to its component type so it can be resolved by name
        self.var_to_binding[node_id] = "text"
        # Track output type (text is String type)
        self.node_output_types[node_id] = {"result": "S"}
        return node_id, "result"

    def _materialize_null(self, ctx_node: ast.AST) -> Tuple[str, str]:
        """Create a null node for None literals used as inputs.

        Does not require 'null' to exist in the registry; assumes a single
        output handle named 'result'.
        """
        node_id = self._unique_node_id("null")
        self.nodes.append({"id": node_id, "type": "null", "params": {}})
        # Bind node id to its component type so it can be resolved by name
        self.var_to_binding[node_id] = "null"
        # Track output type (null is Any type)
        self.node_output_types[node_id] = {"result": "A"}
        return node_id, "result"

    @staticmethod
    def _normalize_handle_id(handle: str, idx: Optional[int] = None) -> str:
        if isinstance(handle, str) and handle.startswith("*"):
            suffix = handle[1:]
            if suffix == "":
                return "SLOT"
            if suffix.isdigit():
                return "SLOT" + suffix
        if handle == "" and idx is not None:
            return "SLOT" if idx == 0 else f"SLOT{idx}"
        return handle

    def _resolve_attribute_handle(self, attr_node: ast.AST, ctx_node: ast.AST) -> Tuple[str, str]:
        if not isinstance(attr_node, ast.Attribute):
            self._error(ctx_node, "Left side must be attribute handle")
        var, handle = self._attribute_to_tuple(attr_node)
        return self._resolve_handle(var, handle, ctx_node)

    def _resolve_handle(self, var: str, handle: str, ctx_node: ast.AST) -> Tuple[str, str]:
        # Check if var is bound to a node.handle
        ref = self.var_to_binding.get(var)
        if ref and "." in ref:
            # Variable is bound to a node.handle, but user is trying to access another handle
            # This is likely an error - you can't access handles on handles
            self._error(ctx_node, f"Cannot access handle '{handle}' on '{var}' which is already bound to '{ref}'")
        
        # Otherwise, var should be a node name
        if var not in self.var_to_binding:
            # Maybe it's a direct node reference
            if any(n.get("id") == var for n in self.nodes):
                comp_type = next(n.get("type") for n in self.nodes if n.get("id") == var)
                comp_meta = self._require_component(comp_type, ctx_node)
            else:
                self._error(ctx_node, f"Unknown node '{var}'")
        else:
            comp_name = self.var_to_binding[var]
            comp_meta = self._require_component(comp_name, ctx_node)
        
        # Extract just the IDs from outputs and inputs (they might be dicts)
        outputs = comp_meta.get("outputs", []) or []
        inputs = comp_meta.get("inputs", []) or []

        # Handle both string lists and dict lists
        if outputs and isinstance(outputs[0], dict):
            outs = set(o.get("id", "") for o in outputs)
        else:
            outs = set(outputs)

        if inputs and isinstance(inputs[0], dict):
            # Handle SLOT naming for inputs
            ins = set()
            for inp in inputs:
                input_id = inp.get("id", "")
                if input_id.startswith("*"):
                    suffix = input_id[1:]
                    input_id = "SLOT" if suffix == "" else f"SLOT{suffix}"
                ins.add(input_id)
        else:
            ins = set(inputs)
        # We don't know direction here; correctness is enforced where used
        if handle not in outs and handle not in ins:
            self._error(ctx_node, f"Unknown handle '{handle}' on '{var}'")
        return var, handle

    def _get_node_output_type(self, node_id: str, handle: str) -> str:
        """Get the output type of a specific node handle."""
        # Check tracked output types
        if node_id in self.node_output_types:
            types = self.node_output_types[node_id]
            # Debug: print what we're getting
            # print(f"DEBUG: node_id={node_id}, handle={handle}, type(handle)={type(handle)}, types={types}, type(types)={type(types)}")
            # Ensure types is a dict before checking handle
            if isinstance(types, dict):
                if handle in types:
                    return types[handle]

        # Check if it's a known node type
        for node in self.nodes:
            if node.get("id") == node_id:
                node_type = node.get("type")
                output_types = self._get_output_types(node_type)
                if handle in output_types:
                    return output_types[handle]

                # Special cases for operators
                if node_type in ("lt", "gt", "lte", "gte", "eq", "neq", "logical_and", "logical_or", "logical_not"):
                    return "B"  # Boolean output
                elif node_type in ("add", "sub", "mul", "div"):
                    return "D"  # Decimal output
                elif node_type == "number":
                    return "D"  # Number literals are decimal
                elif node_type in ("bool_true", "bool_false"):
                    return "B"  # Boolean literals
                elif node_type == "text":
                    return "S"  # Text literals are String type
                elif node_type == "null":
                    return "A"  # Null literals are Any type

        # Default to Any if unknown
        return "A"

    def _wire_inputs(self, node_id: str, comp_meta: Dict[str, Any], args: List[Tuple[str, Any]], kwargs: Dict[str, Tuple[str, Any]], ctx_node: ast.AST) -> None:
        # Extract input IDs from input metadata if they're dicts
        inputs = comp_meta.get("inputs", []) or []
        if inputs and isinstance(inputs[0], dict):
            input_ids = [inp.get("id", "") for inp in inputs]
        else:
            input_ids = inputs
        ordered_inputs = [self._normalize_handle_id(h, idx=i) for i, h in enumerate(input_ids)]

        # Get the component name for type lookups
        comp_name = None
        for node in self.nodes:
            if node.get("id") == node_id:
                comp_name = node.get("type")
                break

        # Get input types for this component
        input_types = self._get_input_types(comp_name) if comp_name else {}

        # Keyword mapping to named handles when provided
        for name, v in kwargs.items():
            src_node, src_handle = self._resolve_value_handle(v, ctx_node)
            # Validate input name exists (accept star-normalized synonyms)
            valid_names = set(ordered_inputs)
            if name not in valid_names:
                self._error(ctx_node, f"Unknown input handle '{name}' for '{node_id}'")

            # Check type compatibility and insert cast if needed
            if name in input_types:
                src_type = self._get_node_output_type(src_node, src_handle)
                target_type = input_types[name]
                src_node, src_handle = self._insert_type_cast(src_node, src_handle, src_type, target_type, ctx_node)

            self.edges.append(Edge(src_node, src_handle, node_id, name))

        # Positional mapping
        if args:
            # Skip validation for components with 0 inputs (like gap_analysis)
            # These are typically transformer tasks that don't need input validation
            if len(ordered_inputs) == 0:
                # For 0-input components, ignore positional arguments
                # This handles cases like: gap_analysis = gap_classify(fill_percent=100)(src)
                # where the component has no declared inputs but is called with arguments
                pass
            else:
                # Check if single input allows multiple connections (like SLOT)
                allows_multiple = self._allows_multiple_connections(comp_name) if comp_name else False

                # Validate arg count (unless allowMultipleConnections is true)
                if len(args) > len(ordered_inputs) and not allows_multiple:
                    self._error(ctx_node, f"Too many positional inputs for '{node_id}'")

                # Wire all args
                multi_input = len(ordered_inputs) > 1
                for idx, v in enumerate(args):
                    src_node, src_handle = self._resolve_value_handle(v, ctx_node)

                    # If single input with allowMultipleConnections, reuse that input for all args
                    if allows_multiple and len(ordered_inputs) == 1:
                        declared = ordered_inputs[0]
                    else:
                        declared = ordered_inputs[idx] if idx < len(ordered_inputs) else None
                        if declared is None:
                            self._error(ctx_node, f"Missing declared input for positional index {idx} on '{node_id}'")
                    # If declared handle is SLOT/SLOT{n}, use that; otherwise use declared named handle
                    if declared.startswith("SLOT"):
                        dst_handle = declared if multi_input else "SLOT"
                    else:
                        dst_handle = declared

                    # Check type compatibility and insert cast if needed
                    if dst_handle in input_types:
                        src_type = self._get_node_output_type(src_node, src_handle)
                        target_type = input_types[dst_handle]
                        src_node, src_handle = self._insert_type_cast(src_node, src_handle, src_type, target_type, ctx_node)

                    self.edges.append(Edge(src_node, src_handle, node_id, dst_handle))


def parse_python_algorithm_to_graph(
    source: str,
    registry: Dict[str, Any],
    transforms_list: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Public API: compile Pythonic algorithm source to nodes/edges using registry.

    Args:
        source: Algorithm source code
        registry: Transform registry dict
        transforms_list: Optional list of transform metadata dicts for type checking

    Returns {"nodes": [...], "edges": [...]} with edges as dicts.
    """
    compiler = AlgorithmAstCompiler(registry, transforms_list)
    return compiler.compile(source)


def compile_algorithm(
    source: str,
    registry: Optional[Dict[str, Any]] = None,
    transforms_list: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to compile algorithm Python code with automatic registry loading.

    Args:
        source: Raw algorithm Python code
        registry: Optional registry dict. If None, loads from transform_registry
        transforms_list: Optional list of transform metadata dicts for type checking.
                        If not provided, the compiler will skip type validation features
                        that depend on transform metadata.

    Returns:
        Algorithm graph dict with nodes and edges, or None if source is empty
    """
    source = source.strip()
    if not source:
        return None

    # Load registry if not provided
    reg = registry or build_core_transform_registry_or_none()
    if not reg:
        raise RuntimeError(
            "Transform registry unavailable. Cannot compile algorithm without registry. "
            "Please ensure the registry is properly initialized."
        )

    compiler = AlgorithmAstCompiler(reg, transforms_list)
    return compiler.compile(source)


__all__ = ["parse_python_algorithm_to_graph", "AlgorithmAstCompiler", "compile_algorithm"]


