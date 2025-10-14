"""
Flask REST API for clustering models.

Supports various clustering algorithms from scikit-learn.
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


def get_model(name, n_clusters=3):
    """
    Get the appropriate clustering model.

    Args:
        name: Model name
        n_clusters: Number of clusters (for applicable models)

    Returns:
        Model instance
    """
    if name == 'kmeans':
        from sklearn.cluster import KMeans
        return KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

    elif name == 'dbscan':
        from sklearn.cluster import DBSCAN
        return DBSCAN(eps=0.5, min_samples=5)

    elif name == 'hierarchical':
        from sklearn.cluster import AgglomerativeClustering
        return AgglomerativeClustering(n_clusters=n_clusters)

    elif name == 'gmm':
        from sklearn.mixture import GaussianMixture
        return GaussianMixture(n_components=n_clusters, random_state=42)

    elif name == 'meanshift':
        from sklearn.cluster import MeanShift
        return MeanShift()

    elif name == 'spectral':
        from sklearn.cluster import SpectralClustering
        return SpectralClustering(n_clusters=n_clusters, random_state=42)

    else:
        raise ValueError(f"Unknown clustering model: {name}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': model_name}), 200


@app.route('/fit', methods=['POST'])
def fit():
    """
    Fit clustering model.

    Expected JSON:
    {
        "model_name": "kmeans",
        "X_train_path": "/data/interim/dataset/X_train.csv",
        "n_clusters": 3
    }
    """
    global model, model_name

    try:
        data = request.get_json()
        model_name = data.get('model_name', 'kmeans')
        X_train_path = data['X_train_path']
        n_clusters = data.get('n_clusters', 3)

        # Load data
        X_train = pd.read_csv(X_train_path).values

        # Get model
        model = get_model(model_name, n_clusters=n_clusters)

        # Fit model
        if model_name == 'gmm':
            # GaussianMixture uses fit()
            model.fit(X_train)
        else:
            # Other models use fit() or fit_predict()
            model.fit(X_train)

        # Save model
        model_path = '/tmp/clustering_model.pkl'
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
    Predict cluster assignments.

    Expected JSON:
    {
        "X_test_path": "/data/interim/dataset/X_test.csv"
    }

    Returns:
        Cluster assignments and metrics
    """
    global model, model_name

    try:
        if model is None:
            # Load saved model
            model_path = '/tmp/clustering_model.pkl'
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

        data = request.get_json()
        X_test_path = data['X_test_path']

        # Load test data
        X_test = pd.read_csv(X_test_path).values

        # Predict
        if model_name == 'gmm':
            predictions = model.predict(X_test)
        elif model_name in ['dbscan', 'meanshift']:
            # DBSCAN and MeanShift don't have separate predict, use fit_predict
            predictions = model.fit_predict(X_test)
        else:
            predictions = model.predict(X_test)

        # Calculate metrics
        metrics = {}
        unique_labels = np.unique(predictions)
        n_clusters = len(unique_labels[unique_labels != -1])  # Exclude noise (-1 for DBSCAN)

        if n_clusters > 1:
            from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

            # Filter out noise points for metrics
            mask = predictions != -1
            X_filtered = X_test[mask]
            labels_filtered = predictions[mask]

            if len(np.unique(labels_filtered)) > 1:
                metrics['silhouette'] = float(silhouette_score(X_filtered, labels_filtered))
                metrics['calinski'] = float(calinski_harabasz_score(X_filtered, labels_filtered))
                metrics['davies_bouldin'] = float(davies_bouldin_score(X_filtered, labels_filtered))

            # Inertia (only for KMeans)
            if model_name == 'kmeans' and hasattr(model, 'inertia_'):
                metrics['inertia'] = float(model.inertia_)

        metrics['n_clusters'] = int(n_clusters)
        metrics['n_noise'] = int(np.sum(predictions == -1))

        return jsonify({
            'status': 'success',
            'predictions': predictions.tolist(),
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
