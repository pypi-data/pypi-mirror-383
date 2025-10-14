"""
Pipeline wrappers for unsupervised learning.

Supports three types of unsupervised learning:
1. Clustering: KMeans, DBSCAN, Hierarchical, GMM, etc.
2. Dimensionality Reduction: PCA, t-SNE, UMAP, etc.
3. Anomaly Detection: IsolationForest, OneClassSVM, LOF, etc.
4. Survival Unsupervised: Survival clustering and risk stratification
"""

from AutoImblearn.components.unsupervised import (
    RunClusteringModel,
    RunDimensionalityReduction,
    RunAnomalyDetection
)
from AutoImblearn.components.survival import RunSurvivalUnsupervised

import logging
import numpy as np
import pandas as pd

# Clustering models - factory functions
clustering_models = {
    'kmeans': lambda **kw: RunClusteringModel(model='kmeans', **kw),
    'dbscan': lambda **kw: RunClusteringModel(model='dbscan', **kw),
    'hierarchical': lambda **kw: RunClusteringModel(model='hierarchical', **kw),
    'gmm': lambda **kw: RunClusteringModel(model='gmm', **kw),
    'meanshift': lambda **kw: RunClusteringModel(model='meanshift', **kw),
    'spectral': lambda **kw: RunClusteringModel(model='spectral', **kw),
}

# Dimensionality reduction models - factory functions
reduction_models = {
    'pca': lambda **kw: RunDimensionalityReduction(model='pca', **kw),
    'tsne': lambda **kw: RunDimensionalityReduction(model='tsne', **kw),
    'umap': lambda **kw: RunDimensionalityReduction(model='umap', **kw),
    'svd': lambda **kw: RunDimensionalityReduction(model='svd', **kw),
    'ica': lambda **kw: RunDimensionalityReduction(model='ica', **kw),
    'nmf': lambda **kw: RunDimensionalityReduction(model='nmf', **kw),
}

# Anomaly detection models - factory functions
anomaly_models = {
    'isoforest': lambda **kw: RunAnomalyDetection(model='isoforest', **kw),
    'ocsvm': lambda **kw: RunAnomalyDetection(model='ocsvm', **kw),
    'lof': lambda **kw: RunAnomalyDetection(model='lof', **kw),
    'elliptic': lambda **kw: RunAnomalyDetection(model='elliptic', **kw),
}

# Survival unsupervised models - factory functions
survival_unsupervised_models = {
    'survival_tree': lambda **kw: RunSurvivalUnsupervised(model='survival_tree', **kw),
    'survival_kmeans': lambda **kw: RunSurvivalUnsupervised(model='survival_kmeans', **kw),
}

# All unsupervised models combined
unsupervised_models = {
    **clustering_models,
    **reduction_models,
    **anomaly_models,
}


class CustomUnsupervisedModel:
    """
    Wrapper for unsupervised learning models (clustering, reduction, anomaly detection).

    Args:
        args: Arguments object with .path for data_folder and .metric for evaluation
    """

    def __init__(self, args):
        self.args = args
        self.data_folder = args.path
        self.model = None
        self.model_name = None
        self.model_type = None  # 'clustering', 'reduction', or 'anomaly'
        self.result = None

    def train(self, X_train: np.ndarray, Y_train: np.ndarray = None, model=None):
        """
        Train unsupervised model.

        Args:
            X_train: Training features
            Y_train: Optional labels (not used for training, only for evaluation)
            model: Model name (e.g., 'kmeans', 'pca', 'isoforest')
        """
        if model in unsupervised_models.keys():
            # Instantiate model with data_folder
            factory = unsupervised_models[model]
            self.model = factory(data_folder=self.data_folder)
            self.model_name = model

            # Determine model type
            if model in clustering_models:
                self.model_type = 'clustering'
            elif model in reduction_models:
                self.model_type = 'reduction'
            elif model in anomaly_models:
                self.model_type = 'anomaly'
            else:
                raise ValueError(f"Unknown unsupervised model: {model}")

        else:
            raise Exception("Unsupervised model {} not defined".format(model))

        # Fit model
        self.model.fit(X_train, Y_train)

    def predict(self, X_test: np.ndarray, Y_test: np.ndarray = None):
        """
        Make predictions and evaluate unsupervised model.

        Args:
            X_test: Test features
            Y_test: Optional ground truth labels (for evaluation)

        Returns:
            Evaluation metric based on args.metric
        """
        predictions = self.model.predict(X_test)

        # Evaluate based on metric
        if self.args.metric == "silhouette" and self.model_type == 'clustering':
            from sklearn.metrics import silhouette_score
            unique_labels = np.unique(predictions)
            if len(unique_labels) > 1:
                score = silhouette_score(X_test, predictions)
            else:
                score = 0.0

        elif self.args.metric == "calinski" and self.model_type == 'clustering':
            from sklearn.metrics import calinski_harabasz_score
            score = calinski_harabasz_score(X_test, predictions)

        elif self.args.metric == "davies_bouldin" and self.model_type == 'clustering':
            from sklearn.metrics import davies_bouldin_score
            score = davies_bouldin_score(X_test, predictions)
            # Lower is better, so negate for consistency
            score = -score

        elif self.args.metric == "reconstruction" and self.model_type == 'reduction':
            # Reconstruction error
            if hasattr(self.model, 'inverse_transform'):
                X_reconstructed = self.model.inverse_transform(predictions)
                score = -np.mean((X_test - X_reconstructed) ** 2)  # Negative MSE (higher is better)
            else:
                score = 0.0

        elif self.args.metric == "f1" and self.model_type == 'anomaly':
            # F1 score for anomaly detection (requires ground truth)
            if Y_test is not None:
                from sklearn.metrics import f1_score
                y_pred_binary = (predictions == -1).astype(int)
                score = f1_score(Y_test, y_pred_binary, zero_division=0)
            else:
                score = 0.0

        else:
            # Default: use the first available metric for the model type
            if self.model_type == 'clustering':
                from sklearn.metrics import silhouette_score
                unique_labels = np.unique(predictions)
                if len(unique_labels) > 1:
                    score = silhouette_score(X_test, predictions)
                else:
                    score = 0.0
            elif self.model_type == 'anomaly':
                # For anomaly detection, return anomaly ratio as default metric
                n_anomalies = np.sum(predictions == -1)
                score = n_anomalies / len(predictions)
            else:
                score = 0.0

        self.result = score

        logging.info(
            f"\t {self.model_type.capitalize()} Model: {self.model_name}, "
            f"Metric: {self.args.metric}, Score: {score:.4f}"
        )

        return score


