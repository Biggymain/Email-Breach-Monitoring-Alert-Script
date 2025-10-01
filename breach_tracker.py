import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
import schedule
import time

# Optional: Uncomment if using Telegram alerts
from telegram import Bot

# -------- CONFIGURATION --------

# Get this from https://haveibeenpwned.com/API/Key
HIBP_API_KEY = 'YOUR_API_KEY_HERE'

# Email alert settings
SENDER_EMAIL = 'barbararyan078@gmail.com'
SENDER_PASSWORD = 'Password'  # Use App Password for Gmail
RECIPIENT_EMAIL = 'fayoyiwamichaelg@gmail.com'

# SMTP server settings for Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Telegram alert settings (optional)
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

# Email to check
EMAIL_TO_CHECK = 'Fayoyiwamick@gmail.com'

# -------------------------------


def check_breach(email):
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        'hibp-api-key': HIBP_API_KEY,
        'user-agent': 'PersonalBreachChecker'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            breaches = response.json()
            print(f"[INFO] Found {len(breaches)} breach(es) for {email}.")
            return breaches
        elif response.status_code == 404:
            print(f"[INFO] No breaches found for {email}.")
            return []
        else:
            print(f"[ERROR] Unexpected status code {response.status_code}.")
            return []
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return []


def send_email_alert(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("[INFO] Alert email sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


def send_telegram_alert(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("[INFO] Telegram alert sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram alert: {e}")


def log_breach(email, breaches):
    with open('breach_log.txt', 'a') as file:
        file.write(f"{datetime.now()}: Checked {email} - {len(breaches)} breach(es)\n")
        for breach in breaches:
            file.write(f"  - {breach['Name']} on {breach['BreachDate']}\n")


def run_check():
    print(f"[INFO] Checking breaches for: {EMAIL_TO_CHECK}")
    breaches = check_breach(EMAIL_TO_CHECK)
    log_breach(EMAIL_TO_CHECK, breaches)

    if breaches:
        subject = f"Data Breach Alert for {EMAIL_TO_CHECK}"
        body = f"Your email {EMAIL_TO_CHECK} was found in the following breaches:\n\n"
        for breach in breaches:
            body += f"- {breach['Name']} (Date: {breach['BreachDate']})\n  {breach['Description']}\n\n"

        send_email_alert(subject, body)
        send_telegram_alert(body)
    else:
        print("[INFO] No breach alerts to send.")


if __name__ == "__main__":
    # Schedule the job to run every day at 9am
    schedule.every().day.at("09:00").do(run_check)

    print("[INFO] Scheduled breach checker started. Press Ctrl+C to stop.")

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)
