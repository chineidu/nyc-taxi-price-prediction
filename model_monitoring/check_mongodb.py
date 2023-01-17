"""
This module is used for checking the data stored on
the MongoDB database.

author: Chinedu Ezeofor
"""
import os
import typing as tp
from pprint import pprint as pp

import click
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


def create_conn() -> tp.Any:
    """This is used to create a connection to the database."""
    MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27018")
    try:
        # Create client
        client = MongoClient(MONGODB_ADDRESS)
        db = client.get_database("prediction_service")  # Create db
        print("Connection successful!\n")
        return db
    except ServerSelectionTimeoutError as e:
        print(e)
        print("Connection NOT successful!")


@click.command()
@click.option("--start-index", help="The start index", default=0)
@click.option("--stop-index", help="The stop index", default=4)
@click.option("-v", "--verbose", help="Increase the verbosity.", default=0, count=True)
@click.option("-d", "--drop", help="Drop the collection", default="false", show_default=True)
def main(start_index: int, stop_index: int, verbose: int, drop: str) -> None:
    """This is the main function for running the project."""
    # Create connection
    db = create_conn()
    data_collection = db.get_collection("data")
    data = [*data_collection.find()]  # Convert to list
    stored_data_size = len(data)

    # Collection for `logs` report
    logs_collection = db.get_collection("report")
    logs = [*logs_collection.find()]

    # Check a slice of the data contained in the list
    result = data[start_index:stop_index]
    if len(result) == 1:
        df = pd.DataFrame(result, index=[0])
    df = pd.DataFrame(result)

    if drop and drop.lower() == "true":
        db.data.drop()  # Used to drop
        click.echo(
            click.style(
                f"WARNING: `data` Collection containing {stored_data_size} records dropped!",
                fg="red",
                bold=True,
            )
        )
        db.report.drop()
        click.echo(
            click.style(
                "WARNING: `report` Collection containing data and quality drift dropped!",
                fg="red",
                bold=True,
            )
        )

    elif verbose >= 2:
        click.echo(
            click.style(f"Data size: {stored_data_size}", fg="green", bold=True)
        )  # Size of the data currently stored
        click.echo()
        click.echo(f"Slice of data: from {start_index} to {stop_index-1}\n{df}")
        click.echo()
        pp(logs)

    elif verbose == 1:
        click.echo(
            click.style(f"Data size: {stored_data_size}", fg="green", bold=True)
        )  # Size of the data currently stored
        click.echo()
        click.echo(f"Slice of data: from {start_index} to {stop_index-1}\n{df}")

    elif verbose == 0 and drop == "false":
        click.echo(f"Data size: {stored_data_size}")  # Size of the data currently stored


if __name__ == "__main__":
    # hello()
    main()