class CustomSurvivalUnsupervisedModel:
    """
    Wrapper for survival unsupervised learning models.

    Args:
        args: Arguments object with .path for data_folder and .metric for evaluation
    """

    def __init__(self, args):
        self.args = args
        self.data_folder = args.path
        self.model = None
        self.model_name = None
        self.result = None

    def train(self, X_train: np.ndarray, Y_train: np.ndarray, model=None):
        """
        Train survival unsupervised model.

        Args:
            X_train: Training features
            Y_train: Structured survival array with 'Status' and 'Survival_in_days'
            model: Model name (e.g., 'survival_tree', 'survival_kmeans')
        """
        if model in survival_unsupervised_models.keys():
            # Instantiate model with data_folder
            factory = survival_unsupervised_models[model]
            self.model = factory(data_folder=self.data_folder)
            self.model_name = model
        else:
            raise Exception("Survival unsupervised model {} not defined".format(model))

        # Fit model
        self.model.fit(X_train, Y_train)

    def predict(self, X_test: np.ndarray, Y_test: np.ndarray):
        """
        Make predictions and evaluate survival unsupervised model.

        Args:
            X_test: Test features
            Y_test: Test survival data (structured array)

        Returns:
            Evaluation metric (log-rank statistic or other)
        """
        predictions = self.model.predict(X_test)

        # Evaluate using log-rank statistic for cluster separation
        if self.args.metric == "log_rank":
            try:
                from sksurv.compare import compare_survival

                # Group by cluster
                unique_clusters = np.unique(predictions)
                if len(unique_clusters) > 1:
                    cluster_groups = [Y_test[predictions == c] for c in unique_clusters]
                    chisq, pvalue = compare_survival(cluster_groups)
                    score = chisq  # Higher chi-square = better cluster separation
                else:
                    score = 0.0
            except Exception as e:
                logging.error(f"Log-rank test failed: {e}")
                score = 0.0

        elif self.args.metric == "silhouette":
            # Silhouette score on survival times
            from sklearn.metrics import silhouette_score
            survival_times = Y_test['Survival_in_days'].reshape(-1, 1)
            unique_clusters = np.unique(predictions)
            if len(unique_clusters) > 1:
                score = silhouette_score(survival_times, predictions)
            else:
                score = 0.0

        else:
            # Default: use log-rank statistic
            try:
                from sksurv.compare import compare_survival
                unique_clusters = np.unique(predictions)
                if len(unique_clusters) > 1:
                    cluster_groups = [Y_test[predictions == c] for c in unique_clusters]
                    chisq, pvalue = compare_survival(cluster_groups)
                    score = chisq
                else:
                    score = 0.0
            except:
                score = 0.0

        self.result = score

        logging.info(
            f"\t Survival Unsupervised Model: {self.model_name}, "
            f"Metric: {self.args.metric}, Score: {score:.4f}, "
            f"N_clusters: {len(np.unique(predictions))}"
        )

        return score
