from AutoImblearn.components.survival import RunSkSurvivalModel, RunSurvivalResampler

import logging
import numpy as np
import pandas as pd

# Docker-based survival models - factory functions
survival_models = {
    'CPH': lambda **kw: RunSkSurvivalModel(model='CPH', **kw),
    'RSF': lambda **kw: RunSkSurvivalModel(model='RSF', **kw),
    'SVM': lambda **kw: RunSkSurvivalModel(model='SVM', **kw),
    'KSVM': lambda **kw: RunSkSurvivalModel(model='KSVM', **kw),
    'LASSO': lambda **kw: RunSkSurvivalModel(model='LASSO', **kw),
    'L1': lambda **kw: RunSkSurvivalModel(model='L1', **kw),
    'L2': lambda **kw: RunSkSurvivalModel(model='L2', **kw),
    'CSA': lambda **kw: RunSkSurvivalModel(model='CSA', **kw),
    'LRSF': lambda **kw: RunSkSurvivalModel(model='LRSF', **kw),
}

# Docker-based survival resamplers - factory functions
survival_resamplers = {
    'rus': lambda **kw: RunSurvivalResampler(model='rus', **kw),
    'ros': lambda **kw: RunSurvivalResampler(model='ros', **kw),
    'smote': lambda **kw: RunSurvivalResampler(model='smote', **kw),
}


def value_counter(Y: np.ndarray):
    """Count events and censored observations in survival data"""
    values, counts = np.unique(Y['Status'], return_counts=True)
    for value, count in zip(values, counts):
        dist = count / Y.shape[0] * 100
        label = "Event" if value else "Censored"
        logging.info("\t\t {}={}, n={},\t ({:.2f}%)".format(label, value, count, dist))


class CustomSurvivalResamplar:
    """
    Survival-aware resampler that preserves censoring information.

    Args:
        X (np.ndarray): Feature matrix
        Y (np.ndarray): Structured survival array with 'Status' and 'Survival_in_days'
    """

    def __init__(self, X: np.ndarray, Y: np.ndarray):
        self.X = X
        self.Y = Y

    def need_resample(self, samratio=None):
        """
        Test if resampling is needed based on event/censored ratio.

        Args:
            samratio: Threshold ratio for resampling decision
        """
        if samratio is None:
            return True

        _, counts = np.unique(self.Y['Status'], return_counts=True)
        # ratio of events to censored
        ratio = counts[1] / counts[0] if len(counts) > 1 else 1.0

        return ratio < samratio

    def resample(self, args, rsp=None, ratio=None):
        """
        Perform survival-aware resampling.

        Args:
            args: Arguments object with .path for data_folder
            rsp: Resampling method ('rus', 'ros', 'smote')
            ratio: Sampling strategy ratio
        """
        logging.info("\t Before Re-Sampling")
        value_counter(self.Y)

        if rsp in survival_resamplers.keys():
            # Instantiate resampler with data_folder
            factory = survival_resamplers[rsp]
            resampler = factory(data_folder=args.path)

            if ratio is None:
                pass
            elif ratio is not None and hasattr(resampler, 'set_params'):
                resampler.set_params(**{"sampling_strategy": ratio})
            else:
                raise ValueError("can't set resampling ratio for {}".format(rsp))
        else:
            raise ValueError("Re-sampling method {} is not defined".format(rsp))

        self.X, self.Y = resampler.fit_resample(self.X, self.Y)
        logging.info("\t After Re-Sampling")
        value_counter(self.Y)

        return self.X, self.Y


class CustomSurvivalModel:
    """
    Wrapper for survival analysis models.

    Supports various models from scikit-survival:
    - Cox Proportional Hazards (CPH)
    - Random Survival Forest (RSF)
    - Survival SVM variants (SVM, KSVM)
    - Regularized Cox models (LASSO, L1, L2, CSA)
    """

    def __init__(self, args):
        self.args = args
        self.data_folder = args.path
        self.model = None
        self.model_name = None
        self.result = None

    def train(self, X_train: np.ndarray, Y_train: np.ndarray, model=None):
        """
        Train survival model.

        Args:
            X_train: Training features
            Y_train: Structured survival array with 'Status' and 'Survival_in_days'
            model: Model name (e.g., 'CPH', 'RSF')
        """
        if model in survival_models.keys():
            # Instantiate model with data_folder
            factory = survival_models[model]
            self.model = factory(data_folder=self.data_folder)
            self.model_name = model
        else:
            raise Exception("Survival model {} not defined".format(model))

        self.model.fit(X_train, Y_train)

    def predict(self, X_test: np.ndarray, Y_test: np.ndarray, Y_train: np.ndarray = None):
        """
        Make predictions and evaluate survival model.

        Args:
            X_test: Test features
            Y_test: Test survival data
            Y_train: Training survival data (needed for Uno's C-index)

        Returns:
            dict: Evaluation metrics (c_index, c_uno)
        """
        if self.args.metric == "c_index":
            # Get risk scores
            predictions = self.model.predict(X_test)

            # Calculate concordance indices
            from sksurv.metrics import concordance_index_censored, concordance_index_ipcw

            c_index = concordance_index_censored(
                Y_test['Status'],
                Y_test['Survival_in_days'],
                predictions
            )[0]

            c_uno = None
            if Y_train is not None:
                try:
                    c_uno = concordance_index_ipcw(Y_train, Y_test, predictions)[0]
                except:
                    c_uno = None

            self.result = {
                'c_index': c_index,
                'c_uno': c_uno,
                'n_events': int(Y_test['Status'].sum())
            }

            logging.info(
                "\t C-index: {:.4f}, C-uno: {}, Events: {}".format(
                    c_index,
                    f"{c_uno:.4f}" if c_uno else "N/A",
                    int(Y_test['Status'].sum())
                )
            )

            return c_index
        else:
            raise ValueError("Metric {} is not supported for survival analysis".format(self.args.metric))
