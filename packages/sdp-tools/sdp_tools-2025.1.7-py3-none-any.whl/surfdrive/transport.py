from pathlib import Path
from sys import argv

import minio_upload
import surfdrive_download


def main():
    # Handle command line arguments
    if len(argv) > 1:
        filename = argv[1]
        fullpath = "/tmp/" + filename

        # Download the CSV
        df = surfdrive_download.download_surfdrive_csv(filename)

        if df is None:
            raise (f"\nCan not download {filename}")
        else:
            # Show basic info
            print(df.head())

            # Save to local file
            df.to_csv(fullpath, index=False)
            # print("Saved to {fullpath}")

            if Path(fullpath).is_file():
                print(f"Uploading file: {fullpath}")
                minio_upload.upload_file(filename, fullpath)
            else:
                raise (f"File {fullpath} is missing")

    else:
        # List uploaded objects
        print("\nFile name not provided ... skipping.")


if __name__ == "__main__":
    main()
