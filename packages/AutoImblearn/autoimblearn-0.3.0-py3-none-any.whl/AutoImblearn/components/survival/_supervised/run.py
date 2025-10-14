import pandas as pd
import numpy as np

from AutoImblearn.components.model_client.base_estimator import BaseEstimator
import os


class RunSkSurvivalModel(BaseEstimator):
    """
    Docker-based survival analysis model client.

    Supports scikit-survival models:
    - CPH: Cox Proportional Hazards
    - RSF: Random Survival Forest
    - SVM: Fast Survival SVM
    - KSVM: Fast Kernel Survival SVM
    - LASSO: Coxnet with L1 regularization
    - L1: Coxnet with full L1
    - L2: Coxnet with full L2
    - CSA: Coxnet with elastic net (l1_ratio=0.5)
    """

    def __init__(self, model="CPH", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"sksurvival-api",
            container_name=f"{model}_survival_container",
            container_port=8080,
            volume_mounts={
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Docker'):
                    "/code/AutoImblearn/Docker",
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
                "/var/run/docker.sock": "/var/run/docker.sock",
            },
            dockerfile_dir = os.path.dirname(os.path.abspath(__file__)),
        )

    @property
    def payload(self):
        return {
            "metric": self.args.metric,
            "model": self.args.model,
            "dataset_name": self.args.dataset,
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
                f"{self.args.dataset}/X_test_{self.container_name}.csv",
                f"{self.args.dataset}/y_test_{self.container_name}.csv"
            ],
        }
