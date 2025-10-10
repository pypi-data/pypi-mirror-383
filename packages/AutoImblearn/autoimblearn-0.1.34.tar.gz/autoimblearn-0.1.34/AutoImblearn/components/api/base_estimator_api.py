from .base_model_api import BaseModelAPI
from abc import abstractmethod
import pickle
import os
import logging


class BaseEstimatorAPI(BaseModelAPI):
    """Abstract base class for sklearn-like estimators/classifiers."""

    def __init__(self, import_name):
        super().__init__(import_name)
        self.fitted_model = None  # Standardized attribute name

    def fit_train(self, args, X_train, y_train, X_test, y_test):
        # fit() RETURNS the fitted model (sklearn pattern!)
        self.fitted_model = self.fit(args, X_train, y_train, X_test, y_test)

        # Save to disk automatically
        self._save_fitted_model(args)

        # Predict on test data (model already in memory)
        result = self.predict(X_test, y_test)
        return result

    def _save_fitted_model(self, params):
        """Save fitted model to disk for persistence"""
        if self.fitted_model is None:
            logging.warning("No fitted_model to save. Skipping persistence.")
            return

        dataset_name = params.dataset_name
        model_dir = os.path.join("/data/interim", dataset_name)
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, "fitted_estimator.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(self.fitted_model, f)

        logging.info(f"✓ Fitted estimator saved to {model_path}")

        # Save metadata
        metadata = {
            'model_class': type(self.fitted_model).__name__,
            'model_name': getattr(self, 'clf_name', None)
        }
        metadata_path = os.path.join(model_dir, "fitted_estimator_metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

    def _load_fitted_model(self, params):
        """Load fitted model from disk if exists"""
        dataset_name = params.dataset_name
        model_path = os.path.join("/data/interim", dataset_name, "fitted_estimator.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Fitted model not found at {model_path}")

        with open(model_path, 'rb') as f:
            self.fitted_model = pickle.load(f)

        logging.info(f"✓ Fitted estimator loaded from {model_path}")

        # Load metadata
        metadata_path = os.path.join("/data/interim", dataset_name, "fitted_estimator_metadata.pkl")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                if 'model_name' in metadata:
                    self.clf_name = metadata['model_name']

    @abstractmethod
    def fit(self, args, X_train, y_train, X_test=None, y_test=None):
        pass

    @abstractmethod
    def predict(self, X_test, y_test):
        pass
