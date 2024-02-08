import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import zipfile
from googleapiclient.errors import HttpError

# Load credentials from token.json
creds = Credentials.from_authorized_user_file('token.json')

# Build the Drive API service
drive_service = build('drive', 'v3', credentials=creds)

# Read file IDs from Gdocs.txt
file_ids = []
with open('GdocIDs.txt', 'r') as file:
    file_ids = [line.strip() for line in file]

# Create a zip archive (you can compress the files afterward)
output_zip_file = 'compressed_docs.zip'
zipf = zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED)

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

        # Save the downloaded file to the zip archive with the custom name
        file_name = f"resume_{file_id}.rtf" if file_metadata['mimeType'] == 'application/vnd.google-apps.document' else file_metadata['name']
        zipf.writestr(file_name, file_content.getvalue())

        print(f"File '{file_metadata['name']}' downloaded and added to zip archive")

    except HttpError as e:
        # Handle the HttpError, for example, print the error message
        print(f"Error downloading file with ID '{file_id}': {e}")

# Split file IDs into batches of 1000
batch_size = 1000
for i in range(0, len(file_ids), batch_size):
    batch_ids = file_ids[i:i + batch_size]
    for x, file_id in enumerate(batch_ids):
        download_and_save_file(file_id)
        print(x/len(file_ids))

# Close the zip file
zipf.close()

print("All files downloaded and added to the zip archive 'compressed_docs.zip'.")
