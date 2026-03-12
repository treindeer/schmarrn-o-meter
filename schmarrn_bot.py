import os
import requests
import json
from datetime import datetime

# --- KONFIGURATION ---
# Für Docker: Wir lesen die Tokens bevorzugt aus Umgebungsvariablen.
# Für lokale Tests: Trage deine Daten hier in den hinteren Anführungszeichen ein!
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
API_URL = "https://akafoe.studylife.org/api/meal-plans/today?canteen_id=a0f40678-5e86-4ae4-9ff1-ae1e9e25934b"

MENSA_URL = "https://www.akafoe.de/essen/mensen-und-cafeterien/speiseplan/a0f40678-5e86-4ae4-9ff1-ae1e9e25934b"
SUCHWORT = "kaiserschmarrn"


def check_mensa_for_schmarrn():
    """Ruft die AKAFÖ-API ab und sucht nach dem magischen Wort."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starte API-Check...")

    try:
        # Wir sagen dem Server, dass wir gerne JSON-Daten hätten
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json'
        }
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()

        # Die API-Antwort direkt in ein Python-Wörterbuch (JSON) umwandeln
        api_daten = response.json()

        # --- DEBUG-OUTPUT ---
        # Wir speichern die Daten schön formatiert in einer Datei,
        # damit wir die genaue Struktur der Speisekarte sehen können!
        with open("debug_mensa_api.json", "w", encoding="utf-8") as file:
            json.dump(api_daten, file, indent=4, ensure_ascii=False)
        print("🔍 Debug-Datei 'debug_mensa_api.json' wurde erstellt!")
        # --------------------

        # Für den ersten Test: Wir wandeln einfach alle API-Daten wieder in kleinen Text um und suchen
        api_text = json.dumps(api_daten).lower()

        if SUCHWORT in api_text:
            print(f"✅ Treffer! '{SUCHWORT.capitalize()}' in den API-Daten gefunden.")
            return True
        else:
            print(f"❌ Kein '{SUCHWORT.capitalize()}' gefunden. Sad life.")
            return False

    except Exception as e:
        print(f"⚠️ Unerwarteter Fehler bei der API-Abfrage: {e}")
        return False


def send_telegram_alert():
    """Sendet die Push-Nachricht in den Telegram-Kanal."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    nachricht = (
        "🚨 **SCHMARRN-ALARM!** 🚨\n\n"
        "Es ist soweit! Laut Speiseplan gibt es heute Kaiserschmarrn in der RUB-Mensa! 🥞🏃‍♂️💨\n\n"
        f"[Hier geht's zum Speiseplan]({MENSA_URL})"
    )

    payload = {
        "chat_id": CHANNEL_ID,
        "text": nachricht,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True  # Verhindert, dass Telegram eine riesige Link-Vorschau erzeugt
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Telegram-Nachricht erfolgreich in den Kanal gepusht!")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Fehler beim Senden an Telegram: {e}")
        # Zeigt an, was Telegram als Fehler zurückgibt (z.B. falsche Kanal-ID)
        print(f"Antwort vom Server: {response.text if 'response' in locals() else 'Keine Antwort'}")


if __name__ == "__main__":
    # 1. Speiseplan checken
    gibt_es_schmarrn = check_mensa_for_schmarrn()

    # 2. Wenn ja, Alarm auslösen!
    if gibt_es_schmarrn:
        # Sicherheitscheck: Verhindert Absturz, falls du vergessen hast, die Tokens einzutragen
        if BOT_TOKEN == "DEIN_BOT_TOKEN_HIER" or CHANNEL_ID == "DEINE_KANAL_ID_HIER":
            print("⚠️ ACHTUNG: Bot-Token oder Kanal-ID fehlen! Kann keine Nachricht senden.")
        else:

            send_telegram_alert()

