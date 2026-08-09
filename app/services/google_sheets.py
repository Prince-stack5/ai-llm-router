import json
import logging
from datetime import datetime
import asyncio
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from app.config.settings import (
    GOOGLE_SHEET_ID,
    GOOGLE_SHEETS_CREDENTIALS_JSON,
    GOOGLE_SHEETS_CREDENTIALS_FILE,
)

logger = logging.getLogger("google_sheets_logger")

class GoogleSheetsLogger:
    """
    Service class to handle logging user queries and predicted categories 
    to a specified Google Sheet.
    """

    def __init__(self):
        self.sheet_id = GOOGLE_SHEET_ID
        self.client: Optional[gspread.Client] = None
        self._is_initialized = False

    def _initialize_client(self):
        """
        Authenticates and initializes the gspread client.
        """
        if self._is_initialized:
            return

        if not self.sheet_id:
            logger.warning("GOOGLE_SHEET_ID is not configured. Google Sheets logging is disabled.")
            return

        try:
            # 1. Try to load credentials from JSON string
            if GOOGLE_SHEETS_CREDENTIALS_JSON:
                try:
                    creds_info = json.loads(GOOGLE_SHEETS_CREDENTIALS_JSON)
                    scopes = [
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
                    self.client = gspread.authorize(creds)
                    logger.info("Authenticated with Google Sheets using JSON string credentials.")
                except Exception as json_err:
                    logger.error(f"Failed to load GOOGLE_SHEETS_CREDENTIALS_JSON: {json_err}")

            # 2. If not initialized, try to load from credentials file
            if not self.client and GOOGLE_SHEETS_CREDENTIALS_FILE:
                try:
                    self.client = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS_FILE)
                    logger.info(f"Authenticated with Google Sheets using file: {GOOGLE_SHEETS_CREDENTIALS_FILE}")
                except Exception as file_err:
                    logger.error(f"Failed to authenticate with file {GOOGLE_SHEETS_CREDENTIALS_FILE}: {file_err}")

            # 3. Fallback to default credentials if available
            if not self.client:
                # We won't block startup if credentials are missing
                logger.warning(
                    "No Google Sheets credentials provided (neither GOOGLE_SHEETS_CREDENTIALS_JSON "
                    "nor GOOGLE_SHEETS_CREDENTIALS_FILE). Google Sheets logging is disabled."
                )
                return

            self._is_initialized = True

        except Exception as e:
            logger.error(f"Initialization of Google Sheets client failed: {e}")

    def log_query_sync(
        self,
        prompt: str,
        category: str,
        confidence: float,
        provider: str,
        model: str
    ):
        """
        Synchronously appends a row to the Google Sheet.
        Automatically adds header row if the sheet is empty.
        """
        try:
            self._initialize_client()
            if not self.client:
                return

            # Open spreadsheet and select first worksheet
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.get_worksheet(0)

            # Ensure header row exists
            headers = ["User Prompt", "Predicted Category"]
            try:
                # get_all_values is slightly safer than checking cell A1 to make sure sheet has rows
                existing_values = worksheet.get_all_values()
                if not existing_values or len(existing_values) == 0:
                    worksheet.append_row(headers)
            except Exception as header_err:
                logger.warning(f"Error checking/creating sheet headers: {header_err}")
                # Try to write them anyway if it was completely empty
                try:
                    worksheet.append_row(headers)
                except Exception:
                    pass

            # Create row content
            row = [
                prompt,
                category
            ]

            worksheet.append_row(row)
            logger.info(f"Successfully logged query to Google Sheets: {category} -> {provider}")

        except Exception as e:
            logger.error(f"Error logging to Google Sheets: {e}")

    async def log_query(
        self,
        prompt: str,
        category: str,
        confidence: float,
        provider: str,
        model: str
    ):
        """
        Asynchronously appends a row to Google Sheets by running the synchronous
        blocking operations in a separate executor thread.
        """
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            self.log_query_sync,
            prompt,
            category,
            confidence,
            provider,
            model
        )


# Global logger instance
sheets_logger = GoogleSheetsLogger()
