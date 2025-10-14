import logging
from tpot import TPOTClassifier
from sklearn.metrics import roc_auc_score, f1_score

from AutoImblearn.components.api import BaseEstimatorAPI


class RunTPOTAPI(BaseEstimatorAPI):
    """TPOT AutoML API following the standardized BaseEstimatorAPI pattern."""

    def __init__(self, import_name):
        super().__init__(import_name)
        self.tpot_model = None
        self.result_metric = None

    def fit(self, args, X_train, y_train, X_test, y_test):
        """
        Train TPOT AutoML model.

        Args:
            args: Parameters including metric, model settings
            X_train: Training features
            y_train: Training labels
            X_test: Test features (for evaluation)
            y_test: Test labels (for evaluation)

        Returns:
            Fitted TPOT model
        """
        # Set up TPOT based on metric
        if self.params.metric == "auroc":
            scoring = 'roc_auc'
        elif self.params.metric == "macro_f1":
            scoring = 'f1_macro'
        else:
            raise ValueError(f"Metric {self.params.metric} not supported for TPOT")

        # Create TPOT classifier
        model = TPOTClassifier(
            generations=5,
            population_size=50,
            verbosity=2,
            random_state=42,
            scoring=scoring,
            max_time_mins=5,  # 5 minutes max
            n_jobs=1
        )

        # Train the model
        logging.info(f"Starting TPOT AutoML training with metric={scoring}...")
        model.fit(X_train, y_train)
        logging.info("✓ TPOT AutoML training complete")

        self.tpot_model = model

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
            y_proba = self.fitted_model.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(y_test, y_proba)
            logging.info(f"✓ TPOT AUROC: {auroc:.4f}")
            return auroc
        elif self.params.metric == "macro_f1":
            # Use TPOT's built-in score method which returns the configured metric
            score = self.fitted_model.score(X_test, y_test)
            logging.info(f"✓ TPOT F1 Score: {score:.4f}")
            return score
        else:
            raise ValueError(f"Metric {self.params.metric} not supported")


if __name__ == '__main__':
    RunTPOTAPI(__name__).run()
