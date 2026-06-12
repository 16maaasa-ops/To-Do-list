import json
import os
import uuid
from datetime import datetime

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["ID", "タイトル", "内容", "期日", "ステータス", "作成日時"]


def get_client():
    creds_json = os.environ["GOOGLE_OAUTH_CREDENTIALS_JSON"]
    creds_dict = json.loads(creds_json)
    creds = Credentials(
        token=None,
        refresh_token=creds_dict["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_dict["client_id"],
        client_secret=creds_dict["client_secret"],
        scopes=SCOPES,
    )
    # トークンが期限切れなら自動リフレッシュ
    if not creds.valid:
        creds.refresh(Request())
    return gspread.authorize(creds)


def get_sheet():
    client = get_client()
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    sheet = client.open_by_key(spreadsheet_id).sheet1
    if sheet.row_count == 0 or sheet.cell(1, 1).value != "ID":
        sheet.insert_row(HEADER, 1)
    return sheet


def get_all_todos():
    sheet = get_sheet()
    return sheet.get_all_records()


def get_todo(todo_id):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for i, row in enumerate(records, start=2):
        if str(row["ID"]) == str(todo_id):
            return row, i
    return None, None


def add_todo(title, content, due_date):
    sheet = get_sheet()
    todo_id = str(uuid.uuid4())[:8]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([todo_id, title, content, due_date, "未完了", created_at])
    return todo_id


def update_todo(todo_id, title, content, due_date):
    sheet = get_sheet()
    _, row_index = get_todo(todo_id)
    if row_index is None:
        return False
    sheet.update(f"B{row_index}:D{row_index}", [[title, content, due_date]])
    return True


def toggle_status(todo_id):
    sheet = get_sheet()
    row, row_index = get_todo(todo_id)
    if row_index is None:
        return False
    new_status = "完了" if row["ステータス"] == "未完了" else "未完了"
    sheet.update_cell(row_index, 5, new_status)
    return True


def delete_todo(todo_id):
    sheet = get_sheet()
    _, row_index = get_todo(todo_id)
    if row_index is None:
        return False
    sheet.delete_rows(row_index)
    return True
