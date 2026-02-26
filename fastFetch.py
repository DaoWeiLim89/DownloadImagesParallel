import requests
from datetime import datetime
import certifi
import threading
import concurrent.futures
import time
import tqdm
import os

# Variable id is used to select which image to download, and to name the file.
# E.g if id = 300, it will download https://picsum.photos/300 and save it as image_300.jpg
url = "https://picsum.photos/"
filename = "image_"

lock = threading.Lock()
def log(status, id, timestamp):
    with lock:
        with open("logger.txt", "a") as f:
            f.write(f"{timestamp} | {url}{id} | {filename}{id}.jpg | {status}\n")

        #print(f"Downloaded: {imagesDownloaded}/{total_images}")

def download_image(id: int):
    retries = 3
    for attempt in range(retries):
        try:
            # timeout=3 means: wait max 3 seconds
            response = requests.get(url + str(id), timeout=3, verify=certifi.where())

            with open(f"images/{filename}{id}.jpg", "wb") as f:
                f.write(response.content)

            log("SUCCESS", id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return True

        except requests.exceptions.Timeout:
            log("TIMEOUT", id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        except Exception:
            log("FAILED", id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def serialDownload(images):
    start_time = time.perf_counter()
    for id in tqdm.tqdm(range(images[0], images[1]), desc="Downloading Serial"):
        download_image(id)

    end_time = time.perf_counter()
    print(f"Serial download took {end_time - start_time:.2f} seconds")

def parallelDownload(images):
    total_images = images[1] - images[0]
    start_time = time.perf_counter()
    imageIDs = [id for id in range(images[0], images[1])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(tqdm.tqdm(
            executor.map(download_image, imageIDs),
            total=total_images,
            desc="Downloading Parallel"
            ))

    end_time = time.perf_counter()
    print(f"Parallel download took {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")

    '''
    if os.path.exists("images"):
        os.rmdir("images") # find a way to delete a full folder
        os.makedirs("images")
    '''
    
    # Clear the log file if it exists
    if os.path.exists("logger.txt"):
        os.remove("logger.txt")

    images = [300, 350]
    serialDownload(images)
    parallelDownload(images)