import asyncio
import os
import sqlite3
import uuid
from contextlib import closing
from typing import List, Tuple

import requests
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")
OPENROUTER_SITE_URL = os.getenv(
    "OPENROUTER_SITE_URL",
    "https://example.com/your-landing",
)
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Volna Bot")
GIGACHAT_AUTH_BASIC = os.getenv("GIGACHAT_AUTH_BASIC")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat")
GIGACHAT_RQUID = os.getenv("GIGACHAT_RQUID", str(uuid.uuid4()))
GIGACHAT_VERIFY = os.getenv("GIGACHAT_VERIFY", "1")
PROMPT_SYSTEM = os.getenv(
    "PROMPT_SYSTEM",
    "Ты — вежливый помощник ЖК \"Волна\" в Уфе."
    " Спроси имя, телефон, бюджет, тип квартиры и желаемую дату въезда,"
    " помоги записаться на показ.",
)
DB_PATH = os.getenv("DB_PATH", "bot_data.db")
AUTO_REPLY_DEFAULT = bool(int(os.getenv("AUTO_REPLY_DEFAULT", "1")))
LLM_KEY_WARNING = None


def _ascii_safe(value: str, fallback: str) -> str:
    """Return an ASCII-only header value to avoid httpx encoding errors."""
    try:
        value.encode("ascii")
        return value
    except UnicodeEncodeError:
        print(
            "⚠️  Значение содержит не-ASCII символы и будет заменено:",
            value,
            "→",
            fallback,
        )
        return fallback


def _gigachat_verify_value():
    normalized = str(GIGACHAT_VERIFY).strip().lower()
    if normalized in {"0", "false", "no"}:
        return False
    if os.path.exists(GIGACHAT_VERIFY):
        return GIGACHAT_VERIFY
    return True


def request_gigachat_token() -> str:
    verify = _gigachat_verify_value()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": GIGACHAT_RQUID,
        "Authorization": f"Basic {GIGACHAT_AUTH_BASIC}",
    }
    response = requests.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        data={"scope": GIGACHAT_SCOPE},
        headers=headers,
        timeout=20,
        verify=verify,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("Gigachat не вернул access_token")
    return token


if LLM_PROVIDER not in {"openrouter", "gigachat"}:
    print("⚠️  Неизвестный LLM_PROVIDER, используем openrouter.")
    LLM_PROVIDER = "openrouter"

if LLM_PROVIDER == "openrouter":
    if LLM_API_KEY and not LLM_API_KEY.startswith("sk-or-"):
        LLM_KEY_WARNING = (
            "LLM_API_KEY не похож на ключ OpenRouter (sk-or-...)."
            " Бот переключится на шаблонные ответы."
        )
        print(f"⚠️  {LLM_KEY_WARNING}")
        LLM_API_KEY = None

    if not LLM_MODEL:
        LLM_MODEL = "tng/deepseek-r1t2-chimera-free"
elif LLM_PROVIDER == "gigachat":
    if not LLM_MODEL:
        LLM_MODEL = GIGACHAT_MODEL

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is required in .env")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


def init_db() -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                auto_reply INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                direction TEXT CHECK(direction IN ('in','out')),
                text TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        conn.commit()


def upsert_user(user: Message) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (user_id, first_name, username, auto_reply)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                first_name=excluded.first_name,
                username=excluded.username
            """,
            (
                user.from_user.id,
                user.from_user.first_name,
                user.from_user.username,
                int(AUTO_REPLY_DEFAULT),
            ),
        )
        conn.commit()


def log_message(user_id: int, direction: str, text: str) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (user_id, direction, text) VALUES (?, ?, ?)",
            (user_id, direction, text),
        )
        conn.commit()


def get_last_messages(user_id: int, limit: int = 10) -> List[Tuple[str, str]]:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT direction, text FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
    return list(reversed(rows))


def is_auto_reply_enabled(user_id: int) -> bool:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT auto_reply FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            return AUTO_REPLY_DEFAULT
        return bool(row[0])


def set_auto_reply(user_id: int, enabled: bool) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET auto_reply = ? WHERE user_id = ?",
            (int(enabled), user_id),
        )
        conn.commit()


def build_prompt(messages_history: List[Tuple[str, str]]) -> List[dict]:
    messages = [{"role": "system", "content": PROMPT_SYSTEM}]
    for direction, text in messages_history:
        role = "user" if direction == "in" else "assistant"
        messages.append({"role": role, "content": text})
    return messages


def format_fallback_reply(user_message: str) -> str:
    lower = user_message.lower()
    if any(k in lower for k in ["цена", "стоимость", "сколько"]):
        return (
            "Стоимость зависит от планировки и этажа."
            " Оставьте телефон, и менеджер подберёт варианты"
            " и вышлет прайс."
        )
    if "показ" in lower or "посмотреть" in lower:
        return "Могу записать вас на показ. Напишите удобный день и телефон."
    return (
        "Спасибо за интерес к ЖК \"Волна\"!"
        " Подскажите, какой формат квартиры интересует и ваш телефон"
        " для связи?"
    )


def gigachat_reply(user_id: int, user_message: str) -> str:
    token = request_gigachat_token()
    history = get_last_messages(user_id)
    prompt_messages = build_prompt(history + [("in", user_message)])

    response = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "model": LLM_MODEL,
            "messages": prompt_messages,
            "temperature": 0.4,
            "max_tokens": 300,
        },
        timeout=20,
        verify=_gigachat_verify_value(),
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def llm_reply(user_id: int, user_message: str) -> str:
    if LLM_PROVIDER == "gigachat":
        if not GIGACHAT_AUTH_BASIC:
            return format_fallback_reply(user_message)
        try:
            return gigachat_reply(user_id, user_message)
        except Exception as exc:  # noqa: BLE001
            print("⚠️  Ошибка Gigachat:", exc)
            return format_fallback_reply(user_message)

    if not LLM_API_KEY:
        return format_fallback_reply(user_message)

    history = get_last_messages(user_id)

    safe_referer = _ascii_safe(OPENROUTER_SITE_URL, "https://example.com/landing")
    safe_title = _ascii_safe(OPENROUTER_APP_NAME, "Volna Bot")

    client = OpenAI(
        api_key=LLM_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": safe_referer,
            "X-Title": safe_title,
        },
    )
    prompt_messages = build_prompt(history + [("in", user_message)])
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=prompt_messages,
        temperature=0.4,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    upsert_user(message)
    greeting = (
        "Здравствуйте! Я виртуальный консультант ЖК \"Волна\" в Уфе."
        " Помогу подобрать квартиру и записать на показ."
        " Напишите, какой формат жилья и бюджет рассматриваете?"
    )
    log_message(message.from_user.id, "in", message.text or "/start")
    log_message(message.from_user.id, "out", greeting)
    await message.answer(greeting)


@dp.message(F.text)
async def handle_message(message: Message) -> None:
    upsert_user(message)
    user_id = message.from_user.id
    user_text = message.text or ""

    log_message(user_id, "in", user_text)

    if not is_auto_reply_enabled(user_id):
        await message.answer(
            "Спасибо! Ваше сообщение передано оператору."
            " Мы ответим в ближайшее время."
        )
        return

    reply_text = llm_reply(user_id, user_text)
    log_message(user_id, "out", reply_text)
    await message.answer(reply_text)


async def main() -> None:
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
