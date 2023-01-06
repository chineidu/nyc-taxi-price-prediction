"""
This module is used to download and saving the dataset.

"""

from tqdm import tqdm
import requests

files = [
    ("yellow_tripdata_2022-01.parquet", "."),
    ("yellow_tripdata_2022-01.parquet", "./evidently_service/datasets"),
]

print(f"Downloading files ...")
for file, path in files:
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file}"
    response = requests.get(url, stream=True)
    save_path = f"{path}/{file}"
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)

    print(f"Downloading `{file} `into `{save_path}`...")
    with open(save_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
    else:
        print("Downloading of files done!")
