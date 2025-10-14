# AutoImblearn/core/pipeline_strategies.py
"""
Pipeline execution strategies using the Strategy Pattern.

This module eliminates code duplication in runpipe.py by providing
separate strategy classes for different pipeline types.
"""

import os
import pickle
import numpy as np
import logging
from abc import ABC, abstractmethod

from ..processing.utils import Samplar
from ..pipelines.customimputation import CustomImputer
from ..pipelines.customrsp import CustomResamplar
from ..pipelines.customclf import CustomClassifier
from ..pipelines.customhbd import CustomHybrid
from ..pipelines.customautoml import CustomAutoML
from ..pipelines.customsurvival import CustomSurvivalModel, CustomSurvivalResamplar
from ..pipelines.customunsupervised import CustomUnsupervisedModel, CustomSurvivalUnsupervisedModel


def average(lst):
    """Calculate average of a list"""
    return sum(lst) / len(lst)


class BasePipelineStrategy(ABC):
    """
    Abstract base class for pipeline execution strategies.

    Each strategy handles a specific pipeline type and encapsulates
    the logic for data loading, K-fold splitting, training, and evaluation.
    """

    def __init__(self, args, dataloader, preprocessor, saver):
        """
        Initialize the strategy.

        Args:
            args: Command-line arguments
            dataloader: DataLoader instance
            preprocessor: DataPreprocess instance
            saver: Result instance for saving/loading results
        """
        self.args = args
        self.dataloader = dataloader
        self.preprocessor = preprocessor
        self.saver = saver

    @abstractmethod
    def validate_pipeline(self, pipe):
        """Validate that the pipeline has the correct format"""
        pass

    @abstractmethod
    def execute_fold(self, pipe, X_train, y_train, X_test, y_test):
        """Execute one fold of the pipeline"""
        pass

    def execute(self, pipe, train_ratio=1.0):
        """
        Main execution method for the pipeline strategy.

        This method:
        1. Validates the pipeline
        2. Loads and preprocesses data
        3. Applies train_ratio if needed
        4. Executes K-fold cross-validation
        5. Averages and saves results

        Args:
            pipe: Pipeline specification (list of component names)
            train_ratio: Fraction of data to use (default 1.0)

        Returns:
            Average result across all folds
        """
        # Validate pipeline format
        self.validate_pipeline(pipe)

        # Load and preprocess raw data (with missing values)
        X, y = self.preprocessor.preprocess(self.args)

        # Apply train_ratio if needed
        if train_ratio != 1.0:
            X, y = self._stratified_sample(X, y, train_ratio)

        logging.info("Data loaded and preprocessed")

        # Create K-fold splits on RAW data (before imputation)
        train_sampler = Samplar(np.array(X), np.array(y))

        results = []
        for X_train, y_train, X_test, y_test in train_sampler.apply_kfold(self.args.n_splits):
            logging.info(f"\t Fold {self.args.repeat}")

            # Execute this fold (strategy-specific logic)
            result = self.execute_fold(pipe, X_train, y_train, X_test, y_test)
            results.append(result)

            self.args.repeat += 1

        # Average results and save
        avg_result = average(results)
        self.saver.append(pipe, avg_result)
        return avg_result

    def _stratified_sample(self, X, y, train_ratio):
        """Apply stratified sampling to reduce dataset size"""
        import pandas as pd

        data = pd.concat([X, y], axis=1)
        new_data = data.groupby('Status', group_keys=False).apply(
            lambda x: x.sample(frac=train_ratio)
        )
        new_data.sort_index(inplace=True)
        new_data.reset_index(inplace=True, drop=True)
        columns = list(new_data.columns.values)
        columns.remove("Status")
        X = new_data[columns].copy()
        y = new_data["Status"].copy()
        return X, y

    def _impute_with_caching(self, imp, X_train, y_train, X_test):
        """
        Perform imputation with intelligent caching.

        This method checks if cached imputation results exist for this fold.
        If so, it loads them. Otherwise, it runs imputation and caches the results.

        Args:
            imp: Imputer name (e.g., 'mean', 'knn')
            X_train: Training features
            y_train: Training labels
            X_test: Test features

        Returns:
            Tuple of (X_train_imputed, X_test_imputed)
        """
        impute_file_name = f"imp_{imp}_fold{self.args.repeat}.p"
        impute_file_path = os.path.join(
            self.dataloader.get_interim_data_folder(),
            self.args.dataset,
            impute_file_name
        )
        impute_test_file_path = impute_file_path.replace('.p', '_test.p')

        # Check if cached imputation results exist
        if os.path.exists(impute_file_path) and os.path.exists(impute_test_file_path):
            # Load cached results - no need to re-run imputation!
            logging.info(f"\t Loading cached imputation from {impute_file_name}")
            with open(impute_file_path, "rb") as f:
                X_train_imputed = pickle.load(f)
            with open(impute_test_file_path, "rb") as f:
                X_test_imputed = pickle.load(f)
            logging.info("\t Cached imputation loaded")
        else:
            # Run imputation - results will be cached automatically
            logging.info("\t Imputation Started")
            imputer = CustomImputer(
                method=imp,
                data_folder=self.args.path,
                dataset_name=self.args.dataset,
                impute_file_path=impute_file_path
            )

            # Fit on train, transform both
            X_train_imputed = imputer.fit_transform(self.args, X_train)
            X_test_imputed = imputer.transform(X_test)

            logging.info("\t Imputation Done")

        return X_train_imputed, X_test_imputed


