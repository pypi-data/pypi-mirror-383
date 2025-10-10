import pandas as pd

# from ..model_client.base_model_client import BaseDockerModelClient
from AutoImblearn.components.model_client.base_transformer import BaseTransformer
from AutoImblearn.processing.utils import SHARED_HOST_DIR
import os


class RunImblearnSampler(BaseTransformer):
    # TODO make model parameter work

    def __init__(self, model="rus"):
        super().__init__(
            image_name=f"imblearnsampler-api",
            container_name=f"{model}_container",
            # TODO make port dynamic
            container_port=8080,
            volume_mounts={
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Docker'):
                    "/code/AutoImblearn/Docker",
                SHARED_HOST_DIR: {
                    'bind': '/data',
                    'mode': 'rw'
                },
                "/var/run/docker.sock": "/var/run/docker.sock",  # give container full control of docker
            },  # mount current dir
            dockerfile_dir = os.path.dirname(os.path.abspath(__file__)),
        )

    @property
    def payload(self):
        # Resamplers only work on training data to balance classes
        # Test data should NEVER be resampled - it must maintain real-world distribution
        return {
            "metric": self.args.metric,
            "model": self.args.model,
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
            ],
        }

