import os
from exchangelib import Credentials, Account, Configuration, DELEGATE
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
EXCHANGE_SERVER = os.getenv("EXCHANGE_SERVER")

BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

def connect():
    creds = Credentials(username=EMAIL, password=PASSWORD)
    config = Configuration(server=EXCHANGE_SERVER, credentials=creds)
    return Account(primary_smtp_address=EMAIL, config=config, autodiscover=False, access_type=DELEGATE)

if __name__ == "__main__":
    print("🔐 Exchange модуль готовий.")