import os, hashlib, json, requests
from bs4 import BeautifulSoup

URL = "https://off.energy.mk.ua/"
STATE = "state.json"
TOKEN = os.environ["TG_TOKEN"]
CHATS = os.environ["TG_CHATS"].split(",")

def fetch_table():
    r = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    tables = soup.find_all("table")
    print("Знайдено таблиць:", len(tables))
    for i, t in enumerate(tables):
        print(i, t.get("class"), t.get("id"), t.get_text(" ", strip=True)[:100])

    table = tables[0]  # якщо потрібна інша, зміни номер
    rows = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        rows.append(" | ".join(cells))
    return "\n".join(rows)

def send(text):
    for chat in CHATS:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat, "text": text[:4000]},
            timeout=30,
        )

text = fetch_table()
h = hashlib.sha256(text.encode()).hexdigest()
old = json.load(open(STATE))["hash"] if os.path.exists(STATE) else None

if h != old:
    send("⚡ Графік оновився:\n\n" + text)
    json.dump({"hash": h}, open(STATE, "w"))
