import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

import sheets

load_dotenv()

LINE_API_URL = "https://api.line.me/v2/bot/message/push"


def send_line_message(text):
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}],
    }
    response = requests.post(LINE_API_URL, headers=headers, json=body)
    response.raise_for_status()


def build_message(todos, tomorrow_str):
    lines = ["【明日が期日のTodo】\n"]
    for todo in todos:
        lines.append(f"📌 {todo['タイトル']}")
        lines.append(f"　重要度：{todo['重要度']}")
        if todo.get("内容"):
            lines.append(f"　内容：{todo['内容']}")
        lines.append("")
    lines.append(f"期日：{tomorrow_str}")
    return "\n".join(lines)


def main():
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    all_todos = sheets.get_all_todos()
    target = [
        t for t in all_todos
        if t.get("期日") == tomorrow_str and t.get("ステータス") == "未完了"
    ]

    if not target:
        print(f"{tomorrow_str} が期日の未完了Todoはありません。通知をスキップします。")
        return

    message = build_message(target, tomorrow_str)
    send_line_message(message)
    print(f"通知を送信しました（{len(target)}件）")


if __name__ == "__main__":
    main()
