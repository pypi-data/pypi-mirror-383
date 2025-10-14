import logging
import h2o
from h2o.sklearn import H2OAutoMLClassifier
from sklearn.metrics import roc_auc_score

from AutoImblearn.components.api import BaseEstimatorAPI


class RunH2OAPI(BaseEstimatorAPI):
    """H2O AutoML API following the standardized BaseEstimatorAPI pattern."""

    def __init__(self, import_name):
        super().__init__(import_name)
        self.automl_model = None
        self.result_metric = None

    def fit(self, args, X_train, y_train, X_test, y_test):
        """
        Train H2O AutoML model.

        Args:
            args: Parameters including metric, model settings
            X_train: Training features
            y_train: Training labels
            X_test: Test features (for evaluation)
            y_test: Test labels (for evaluation)

        Returns:
            Fitted H2O model
        """
        # Initialize H2O
        try:
            h2o.init(ip="localhost", port=54323)
            logging.info("✓ H2O initialized")
        except Exception as e:
            logging.warning(f"H2O already initialized or init failed: {e}")

        # Set up AutoML based on metric
        if self.params.metric == "auroc":
            model = H2OAutoMLClassifier(
                max_models=10,
                seed=42,
                sort_metric='auc',
                max_runtime_secs=300  # 5 minutes max
            )
        elif self.params.metric == "macro_f1":
            model = H2OAutoMLClassifier(
                max_models=10,
                seed=42,
                sort_metric='mean_per_class_error',
                max_runtime_secs=300
            )
        else:
            raise ValueError(f"Metric {self.params.metric} not supported for H2O AutoML")

        # Train the model
        logging.info("Starting H2O AutoML training...")
        model.fit(X_train, y_train)
        logging.info("✓ H2O AutoML training complete")

        self.automl_model = model

        # Compute metric on test data
        self.fitted_model = model  # Temporarily set for predict() to work
        self.result_metric = self.predict(X_test, y_test)
        self.result = self.result_metric

        # Return fitted model (BaseEstimatorAPI will save it)
        return model

    def predict(self, X_test, y_test):
        """
        Predict and compute metric on test data.

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Metric value (AUROC or F1)
        """
        if self.params.metric == "auroc":
            y_proba = self.fitted_model.predict_proba(X_test)
            # H2O returns dataframe, extract probability column
            if hasattr(y_proba, 'values'):
                y_proba = y_proba.values[:, 1] if y_proba.ndim > 1 else y_proba.values
            auroc = roc_auc_score(y_test, y_proba)
            logging.info(f"✓ H2O AUROC: {auroc:.4f}")
            return auroc
        elif self.params.metric == "macro_f1":
            # Use H2O's built-in score method
            score = self.fitted_model.score(X_test, y_test)
            logging.info(f"✓ H2O F1 Score: {score:.4f}")
            return score
        else:
            raise ValueError(f"Metric {self.params.metric} not supported")


if __name__ == '__main__':
    RunH2OAPI(__name__).run()
