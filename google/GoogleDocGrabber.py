import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from googleapiclient.errors import HttpError
import concurrent.futures

# Load credentials from token.json
creds = Credentials.from_authorized_user_file('creds/token.json')

# Build the Drive API service
drive_service = build('drive', 'v3', credentials=creds)

# Read file IDs from Gdocs.txt
file_ids = []
with open('GdocIDs.txt', 'r') as file:
    file_ids = [line.strip() for line in file]

output_dir = 'out'  # Removed the leading '/' as it is not needed for creating the directory

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to download and save a file
def download_and_save_file(file_id):
    try:
        # Request file metadata
        file_metadata = drive_service.files().get(fileId=file_id).execute()

        # Check if the file is a Google Docs file (doc, docx, etc.)
        if file_metadata['mimeType'] == 'application/vnd.google-apps.document':
            # Export the file as RTF
            request = drive_service.files().export_media(fileId=file_id, mimeType='application/rtf')
        else:
            # Download the file as is
            request = drive_service.files().get_media(fileId=file_id)

        # Create a bytes IO stream to save the file content
        file_content = io.BytesIO()

        # Download the file
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")

        # Save the downloaded file to the output directory with the custom name
        file_name = f"resume_{file_id}.rtf" if file_metadata['mimeType'] == 'application/vnd.google-apps.document' else file_metadata['name']
        with open(os.path.join(output_dir, file_name), 'wb') as scraped_file:  # Use 'wb' for binary data
            scraped_file.write(file_content.getvalue())

        print(f"File '{file_metadata['name']}' downloaded and saved in '{output_dir}'")

    except HttpError as e:
        # Handle the HttpError, for example, print the error message
        print(f"Error downloading file with ID '{file_id}': {e}")

# Add the following block at the end of your script
if __name__ == '__main__':
    # Split file IDs into batches of 1000
    batch_size = 1000
    for i in range(0, len(file_ids), batch_size):
        batch_ids = file_ids[i:i + batch_size]
        with concurrent.futures.ProcessPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(download_and_save_file, file_id): file_id for file_id in batch_ids}
            for future in concurrent.futures.as_completed(futures):
                file_id = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Download for file with ID '{file_id}' raised an exception: {e}")

    print("All files downloaded and added to the zip archive 'compressed_docs.zip'.")
