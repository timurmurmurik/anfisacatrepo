import os
import sqlite3
from contextlib import closing
from typing import List, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_PATH = os.getenv("DB_PATH", "bot_data.db")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is required in .env")


def fetch_users(limit: int = 20) -> List[Tuple[int, str, str, str, str, bool]]:
    query = """
    SELECT u.user_id, u.first_name, u.username, MAX(m.created_at) as last_time,
           MAX(CASE WHEN m.id IS NOT NULL THEN m.text ELSE '' END) as last_text,
           u.auto_reply
    FROM users u
    LEFT JOIN messages m ON u.user_id = m.user_id
    GROUP BY u.user_id
    ORDER BY last_time DESC
    LIMIT ?
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        rows = cur.execute(query, (limit,)).fetchall()
    return rows


def fetch_dialog(user_id: int) -> List[Tuple[str, str, str]]:
    query = """
    SELECT direction, text, created_at
    FROM messages
    WHERE user_id = ?
    ORDER BY id ASC
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        rows = cur.execute(query, (user_id,)).fetchall()
    return rows


def send_message(user_id: int, text: str) -> None:
    payload = {"chat_id": user_id, "text": text}
    response = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
    response.raise_for_status()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (user_id, direction, text) VALUES (?, 'out', ?)",
            (user_id, text),
        )
        conn.commit()


def toggle_auto_reply(user_id: int, enabled: bool) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET auto_reply = ? WHERE user_id = ?", (int(enabled), user_id))
        conn.commit()


def print_header(title: str) -> None:
    line = "=" * 60
    print(f"\n{line}\n{title}\n{line}")


def choose_user() -> int:
    users = fetch_users()
    if not users:
        print("Пользователей пока нет. Напишите что-нибудь боту.")
        return -1

    print_header("Список диалогов")
    for idx, (uid, first, username, last_time, last_text, auto_reply) in enumerate(users, start=1):
        label = first or username or str(uid)
        time_str = last_time or "—"
        short = (last_text or "").replace("\n", " ")[:60]
        status = "авто" if auto_reply else "ручной"
        print(f"[{idx}] {label} (id: {uid}, режим: {status}, последнее: {time_str})")
        if short:
            print(f"    → {short}")

    choice = input("\nВведите номер пользователя: ")
    try:
        idx = int(choice)
    except ValueError:
        return -1
    if idx < 1 or idx > len(users):
        return -1
    return users[idx - 1][0]


def action_view_dialog() -> None:
    user_id = choose_user()
    if user_id == -1:
        return
    dialog = fetch_dialog(user_id)
    print_header(f"Диалог с {user_id}")
    for direction, text, created_at in dialog:
        prefix = "ПОЛЬЗОВАТЕЛЬ" if direction == "in" else "БОТ/ОПЕРАТОР"
        time_str = created_at or ""
        print(f"[{time_str}] {prefix}: {text}")


def action_send_reply() -> None:
    user_id = choose_user()
    if user_id == -1:
        return
    text = input("Ваш ответ пользователю: ")
    if not text.strip():
        print("Пустое сообщение не отправлено.")
        return
    send_message(user_id, text.strip())
    print("Сообщение отправлено и записано в историю.")


def action_toggle_auto() -> None:
    user_id = choose_user()
    if user_id == -1:
        return
    choice = input("Включить автоответчик? (y/n): ").lower().strip()
    enabled = choice.startswith("y")
    toggle_auto_reply(user_id, enabled)
    status = "включен" if enabled else "выключен"
    print(f"Автоответчик {status} для пользователя {user_id}.")


def main() -> None:
    while True:
        print_header("Операторская консоль ЖК \"Волна\"")
        print("1 — Просмотреть диалог")
        print("2 — Ответить пользователю")
        print("3 — Переключить автоответчик")
        print("0 — Выход")
        choice = input("Выберите пункт: ").strip()
        if choice == "1":
            action_view_dialog()
        elif choice == "2":
            action_send_reply()
        elif choice == "3":
            action_toggle_auto()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