class ThreeElementPipelineStrategy(BasePipelineStrategy):
    """
    Strategy for 3-element pipelines: Imputer -> Resampler -> Classifier

    Example: ['median', 'smote', 'lr']
    """

    def validate_pipeline(self, pipe):
        """Ensure pipeline has exactly 3 elements"""
        if len(pipe) != 3:
            raise ValueError(
                f"Pipeline {pipe} length is not correct, not a regular method pipeline"
            )

    def execute_fold(self, pipe, X_train, y_train, X_test, y_test):
        """
        Execute one fold of a 3-element pipeline.

        Steps:
        1. Imputation (with caching)
        2. Resampling (on training data only)
        3. Classification
        4. Prediction
        """
        imp, rsp, clf = pipe

        # Imputation level - FIT on train, TRANSFORM both train and test
        X_train_imputed, X_test_imputed = self._impute_with_caching(
            imp, X_train, y_train, X_test
        )

        # Resampling level - ONLY on training data
        resamplar = CustomResamplar(X_train_imputed, y_train)
        if resamplar.need_resample():
            logging.info("\t Re-Sampling Started")
            X_train_imputed, y_train = resamplar.resample(self.args, rsp=rsp)
            logging.info("\t Re-Sampling Done")

        # Classification level
        logging.info(f"\t Training in fold {self.args.repeat} Start")
        trainer = CustomClassifier(self.args)
        trainer.train(X_train_imputed, y_train, clf=clf)
        logging.info(f"\t Training in fold {self.args.repeat} Done")

        # Validation on imputed test data
        trainer.predict(X_test_imputed, y_test)

        result = trainer.result
        del trainer

        return result


