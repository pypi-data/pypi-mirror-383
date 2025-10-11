import subprocess
import sys
import os
from typing import Any


import tempfile
from mixtrain.client import MixClient

import time


# def install_package(packages):
#     """Installs a given Python package using pip."""
#     try:
#         subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
#         print(f"Successfully installed {packages}")
#     except subprocess.CalledProcessError as e:
#         print(f"Error installing {packages}: {e}")


# Example usage:
# install_package(["fal_client"])

# import fal_client
import pandas as pd

print(os.environ)
input_dataset_name = "t2i_100"
output_dataset_name = "t2i_eval_results2"
evaluation_name = "t2i_eval2"

model_names = ["fal-ai/hunyuan-image/v3/text-to-image", "fal-ai/qwen-image"]

mix = MixClient(
    api_key="mix-0ffca1a34c351bc3c3e9a19cfbd9e8f3bc72018fa5e8df5a0a295b12d3162187"
)
print("Client initialized")

catalog_config = {
    "type": "sql",
    "uri": "postgresql://postgres.hryawbrfdsohnxynxkmy:FJ1tSLbyKoF2NESm@aws-1-us-east-1.pooler.supabase.com:5432/postgres",
    # "warehouse": "gs://mixtrain-datasets/",
    "warehouse": "/tmp/iceberg_warehouse/default",
}
from pyiceberg.catalog import Catalog, load_catalog

# catalog: Catalog = load_catalog("default", **catalog_config)
# input_dataset = catalog.load_table("test-prod.t2i_100")
input_dataset = mix.get_dataset(input_dataset_name)
print(input_dataset)
print(os.environ)
prompts = input_dataset.scan().to_pandas()["prompt"][:1].tolist()

print(prompts)
exit()


class MixModel:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def run(self, args: dict):
        pass

    def submit(self, args: dict):
        raise NotImplementedError("Submitting is not supported for this model")


class ModalModel(MixModel):
    def __init__(self, model_name: str):
        super().__init__(model_name)


class FalModel(MixModel):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.setup()

    def setup(self):
        os.environ["FAL_KEY"] = mix.get_secret("FAL_KEY")

    def cleanup(self):
        os.environ.pop("FAL_KEY")

    def __del__(self):
        self.cleanup()

    def run(self, args: dict):
        request_id = self.submit(args)
        return self.wait_for_completion(request_id)

    def wait_for_completion(self, request_id: str):
        while True:
            status = fal_client.status(self.model_name, request_id)
            if isinstance(status, fal_client.Completed):
                result = fal_client.result(self.model_name, (request_id))
                return result
            else:
                time.sleep(1)

    def submit(self, args: dict):
        handler = fal_client.submit(
            self.model_name,
            arguments=args,
        )

        request_id = handler.request_id
        return request_id


def get_model(model_name: str) -> MixModel:
    if model_name.startswith("fal-ai/"):  # TODO: handle private models
        return FalModel(model_name)
    elif model_name.startswith("modal/"):
        return ModalModel(model_name)
    else:
        raise ValueError(f"Model {model_name} not supported")


viz_config = {
    "datasets": [
        {
            "columnName": "prompt",
            "tableName": output_dataset_name,
            "dataType": "text",
        },
    ]
}

# columns = [prompt,m1,m2,m3]
# rows = [p1,u1,u2,u3]

# Create dataframe columns: prompt + model names
columns = ["prompt"] + santized_model_names
df = pd.DataFrame(columns=columns)


def evaluate_prompt(prompt, model_name: str):
    results = get_model(model_name).run({"prompt": prompt})
    return results["images"][0]["url"]


# Evaluate each prompt with each model

df = pd.DataFrame({"prompt": prompts})
df[santized_model_names] = pd.DataFrame(
    df["prompt"].map(lambda p: [evaluate_prompt(p, m) for m in model_names]).tolist(),
    index=df.index,
    columns=santized_model_names,
)
print(df)


class MixFlow:
    def __init__(self, evaluation_name: str):
        self.evaluation_name = evaluation_name

    def run(self):
        pass


class T2IEvaluation(MixFlow):
    def __init__(
        self, input_dataset_name: str, evaluation_name: str, model_names: list[str]
    ):
        self.input_dataset_name = input_dataset_name
        self.evaluation_name = evaluation_name
        self.model_names = model_names
        super().__init__(evaluation_name)

    def run(self):
        input_dataset = mix.get_dataset(self.input_dataset_name)
        prompts = input_dataset.scan().to_pandas()["prompt"].tolist()
        df = pd.DataFrame({"prompt": prompts})
        santized_model_names = [
            m.replace("fal-ai/", "").replace("/", "_").replace("-", "_")
            for m in self.model_names
        ]

        df[santized_model_names] = pd.DataFrame(
            df["prompt"]
            .map(lambda p: [evaluate_prompt(p, m) for m in self.model_names])
            .tolist(),
            index=df.index,
            columns=santized_model_names,
        )
        # Create output dataset from results
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            df.to_csv(f.name, index=False)
            mix.delete_dataset(output_dataset_name)
            mix.create_dataset_from_file(output_dataset_name, f.name)

            # Add model columns to viz_config
        for model_name in santized_model_names:
            viz_config["datasets"].append(
                {
                    "columnName": model_name,
                    "tableName": output_dataset_name,
                    "dataType": "link-image",
                }
            )

        mix.create_evaluation(self.evaluation_name, viz_config)


T2IEvaluation(input_dataset_name, evaluation_name, model_names).run()
