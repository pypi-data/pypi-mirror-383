"""
EpochFlow Compiler Module

Parses Python AST and compiles to nodes/edges dataflow graph.
"""

from epochflow.compiler.ast_compiler import (
    compile_algorithm,
    parse_python_algorithm_to_graph,
    AlgorithmAstCompiler
)

# Aliases for convenience
parse_algorithm_to_graph = parse_python_algorithm_to_graph
AlgorithmCompiler = AlgorithmAstCompiler

__all__ = [
    "compile_algorithm",
    "parse_python_algorithm_to_graph",
    "parse_algorithm_to_graph",
    "AlgorithmAstCompiler",
    "AlgorithmCompiler"
]
