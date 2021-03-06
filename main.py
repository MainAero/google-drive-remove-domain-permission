from google.oauth2 import service_account
from pprint import pprint
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload
import shutil
import json
from argparse import ArgumentParser
import sys
import time


def print_status(index, status):
    if index > 0 and index % 30 == 0:
        print(status)
    else:
        sys.stdout.write(status)
        sys.stdout.flush()
        
def get_drive_service(email):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'service.json'
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    delegated_credentials = credentials.with_subject(email)
    drive_service = build('drive', 'v3', credentials=delegated_credentials)
    return drive_service

def get_files(drive_service, email, page_token, drive_id=None, counter=0):
    try:
        query=None
        corpora=None
        if email and drive_id == None:
            query = "'"+email+"' in owners"
        if drive_id:
            corpora = 'drive'

        return drive_service.files().list(q=query,
                                            driveId=drive_id,
                                            corpora=corpora,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            includeItemsFromAllDrives=True,
                                            supportsAllDrives=True,
                                            pageToken=page_token).execute()
    except:
        counter+=1
        time.sleep(1)
        if counter > 10:
            print('API error on fetching files for %s' % email)
            return
        return get_files(drive_service, email, page_token, counter)

def get_permissions(drive_service, file_id, counter=0):
    try:
        return drive_service.permissions().list(fileId=file_id,supportsAllDrives=True).execute()
    except:
        counter+=1
        time.sleep(1)
        if counter > 10:
            print('API error on getting permissions for file %s' % file_id)
            return
        return get_permissions(drive_service, file_id, counter)


def delete_permission(drive_service, file_id, p_id, counter=0):
    try:
        drive_service.permissions().delete(fileId=file_id, permissionId=p_id, supportsAllDrives=True).execute()
    except:
        counter+=1
        time.sleep(1)
        if counter > 10:
            print('API error on deleting permission for file %s' % file_id)
            return
        delete_permission(drive_service, file_id, p_id, counter)

def main():
    print('')
    parser = ArgumentParser(description='Removes the domain permission of all files and folders in Google Drive of a domain user')
    parser.add_argument('-e', '--email', dest='email', required=True,
                    help='email of the user')
    parser.add_argument('-d', '--driveId', dest='drive_id', required=False,
                    help='drive id if you want to apply it on a shared drive')

    if len(sys.argv)==1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()  
    EMAIL = args.email
    DRIVE_ID = args.drive_id

    print('Recursive checking all files / folders of %s ...' % (EMAIL))

    drive_service = get_drive_service(EMAIL)
    deleted_permissions = []
    page_token = None
    index = 1

    while True:
        response = get_files(drive_service, EMAIL, page_token, DRIVE_ID)
        for file in response.get('files', []):
            status='.'
            res = get_permissions(drive_service, file.get('id'))
            permissions = res['permissions']

            for p in permissions:
                if p['type'] == "domain":
                    delete_permission(drive_service, file.get('id'), p['id'])
                    deleted_permissions.append(file)
                    status='d'
            print_status(index, status)
            index += 1

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    
    print('Deleted permissions of %s files / folders:' % len(deleted_permissions))
    for item in deleted_permissions:
        print('- %s (%s)' % (file.get('name'), file.get('id')))

if __name__ == '__main__':
    main()