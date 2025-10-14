import logging

import numpy as np
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, classification_report, \
    average_precision_score

from AutoImblearn.components.api import BaseEstimatorAPI

clfs = {
    "lr": LogisticRegression(random_state=42, max_iter=500, solver='lbfgs'),
    "mlp": MLPClassifier(alpha=1, random_state=42, max_iter=1000),
    "ada": AdaBoostClassifier(random_state=42),
    "svm": svm.SVC(random_state=42, probability=True, kernel='linear'),
    # "SVM": svm.SVC(random_state=42, probability=True, kernel='poly'),
    # "rf": RandomForestClassifier(random_state=42),
    # "ensemble": XGBClassifier(learning_rate=1.0, max_depth=10, min_child_weight=15, n_estimators=100, n_jobs=1, subsample=0.8, verbosity=0),
    # "bst": GradientBoostingClassifier(random_state=42),
}

hyperparameter_search_space = {
    "lr": {
        "penalty": {
            "type": "categorical",
            "choices": ["l2", "l1", "elasticnet", "none"],
            "default": "l2"
        },
        "C": {
            "type": "float",
            "min": 0.01,
            "max": 10.0,
            "default": 1.0,
            "log_scale": True
        },
        "solver": {
            "type": "categorical",
            "choices": ["lbfgs", "liblinear", "saga", "newton-cg", "sag"],
            "default": "lbfgs"
        },
        "max_iter": {
            "type": "int",
            "min": 100,
            "max": 1000,
            "default": 500
        }
    },
    "mlp": {
        "hidden_layer_sizes": {
            "type": "categorical",
            "choices": [(50,), (100,), (100, 50), (100, 100)],
            "default": (100,)
        },
        "activation": {
            "type": "categorical",
            "choices": ["relu", "tanh", "logistic"],
            "default": "relu"
        },
        "solver": {
            "type": "categorical",
            "choices": ["adam", "sgd", "lbfgs"],
            "default": "adam"
        },
        "alpha": {
            "type": "float",
            "min": 1e-5,
            "max": 1.0,
            "default": 1.0,
            "log_scale": True
        },
        "learning_rate": {
            "type": "categorical",
            "choices": ["constant", "invscaling", "adaptive"],
            "default": "constant"
        },
        "max_iter": {
            "type": "int",
            "min": 200,
            "max": 2000,
            "default": 1000
        }
    },
    "ada": {
        "n_estimators": {
            "type": "int",
            "min": 10,
            "max": 1000,
            "default": 50
        },
        "learning_rate": {
            "type": "float",
            "min": 0.01,
            "max": 2.0,
            "default": 1.0,
            "log_scale": True
        },
        "algorithm": {
            "type": "categorical",
            "choices": ["SAMME", "SAMME.R"],
            "default": "SAMME.R"
        }
    },
    "svm": {
        "C": {
            "type": "float",
            "min": 0.01,
            "max": 10.0,
            "default": 1.0,
            "log_scale": True
        },
        "kernel": {
            "type": "categorical",
            "choices": ["linear", "poly", "rbf", "sigmoid"],
            "default": "linear"
        },
        "degree": {
            "type": "int",
            "min": 2,
            "max": 5,
            "default": 3  # used in poly kernel
        },
        "gamma": {
            "type": "categorical",
            "choices": ["scale", "auto"],
            "default": "scale"
        },
        "coef0": {
            "type": "float",
            "min": 0.0,
            "max": 1.0,
            "default": 0.0
        },
        "probability": {
            "type": "categorical",
            "choices": [True, False],
            "default": True
        }
    },
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
    },
    "rf": {
        "n_estimators": {
            "type": "int",
            "min": 10,
            "max": 500,
            "default": 100
        },
        "max_depth": {
            "type": "int",
            "min": 3,
            "max": 30,
            "default": 10
        },
        "min_samples_split": {
            "type": "int",
            "min": 2,
            "max": 20,
            "default": 2
        },
        "min_samples_leaf": {
            "type": "int",
            "min": 1,
            "max": 10,
            "default": 1
        },
        "max_features": {
            "type": "categorical",
            "choices": ["sqrt", "log2", None],
            "default": "sqrt"
        }
    },
    "dt": {
        "max_depth": {
            "type": "int",
            "min": 3,
            "max": 30,
            "default": 10
        },
        "min_samples_split": {
            "type": "int",
            "min": 2,
            "max": 20,
            "default": 2
        },
        "min_samples_leaf": {
            "type": "int",
            "min": 1,
            "max": 10,
            "default": 1
        },
        "criterion": {
            "type": "categorical",
            "choices": ["gini", "entropy"],
            "default": "gini"
        }
    },
    "gb": {
        "n_estimators": {
            "type": "int",
            "min": 10,
            "max": 500,
            "default": 100
        },
        "learning_rate": {
            "type": "float",
            "min": 0.001,
            "max": 1.0,
            "default": 0.1,
            "log_scale": True
        },
        "max_depth": {
            "type": "int",
            "min": 3,
            "max": 20,
            "default": 3
        },
        "subsample": {
            "type": "float",
            "min": 0.5,
            "max": 1.0,
            "default": 1.0
        }
    },
    "knn_clf": {
        "n_neighbors": {
            "type": "int",
            "min": 1,
            "max": 30,
            "default": 5
        },
        "weights": {
            "type": "categorical",
            "choices": ["uniform", "distance"],
            "default": "uniform"
        },
        "algorithm": {
            "type": "categorical",
            "choices": ["auto", "ball_tree", "kd_tree", "brute"],
            "default": "auto"
        },
        "leaf_size": {
            "type": "int",
            "min": 10,
            "max": 50,
            "default": 30
        }
    },
    "gnb": {},  # No hyperparameters
    "lda": {
        "solver": {
            "type": "categorical",
            "choices": ["svd", "lsqr", "eigen"],
            "default": "svd"
        }
    },
    "qda": {
        "reg_param": {
            "type": "float",
            "min": 0.0,
            "max": 1.0,
            "default": 0.0
        }
    }
}

class RunSklearnClassifierAPI(BaseEstimatorAPI):

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
            # No defined param space, allow anything
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
        if clf_name == "lr":
            classifier = LogisticRegression(random_state=42, **final_params)
        elif clf_name == "mlp":
            classifier = MLPClassifier(random_state=42, **final_params)
        elif clf_name == "ada":
            classifier = AdaBoostClassifier(random_state=42, **final_params)
        elif clf_name == "svm":
            classifier = svm.SVC(random_state=42, **final_params)
        elif clf_name == "rf":
            classifier = RandomForestClassifier(random_state=42, **final_params)
        elif clf_name == "dt":
            classifier = DecisionTreeClassifier(random_state=42, **final_params)
        elif clf_name == "gb":
            classifier = GradientBoostingClassifier(random_state=42, **final_params)
        elif clf_name == "knn_clf":
            classifier = KNeighborsClassifier(**final_params)
        elif clf_name == "gnb":
            classifier = GaussianNB(**final_params)
        elif clf_name == "lda":
            classifier = LinearDiscriminantAnalysis(**final_params)
        elif clf_name == "qda":
            classifier = QuadraticDiscriminantAnalysis(**final_params)
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
    RunSklearnClassifierAPI(__name__).run()
