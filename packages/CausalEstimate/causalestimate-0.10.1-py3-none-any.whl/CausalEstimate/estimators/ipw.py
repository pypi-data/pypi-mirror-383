import pandas as pd

from CausalEstimate.estimators.base import BaseEstimator
from CausalEstimate.estimators.functional.ipw import (
    compute_ipw_ate,
    compute_ipw_att,
    compute_ipw_risk_ratio,
    compute_ipw_risk_ratio_treated,
)


class IPW(BaseEstimator):
    def __init__(
        self,
        effect_type="ATE",
        treatment_col="treatment",
        outcome_col="outcome",
        ps_col="ps",
        clip_percentile: float = 1,
        eps: float = 1e-9,
    ):
        """
        Inverse Probability Weighting estimator.

        Args:
            effect_type: Type of causal effect to estimate
            treatment_col: Name of treatment column
            outcome_col: Name of outcome column
            ps_col: Name of propensity score column
            clip_percentile: percentile to clip the weights at
            eps: Small constant for numerical stability in denominators
        """
        # Initialize base class with core parameters
        super().__init__(
            effect_type=effect_type,
            treatment_col=treatment_col,
            outcome_col=outcome_col,
            ps_col=ps_col,
        )
        self.clip_percentile = clip_percentile
        self.eps = eps

    def _compute_effect(self, df: pd.DataFrame) -> dict:
        """Calculate causal effect using IPW."""
        A, Y, ps = self._get_numpy_arrays(
            df, [self.treatment_col, self.outcome_col, self.ps_col]
        )

        if self.effect_type in ["ATE", "ARR"]:
            return compute_ipw_ate(
                A, Y, ps, clip_percentile=self.clip_percentile, eps=self.eps
            )
        elif self.effect_type == "ATT":
            return compute_ipw_att(
                A, Y, ps, clip_percentile=self.clip_percentile, eps=self.eps
            )
        elif self.effect_type == "RR":
            return compute_ipw_risk_ratio(
                A, Y, ps, clip_percentile=self.clip_percentile, eps=self.eps
            )
        elif self.effect_type == "RRT":
            return compute_ipw_risk_ratio_treated(
                A, Y, ps, clip_percentile=self.clip_percentile, eps=self.eps
            )
        else:
            raise ValueError(f"Effect type '{self.effect_type}' is not supported.")
