import pytest
from app.router.classifier import VALID_CATEGORIES, QueryClassifier
from app.router.router import LLMRouter
from app.services.google_sheets import GoogleSheetsLogger

def test_new_categories_routing():
    router = LLMRouter()
    
    # Test router maps new categories to correct providers
    assert router.select_provider("Coding")[0] == "provider_a"
    assert router.select_provider("Mathematics")[0] == "provider_a"
    assert router.select_provider("Reasoning")[0] == "provider_b"
    assert router.select_provider("Translation")[0] == "provider_b"
    assert router.select_provider("Summarization")[0] == "provider_a"
    assert router.select_provider("Email Writing")[0] == "provider_b"
    assert router.select_provider("Creative Writing")[0] == "provider_b"
    assert router.select_provider("General Knowledge")[0] == "provider_a"
    assert router.select_provider("Explanation / Education")[0] == "provider_a"
    assert router.select_provider("Analysis")[0] == "provider_a"
    assert router.select_provider("Data / SQL")[0] == "provider_a"
    assert router.select_provider("Web / Research")[0] == "provider_a"
    assert router.select_provider("Planning")[0] == "provider_b"
    assert router.select_provider("Conversation")[0] == "provider_b"
    assert router.select_provider("Document / Content Generation")[0] == "provider_a"


@pytest.mark.asyncio
async def test_classify_json_parsing(monkeypatch):
    classifier = QueryClassifier.__new__(QueryClassifier)
    
    class MockResponse:
        def __init__(self, text):
            self.text = text
            
    class MockClient:
        class Models:
            def generate_content(self, model, contents):
                pass
        models = Models()
        
    classifier.client = MockClient()
    
    # Case 1: Exact matches
    monkeypatch.setattr(classifier.client.models, "generate_content", lambda *args, **kwargs: MockResponse('{"category": "Coding", "confidence": 0.95}'))
    cat, conf = await classifier.classify("test")
    assert cat == "Coding"
    assert conf == 0.95
    
    # Case 2: Lowercase matches
    monkeypatch.setattr(classifier.client.models, "generate_content", lambda *args, **kwargs: MockResponse('{"category": "mathematics", "confidence": 0.8}'))
    cat, conf = await classifier.classify("test")
    assert cat == "Mathematics"
    assert conf == 0.8
    
    # Case 3: Legacy match (writing -> Creative Writing)
    monkeypatch.setattr(classifier.client.models, "generate_content", lambda *args, **kwargs: MockResponse('{"category": "writing", "confidence": 0.8}'))
    cat, conf = await classifier.classify("test")
    assert cat == "Creative Writing"
    
    # Case 4: Invalid/unsupported category -> General Knowledge
    monkeypatch.setattr(classifier.client.models, "generate_content", lambda *args, **kwargs: MockResponse('{"category": "super-advanced-magic", "confidence": 0.9}'))
    cat, conf = await classifier.classify("test")
    assert cat == "General Knowledge"
    
    # Case 5: Broken JSON -> General Knowledge
    monkeypatch.setattr(classifier.client.models, "generate_content", lambda *args, **kwargs: MockResponse('invalid json'))
    cat, conf = await classifier.classify("test")
    assert cat == "General Knowledge"
    assert conf == 0.0

def test_google_sheets_logger_degrade_gracefully(monkeypatch):
    # Ensure credentials are mock-cleared
    monkeypatch.setattr("app.services.google_sheets.GOOGLE_SHEETS_CREDENTIALS_JSON", None)
    monkeypatch.setattr("app.services.google_sheets.GOOGLE_SHEETS_CREDENTIALS_FILE", None)
    monkeypatch.setattr("app.services.google_sheets.GOOGLE_SHEET_ID", None)

    # Test that calling logger when not configured doesn't crash the app
    logger = GoogleSheetsLogger()
    # It has no credentials, so it should log a warning and do nothing
    logger.log_query_sync("test prompt", "Coding", 0.95, "provider_a", "gemini-3.6-flash")
    assert logger._is_initialized is False
    assert logger.client is None
