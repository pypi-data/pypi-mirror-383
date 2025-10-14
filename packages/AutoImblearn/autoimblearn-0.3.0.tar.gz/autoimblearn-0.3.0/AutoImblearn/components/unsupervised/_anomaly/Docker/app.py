"""
Flask REST API for anomaly detection models.

Supports various anomaly detection algorithms from scikit-learn.
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

# Global model storage
model = None
model_name = None


def get_model(name, contamination=0.1):
    """
    Get the appropriate anomaly detection model.

    Args:
        name: Model name
        contamination: Expected proportion of outliers in the dataset

    Returns:
        Model instance
    """
    if name == 'isoforest':
        from sklearn.ensemble import IsolationForest
        return IsolationForest(contamination=contamination, random_state=42)

    elif name == 'ocsvm':
        from sklearn.svm import OneClassSVM
        return OneClassSVM(nu=contamination)

    elif name == 'lof':
        from sklearn.neighbors import LocalOutlierFactor
        return LocalOutlierFactor(contamination=contamination, novelty=True)

    elif name == 'elliptic':
        from sklearn.covariance import EllipticEnvelope
        return EllipticEnvelope(contamination=contamination, random_state=42)

    else:
        raise ValueError(f"Unknown anomaly detection model: {name}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': model_name}), 200


@app.route('/fit', methods=['POST'])
def fit():
    """
    Fit anomaly detection model.

    Expected JSON:
    {
        "model_name": "isoforest",
        "X_train_path": "/data/interim/dataset/X_train.csv",
        "contamination": 0.1
    }
    """
    global model, model_name

    try:
        data = request.get_json()
        model_name = data.get('model_name', 'isoforest')
        X_train_path = data['X_train_path']
        contamination = data.get('contamination', 0.1)

        # Load data
        X_train = pd.read_csv(X_train_path).values

        # Get model
        model = get_model(model_name, contamination=contamination)

        # Fit model
        model.fit(X_train)

        # Save model
        model_path = '/tmp/anomaly_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        return jsonify({
            'status': 'success',
            'message': f'Model {model_name} fitted successfully',
            'model_path': model_path
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict anomalies.

    Expected JSON:
    {
        "X_test_path": "/data/interim/dataset/X_test.csv",
        "y_test_path": "/data/interim/dataset/y_test.csv"  (optional, for evaluation)
    }

    Returns:
        Predictions (-1 for anomaly, 1 for normal) and anomaly scores
    """
    global model, model_name

    try:
        if model is None:
            # Load saved model
            model_path = '/tmp/anomaly_model.pkl'
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

        data = request.get_json()
        X_test_path = data['X_test_path']
        y_test_path = data.get('y_test_path')

        # Load test data
        X_test = pd.read_csv(X_test_path).values

        # Predict
        predictions = model.predict(X_test)

        # Get anomaly scores
        if hasattr(model, 'score_samples'):
            anomaly_scores = model.score_samples(X_test)
        elif hasattr(model, 'decision_function'):
            anomaly_scores = model.decision_function(X_test)
        else:
            anomaly_scores = None

        # Calculate metrics if ground truth is provided
        metrics = {}
        if y_test_path and os.path.exists(y_test_path):
            try:
                y_test = pd.read_csv(y_test_path).values.ravel()

                # Convert predictions to binary (1 for anomaly, 0 for normal)
                y_pred_binary = (predictions == -1).astype(int)
                y_true_binary = y_test.astype(int)

                from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

                metrics['accuracy'] = float(accuracy_score(y_true_binary, y_pred_binary))
                metrics['precision'] = float(precision_score(y_true_binary, y_pred_binary, zero_division=0))
                metrics['recall'] = float(recall_score(y_true_binary, y_pred_binary, zero_division=0))
                metrics['f1'] = float(f1_score(y_true_binary, y_pred_binary, zero_division=0))

            except Exception as e:
                metrics['evaluation_error'] = str(e)

        # Count anomalies
        n_anomalies = int(np.sum(predictions == -1))
        n_normal = int(np.sum(predictions == 1))

        metrics['n_anomalies'] = n_anomalies
        metrics['n_normal'] = n_normal
        metrics['anomaly_ratio'] = float(n_anomalies / len(predictions))

        result = {
            'status': 'success',
            'predictions': predictions.tolist(),
            'metrics': metrics
        }

        if anomaly_scores is not None:
            result['anomaly_scores'] = anomaly_scores.tolist()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/set_params', methods=['POST'])
def set_params():
    """Set model hyperparameters."""
    global model

    try:
        if model is None:
            return jsonify({'status': 'error', 'message': 'Model not initialized'}), 400

        params = request.get_json()
        model.set_params(**params)

        return jsonify({'status': 'success', 'message': 'Parameters updated'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
