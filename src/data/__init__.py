"""
Data pipeline submodule for KAN-SR project.

This module provides functionality for:
- Downloading ARPA-E PERFORM data from S3 (download.py)
- Data preprocessing and cleaning (preprocess.py)
- Meteorological feature acquisition (meteorology.py)
- Feature engineering (features.py)
- Train/val/test splitting and normalization (split.py)
"""

__all__ = [
    "download",
    "preprocess",
    "meteorology",
    "features",
    "split",
]
