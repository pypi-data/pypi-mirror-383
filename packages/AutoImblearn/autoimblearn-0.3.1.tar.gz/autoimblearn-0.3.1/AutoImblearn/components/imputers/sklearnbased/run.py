# AutoImblearn/components/imputers/sklearnbased/run.py
from functools import cached_property
import os

from AutoImblearn.components.model_client.base_transformer import BaseTransformer


class RunSklearnImpute(BaseTransformer):
    # TODO make model parameter work

    def __init__(self, model="ii", data_folder=None, categorical_columns=None, impute_file_path=None, **imputer_kwargs):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"sklearnimpute-api",
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
        self.model = model
        self.categorical_columns = categorical_columns
        self.impute_file_path = impute_file_path
        self.impute_file_name = os.path.basename(self.impute_file_path)
        self.imputer_kwargs = imputer_kwargs

    @cached_property
    def payload(self):
        # Get hyperparameters: first check args.hyperparams, then fall back to self.imputer_kwargs
        imputer_params = self.imputer_kwargs  # From constructor
        if hasattr(self.args, 'hyperparams') and self.args.hyperparams:
            # Override with hyperparams from args if provided
            imputer_params = self.args.hyperparams.get(self.model, imputer_params)

        # Imputers only need X (features), not y (target)
        # Imputation is unsupervised - it fills missing values based on feature patterns
        # Files are saved to /data/interim/{dataset_name}/
        return {
            "metric": self.args.metric,
            "model": self.model,
            "dataset_name": self.args.dataset,
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                # f"{self.args.dataset}/X_test_{self.container_name}.csv"
            ],
            "categorical_columns": self.categorical_columns,
            "imputer_kwargs": imputer_params,  # Pass hyperparameters
            "impute_file_name": self.impute_file_name
        }

