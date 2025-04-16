from exchangelib import Credentials, Account, DELEGATE, Configuration
import os

def connect_to_exchange():
    email = os.getenv("EXCHANGE_EMAIL")
    password = os.getenv("EXCHANGE_PASSWORD")
    if not email or not password:
        raise ValueError("EXCHANGE_EMAIL або EXCHANGE_PASSWORD не задані")

    creds = Credentials(email, password)
    config = Configuration(server='outlook.office365.com', credentials=creds)
    account = Account(primary_smtp_address=email, credentials=creds, autodiscover=False, config=config, access_type=DELEGATE)
    return account

def fetch_emails(account, max_items=5):
    inbox = account.inbox
    messages = inbox.all().order_by('-datetime_received')[:max_items]
    results = []

    for msg in messages:
        subject = msg.subject
        sender = msg.sender.email_address if msg.sender else "невідомо"
        body_preview = msg.text_body[:200] if msg.text_body else "немає тексту"
        print(f"[📩] {subject} — {sender}")
        results.append((subject, sender, body_preview))

    return results
