"""
Curation Workflow Example
This example demonstrates a complete curation workflow using the Postrix SDK.
"""

import logging

import pandas as pd
from postrix.client import URI, MixDataset, Vector, create_dataset
from pydantic import ConfigDict

logger = logging.getLogger(__name__)

class InputDataset(MixDataset):
    # Allow non-standard types like `postrix.client.URI` and the embedding Field
    model_config = ConfigDict(arbitrary_types_allowed=True)
    caption: str
    image: URI
    embedding: Vector | None = Vector(
        on_column="caption",
        model="openai",
        frequency="on_demand",
        description="Embedding for the main text content."
    )


def main():
    print("=== Curation Workflow Example ===")
    dataset_name = "test_video_dataset"
    # delete_dataset(dataset_name)
    dataset = create_dataset(dataset_name, InputDataset)
    df = pd.DataFrame([
        {"caption": "This is a test caption", "image": URI("https://example.com/image.jpg")},
        {"caption": "This is a test caption", "image": URI("https://example.com/image.jpg")},
    ])
    dataset.append(df)
    rows_to_append = dataset.query(f"SELECT * FROM {dataset_name}")
    for row in rows_to_append:
        row.caption = "This is a test caption"
        row.image = URI("https://example.com/image.jpg")
    dataset.append(rows_to_append)
    dataset.run(InputDataset.generate_embedding)
    # Set up the evaluation environment

    print("\nCuration workflow completed!")

if __name__ == "__main__":
    main()
