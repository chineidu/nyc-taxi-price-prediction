"""
This module is used for checking the data stored on
the MongoDB database.

author: Chinedu Ezeofor
"""
import os
import pandas as pd
from argparse import ArgumentParser
from pprint import pprint as pp
from pymongo import MongoClient


MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27018")

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
    required=True,
    type=int,
)
parser.add_argument(
    "-v", "--verbose", action="count", help="Increase the verbosity", default=0
)
parser.add_argument("-d", "--drop-collection", required=False, type=str)

args = parser.parse_args()
start, stop, drop_coll = (
    args.start_index,
    args.stop_index,
    args.drop_collection,
)


# Create client
client = MongoClient(MONGODB_ADDRESS)
db = client.get_database("prediction_service")  # Create db


data_collection = db.get_collection("data")
data = [*data_collection.find()]  # Convert to list
stored_data_size = len(data)
# Check a slice of the data contained in the list
result = data[start:stop]
if len(result) == 1:
    df = pd.DataFrame(result, index=[0])
df = pd.DataFrame(result)

if drop_coll and drop_coll.lower() == "true":
        db.data.drop()  # Used to drop
        print("Collection `data` dropped!")

if args.verbose >= 1:
    print(f"Data size: {stored_data_size}")  # Size of the data currently stored
    print()
    print(f"Slice of data: \n{df}")

elif args.verbose == 0:
    print(f"Data size: {stored_data_size}")  # Size of the data currently stored