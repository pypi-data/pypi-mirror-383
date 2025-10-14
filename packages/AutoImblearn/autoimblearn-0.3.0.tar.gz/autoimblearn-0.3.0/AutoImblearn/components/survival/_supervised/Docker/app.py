from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path

from sksurv.ensemble import RandomSurvivalForest
from sksurv.linear_model import CoxPHSurvivalAnalysis, CoxnetSurvivalAnalysis
from sksurv.svm import FastSurvivalSVM, FastKernelSurvivalSVM
from sksurv.metrics import concordance_index_censored, concordance_index_ipcw
from sksurv.util import Surv

app = Flask(__name__)

# Global state for model and data
model = None
model_name = None
X_train = None
y_train = None
X_test = None
y_test = None
dataset_name = None
metric = None


def get_model(model_name):
    """Factory function to create survival models"""
    models = {
        'CPH': lambda: CoxPHSurvivalAnalysis(alpha=0.0001),
        'RSF': lambda: RandomSurvivalForest(random_state=42, n_jobs=-1),
        'KSVM': lambda: FastKernelSurvivalSVM(random_state=42, kernel='poly'),
        'SVM': lambda: FastSurvivalSVM(random_state=42),
        'LASSO': lambda: CoxnetSurvivalAnalysis(l1_ratio=1, alpha_min_ratio=0.01),
        'L1': lambda: CoxnetSurvivalAnalysis(l1_ratio=1),
        'L2': lambda: CoxnetSurvivalAnalysis(l1_ratio=1e-16),
        'CSA': lambda: CoxnetSurvivalAnalysis(l1_ratio=0.5),
        'LRSF': lambda: RandomSurvivalForest(random_state=42, max_depth=10, n_estimators=20, max_samples=0.4),
    }

    if model_name not in models:
        raise ValueError(f"Unknown model: {model_name}")

    return models[model_name]()


def load_survival_data(filepath):
    """
    Load survival data from CSV.
    Expected format: Status (bool), Survival_in_days (float)
    """
    df = pd.read_csv(filepath)

    # Check if this is the target (y) file with Status and Survival_in_days
    if 'Status' in df.columns and 'Survival_in_days' in df.columns:
        # Create structured array for scikit-survival
        y = Surv.from_dataframe('Status', 'Survival_in_days', df)
        return y
    else:
        # This is feature data (X)
        return df.values


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/fit', methods=['POST'])
def fit():
    """Train the survival model"""
    global model, model_name, X_train, y_train, dataset_name, metric

    try:
        data = request.get_json()
        model_name = data['model']
        dataset_name = data['dataset_name']
        metric = data.get('metric', 'c_index')
        dataset_files = data['dataset']

        # Load training data
        X_train_path = f"/data/interim/{dataset_files[0]}"
        y_train_path = f"/data/interim/{dataset_files[1]}"

        X_train = pd.read_csv(X_train_path).values
        y_train = load_survival_data(y_train_path)

        # Create and fit model
        model = get_model(model_name)
        model.fit(X_train, y_train)

        # Save fitted model
        model_dir = f"/data/models/{dataset_name}"
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        model_path = os.path.join(model_dir, f"{model_name}_survival_model.pkl")

        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        return jsonify({
            "status": "success",
            "message": f"Model {model_name} trained successfully",
            "model_path": model_path
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/predict', methods=['POST'])
def predict():
    """Make predictions and evaluate model"""
    global model, X_test, y_test, y_train

    try:
        data = request.get_json()
        dataset_files = data['dataset']

        # Load test data
        X_test_path = f"/data/interim/{dataset_files[2]}"
        y_test_path = f"/data/interim/{dataset_files[3]}"

        X_test = pd.read_csv(X_test_path).values
        y_test = load_survival_data(y_test_path)

        if model is None:
            return jsonify({
                "status": "error",
                "message": "Model not trained. Call /fit first."
            }), 400

        # Make predictions (risk scores)
        predictions = model.predict(X_test)

        # Calculate concordance index
        c_index = concordance_index_censored(
            y_test['Status'],
            y_test['Survival_in_days'],
            predictions
        )[0]

        # Calculate Uno's C-index if training data is available
        c_uno = None
        if y_train is not None:
            try:
                c_uno = concordance_index_ipcw(y_train, y_test, predictions)[0]
            except:
                c_uno = None

        result = {
            "c_index": float(c_index),
            "c_uno": float(c_uno) if c_uno is not None else None,
            "n_events": int(y_test['Status'].sum()),
            "n_samples": len(y_test)
        }

        return jsonify({
            "status": "success",
            "result": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/predict_proba', methods=['POST'])
def predict_proba():
    """Get survival function predictions (for models that support it)"""
    global model, X_test

    try:
        if model is None:
            return jsonify({
                "status": "error",
                "message": "Model not trained. Call /fit first."
            }), 400

        if not hasattr(model, 'predict_survival_function'):
            return jsonify({
                "status": "error",
                "message": f"Model {model_name} does not support survival function prediction"
            }), 400

        data = request.get_json()
        dataset_files = data['dataset']

        # Load test data
        X_test_path = f"/data/interim/{dataset_files[2]}"
        X_test = pd.read_csv(X_test_path).values

        # Get survival functions
        surv_funcs = model.predict_survival_function(X_test)

        # Return first few time points as example
        times = surv_funcs[0].x[:10].tolist()
        probs = [sf(times).tolist() for sf in surv_funcs[:5]]  # First 5 samples

        return jsonify({
            "status": "success",
            "times": times,
            "survival_probabilities": probs,
            "note": "Showing first 5 samples and 10 time points"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
