import os
import csv
import json
import boto3
import gspread
import logging
import datetime
import dateparser
from time import sleep
from gspread_formatting import Color, CellFormat, format_cell_range
from oauth2client.service_account import ServiceAccountCredentials

from backup_reporter.dataclass import BackupMetadata, BackupFileInfo


class BackupCollector:
    def __init__(self, buckets: list,
            google_spreadsheet_credentials_path: str,
            spreadsheet_name: str,
            worksheet_name: str,
            sheet_owner: str) -> None:
        self.buckets = buckets
        self.credentials_path = google_spreadsheet_credentials_path
        self.spreadsheet_name = spreadsheet_name
        self.worksheet_name = worksheet_name
        self.sheet_owner = sheet_owner

        self.color_neutral = Color(1,1,1) # White
        self.color_warning = Color(1,0.5,0) # Orange
        self.color_alarm = Color(1,0,0) # Red

    def _collect_from_bucket(
            self,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            aws_region: str,
            s3_path: str,
            aws_endpoint_url: str = None) -> BackupMetadata:

        kwargs = {
           "aws_access_key_id": aws_access_key_id,
           "aws_secret_access_key": aws_secret_access_key,
           "region_name": aws_region,
           "endpoint_url": aws_endpoint_url
        }

        s3 = boto3.resource(
            's3',
            **{k:v for k,v in kwargs.items() if v is not None}
        )

        logging.info(f"Collect metadata from {s3_path} ...")

        metadata_file_name = "/".join(s3_path.split("/")[3:])
        s3_path = s3_path.split("/")[2]
        metadata = s3.Object(s3_path, metadata_file_name).get()['Body'].read().decode("utf-8")
        metadata = json.loads(metadata)

        result = BackupMetadata()
        result.type = metadata.get("type", "None")
        result.size = metadata.get("size", "None")
        result.time = metadata.get("time", "None")
        result.customer = metadata.get("customer", "None")
        result.placement = metadata.get("placement", "None")
        result.backup_name = metadata.get("backup_name", "None")
        result.description = metadata.get("description", "None")
        result.count_of_backups = metadata.get("count_of_backups", "None")
        result.last_backup_date = metadata.get("last_backup_date", "None")
        result.supposed_backups_count = metadata.get("supposed_backups_count", "None")
        result.sha1sum = metadata.get("sha1sum", "None")
        for item in metadata.get("backups", []):
            result.backups.append(BackupFileInfo(
                backup_name=item.get("backup_name", "None"),
                size=item.get("size", "None"),
                backup_date=item.get("backup_date", "None"),
                sha1sum=item.get("sha1sum", "None")
            ))
        logging.info(f"Collect metadata from {s3_path} complete")
        return result

    def _csv_write(self, data: list, csv_path: str) -> None:
        with open(csv_path, 'a') as csvfile:
            csv_file = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in data:
                csv_file.writerow(row)

    def _compile_csv(self, metadata: list) -> str:
        logging.info(f"Compile csv file")
        csv_path = "tmp_report.csv"
        self._csv_write([[ "Customer", "DB type", "Backup Placement", "Size in MB", "Backup time spent", "Backup name", "Backup sha1 hash sum", "Backups count", "Supposed Backups Count", "Last Backup Date", "Description" ]], csv_path)

        backups_info = []
        for data in metadata:
            row = [ data.customer, data.type, data.placement, data.size, data.time, data.backup_name, data.sha1sum, data.count_of_backups, data.supposed_backups_count, data.last_backup_date, data.description ]
            backups_info.append(row)

        self._csv_write(backups_info, csv_path)

        return csv_path

    def _compile_file_backups_csv(self, metadata: list) -> str:
        logging.info(f"Compile csv file")
        csv_path = "tmp_report_file_backups.csv"
        self._csv_write([[ "Customer", "Description", "Backup name", "Backup sha1 hash sum", "Size in MB", "Backup Date" ]], csv_path)

        backups_info = []
        for data in metadata:
            if data.backups:
                for backup_file in data.backups:
                    row = [ data.customer, data.description, backup_file.backup_name, backup_file.sha1sum, backup_file.size, backup_file.backup_date ]
                    backups_info.append(row)

        self._csv_write(backups_info, csv_path)

        return csv_path

    def _upload_csv(self, csv_path: str, worksheet_name: str) -> None:
        logging.info(f"Upload csv to google sheet")
        scope = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        client = gspread.authorize(credentials)
        try:
            spreadsheet = client.open(self.spreadsheet_name)
            logging.debug("List current permissions")
            permissions = spreadsheet.list_permissions()
            logging.debug(permissions)
            for user in permissions:
                if user.get("emailAddress", None) == self.sheet_owner and user["role"] != "owner":
                    logging.info(f"Change owner to {self.sheet_owner}")
                    spreadsheet.transfer_ownership(user["id"])
                    break
        except gspread.exceptions.SpreadsheetNotFound as e:
            spreadsheet = client.create(self.spreadsheet_name)
            spreadsheet.share(self.sheet_owner, perm_type='user', role='writer')

        try:
            logging.debug(f"Worksheets are: {spreadsheet.worksheets()}")
            spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound as e:
            spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

        spreadsheet.values_clear(worksheet_name + "!A1:L10000")
        spreadsheet.values_update(
            worksheet_name,
            params={'valueInputOption': 'USER_ENTERED'},
            body={'values': list(csv.reader(open(csv_path)))}
        )

    def _get_backups_count(self, metadata: BackupMetadata) -> int:
        '''
            Return count of backups
        '''
        try:
            return int(metadata.count_of_backups)
        except ValueError as exc:
            # there are cases when total count string looks like "67 total / 10 full / 57 incremental"
            # so we need to parse it explicitly
            return int(metadata.count_of_backups.split(" ")[0])

    def _color_backup_count(self, metadata: BackupMetadata) -> Color:
        '''
            Select color for Backup count cell
        '''
        if self._get_backups_count(metadata) < 3:
            return self.color_alarm
        return self.color_neutral

    def _color_supposed_backups_count(self, metadata: BackupMetadata) -> Color:
        '''
            Select color for Supposed Backups Count
        '''
        if self._get_backups_count(metadata) <= int(metadata.supposed_backups_count) - 3:
            return self.color_alarm
        elif self._get_backups_count(metadata) <  int(metadata.supposed_backups_count) - 2:
            return self.color_warning
        return self.color_neutral

    def _color_last_backup_date(self, metadata: BackupMetadata) -> Color:
        '''
            Select color for Last Backup Date
        '''
        last_backup_date = dateparser.parse(metadata.last_backup_date)
        time_delta = datetime.datetime.now() - last_backup_date.replace(tzinfo=None)
        if time_delta.days > 7:
            return self.color_alarm
        return self.color_neutral

    def _set_color_matrix(self, metadata: list) -> list:
        '''
            Compile color matrix by collected metadata for google worksheet
        '''
        result = [[self.color_neutral, self.color_neutral, self.color_neutral, self.color_neutral, self.color_neutral]] # Worksheet header always white
        # Iterate over metadata, compile worksheet rows and colorize them
        for data in metadata:
            result.append([
                self.color_neutral, # Customer
                self.color_neutral, # DB type
                self.color_neutral, # Backup Placement
                self.color_neutral, # Size in MB
                self.color_neutral, # Backup time spent
                self.color_neutral, # Backup name
                self.color_neutral, # Backup hash sum
                self._color_backup_count(data), # Backup count
                self._color_supposed_backups_count(data), # Supposed Backups Count
                self._color_last_backup_date(data) , # Last Backup Date
                self.color_neutral, # Description
            ])

        return result

    def _get_column_name(self, n):
        '''
            Get letter from english alphabet by position number
        '''
        if n > 26:
            raise Exception("Function _get_column_name accepts a number from 0 to 26")

        result = ''
        while n > 0:
            index = (n - 1) % 26
            result += chr(index + ord('A'))
            n = (n - 1) // 26

        return result[::-1]

    def _colorize_worksheet(self, color_matrix: list) -> None:
        '''
            Colorize spreadsheet with colors sets in color_matrix
        '''
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        spreadsheet = gspread.authorize(credentials).open(self.spreadsheet_name)
        worksheet = spreadsheet.worksheet(self.worksheet_name)

        # Drop all worksheet colors
        format_cell_range(
            worksheet=worksheet,
            name="0", # Set all cells for that operation
            cell_format=CellFormat(backgroundColor=Color(1, 1, 1)) # Colorize cells to white
        )

        # Iterate over color_matrix like over worksheet rows and its numbers
        for y, row in enumerate(color_matrix):
            # Iterate over worksheet cells in row and its column numbers
            for x, col in enumerate(row):
                if col == self.color_neutral: # Check if cell is white
                    continue
                sleep(5)
                format_cell_range(
                    worksheet=worksheet,
                    name=self._get_column_name(x+1)+str(y+1), # Compile cell name in format like "A1", "B2" etc
                    cell_format=CellFormat(backgroundColor=col)
                )

    def collect(self):
        metadata = []
        for bucket in self.buckets:
            metadata.append(
                self._collect_from_bucket(
                    aws_access_key_id=bucket.get("aws_access_key_id"),
                    aws_secret_access_key=bucket.get("aws_secret_access_key"),
                    aws_region=bucket.get("aws_region"),
                    s3_path=bucket.get("s3_path"),
                    aws_endpoint_url=bucket.get("aws_endpoint_url")
                )
            )

        csv = self._compile_csv(metadata)
        file_backups_csv = self._compile_file_backups_csv(metadata)
        self._upload_csv(csv, self.worksheet_name)
        self._upload_csv(file_backups_csv, self.worksheet_name + '_files')
        os.remove(csv)
        os.remove(file_backups_csv)

        color_matrix = self._set_color_matrix(metadata)
        self._colorize_worksheet(color_matrix)
