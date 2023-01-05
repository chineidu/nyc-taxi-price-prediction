"""
This module is used to download and saving the dataset 
(copied from https://github.com/chineidu/mlops-zoomcamp/blob/main/05-monitoring/prepare.py)
"""

from tqdm import tqdm
import requests

files = [
    ("yellow_tripdata_2022-01.parquet", "."),
    ("yellow_tripdata_2022-01.parquet", "./evidently_service/datasets"),
]

print(f"Download files:")
for file, path in files:
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file}"
    resp = requests.get(url, stream=True)
    save_path = f"{path}/{file}"
    with open(save_path, "wb") as handle:
        for data in tqdm(
            resp.iter_content(),
            desc=f"{file}",
            postfix=f"save to {save_path}",
            total=int(resp.headers["Content-Length"]),
        ):
            handle.write(data)
