"""
Abstract base contracts for Query Transformation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
import pandas as pd

class Transformer(ABC):
    """An Transformer appends new columns to a DataFrame without mutating inputs.

    Contract:
      - Input: pd.DataFrame (query result) and params via kwargs
      - Output: New pd.DataFrame with appended columns; same index/rows expected
      - Must not drop/rename existing columns
    """

    @abstractmethod
    def transform(self, df: pd.DataFrame, **params: Any) -> pd.DataFrame:
        """Return a new DataFrame with appended columns; must not mutate input."""
        raise NotImplementedError
