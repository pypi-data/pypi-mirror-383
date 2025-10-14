
from __future__ import annotations
from typing import Optional
from .design import SurveyDesign
from .glm import SurveyGLM

def survey_glm_domain(design: SurveyDesign, formula: str, *, family: str="gaussian",
                      domain: Optional[str]=None, zero_outside: bool=True,
                      variance: str="replicate", replicates: tuple|None=None,
                      max_iter: int=100, tol: float=1e-8) -> SurveyGLM:
    """
    Fit a SurveyGLM on a subpopulation. If zero_outside=True, keep full design and zero weights outside domain.
    """
    if domain:
        d = design.copy()
        m = d.df.eval(domain).astype(bool)
        if zero_outside:
            col = d.weight or "__w__"
            w = d.weights.copy()
            w[~m] = 0.0
            d.df[col] = w; d.weight = col
        else:
            d.df = d.df.loc[m].copy()
    else:
        d = design
    glm = SurveyGLM(formula, family=family, variance=variance, replicates=replicates, max_iter=max_iter, tol=tol).fit(d)
    return glm
