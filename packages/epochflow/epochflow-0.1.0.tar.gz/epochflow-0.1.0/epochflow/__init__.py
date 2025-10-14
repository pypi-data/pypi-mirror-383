"""
EpochFlow - Algorithm Graph Compiler for DataFlow Execution

Compiles Python-like algorithm specifications into nodes/edges graphs
for the EpochStratifyX DataFlowRuntimeOrchestrator.

This package provides the core compiler infrastructure that transforms
constrained Python syntax into dataflow graph representations that can
be executed by the C++ backend.
"""

from epochflow.compiler import compile_algorithm, AlgorithmCompiler
from epochflow.registry import (
    TransformRegistry,
    build_transform_registry,
    get_transforms_list,
    set_transforms_list,
    set_transforms_loader,
)
from epochflow.syntax import STRATEGY_BUILDER_RULE, QUANT_RESEARCHER_RULE

__version__ = "0.1.0"
__all__ = [
    "compile_algorithm",
    "AlgorithmCompiler",
    "TransformRegistry",
    "build_transform_registry",
    "get_transforms_list",
    "set_transforms_list",
    "set_transforms_loader",
    "STRATEGY_BUILDER_RULE",
    "QUANT_RESEARCHER_RULE"
]
