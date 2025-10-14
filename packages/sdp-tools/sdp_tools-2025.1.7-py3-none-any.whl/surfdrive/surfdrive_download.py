from os import getenv
from sys import argv

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

SURFDRIVE_WEBDAV = "https://surfdrive.surf.nl/files/public.php/webdav"

# Get credentials from environment variables
share_token = getenv("SURFDRIVE_SHARE_TOKEN")
password = getenv("SURFDRIVE_PASSWORD")


def download_surfdrive_csv(filename):
    """Download CSV from SURFdrive public share and return as DataFrame"""

    # Setup authentication
    auth = HTTPBasicAuth(share_token, password)

    response = requests.get(SURFDRIVE_WEBDAV, auth=auth)

    if response.status_code == 200:
        # Convert to DataFrame
        df = pd.read_csv(pd.io.common.StringIO(response.text))
        print(f"Downloaded successfully! Shape: {df.shape}")
        return df
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def main():
    # Handle command line arguments
    if len(argv) > 1:
        path = argv[1]
        # Download the CSV
        df = download_surfdrive_csv(path)

        if df is not None:
            # Show basic info
            print(df.head())

            # Save to local file
            df.to_csv(path, index=False)
            print("Saved to {path}")

    else:
        # List uploaded objects
        print("\nFile name not provided ... skipping.")


if __name__ == "__main__":
    main()
