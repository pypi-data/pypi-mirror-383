import pandas as pd
from topsisx.ahp import ahp
from topsisx.entropy import entropy_weights
from topsisx.topsis import topsis
from topsisx.vikor import vikor

class DecisionPipeline:
    def __init__(self, weights="entropy", method="topsis"):
        self.weights_method = weights.lower()
        self.ranking_method = method.lower()

    def compute_weights(self, df: pd.DataFrame, pairwise_matrix=None):
        if self.weights_method == "ahp":
            return ahp(pairwise_matrix)
        elif self.weights_method == "entropy":
            return entropy_weights(df)
        elif self.weights_method == "equal":
            return [1 / df.shape[1]] * df.shape[1]
        else:
            raise ValueError(f"Unsupported weight method: {self.weights_method}")

    def run(self, df: pd.DataFrame, impacts=None, pairwise_matrix=None):
        weights = self.compute_weights(df, pairwise_matrix)

        if self.ranking_method == "topsis":
            return topsis(df, weights, impacts)
        elif self.ranking_method == "vikor":
            return vikor(df, weights, impacts)
        elif self.ranking_method == "ahp":
            return ahp(pairwise_matrix if pairwise_matrix is not None else df)
        else:
            raise ValueError(f"Unsupported ranking method: {self.ranking_method}")
