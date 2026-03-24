import os
import requests
import json
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
API_URL = "https://akafoe.studylife.org/api/meal-plans/today?canteen_id=a0f40678-5e86-4ae4-9ff1-ae1e9e25934b"

MENSA_URL = "https://www.akafoe.de/essen/mensen-und-cafeterien/speiseplan/a0f40678-5e86-4ae4-9ff1-ae1e9e25934b"
SUCHWORT = "kaiserschmarrn"


def update_history():
    """Liest die alte Historie, fügt das heutige Datum hinzu und speichert sie."""
    history_file = "history.json"
    heute = datetime.now().strftime('%d.%m.%Y')
    historie = []

    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            try:
                historie = json.load(file)
            except json.JSONDecodeError:
                pass

    if heute not in historie:
        historie.insert(0, heute)

    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(historie, file, indent=4)
    print(f"📁 Historie aktualisiert: {heute} hinzugefügt.")

def send_telegram_alert(nachricht):
    """Sendet die maßgeschneiderte Nachricht an den Kanal."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": nachricht,
        "parse_mode": "HTML" # Erlaubt uns fette und kursive Schrift!
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Telegram-Nachricht mit Details erfolgreich gesendet!")
    else:
        print(f"❌ Fehler beim Senden: {response.text}")

def check_mensa_for_schmarrn():
    """Liest die API wie ein echter Student und sucht nach dem magischen Gericht."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starte API-Check...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        api_daten = response.json()

        # Wir gehen jedes einzelne Gericht ("meal") in der Liste "data" durch
        for gericht in api_daten.get("data", []):
            titel = gericht.get("title", "")

            # Wenn das Suchwort im Titel steckt...
            if SUCHWORT in titel.lower():

                # ... schnappen wir uns den Studenten-Preis!
                preis_studi = gericht.get("price_student", "Unbekannt")

                # Wenn der Preis eine Zahl ist, machen wir daraus z.B. "2,60 €"
                if isinstance(preis_studi, (int, float)):
                    preis_studi_str = f"{preis_studi:.2f}".replace(".", ",") + " €"
                else:
                    preis_studi_str = f"{preis_studi} €"

                print(f"🎯 BINGO! {titel} für {preis_studi_str} gefunden.")
                return titel, preis_studi_str # Wir geben die Details zurück!

        print(f"❌ Kein '{SUCHWORT.capitalize()}' heute. Sad life.")
        return None, None

    except Exception as e:
        print(f"⚠️ Unerwarteter Fehler bei der API-Abfrage: {e}")
        return None, None

# --- DAS HAUPTPROGRAMM ---
if __name__ == "__main__":
    # Wir rufen die Check-Funktion auf und fangen Titel und Preis auf
    gefundener_titel, gefundener_preis = check_mensa_for_schmarrn()

    if gefundener_titel: # Wenn ein Titel zurückkam, gab es einen Treffer
        update_history() # Website aktualisieren

        # Jetzt bauen wir die richtig coole Nachricht zusammen
        alarm_text = (
            f"🚨 <b>KAISERSCHMARRN ALARM!</b> 🚨\n\n"
            f"Der Bot hat soeben den Speiseplan gescannt. Heute gibt es in der Mensa:\n\n"
            f"🥞 <i>{gefundener_titel}</i>\n"
            f"💸 Studi-Preis: <b>{gefundener_preis}</b>\n\n"
            f"Nichts wie hin! 🏃‍♂️💨"
        )

        if BOT_TOKEN and BOT_TOKEN != "DEIN_BOT_TOKEN_HIER":
            send_telegram_alert(alarm_text)
        else:
            print("⚠️ Bot-Token fehlt. Nachricht würde so aussehen:\n")
            print(alarm_text)