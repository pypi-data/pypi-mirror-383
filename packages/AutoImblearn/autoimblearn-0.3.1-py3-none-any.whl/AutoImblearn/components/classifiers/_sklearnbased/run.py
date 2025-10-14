import pandas as pd

# from ..model_client.base_model_client import BaseDockerModelClient
from AutoImblearn.components.model_client.base_estimator import BaseEstimator
import os


class RunSklearnClf(BaseEstimator):
    # TODO make model parameter work

    def __init__(self, model="svm", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"sklearnclf-api",
            container_name=f"{model}_container",
            # TODO make port dynamic
            container_port=8080,
            volume_mounts={
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Docker'):
                    "/code/AutoImblearn/Docker",
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
                "/var/run/docker.sock": "/var/run/docker.sock",  # give container full control of docker
            },  # mount current dir
            dockerfile_dir = os.path.dirname(os.path.abspath(__file__)),
        )

    @property
    def payload(self):
        # Get hyperparameters for this specific model (if provided)
        hyperparams = None
        if hasattr(self.args, 'hyperparams') and self.args.hyperparams:
            # args.hyperparams is a dict: {'lr': {'C': 0.1, 'penalty': 'l1'}, 'smote': {...}}
            hyperparams = self.args.hyperparams.get(self.args.model, None)

        return {
            "metric": self.args.metric,
            "model": self.args.model,
            "dataset_name": self.args.dataset,  # Required for saving fitted models
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
                f"{self.args.dataset}/X_test_{self.container_name}.csv",
                f"{self.args.dataset}/y_test_{self.container_name}.csv"
            ],
            "params": hyperparams,  # Pass hyperparameters (or None for defaults)
        }

