"""
ローカルで一度だけ実行して、リフレッシュトークンを取得するスクリプト。
取得した JSON を GOOGLE_OAUTH_CREDENTIALS_JSON 環境変数に設定する。
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0)

output = {
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "refresh_token": creds.refresh_token,
}

print("\n=== 以下の JSON を GOOGLE_OAUTH_CREDENTIALS_JSON 環境変数に設定してください ===\n")
print(json.dumps(output))
