
import os
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http

# NOTE: if modifying these scopes, delete the file token.json
g_scopes = ['https://www.googleapis.com/auth/drive.metadata.readonly']

class GoogleDriveClient:
    def __init__(self, token_full_path: str, creds_full_path: str):
        self.token_full_path = token_full_path
        self.creds_full_path = creds_full_path
        self.google_drive_service : googleapiclient.discovery.Resource = self.ConnectToGoogleCloud()

    # public
    def RefreshMetadataTree(self):
        try:
            # results = service.files().list(pageSize=50, fields="nextPageToken, files(id, name)").execute()
            # q="mimeType='application/vnd.google-apps.folder'",
            # q="mimeType='application/vnd.google-apps.file'"
            result = self.google_drive_service.files().list(
                q="mimeType!='application/vnd.google-apps.presentation' and mimeType!='application/vnd.google-apps.spreadsheet' and mimeType!='application/vnd.google-apps.document'",
                pageSize=1000,
                fields='files(id,name,parents,mimeType)').execute()

            files_meta = result.get('files', [])

            if not files_meta:
                print('No files found.')
                return 1

            print('--------------------------')
            print('files on my cloud storage:')
            print('count: {}'.format(len(files_meta)))
            print('--------------------------')
            for file_meta in files_meta:
                # print("{} {} {}".format(file_meta['name'], file_meta['id'], file_meta['fullFileExtension']))
                print(file_meta)

        except googleapiclient.errors.HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f'An error occurred: {error}')

    def GetMetadataTree(self):
        pass

    def DownloadEntity(self, file_id: str):
        # pylint: disable=maybe-no-member
        request = self.google_drive_service.files().get_media(fileId=file_id)
        file = io.BytesIO()

        downloader = googleapiclient.http.MediaIoBaseDownload(file, request)

        done = False
        status: googleapiclient.http.MediaDownloadProgress = None
        while done == False:
            status, done = downloader.next_chunk()
            print("download progress: {}".format(int(status.progress() * 100)))


    def UploadEntity(self, file_name: str, parent_dir_id: str) -> bool:
            if len(file_name) == 0:
                print("name of file for upload is empty")
                return False

            if not os.path.exists(file_name):
                print("file for upload is not exist")
                return False

            if len(parent_dir_id) == 0:
                print("parent dir id for uploadable file is empty")
                return False

            # TODO: find such id in metadata
            base_name_of_file = ""

            file_metadata = {'name': file_name, 'parents': [parent_dir_id]}
            media = googleapiclient.http.MediaFileUpload(base_name_of_file, mimetype='image/jpeg', resumable=True)

            # pylint: disable=maybe-no-member
            file = self.google_drive_service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()

            print(F'File ID: "{file.get("id")}".')
            return True

    def RemoveEntity(self):
        pass

    # private
    def ConnectToGoogleCloud(self) -> googleapiclient.discovery.Resource:
        try:
            creds = None

            # the file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists(self.token_full_path):
                creds = Credentials.from_authorized_user_file(self.token_full_path, g_scopes)

            # if there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.creds_full_path, g_scopes)
                    creds = flow.run_local_server(port=0)
                # save the credentials for the next run
                with open(self.token_full_path, 'w') as token_file:
                    token_file.write(creds.to_json())

            return googleapiclient.discovery.build('drive', 'v3', credentials=creds)

        except googleapiclient.errors.HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f'An error occurred: {error}')


