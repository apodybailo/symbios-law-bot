from exchangelib import Credentials, Account, DELEGATE, Configuration
import os

def connect_to_exchange():
    email = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    server = os.getenv("EXCHANGE_SERVER", "outlook.office365.com")
    creds = Credentials(email, password)
    config = Configuration(server=server, credentials=creds)
    account = Account(primary_smtp_address=email, credentials=creds, autodiscover=False, config=config, access_type=DELEGATE)
    return account

def fetch_emails(account, max_items=5):
    inbox = account.inbox
    messages = inbox.all().order_by('-datetime_received')[:max_items]
    for msg in messages:
        subject = msg.subject
        sender = msg.sender.email_address if msg.sender else "невідомо"
        print(f"[📩] {subject} — {sender}")