from neo_monitor.metadata import build_project_metadata, format_project_metadata


def test_project_metadata_reports_missing_api_key_without_secret_value():
    metadata = build_project_metadata(api_key=None)

    assert not metadata.api_key_configured

    text = format_project_metadata(metadata)
    assert "NASA_API_KEY: missing" in text
    assert "data/raw/" in text
    assert "uv run python -m pytest" in text


def test_project_metadata_reports_configured_api_key_without_printing_value():
    metadata = build_project_metadata(api_key="secret-test-key")

    assert metadata.api_key_configured

    text = format_project_metadata(metadata)
    assert "NASA_API_KEY: configured" in text
    assert "secret-test-key" not in text
