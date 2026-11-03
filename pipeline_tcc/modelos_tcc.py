"""Envoltório do CatBoost compatível com a clonagem do scikit-learn (usado na busca em grade)."""
from sklearn.base import BaseEstimator, RegressorMixin
from catboost import CatBoostRegressor


class CatBoostCategorico(RegressorMixin, BaseEstimator):
    def __init__(self, cat_features=None, iterations=500, learning_rate=0.03, depth=6, random_seed=42, thread_count=2):
        self.cat_features = cat_features
        self.iterations = iterations
        self.learning_rate = learning_rate
        self.depth = depth
        self.random_seed = random_seed
        self.thread_count = thread_count

    def fit(self, X, y):
        self.model_ = CatBoostRegressor(iterations=self.iterations, learning_rate=self.learning_rate, depth=self.depth,
                                        random_seed=self.random_seed, thread_count=self.thread_count, verbose=0,
                                        cat_features=list(self.cat_features))
        self.model_.fit(X, y)
        return self

    def predict(self, X):
        return self.model_.predict(X)
