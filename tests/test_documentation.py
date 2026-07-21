from pathlib import Path

from neo_monitor.output import PROCESSED_CSV_FIELDS


PROJECT_ROOT = Path(__file__).parents[1]


def test_data_dictionary_covers_the_processed_csv_schema():
    """Catch schema changes that leave the durable field reference behind."""

    data_dictionary = (PROJECT_ROOT / "docs" / "data-dictionary.md").read_text()

    for field in PROCESSED_CSV_FIELDS:
        assert f"`{field}`" in data_dictionary
