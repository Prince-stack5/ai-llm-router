from app.router.router import LLMRouter


def test_coding_routes_to_provider_a():
    router = LLMRouter()

    provider_name, _ = router.select_provider("coding")

    assert provider_name == "provider_a"


def test_writing_routes_to_provider_b():
    router = LLMRouter()

    provider_name, _ = router.select_provider("writing")

    assert provider_name == "provider_b"


def test_translation_routes_to_provider_b():
    router = LLMRouter()

    provider_name, _ = router.select_provider("translation")

    assert provider_name == "provider_b"


def test_reasoning_routes_to_provider_b():
    router = LLMRouter()

    provider_name, _ = router.select_provider("reasoning")

    assert provider_name == "provider_b"


def test_unknown_task_uses_default_provider():
    router = LLMRouter()

    provider_name, _ = router.select_provider("unknown")

    assert provider_name == "provider_a"


def test_provider_a_fallback_is_provider_b():
    router = LLMRouter()

    fallback_name, _ = router.get_fallback("provider_a")

    assert fallback_name == "provider_b"


def test_provider_b_fallback_is_provider_a():
    router = LLMRouter()

    fallback_name, _ = router.get_fallback("provider_b")

    assert fallback_name == "provider_a"