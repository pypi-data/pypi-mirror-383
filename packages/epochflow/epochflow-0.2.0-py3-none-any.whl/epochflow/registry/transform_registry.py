"""
Transforms-only registry builder with stable versioning.

This module creates a canonical manifest of transform components for use by
the Pythonic algorithm AST compiler and other validators. The manifest is
reduced to only the fields required for compilation and validation to ensure
stability and deterministic hashing.
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Any, Optional, Callable

# Optional import - for compatibility with EpochAI parent project
_TRANSFORMS_LIST = None
_TRANSFORMS_LOADER = None

try:
    from common.data_utils.doc import TRANSFORMS_LIST as _TRANSFORMS_LIST
except ImportError:
    pass  # Not running within EpochAI - will need to provide transforms_list explicitly


def _canonicalize(obj: Any) -> Any:
    """Return a canonicalized JSON structure (sorted keys, compact separators).

    This ensures deterministic hashing across runs and environments.
    """
    return json.loads(json.dumps(obj, sort_keys=True, separators=(",", ":")))


def _compute_registry_version(manifest: Dict[str, Any]) -> str:
    """Compute a stable version hash for a given manifest.

    Uses SHA-256 of the canonicalized JSON and prefixes with "tr-".
    """
    canonical = json.dumps(_canonicalize(manifest), sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    return f"tr-{digest[:12]}"


def build_transform_registry(transforms_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a minimal transforms registry from a raw TRANSFORMS_LIST.

    The resulting structure is:
    {
      "version": "tr-<hash>",
      "manifest": {
        "components": {
          <component_id>: {
            "id": <component_id>,
            "inputs": [<input_id0>, <input_id1>, ...],  # in declared order
            "outputs": [<output_id0>, <output_id1>, ...],
            "flags": {
              "requiresTimeFrame": <bool>,
              "isCrossSectional": <bool>,
              "atLeastOneInputRequired": <bool>
            }
          },
          ...
        }
      }
    }
    """
    components: Dict[str, Dict[str, Any]] = {}
    for t in transforms_list:
        component_id = t.get("id")
        if not component_id:
            # Skip malformed entries without an id
            continue

        inputs = [i.get("id") for i in (t.get("inputs", []) or []) if i.get("id")]
        outputs = [o.get("id") for o in (t.get("outputs", []) or []) if o.get("id")]

        option_ids = []
        for opt in t.get("options", []) or []:
            oid = opt.get("id")
            if oid:
                option_ids.append(oid)

        components[component_id] = {
            "id": component_id,
            "inputs": inputs,
            "outputs": outputs,
            "options": option_ids,
            "flags": {
                "requiresTimeFrame": bool(t.get("requiresTimeFrame") or t.get("requiresTimeframe")),
                "isCrossSectional": bool(t.get("isCrossSectional")),
                "atLeastOneInputRequired": bool(t.get("atLeastOneInputRequired")),
            },
        }

    manifest = {"components": _canonicalize(components)}
    version = _compute_registry_version(manifest)
    return {"version": version, "manifest": manifest}


def set_transforms_loader(loader: Callable[[], List[Dict[str, Any]]]) -> None:
    """Set a custom loader function for transforms metadata.

    This allows external applications to provide their own transforms source
    without depending on the EpochAI common module.

    Args:
        loader: A callable that returns a list of transform metadata dictionaries

    Example:
        >>> def my_loader():
        ...     return requests.get("https://api.example.com/transforms").json()
        >>> set_transforms_loader(my_loader)
    """
    global _TRANSFORMS_LOADER
    _TRANSFORMS_LOADER = loader


def set_transforms_list(transforms: List[Dict[str, Any]]) -> None:
    """Set the transforms list directly.

    This allows external applications to provide transforms metadata directly
    without depending on the EpochAI common module.

    Args:
        transforms: List of transform metadata dictionaries

    Example:
        >>> import json
        >>> with open("transforms.json") as f:
        ...     transforms = json.load(f)
        >>> set_transforms_list(transforms)
    """
    global _TRANSFORMS_LIST
    _TRANSFORMS_LIST = transforms


def _get_transforms_list() -> Optional[List[Dict[str, Any]]]:
    """Internal helper to get transforms list from various sources."""
    # Try custom loader first
    if _TRANSFORMS_LOADER is not None:
        try:
            return _TRANSFORMS_LOADER()
        except Exception:
            pass

    # Fall back to module-level import (EpochAI compatibility)
    return _TRANSFORMS_LIST


def build_core_transform_registry_or_none() -> Optional[Dict[str, Any]]:
    """Attempt to build a registry from available transforms metadata.

    Returns None if transforms cannot be loaded or is empty.

    Tries in order:
    1. Custom loader set via set_transforms_loader()
    2. Direct list set via set_transforms_list()
    3. EpochAI common.data_utils.doc.TRANSFORMS_LIST (if available)
    """
    transforms = _get_transforms_list()
    if transforms is None:
        return None
    if not transforms:
        # Empty list means API call likely failed
        return None
    return build_transform_registry(transforms)


def get_transform_registry(transforms_list: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Get the transform registry for use in parsing.

    Args:
        transforms_list: Optional explicit list of transforms. If not provided,
                        will attempt to load from configured sources.

    Returns:
        Registry dictionary with version and manifest

    Raises:
        ImportError: If transforms cannot be loaded from any source
    """
    if transforms_list is not None:
        return build_transform_registry(transforms_list)

    transforms = _get_transforms_list()
    if transforms is None:
        raise ImportError(
            "No transforms metadata available. Either:\n"
            "1. Call set_transforms_list() with your transforms data\n"
            "2. Call set_transforms_loader() with a loader function\n"
            "3. Ensure common.data_utils.doc.TRANSFORMS_LIST is available"
        )
    return build_transform_registry(transforms)


def get_transforms_list() -> Optional[List[Dict[str, Any]]]:
    """Get the raw transforms list for passing to the compiler.

    Returns None if transforms cannot be loaded from any source.
    This is useful for type checking and validation features in the compiler.
    """
    return _get_transforms_list()


__all__ = [
    "build_transform_registry",
    "build_core_transform_registry_or_none",
    "get_transform_registry",
    "get_transforms_list",
    "set_transforms_loader",
    "set_transforms_list",
]


