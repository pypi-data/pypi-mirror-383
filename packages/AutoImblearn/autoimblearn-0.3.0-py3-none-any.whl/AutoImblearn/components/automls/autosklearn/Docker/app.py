import logging
import shutil
import autosklearn.classification
from autosklearn.metrics import f1_macro, roc_auc

from AutoImblearn.components.api import BaseEstimatorAPI


class RunAutoSklearnAPI(BaseEstimatorAPI):
    """Auto-sklearn AutoML API following the standardized BaseEstimatorAPI pattern."""

    def __init__(self, import_name):
        super().__init__(import_name)
        self.automl_model = None
        self.result_metric = None

    def fit(self, args, X_train, y_train, X_test, y_test):
        """
        Train Auto-sklearn AutoML model.

        Args:
            args: Parameters including metric, model settings
            X_train: Training features
            y_train: Training labels
            X_test: Test features (for evaluation)
            y_test: Test labels (for evaluation)

        Returns:
            Fitted Auto-sklearn model
        """
        # Clean up /tmp folder for auto-sklearn
        shutil.rmtree('/tmp/autosklearn_classification_example_tmp', ignore_errors=True)

        # Set up Auto-sklearn based on metric
        if self.params.metric == "auroc":
            metric = roc_auc
        elif self.params.metric == "macro_f1":
            metric = f1_macro
        else:
            raise ValueError(f"Metric {self.params.metric} not supported for Auto-sklearn")

        # Create Auto-sklearn classifier
        model = autosklearn.classification.AutoSklearnClassifier(
            time_left_for_this_task=300,  # 5 minutes total
            per_run_time_limit=30,
            tmp_folder="/tmp/autosklearn_classification_example_tmp",
            metric=metric,
            resampling_strategy="cv",
            resampling_strategy_arguments={"folds": 5},  # Reduced for speed
            ensemble_size=1,  # Faster ensemble
            seed=42
        )

        # Train the model
        logging.info(f"Starting Auto-sklearn training with metric={self.params.metric}...")
        model.fit(X_train, y_train)
        logging.info("✓ Auto-sklearn training complete")

        # Print statistics
        logging.info(f"Auto-sklearn statistics:\n{model.sprint_statistics()}")

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
            # Auto-sklearn's roc_auc metric expects (y_true, y_pred_proba)
            result = roc_auc(y_test, y_proba)
            logging.info(f"✓ Auto-sklearn AUROC: {result:.4f}")
            return result
        elif self.params.metric == "macro_f1":
            y_pred = self.fitted_model.predict(X_test)
            # Auto-sklearn's f1_macro metric expects (y_true, y_pred)
            result = f1_macro(y_test, y_pred)
            logging.info(f"✓ Auto-sklearn F1 Score: {result:.4f}")
            return result
        else:
            raise ValueError(f"Metric {self.params.metric} not supported")


if __name__ == '__main__':
    RunAutoSklearnAPI(__name__).run()
