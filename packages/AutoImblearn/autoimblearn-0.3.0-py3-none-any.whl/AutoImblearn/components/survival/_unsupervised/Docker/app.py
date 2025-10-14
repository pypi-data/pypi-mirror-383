"""
Flask REST API for survival unsupervised learning models.

Supports:
- Survival Tree Clustering (subgroup discovery)
- KMeans adapted for survival data
- Risk stratification
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from sksurv.util import Surv

app = Flask(__name__)

# Global model storage
model = None
model_name = None


def get_model(name):
    """
    Get the appropriate survival unsupervised model.

    Args:
        name: Model name

    Returns:
        Model instance
    """
    if name == 'survival_tree':
        # Survival tree for subgroup discovery
        from sksurv.tree import SurvivalTree
        return SurvivalTree(max_depth=3, min_samples_split=20, min_samples_leaf=10)

    elif name == 'survival_kmeans':
        # KMeans on survival times (ignoring censoring for clustering)
        from sklearn.cluster import KMeans
        return KMeans(n_clusters=3, random_state=42)

    else:
        raise ValueError(f"Unknown survival unsupervised model: {name}")


def load_survival_data(filepath):
    """Load survival data from CSV file."""
    df = pd.read_csv(filepath)

    # Check if survival columns exist
    if 'Status' in df.columns and 'Survival_in_days' in df.columns:
        # Create structured array for survival analysis
        y = Surv.from_dataframe('Status', 'Survival_in_days', df)

        # Features are all columns except Status and Survival_in_days
        feature_cols = [col for col in df.columns if col not in ['Status', 'Survival_in_days']]
        X = df[feature_cols].values

        return X, y
    else:
        raise ValueError("Missing 'Status' or 'Survival_in_days' columns")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': model_name}), 200


@app.route('/fit', methods=['POST'])
def fit():
    """
    Fit survival unsupervised model.

    Expected JSON:
    {
        "model_name": "survival_tree",
        "X_train_path": "/data/interim/dataset/X_train.csv",
        "y_train_path": "/data/interim/dataset/y_train.csv"
    }
    """
    global model, model_name

    try:
        data = request.get_json()
        model_name = data.get('model_name', 'survival_tree')
        X_train_path = data['X_train_path']
        y_train_path = data['y_train_path']

        # Load data
        X_train, y_train = load_survival_data(y_train_path)
        X_train_df = pd.read_csv(X_train_path)

        # Get model
        model = get_model(model_name)

        # Fit model
        if model_name == 'survival_tree':
            # Survival tree can directly use structured array
            model.fit(X_train_df.values, y_train)

        elif model_name == 'survival_kmeans':
            # KMeans on survival times (for uncensored data or treating time as feature)
            # This is a simple approach - cluster based on survival times
            survival_times = y_train['Survival_in_days'].reshape(-1, 1)
            model.fit(survival_times)

        # Save model
        model_path = '/tmp/survival_unsupervised_model.pkl'
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
    Predict cluster assignments or risk scores.

    Expected JSON:
    {
        "X_test_path": "/data/interim/dataset/X_test.csv",
        "y_test_path": "/data/interim/dataset/y_test.csv"  (optional, for evaluation)
    }

    Returns:
        Cluster assignments or risk scores
    """
    global model, model_name

    try:
        if model is None:
            # Load saved model
            model_path = '/tmp/survival_unsupervised_model.pkl'
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

        data = request.get_json()
        X_test_path = data['X_test_path']
        y_test_path = data.get('y_test_path')

        # Load test data
        X_test_df = pd.read_csv(X_test_path)

        if model_name == 'survival_tree':
            # Predict risk scores (leaf node IDs)
            predictions = model.apply(X_test_df.values)

        elif model_name == 'survival_kmeans':
            # Load survival times for clustering
            if y_test_path:
                _, y_test = load_survival_data(y_test_path)
                survival_times = y_test['Survival_in_days'].reshape(-1, 1)
            else:
                # If no survival data, cluster based on features (fallback)
                survival_times = X_test_df.values

            predictions = model.predict(survival_times)

        # Calculate metrics if y_test is provided
        metrics = {}
        if y_test_path:
            try:
                _, y_test = load_survival_data(y_test_path)

                # Calculate log-rank statistic for cluster separation
                from sksurv.compare import compare_survival

                # Group by cluster
                unique_clusters = np.unique(predictions)
                if len(unique_clusters) > 1:
                    cluster_groups = [y_test[predictions == c] for c in unique_clusters]
                    chisq, pvalue = compare_survival(cluster_groups)
                    metrics['log_rank_chi2'] = float(chisq)
                    metrics['log_rank_pvalue'] = float(pvalue)

                # Calculate silhouette score (if applicable)
                if model_name == 'survival_kmeans':
                    from sklearn.metrics import silhouette_score
                    survival_times = y_test['Survival_in_days'].reshape(-1, 1)
                    if len(unique_clusters) > 1:
                        silhouette = silhouette_score(survival_times, predictions)
                        metrics['silhouette'] = float(silhouette)

            except Exception as e:
                metrics['evaluation_error'] = str(e)

        return jsonify({
            'status': 'success',
            'predictions': predictions.tolist(),
            'n_clusters': int(len(np.unique(predictions))),
            'metrics': metrics
        }), 200

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
