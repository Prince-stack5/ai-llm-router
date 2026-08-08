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