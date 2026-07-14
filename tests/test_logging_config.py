import logging

from neo_monitor.logging_config import configure_logging


def test_verbose_stderr_and_log_file_use_different_detail_levels(tmp_path, capsys):
    log_path = tmp_path / "logs" / "neo-monitor.log"
    logger = logging.getLogger("neo_monitor.api")

    try:
        configure_logging(verbose=True, log_file=log_path)
        logger.debug("debug detail for the file")
        logger.info("useful detail for the terminal")

        stderr = capsys.readouterr().err
        file_log = log_path.read_text()

        assert "useful detail for the terminal" in stderr
        assert "debug detail for the file" not in stderr
        assert "debug detail for the file" in file_log
        assert "useful detail for the terminal" in file_log
    finally:
        configure_logging(verbose=False, log_file=None)
