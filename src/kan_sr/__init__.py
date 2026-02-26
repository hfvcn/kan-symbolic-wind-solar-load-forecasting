"""
KAN-SR training and analysis utilities.

This package contains the Phase 2+ pipeline:
- Loading processed Parquet splits produced by Phase 1
- Building KAN datasets (torch tensors)
- Training with composite regularization + checkpointing
- Sparsity/pruning reports used downstream for symbolic extraction and evaluation
"""

from __future__ import annotations

__all__ = [
    "dataset",
    "metrics",
    "sparsity",
]