class HybridPipelineStrategy(BasePipelineStrategy):
    """
    Strategy for 2-element pipelines: Imputer -> Hybrid Method

    Hybrid methods combine resampling and classification in one step.
    Example: ['median', 'autosmote']
    """

    def validate_pipeline(self, pipe):
        """Ensure pipeline has exactly 2 elements"""
        if len(pipe) != 2:
            raise ValueError(
                f"Pipeline {pipe} length is not correct, not a hybrid method pipeline"
            )

    def execute_fold(self, pipe, X_train, y_train, X_test, y_test):
        """
        Execute one fold of a 2-element hybrid pipeline.

        Steps:
        1. Imputation (with caching)
        2. Hybrid method (combines resampling + classification)
        3. Prediction
        """
        imp, hbd = pipe

        # Imputation level - FIT on train, TRANSFORM both train and test
        X_train_imputed, X_test_imputed = self._impute_with_caching(
            imp, X_train, y_train, X_test
        )

        # Hybrid method (combines resampling + classification)
        logging.info(f"\t Training in fold {self.args.repeat} Start")
        trainer = CustomHybrid(args=self.args, pipe=pipe)

        if self.args.metric not in trainer.hbd.supported_metrics:
            raise ValueError(
                f"Metric {self.args.metric} not yet supported for model {hbd}"
            )

        # Hybrid methods train on imputed data
        trainer.train(
            X_train=X_train_imputed,
            y_train=y_train,
            X_test=X_test_imputed,
            y_test=y_test
        )
        logging.info(f"\t Training in fold {self.args.repeat} Done")

        # Predict on imputed test data
        trainer.predict(X_test=X_test_imputed, y_test=y_test)

        result = trainer.result
        del trainer

        return result


class AutoMLPipelineStrategy(BasePipelineStrategy):
    """
    Strategy for 1-element pipelines: AutoML only

    AutoML methods handle imputation, resampling, and classification internally.
    Example: ['autosklearn']

    Note: This strategy doesn't use K-fold cross-validation because
    AutoML methods typically handle cross-validation internally.
    """

    def validate_pipeline(self, pipe):
        """Ensure pipeline has exactly 1 element"""
        if len(pipe) != 1:
            raise ValueError(
                f"Pipeline {pipe} length is not correct, not a AutoML method pipeline"
            )

    def execute(self, pipe, train_ratio=1.0):
        """
        Execute AutoML pipeline (overrides base execute method).

        AutoML methods don't use K-fold cross-validation - they handle
        validation internally.
        """
        self.validate_pipeline(pipe)

        automl = pipe[0]

        # Load and preprocess data
        X, y = self.preprocessor.preprocess(self.args)

        # Fit
        logging.info(f"\t Training of {pipe} Start")
        trainer = CustomAutoML(self.args, automl)
        trainer.train(X, y)
        logging.info(f"\t Training of {pipe} Ended")

        # Predict
        logging.info(f"\t Predicting of {pipe} Start")
        result = trainer.predict()
        logging.info(f"\t Predicting of {pipe} Ended")

        self.args.repeat += 1

        self.saver.append(pipe, result)
        return result

    def execute_fold(self, pipe, X_train, y_train, X_test, y_test):
        """Not used for AutoML pipelines"""
        raise NotImplementedError("AutoML pipelines don't use fold-based execution")


class SurvivalPipelineStrategy(BasePipelineStrategy):
    """
    Strategy for 3-element survival pipelines: Imputer -> Survival Resampler -> Survival Model

    Example: ['median', 'rus', 'CPH']

    Handles survival data with structured arrays containing event indicators and times.
    """

    def validate_pipeline(self, pipe):
        """Ensure pipeline has exactly 3 elements"""
        if len(pipe) != 3:
            raise ValueError(
                f"Pipeline {pipe} length is not correct, not a survival method pipeline"
            )

    def execute_fold(self, pipe, X_train, y_train, X_test, y_test):
        """
        Execute one fold of a 3-element survival pipeline.

        Steps:
        1. Imputation (with caching) - same as regular pipelines
        2. Survival-aware resampling (on training data only, preserves censoring)
        3. Survival model training and prediction

        Args:
            pipe: [imputer, survival_resampler, survival_model]
            X_train, y_train: Training data (y_train is structured survival array)
            X_test, y_test: Test data (y_test is structured survival array)
        """
        imp, rsp, model = pipe

        # Imputation level - FIT on train, TRANSFORM both train and test
        # Note: Imputation only works on features (X), not on survival outcomes (y)
        X_train_imputed, X_test_imputed = self._impute_with_caching(
            imp, X_train, y_train, X_test
        )

        # Store original y_train for Uno's C-index calculation
        y_train_original = y_train.copy()

        # Survival resampling level - ONLY on training data
        resamplar = CustomSurvivalResamplar(X_train_imputed, y_train)
        if resamplar.need_resample():
            logging.info("\t Survival Re-Sampling Started")
            X_train_imputed, y_train = resamplar.resample(self.args, rsp=rsp)
            logging.info("\t Survival Re-Sampling Done")

        # Survival model training
        logging.info(f"\t Survival Training in fold {self.args.repeat} Start")
        trainer = CustomSurvivalModel(self.args)
        trainer.train(X_train_imputed, y_train, model=model)
        logging.info(f"\t Survival Training in fold {self.args.repeat} Done")

        # Prediction and evaluation on test data
        result = trainer.predict(X_test_imputed, y_test, Y_train=y_train_original)

        del trainer

        return result


