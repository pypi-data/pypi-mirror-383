
from __future__ import annotations
import numpy as np, pandas as pd
from dataclasses import dataclass
from typing import Optional
from .exceptions import SurveyError

@dataclass
class SurveyDesign:
    df: pd.DataFrame
    weight: Optional[str]=None
    strata: Optional[str]=None
    psu: Optional[str]=None
    ssu: Optional[str]=None
    fpc_strata: Optional[str]=None
    fpc_psu: Optional[str]=None
    repweights: Optional[pd.DataFrame]=None

    def copy(self):
        return SurveyDesign(self.df.copy(), self.weight, self.strata, self.psu, self.ssu, self.fpc_strata, self.fpc_psu,
                            None if self.repweights is None else self.repweights.copy())

    @property
    def weights(self) -> pd.Series:
        if self.weight is None:
            return pd.Series(np.ones(len(self.df)), index=self.df.index, name="__w__")
        return self.df[self.weight].astype(float)

    def validate(self):
        if self.strata is not None and self.psu is not None:
            c = self.df.groupby(self.strata)[self.psu].nunique()
            if (c < 2).any():
                bad = c[c<2].index.tolist()
                raise SurveyError(f"Each stratum must have ≥2 PSUs for variance; failing strata: {bad}")
        if self.ssu is not None and self.psu is None:
            raise SurveyError("SSU provided but PSU missing. Provide both for two-stage designs.")
        return self

    def domain_mask(self, expr: Optional[str]):
        if not expr:
            return pd.Series(np.ones(len(self.df), dtype=bool), index=self.df.index)
        return self.df.eval(expr).astype(bool)

    def _S(self):
        return self.df[self.strata] if self.strata else pd.Series(1, index=self.df.index)
    def _P(self):
        return self.df[self.psu] if self.psu else pd.Series(np.arange(len(self.df)), index=self.df.index)
    def _Q(self):
        return self.df[self.ssu] if self.ssu else None
