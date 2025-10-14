import pandas as pd

# from ..model_client.base_model_client import BaseDockerModelClient
from AutoImblearn.components.model_client.base_transformer import BaseTransformer
import os


class RunImblearnSampler(BaseTransformer):
    # TODO make model parameter work

    def __init__(self, model="rus", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"imblearnsampler-api",
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
            # args.hyperparams is a dict: {'smote': {'k_neighbors': 7}, 'lr': {...}}
            hyperparams = self.args.hyperparams.get(self.args.model, None)

        # Resamplers only work on training data to balance classes
        # Test data should NEVER be resampled - it must maintain real-world distribution
        return {
            "metric": self.args.metric,
            "model": self.args.model,
            "dataset_name": self.args.dataset,  # Required for saving results
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
            ],
            "params": hyperparams,  # Pass hyperparameters (or None for defaults)
        }

