# AutoImblearn/core/runpipe.py
import os
import pickle
import numpy as np
import pandas as pd
import logging

from AutoImblearn.pipelines import CustomImputer
from ..processing.utils import DataLoader, Samplar, Result
from ..processing.preprocessing import DataPreprocess
from .pipeline_strategies import (
    ThreeElementPipelineStrategy,
    HybridPipelineStrategy,
    AutoMLPipelineStrategy,
    SurvivalPipelineStrategy,
    UnsupervisedPipelineStrategy,
    SurvivalUnsupervisedPipelineStrategy
)
from ..pipelines.customsurvival import survival_models
from ..pipelines.customunsupervised import unsupervised_models, survival_unsupervised_models

class RunPipe:
    """ Run different pipelines and save the trained results
    Parameters
    ----------
    args : The command line arguments that define how the code should run

    Attributes
    ----------
    preprocessor : Split data into features (X) and target (y)
    args : The command line arguments that define how the code should run
    X : Features
    y : Target
    saver : The class to save trained results and load saved results

    """
    def __init__(self, args=None):
        self.preprocessor = None
        self.args = args
        self.X = None
        self.y = None

        self.dataloader = None
        self.saver = None

    def loadData(self):

        # Load data
        logging.info("Loading Start")
        self.dataloader = DataLoader(self.args.dataset, path=self.args.path)
        data = self.dataloader.train_loader()
        logging.info("Loading Done")

        # Load saved result if it exists
        self.saver = Result(str(self.args.train_ratio), self.args.metric, self.args.dataset, dataloader=self.dataloader)
        self.saver.load_saved_result()

        # Proprocess data
        logging.info("Preprocessing Start")
        self.preprocessor = DataPreprocess(data, self.args)

    def _get_strategy(self, pipe):
        """
        Select the appropriate pipeline strategy based on pipeline length and components.

        Args:
            pipe: Pipeline specification (list of component names)

        Returns:
            Appropriate PipelineStrategy instance
        """
        pipe_length = len(pipe)

        if pipe_length == 3:
            # Check if this is a survival pipeline by examining the model (third element)
            model = pipe[2]
            if model in survival_models:
                # Imputer -> Survival Resampler -> Survival Model
                return SurvivalPipelineStrategy(
                    self.args, self.dataloader, self.preprocessor, self.saver
                )
            else:
                # Imputer -> Resampler -> Classifier
                return ThreeElementPipelineStrategy(
                    self.args, self.dataloader, self.preprocessor, self.saver
                )
        elif pipe_length == 2:
            # Check if this is an unsupervised pipeline by examining the second element
            model = pipe[1]

            if model in survival_unsupervised_models:
                # Imputer -> Survival Unsupervised Model
                return SurvivalUnsupervisedPipelineStrategy(
                    self.args, self.dataloader, self.preprocessor, self.saver
                )
            elif model in unsupervised_models:
                # Imputer -> Unsupervised Model (clustering, reduction, anomaly)
                return UnsupervisedPipelineStrategy(
                    self.args, self.dataloader, self.preprocessor, self.saver
                )
            else:
                # Imputer -> Hybrid Method
                return HybridPipelineStrategy(
                    self.args, self.dataloader, self.preprocessor, self.saver
                )
        elif pipe_length == 1:
            # AutoML only
            return AutoMLPipelineStrategy(
                self.args, self.dataloader, self.preprocessor, self.saver
            )
        else:
            raise ValueError(
                f"Invalid pipeline length {pipe_length}. "
                f"Expected 1 (AutoML), 2 (Hybrid/Unsupervised), 3 (Regular/Survival) elements."
            )

    def impute_data(self, imp, train_ratio=1.0):
        """
        Perform data imputation and delegate the storage responsibility to the model.

        This method checks whether an imputed dataset already exists. If so, it loads
        the stored imputation results from disk. Otherwise, it preprocesses the raw data,
        applies the specified imputation method, and lets the model handle persistence
        of the imputed output.

        Parameters
        ----------
        imp : str
            The name of the imputation method to apply (e.g., 'mean', 'knn', etc.).
        train_ratio : float, optional (default=1.0)
            The proportion of the dataset to retain after imputation. If less than 1.0,
            a stratified subsample is returned to preserve class distribution.

        Returns
        -------
        X : array-like
            The imputed feature matrix.
        y : array-like
            The corresponding target labels.
        """
        impute_file_name = "imp_" + imp + ".p"
        impute_file_path = os.path.join(self.dataloader.get_interim_data_folder(), self.args.dataset, impute_file_name)

        if os.path.exists(impute_file_path):
            # Load Saved imputation files
            with open(impute_file_path, "rb") as f:
                X, y = pickle.load(f)
        else:
            # Compute imputation files
            X, y = self.preprocessor.preprocess(self.args)
            imputer = CustomImputer(method=imp, data_folder=self.args.path, dataset_name=self.args.dataset, impute_file_path=impute_file_path)
            X = imputer.fit_transform(X, y)

        if train_ratio != 1.0:
            X, y = self.stratifiedSample(X, y, train_ratio)
        return X, y

    def fit_automl(self, pipe, train_ratio=1.0, hyperparams=None):
        """
        Execute a 1-element AutoML pipeline.

        Args:
            pipe: Pipeline with 1 element (AutoML method name)
            train_ratio: Fraction of data to use (default 1.0)
            hyperparams: Dict mapping component names to hyperparameters (optional)
                         e.g., {'autosklearn': {...}}

        Returns:
            Result from AutoML execution
        """
        # Store hyperparams in args for components to access
        if hyperparams:
            self.args.hyperparams = hyperparams

        strategy = self._get_strategy(pipe)
        return strategy.execute(pipe, train_ratio)

    def fit_hybrid(self, pipe, train_ratio=1.0, hyperparams=None):
        """
        Execute a 2-element hybrid pipeline (Imputer -> Hybrid Method).

        Args:
            pipe: Pipeline with 2 elements [imputer, hybrid_method]
            train_ratio: Fraction of data to use (default 1.0)
            hyperparams: Dict mapping component names to hyperparameters (optional)
                         e.g., {'median': {}, 'autosmote': {...}}

        Returns:
            Average result across all K-folds
        """
        # Store hyperparams in args for components to access
        if hyperparams:
            self.args.hyperparams = hyperparams

        strategy = self._get_strategy(pipe)
        return strategy.execute(pipe, train_ratio)

    def fit(self, pipe, train_ratio=1.0, hyperparams=None):
        """
        Execute a 3-element pipeline (Imputer -> Resampler -> Classifier).

        Args:
            pipe: Pipeline with 3 elements [imputer, resampler, classifier]
            train_ratio: Fraction of data to use (default 1.0)
            hyperparams: Dict mapping component names to hyperparameters (optional)
                         e.g., {'smote': {'k_neighbors': 7}, 'lr': {'C': 0.1, 'penalty': 'l1'}}

        Returns:
            Average result across all K-folds
        """
        # Store hyperparams in args for components to access
        if hyperparams:
            self.args.hyperparams = hyperparams

        strategy = self._get_strategy(pipe)
        return strategy.execute(pipe, train_ratio)


if __name__ == "__main__":
    # import logging
    import warnings

    logging.basicConfig(filename='django_frontend.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    warnings.filterwarnings("ignore")

    class Args:
        def __init__(self):
            self.train_ratio=1.0
            self.n_splits = 10
            self.repeat = 0
            self.dataset = "nhanes.csv"
            self.metric = "auroc"
            self.target = "Status"
    args = Args()
    run_pipe = RunPipe(args)
    # run_pipe.fit("MIRACLE", "mwmote", "lr")
    # print(run_pipe.fit_hybrid(["imp", "hbd"]))
    # print(run_pipe.fit(["imp", "rsp", "clf"]))
    run_pipe.loadData()
    run_pipe.fit_hybrid(["median", "autosmote"])
    # print(run_pipe.fit_automl(["autosklearn"]))
