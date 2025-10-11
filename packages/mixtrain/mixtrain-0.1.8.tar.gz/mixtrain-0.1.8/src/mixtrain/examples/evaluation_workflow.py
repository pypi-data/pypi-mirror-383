"""
Evaluation Workflow Example
This example demonstrates a complete evaluation workflow using the Postrix SDK.
"""

import os
import time

import duckdb
import polars
from postrix.client import (
    URI,
    MixDataset,
    Vector,
    dataset_exists,
    delete_dataset,
    get_eval_status,
    start_eval,
)
from postrix.dataset import create
from postrix.embed_util import embed_text
from pydantic import ConfigDict
from pyiceberg.catalog import load_catalog
from pyiceberg.types import StringType

from logging import getLogger

logger = getLogger(__name__)

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


def generate_embedding(row: InputDataset):
    return embed_text(row.scene_description)


def setup_evaluation_environment():
    """Set up the evaluation environment by creating necessary datasets."""
    workspace_name = "pyiceberg"
    dataset_name = "mixkit8"
    if dataset_exists(dataset_name, workspace_name=workspace_name):
        logger.info(f"Deleting dataset {dataset_name}")
        delete_dataset(dataset_name, workspace_name=workspace_name)
    # dataset = create_dataset(dataset_name, InputDataset, workspace_name=workspace_name)
    file_path = "/Users/dk/Downloads/grouped_metadata.parquet"
    create(dataset_name, file_path=file_path, workspace_name=workspace_name)

    warehouse_path = f"/tmp/new_iceberg_warehouse/{workspace_name}"
    os.makedirs(warehouse_path, exist_ok=True)
    catalog = load_catalog(
        workspace_name,
        **{
            'type': 'sql',
            "uri": f"sqlite:////tmp/new_iceberg_catalog_{workspace_name}.db",
            "warehouse": f"file://{warehouse_path}",
        },
    )
    table = catalog.load_table(f"{workspace_name}.{dataset_name}")
    logger.info(table.schema())
    df = polars.scan_iceberg(table)
    sql_context = polars.SQLContext()
    sql_context.register(dataset_name, df)
    print(sql_context.execute(f"select * from {dataset_name} limit 10").collect())
    print(df.collect())
    with table.update_schema() as update:
        # update.add_column("retries", pa.string(), "Number of retries to place the bid")
        update.add_column("embedding", StringType(), "Embedding for the main text content.")

    logger.info(table.schema)
    con = duckdb.connect(database=':memory:')
    # con.execute("INSTALL vss;")
    # con.execute("LOAD vss;")


    con.execute("CREATE TABLE my_vector_table (vec FLOAT[3]);")
    con.execute("INSERT INTO my_vector_table SELECT array_value(a, b, c) FROM range(1, 10) ra(a), range(1, 10) rb(b), range(1, 10) rc(c);")
    # con.execute("CREATE INDEX my_hnsw_index ON my_vector_table USING HNSW (vec);")
    print(con.execute("SELECT * FROM my_vector_table ORDER BY array_distance(vec, [1, 2, 3]::FLOAT[3]) LIMIT 1;").fetchall())


    df = table.scan().to_duckdb(table_name="df", connection=con)
    result = con.sql("select * from df limit 10")
    # print(result.columns)
    print(result.fetchall())
    # con.execute("INSTALL postgres;")
    # con.execute("LOAD ducklake;")



    # dataset.generate_column(
    #     input_column='scene_description',
    #     func=generate_embedding,
    #     output_column='scene_description_embedding'
    #     # optional length figured out automatically for known models.
    # )

    # row = dataset[0]

    # append the file to the dataset

    # ensure the file columns match the dataset schema
    # df = pd.read_parquet(file_path)
    # df = df.drop(columns=["id"])
    # print(df.columns)
    # dataset.append(df)


    # dataset.run(InputDataset.generate_embedding)
    # Create a sample row; URI is a str subclass so instantiate with the raw URL string
    # d1 = InputDataset(caption="This is a test caption", image=URI("https://example.com/image.jpg"))


def run_evaluation():
    """Run the evaluation process and monitor its progress."""
    print("\nStarting evaluation...")
    start_eval()

    # Monitor evaluation status
    print("\nMonitoring evaluation progress...")
    for _ in range(3):
        get_eval_status()
        time.sleep(2)  # Check status every 2 seconds

def main():
    print("=== Evaluation Workflow Example ===")

    # Set up the evaluation environment
    setup_evaluation_environment()

    # Run and monitor evaluation
    # run_evaluation()

    print("\nEvaluation workflow completed!")

if __name__ == "__main__":
    main()
