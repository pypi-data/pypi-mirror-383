from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os
from pathlib import Path

from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from sksurv.util import Surv
from sksurv.datasets import get_x_y

app = Flask(__name__)

# Global state
resampler = None
model_name = None
X_resampled = None
y_resampled = None


def load_survival_data(X_path, y_path):
    """
    Load survival data from CSV files.
    X: Features
    y: Status (bool), Survival_in_days (float)
    """
    X = pd.read_csv(X_path).values
    y_df = pd.read_csv(y_path)

    # Create structured array for scikit-survival
    y = Surv.from_dataframe('Status', 'Survival_in_days', y_df)

    return X, y, y_df.columns.tolist()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/fit_resample', methods=['POST'])
def fit_resample():
    """
    Perform survival-aware resampling.

    Strategy based on data/raw/src/resampler.py:
    - Undersampling: Sample based on Status, preserve survival times via indices
    - Oversampling/SMOTE: Treat time as feature, resample, then reconstruct
    """
    global resampler, model_name, X_resampled, y_resampled

    try:
        data = request.get_json()
        model_name = data['model']
        dataset_name = data['dataset_name']
        dataset_files = data['dataset']
        sampling_strategy = data.get('sampling_strategy', 'auto')

        # Load training data
        X_path = f"/data/interim/{dataset_files[0]}"
        y_path = f"/data/interim/{dataset_files[1]}"

        X, y, column_names = load_survival_data(X_path, y_path)

        # Get feature column names from X
        X_df = pd.read_csv(X_path)
        feature_columns = X_df.columns.tolist()

        # Create resampler
        if model_name == 'rus':
            resampler = RandomUnderSampler(
                sampling_strategy=sampling_strategy,
                random_state=42
            )
        elif model_name == 'ros':
            resampler = RandomOverSampler(
                sampling_strategy=sampling_strategy,
                random_state=42
            )
        elif model_name == 'smote':
            resampler = SMOTE(
                sampling_strategy=sampling_strategy,
                random_state=42
            )
        else:
            return jsonify({
                "status": "error",
                "message": f"Unknown resampler: {model_name}"
            }), 400

        # Perform resampling
        if model_name == 'rus':
            # Undersampling: sample based on Status only
            X_resampled, _ = resampler.fit_resample(X, y['Status'])
            # Preserve survival times using sample indices
            y_resampled = y[resampler.sample_indices_]

        elif model_name in ['ros', 'smote']:
            # Oversampling/SMOTE: treat time as a feature
            # Append survival time to features
            X_with_time = np.column_stack([X, y['Survival_in_days']])

            # Resample based on event status
            X_resampled_with_time, status_resampled = resampler.fit_resample(
                X_with_time, y['Status']
            )

            # Separate features and time
            X_resampled = X_resampled_with_time[:, :-1]
            time_resampled = X_resampled_with_time[:, -1]

            # Reconstruct structured array
            df_resampled = pd.DataFrame(
                X_resampled,
                columns=feature_columns
            )
            df_resampled['Survival_in_days'] = time_resampled
            df_resampled['Status'] = status_resampled

            # Convert back to sksurv format
            X_resampled, y_resampled = get_x_y(
                df_resampled,
                attr_labels=['Status', 'Survival_in_days'],
                pos_label=1
            )

        # Save resampled data
        output_dir = f"/data/interim/{dataset_name}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Save features
        X_output_path = os.path.join(output_dir, f"X_train_resampled.csv")
        pd.DataFrame(X_resampled, columns=feature_columns).to_csv(
            X_output_path, index=False
        )

        # Save survival data
        y_output_path = os.path.join(output_dir, f"y_train_resampled.csv")
        y_df = pd.DataFrame({
            'Status': y_resampled['Status'],
            'Survival_in_days': y_resampled['Survival_in_days']
        })
        y_df.to_csv(y_output_path, index=False)

        # Statistics
        original_counts = np.unique(y['Status'], return_counts=True)
        resampled_counts = np.unique(y_resampled['Status'], return_counts=True)

        return jsonify({
            "status": "success",
            "message": f"Resampling with {model_name} completed",
            "original_distribution": {
                "censored": int(original_counts[1][0]),
                "events": int(original_counts[1][1])
            },
            "resampled_distribution": {
                "censored": int(resampled_counts[1][0]),
                "events": int(resampled_counts[1][1])
            },
            "original_size": len(y),
            "resampled_size": len(y_resampled),
            "output_files": {
                "X": X_output_path,
                "y": y_output_path
            }
        }), 200

    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/transform', methods=['POST'])
def transform():
    """
    Transform is not applicable for resamplers.
    Resamplers only fit_resample on training data.
    """
    return jsonify({
        "status": "error",
        "message": "transform() not supported for resamplers. Use fit_resample()."
    }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