class UnsupervisedPipelineStrategy(BasePipelineStrategy):
    """
    Strategy for 2-element unsupervised pipelines: Imputer -> Unsupervised Model

    Supports clustering, dimensionality reduction, and anomaly detection.
    Example: ['median', 'kmeans'], ['knn', 'pca'], ['mean', 'isoforest']
    """

    def validate_pipeline(self, pipe):
        """Ensure pipeline has exactly 2 elements"""
        if len(pipe) != 2:
            raise ValueError(
                f"Pipeline {pipe} length is not correct, not an unsupervised pipeline"
            )

    def execute_fold(self, pipe, X_train, y_train, X_test, y_test):
        """
        Execute one fold of a 2-element unsupervised pipeline.

        Steps:
        1. Imputation (with caching)
        2. Unsupervised model training and prediction

        Note: y_train and y_test may be used for evaluation but not for training
        """
        imp, model = pipe

        # Imputation level - FIT on train, TRANSFORM both train and test
        X_train_imputed, X_test_imputed = self._impute_with_caching(
            imp, X_train, y_train, X_test
        )

        # Unsupervised model training
        logging.info(f"\t Training unsupervised model in fold {self.args.repeat} Start")
        trainer = CustomUnsupervisedModel(self.args)
        trainer.train(X_train_imputed, y_train, model=model)
        logging.info(f"\t Training unsupervised model in fold {self.args.repeat} Done")

        # Prediction and evaluation on test data
        result = trainer.predict(X_test_imputed, y_test)

        del trainer

        return result


class SurvivalUnsupervisedPipelineStrategy(BasePipelineStrategy):
    """
    Strategy for 2-element survival unsupervised pipelines: Imputer -> Survival Unsupervised Model

    Supports survival clustering and risk stratification.
    Example: ['median', 'survival_tree'], ['knn', 'survival_kmeans']
    """

    def validate_pipeline(self, pipe):
        """Ensure pipeline has exactly 2 elements"""
        if len(pipe) != 2:
            raise ValueError(
                f"Pipeline {pipe} length is not correct, not a survival unsupervised pipeline"
            )

    def execute_fold(self, pipe, X_train, y_train, X_test, y_test):
        """
        Execute one fold of a 2-element survival unsupervised pipeline.

        Steps:
        1. Imputation (with caching) - same as regular pipelines
        2. Survival unsupervised model training and prediction

        Args:
            pipe: [imputer, survival_unsupervised_model]
            X_train, y_train: Training data (y_train is structured survival array)
            X_test, y_test: Test data (y_test is structured survival array)
        """
        imp, model = pipe

        # Imputation level - FIT on train, TRANSFORM both train and test
        X_train_imputed, X_test_imputed = self._impute_with_caching(
            imp, X_train, y_train, X_test
        )

        # Survival unsupervised model training
        logging.info(f"\t Training survival unsupervised model in fold {self.args.repeat} Start")
        trainer = CustomSurvivalUnsupervisedModel(self.args)
        trainer.train(X_train_imputed, y_train, model=model)
        logging.info(f"\t Training survival unsupervised model in fold {self.args.repeat} Done")

        # Prediction and evaluation on test data
        result = trainer.predict(X_test_imputed, y_test)

        del trainer

        return result
