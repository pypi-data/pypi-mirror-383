"""
Flask REST API for dimensionality reduction models.

Supports various dimensionality reduction algorithms.
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


def get_model(name, n_components=2):
    """
    Get the appropriate dimensionality reduction model.

    Args:
        name: Model name
        n_components: Number of components/dimensions

    Returns:
        Model instance
    """
    if name == 'pca':
        from sklearn.decomposition import PCA
        return PCA(n_components=n_components, random_state=42)

    elif name == 'tsne':
        from sklearn.manifold import TSNE
        return TSNE(n_components=n_components, random_state=42, n_iter=1000)

    elif name == 'umap':
        try:
            import umap
            return umap.UMAP(n_components=n_components, random_state=42)
        except ImportError:
            raise ValueError("UMAP not installed. Install with: pip install umap-learn")

    elif name == 'svd':
        from sklearn.decomposition import TruncatedSVD
        return TruncatedSVD(n_components=n_components, random_state=42)

    elif name == 'ica':
        from sklearn.decomposition import FastICA
        return FastICA(n_components=n_components, random_state=42)

    elif name == 'nmf':
        from sklearn.decomposition import NMF
        return NMF(n_components=n_components, random_state=42, init='nndsvda')

    else:
        raise ValueError(f"Unknown dimensionality reduction model: {name}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': model_name}), 200


@app.route('/fit', methods=['POST'])
def fit():
    """
    Fit dimensionality reduction model.

    Expected JSON:
    {
        "model_name": "pca",
        "X_train_path": "/data/interim/dataset/X_train.csv",
        "n_components": 2
    }
    """
    global model, model_name

    try:
        data = request.get_json()
        model_name = data.get('model_name', 'pca')
        X_train_path = data['X_train_path']
        n_components = data.get('n_components', 2)

        # Load data
        X_train = pd.read_csv(X_train_path).values

        # Get model
        model = get_model(model_name, n_components=n_components)

        # Fit model
        model.fit(X_train)

        # Save model
        model_path = '/tmp/reduction_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        # Calculate training metrics
        metrics = {}
        if hasattr(model, 'explained_variance_ratio_'):
            metrics['explained_variance_ratio'] = model.explained_variance_ratio_.tolist()
            metrics['cumulative_variance'] = float(np.sum(model.explained_variance_ratio_))

        if hasattr(model, 'kl_divergence_'):
            metrics['kl_divergence'] = float(model.kl_divergence_)

        return jsonify({
            'status': 'success',
            'message': f'Model {model_name} fitted successfully',
            'model_path': model_path,
            'metrics': metrics
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/predict', methods=['POST'])
def predict():
    """
    Transform data to reduced dimensionality.

    Expected JSON:
    {
        "X_test_path": "/data/interim/dataset/X_test.csv"
    }

    Returns:
        Transformed data and metrics
    """
    global model, model_name

    try:
        if model is None:
            # Load saved model
            model_path = '/tmp/reduction_model.pkl'
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

        data = request.get_json()
        X_test_path = data['X_test_path']

        # Load test data
        X_test = pd.read_csv(X_test_path).values

        # Transform
        if model_name in ['tsne', 'umap']:
            # t-SNE and UMAP don't support transform, must use fit_transform
            # For test data, we refit (not ideal but necessary for t-SNE/UMAP)
            X_transformed = model.fit_transform(X_test)
        else:
            X_transformed = model.transform(X_test)

        # Calculate metrics
        metrics = {}

        # Reconstruction error (for models that support inverse_transform)
        if hasattr(model, 'inverse_transform'):
            try:
                X_reconstructed = model.inverse_transform(X_transformed)
                reconstruction_error = np.mean((X_test - X_reconstructed) ** 2)
                metrics['reconstruction_error'] = float(reconstruction_error)
            except:
                pass

        # Explained variance
        if hasattr(model, 'explained_variance_ratio_'):
            metrics['explained_variance_ratio'] = model.explained_variance_ratio_.tolist()
            metrics['cumulative_variance'] = float(np.sum(model.explained_variance_ratio_))

        # KL divergence (t-SNE)
        if hasattr(model, 'kl_divergence_'):
            metrics['kl_divergence'] = float(model.kl_divergence_)

        # Save transformed data
        transformed_path = '/tmp/X_transformed.csv'
        pd.DataFrame(X_transformed).to_csv(transformed_path, index=False)

        return jsonify({
            'status': 'success',
            'transformed_path': transformed_path,
            'transformed_shape': list(X_transformed.shape),
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
