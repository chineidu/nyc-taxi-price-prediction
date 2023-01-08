"""
This module is used for checking the data stored on
the MongoDB database.

author: Chinedu Ezeofor
"""
import os
import typing as tp
from pprint import pprint as pp
from argparse import ArgumentParser

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


def main() -> None:
    """This is the main function for running the project."""
    # Create connection
    db = create_conn()

    parser = ArgumentParser(
        prog="Database size",
        description="For checking the data stored on the MongoDB database.",
    )
    parser.add_argument(
        "--start-index",
        help="The starting index for slicing the result.",
        required=True,
        type=int,
    )
    parser.add_argument(
        "--stop-index",
        help="The stopping index for slicing the result.",
        required=False,
        type=int,
        default=4,
    )
    parser.add_argument(
        "-v", "--verbose", action="count", help="Increase the verbosity", default=0
    )
    parser.add_argument(
        "-d",
        "--drop-collection",
        help="To drop the collection, type: `True`",
        required=False,
        type=str,
        default="false",
    )

    args = parser.parse_args()
    start, stop, drop_coll = (
        args.start_index,
        args.stop_index,
        args.drop_collection,
    )

    data_collection = db.get_collection("data")
    data = [*data_collection.find()]  # Convert to list
    stored_data_size = len(data)

    #Collection for `logs` report
    logs_collection = db.get_collection("report")
    logs = [*logs_collection.find()]

    # Check a slice of the data contained in the list
    result = data[start:stop]
    if len(result) == 1:
        df = pd.DataFrame(result, index=[0])
    df = pd.DataFrame(result)

    if drop_coll and drop_coll.lower() == "true":
        db.data.drop()  # Used to drop
        print(f"WARNING: `data` Collection containing {stored_data_size} records dropped!")
        db.report.drop()
        print(f"WARNING: `report` Collection containing data and quality drift dropped!")

    elif args.verbose >= 2:
        print(f"Data size: {stored_data_size}")  # Size of the data currently stored
        print()
        print(f"Slice of data: from {start} to {stop-1}\n{df}")
        print()
        pp(logs)

    elif args.verbose == 1:
        print(f"Data size: {stored_data_size}")  # Size of the data currently stored
        print()
        print(f"Slice of data: from {start} to {stop-1}\n{df}")

    elif args.verbose == 0 and drop_coll == "false":
        print(f"Data size: {stored_data_size}")  # Size of the data currently stored


if __name__ == "__main__":
    main()
