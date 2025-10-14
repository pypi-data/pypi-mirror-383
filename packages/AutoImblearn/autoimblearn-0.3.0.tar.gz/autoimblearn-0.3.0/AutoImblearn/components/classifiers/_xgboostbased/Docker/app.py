import logging

import numpy as np
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

from xgboost import XGBClassifier

from AutoImblearn.components.api import BaseEstimatorAPI

clfs = {
    "ensemble": XGBClassifier(learning_rate=1.0, max_depth=10, min_child_weight=15, n_estimators=100, n_jobs=1, subsample=0.8, verbosity=0),
}

hyperparameter_search_space = {
    "ensemble": {
        "learning_rate": {
            "type": "float",
            "min": 0.01,
            "max": 1.0,
            "default": 1.0,
            "log_scale": True
        },
        "max_depth": {
            "type": "int",
            "min": 1,
            "max": 20,
            "default": 10
        },
        "min_child_weight": {
            "type": "int",
            "min": 1,
            "max": 30,
            "default": 15
        },
        "n_estimators": {
            "type": "int",
            "min": 10,
            "max": 1000,
            "default": 100
        },
        "subsample": {
            "type": "float",
            "min": 0.5,
            "max": 1.0,
            "default": 0.8
        },
        "colsample_bytree": {
            "type": "float",
            "min": 0.5,
            "max": 1.0,
            "default": 1.0
        },
        "gamma": {
            "type": "float",
            "min": 0.0,
            "max": 5.0,
            "default": 0.0
        },
        "reg_alpha": {
            "type": "float",
            "min": 0.0,
            "max": 5.0,
            "default": 0.0
        },
        "reg_lambda": {
            "type": "float",
            "min": 0.0,
            "max": 5.0,
            "default": 1.0
        },
        "n_jobs": {
            "type": "int",
            "min": 1,
            "max": 16,
            "default": 1
        },
        "verbosity": {
            "type": "categorical",
            "choices": [0, 1, 2, 3],
            "default": 0
        }
    }
}

class RunXGBoostClassifierAPI(BaseEstimatorAPI):

    def __init__(self, import_name):
        super().__init__(import_name)
        self.clf_name = None
        self.result_metric = None  # Store the computed metric result
        self.param_space = hyperparameter_search_space

    def get_hyperparameter_search_space(self):
        clf = self.params.model
        return self.param_space.get(clf, {})

    def _validate_kwargs(self, clf_name: str, kwargs: dict):
        """Validate that provided hyperparameters are allowed for this classifier."""
        if clf_name not in self.param_space:
            return
        allowed = set(self.param_space[clf_name].keys())
        unknown = set(kwargs) - allowed
        if unknown:
            raise ValueError(
                f"Unsupported parameters for '{clf_name}': {sorted(unknown)}. "
                f"Allowed: {sorted(allowed)}"
            )

    def _get_default_params(self, clf_name: str) -> dict:
        """Get default hyperparameters for a classifier."""
        if clf_name not in self.param_space:
            return {}

        defaults = {}
        for param_name, param_config in self.param_space[clf_name].items():
            if 'default' in param_config:
                defaults[param_name] = param_config['default']
        return defaults

    def fit(self, args, X_train, y_train, X_test, y_test):
        clf_name = self.params.model
        self.clf_name = clf_name

        # Get hyperparameters from params (if provided)
        try:
            clf_kwargs = self.params.params if hasattr(self.params, 'params') and self.params.params else {}
        except AttributeError:
            clf_kwargs = {}

        # Validate hyperparameters
        self._validate_kwargs(clf_name, clf_kwargs)

        # Merge with defaults
        final_params = {**self._get_default_params(clf_name), **clf_kwargs}

        # Instantiate classifier with hyperparameters
        if clf_name == "ensemble":
            classifier = XGBClassifier(random_state=42, **final_params)
        else:
            # Fallback to old hardcoded dict
            if clf_name in clfs.keys():
                classifier = clfs[clf_name]
            else:
                raise Exception(f"Classifier '{clf_name}' not defined")

        logging.info(f"Training {clf_name} with params: {final_params}")
        classifier.fit(X_train, y_train)
        logging.info("finished classifier training")

        # Compute the metric and store it as result
        # Use classifier directly (not yet in self.fitted_model)
        self.fitted_model = classifier  # Temporarily set for predict() to work
        self.result_metric = self.predict(X_test, y_test)
        self.result = self.result_metric

        # RETURN the fitted model (sklearn pattern!)
        # Base class will assign it to self.fitted_model and save to disk
        return classifier

    def predict(self, X_test, y_test):
        """Predict and compute metric on test data"""
        # Base class ensures self.fitted_model is loaded - no checking needed!

        if self.params.metric == "auroc":
            y_proba = self.fitted_model.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(y_test, y_proba)
            return auroc
        elif self.params.metric == "macro_f1":
            y_pred = self.fitted_model.predict(X_test)
            _, _, f1, _ = (
                precision_recall_fscore_support(y_test, y_pred, average='macro'))
            return f1
        else:
            error_message = "Metric {} is not supported in {} yet".format(self.params.metric, self.clf_name)
            logging.error(error_message)
            raise ValueError(error_message)


if __name__ == '__main__':
    RunXGBoostClassifierAPI(__name__).run()
