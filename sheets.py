import json
import os
import uuid
from datetime import datetime

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["ID", "タイトル", "内容", "期日", "ステータス", "作成日時", "重要度", "カテゴリ"]
PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}
CATEGORIES = ["仕事", "プライベート", "勉強", "その他"]


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
    first_row = sheet.row_values(1)
    if not first_row or first_row[0] != "ID":
        sheet.insert_row(HEADER, 1)
    elif "重要度" not in first_row:
        sheet.update_cell(1, 7, "重要度")
    if "カテゴリ" not in sheet.row_values(1):
        sheet.update_cell(1, 8, "カテゴリ")
    return sheet


def get_all_todos(sort="created", category="すべて"):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for r in records:
        r.setdefault("重要度", "中")
        r.setdefault("カテゴリ", "その他")
    if category != "すべて":
        records = [r for r in records if r["カテゴリ"] == category]
    if sort == "priority":
        records.sort(key=lambda r: PRIORITY_ORDER.get(r["重要度"], 1))
    elif sort == "due_date":
        records.sort(key=lambda r: (r["期日"] == "", r["期日"]))
    return records


def get_todo(todo_id):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for i, row in enumerate(records, start=2):
        if str(row["ID"]) == str(todo_id):
            return row, i
    return None, None


def add_todo(title, content, due_date, priority="中", category="その他"):
    sheet = get_sheet()
    todo_id = str(uuid.uuid4())[:8]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([todo_id, title, content, due_date, "未完了", created_at, priority, category])
    return todo_id


def update_todo(todo_id, title, content, due_date, priority="中", category="その他"):
    sheet = get_sheet()
    _, row_index = get_todo(todo_id)
    if row_index is None:
        return False
    sheet.update(f"B{row_index}:D{row_index}", [[title, content, due_date]])
    sheet.update_cell(row_index, 7, priority)
    sheet.update_cell(row_index, 8, category)
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
