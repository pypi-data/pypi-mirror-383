import pandas as pd
import numpy as np

from AutoImblearn.components.model_client.base_transformer import BaseTransformer
import os


class RunSurvivalResampler(BaseTransformer):
    """
    Docker-based survival resampler client.

    Supports resampling methods that preserve survival data structure:
    - rus: Random Under Sampling (preserves censoring info)
    - ros: Random Over Sampling (treats time as feature)
    - smote: SMOTE (treats time as feature, then reconstructs)
    """

    def __init__(self, model="rus", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"survivalresampler-api",
            container_name=f"{model}_survival_resampler_container",
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
        # Survival resamplers only work on training data
        return {
            "metric": self.args.metric,
            "model": self.args.model,
            "dataset_name": self.args.dataset,
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
            ],
        }
