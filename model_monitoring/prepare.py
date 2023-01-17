"""
This module is used to download and saving the dataset.

"""

import requests  # type: ignore
from tqdm import tqdm

files = [
    ("yellow_tripdata_2022-01.parquet", "."),
    ("yellow_tripdata_2022-01.parquet", "./evidently_service/datasets"),
]

print("Downloading files ...")
for file, path in files:
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file}"
    response = requests.get(url, stream=True)
    save_path = f"{path}/{file}"
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)

    print(f"Downloading `{file} `into `{save_path}`...")
    with open(save_path, "wb") as file:  # type: ignore
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)  # type: ignore
    progress_bar.close()

    if total_size_in_bytes not in {0, progress_bar.n}:
        print("ERROR, something went wrong")
    else:
        print("Downloading of files done!")
