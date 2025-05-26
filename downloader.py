# download all the papers from the url and save them to the data folder, naming convention is as follows: papers/year-paper1.pdf, papers/year-paper2.pdf, markingscheme/year-markingscheme.pdf, and for later years, deferrepaper/year-paper1.pdf, deferrepaper/year-paper2.pdf, deferredmarkingscheme/year-markingscheme.pdf

import requests
import os
import json
import time
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create necessary directories
directories = ["papers", "markingscheme", "deferredpaper", "deferredmarkingscheme"]
for dir_name in directories:
    Path(dir_name).mkdir(exist_ok=True)

# Base URLs for different types of documents
PAPER_BASE_URL = "https://www.examinations.ie/archive/exampapers/"
MARKING_SCHEME_BASE_URL = "https://www.examinations.ie/archive/markingschemes/"

# Configure retry strategy
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
)

# Create a session with retry strategy
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Load the data
with open("hl-maths-data.json", "r") as f:
    data = json.load(f)


def download_file(url, save_path):
    """Download a file from the given URL and save it to the specified path."""
    try:
        # Add a delay between requests to avoid rate limiting
        time.sleep(0.5)  # 2 second delay between requests

        response = session.get(url)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"Successfully downloaded: {save_path}")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"File not found: {url}")
        else:
            print(f"HTTP Error downloading {url}: {str(e)}")
        return False
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False


# Iterate through each year
for year, year_data in data.items():
    print(f"\nProcessing year {year}...")

    # Process each type of document
    for doc_type, documents in year_data.items():
        for doc in documents:
            # Determine the save directory based on document type
            if doc_type == "Exam Paper":
                save_dir = "papers"
                base_url = PAPER_BASE_URL
            elif doc_type == "Marking Scheme":
                save_dir = "markingscheme"
                base_url = MARKING_SCHEME_BASE_URL
            elif doc_type == "Deferred Exam Paper":
                save_dir = "deferredpaper"
                base_url = PAPER_BASE_URL
            elif doc_type == "Deferred Marking Scheme":
                save_dir = "deferredmarkingscheme"
                base_url = MARKING_SCHEME_BASE_URL
            else:
                continue

            # Create the filename
            if "Paper One" in doc["details"]:
                paper_num = "1"
            elif "Paper Two" in doc["details"]:
                paper_num = "2"
            else:
                paper_num = ""

            # Construct the save path
            if paper_num:
                save_path = f"{save_dir}/{year}-paper{paper_num}.pdf"
            else:
                save_path = f"{save_dir}/{year}-markingscheme.pdf"

            # Construct the full URL with year in the path
            full_url = f"{base_url}{year}/{doc['url']}"

            # Try to download the file
            success = download_file(full_url, save_path)

            # If failed, try alternative URL patterns
            if not success:
                # Try without the year in the path
                alt_url = f"{base_url}{doc['url']}"
                download_file(alt_url, save_path)

print("\nDownload process completed!")
