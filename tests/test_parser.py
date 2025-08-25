"""Tests for log parsing functionality."""

from datetime import datetime

from access_log_analyzer.parser import LogParser


class TestLogParser:
    """Test cases for LogParser."""

    def test_parse_valid_log_line(self) -> None:
        """Test parsing a valid log line."""
        parser = LogParser()
        line = (
            "173.252.95.18 - - [31/Jul/2025:17:03:16 -0700] "
            '"GET /rental HTTP/1.1" 301 292 "-" '
            '"facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"'
        )

        entry = parser.parse_log_line(line)

        assert entry is not None
        assert entry.ip == "173.252.95.18"
        assert entry.method == "GET"
        assert entry.path == "/rental"
        assert entry.protocol == "HTTP/1.1"
        assert entry.status == 301
        assert entry.response_bytes == "292"
        assert entry.parsed_datetime == datetime(2025, 7, 31, 17, 3, 16)
        assert entry.browser == "Facebook Bot"

    def test_parse_invalid_log_line(self) -> None:
        """Test parsing an invalid log line."""
        parser = LogParser()
        line = "This is not a valid log line"

        entry = parser.parse_log_line(line)

        assert entry is None

    def test_parse_browser_chrome(self) -> None:
        """Test browser parsing for Chrome."""
        parser = LogParser()
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        browser = parser._parse_browser(ua)

        assert browser == "Chrome"

    def test_parse_browser_firefox(self) -> None:
        """Test browser parsing for Firefox."""
        parser = LogParser()
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"

        browser = parser._parse_browser(ua)

        assert browser == "Firefox"

    def test_parse_browser_safari(self) -> None:
        """Test browser parsing for Safari."""
        parser = LogParser()
        ua = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        )

        browser = parser._parse_browser(ua)

        assert browser == "Safari"

    def test_parse_browser_bot(self) -> None:
        """Test browser parsing for bots."""
        parser = LogParser()
        ua = "facebookexternalhit/1.1"

        browser = parser._parse_browser(ua)

        assert browser == "Facebook Bot"

    def test_parse_browser_unknown(self) -> None:
        """Test browser parsing for unknown user agent."""
        parser = LogParser()
        ua = "SomeUnknownBrowser/1.0"

        browser = parser._parse_browser(ua)

        assert browser == "Other"
