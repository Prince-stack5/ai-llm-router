import os

from dotenv import load_dotenv

load_dotenv()


PROVIDER_A_API_KEY = os.getenv("PROVIDER_A_API_KEY")
PROVIDER_B_API_KEY = os.getenv("PROVIDER_B_API_KEY")

PROVIDER_A_MODEL = os.getenv(
    "PROVIDER_A_MODEL",
    "gemini-3.6-flash",
)

PROVIDER_B_MODEL = os.getenv(
    "PROVIDER_B_MODEL",
    "llama-3.3-70b-versatile",
)

CLASSIFIER_MODEL = os.getenv(
    "CLASSIFIER_MODEL",
    "gemini-3.6-flash",
)

GOOGLE_SHEET_ID = os.getenv(
    "GOOGLE_SHEET_ID",
    "1D4dysPlQK0n1CLrhDvrgs6vQRA32Mqgke3vaJGG9AVI",
)
GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")