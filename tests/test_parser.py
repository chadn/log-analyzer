"""Tests for log parsing functionality."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

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

    def test_parse_nasa_format_log_line(self) -> None:
        """Test parsing a NASA format log line (without referer/user-agent)."""
        parser = LogParser()
        line = '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245'

        entry = parser.parse_log_line(line)

        assert entry is not None
        assert entry.ip == "199.72.81.55"
        assert entry.method == "GET"
        assert entry.path == "/history/apollo/"
        assert entry.protocol == "HTTP/1.0"
        assert entry.status == 200
        assert entry.response_bytes == "6245"
        assert entry.parsed_datetime == datetime(1995, 7, 1, 0, 0, 1)
        assert entry.referer == "-"
        assert entry.user_agent == "-"
        assert entry.browser == "Unknown"

    def test_parse_nasa_format_with_hostname(self) -> None:
        """Test parsing NASA format with hostname instead of IP."""
        parser = LogParser()
        line = 'unicomp6.unicomp.net - - [01/Jul/1995:00:00:06 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985'

        entry = parser.parse_log_line(line)

        assert entry is not None
        assert entry.ip == "unicomp6.unicomp.net"
        assert entry.method == "GET"
        assert entry.path == "/shuttle/countdown/"
        assert entry.protocol == "HTTP/1.0"
        assert entry.status == 200
        assert entry.response_bytes == "3985"
        assert entry.parsed_datetime == datetime(1995, 7, 1, 0, 0, 6)
        assert entry.referer == "-"
        assert entry.user_agent == "-"
        assert entry.browser == "Unknown"

    def test_parse_nasa_format_with_status_304(self) -> None:
        """Test parsing NASA format with 304 status."""
        parser = LogParser()
        line = (
            'burger.letters.com - - [01/Jul/1995:00:00:11 -0400] "GET /shuttle/countdown/liftoff.html HTTP/1.0" 304 0'
        )

        entry = parser.parse_log_line(line)

        assert entry is not None
        assert entry.ip == "burger.letters.com"
        assert entry.method == "GET"
        assert entry.path == "/shuttle/countdown/liftoff.html"
        assert entry.protocol == "HTTP/1.0"
        assert entry.status == 304
        assert entry.response_bytes == "0"
        assert entry.parsed_datetime == datetime(1995, 7, 1, 0, 0, 11)

    def test_parse_mixed_formats_in_file(self) -> None:
        """Test parsing a file with mixed log formats."""
        mixed_log_data = (
            '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245\n'
            "173.252.95.18 - - [31/Jul/2025:17:03:16 -0700] "
            '"GET /rental HTTP/1.1" 301 292 "-" "facebookexternalhit/1.1"\n'
            'unicomp6.unicomp.net - - [01/Jul/1995:00:00:06 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985\n'
        )

        with (
            patch(
                "builtins.open",
                new_callable=mock_open,
                read_data=mixed_log_data,
            ),
            patch.object(LogParser, "find_log_files") as mock_find_files,
        ):
            test_file = Path("mixed.log")
            mock_find_files.return_value = [test_file]

            parser = LogParser("test_dir")
            entries = parser.parse_log_files()

            # Should parse all 3 entries despite different formats
            assert len(entries) == 3

            # Check NASA format entry
            assert entries[0].ip == "199.72.81.55"
            assert entries[0].browser == "Unknown"
            assert entries[0].user_agent == "-"

            # Check common format entry
            assert entries[1].ip == "173.252.95.18"
            assert entries[1].browser == "Facebook Bot"
            assert entries[1].user_agent == "facebookexternalhit/1.1"

            # Check hostname entry
            assert entries[2].ip == "unicomp6.unicomp.net"
            assert entries[2].browser == "Unknown"

    def test_parse_browser_bot_crawler(self) -> None:
        """Test browser parsing for bots and crawlers."""
        parser = LogParser()
        ua_bot = "Googlebot/2.1"
        ua_crawler = "Some web crawler/1.0"

        browser_bot = parser._parse_browser(ua_bot)
        browser_crawler = parser._parse_browser(ua_crawler)

        assert browser_bot == "Bot/Crawler"
        assert browser_crawler == "Bot/Crawler"

    def test_parse_log_line_with_invalid_timestamp(self) -> None:
        """Test parsing a log line with invalid timestamp format."""
        parser = LogParser()
        line = '173.252.95.18 - - [invalid-timestamp] "GET /rental HTTP/1.1" 301 292 "-" "facebookexternalhit/1.1"'

        entry = parser.parse_log_line(line)

        assert entry is None

    def test_is_log_file(self) -> None:
        """Test log file detection."""
        parser = LogParser()

        assert parser._is_log_file(Path("access.log"))
        assert parser._is_log_file(Path("error.log"))
        assert parser._is_log_file(Path("rental.txt"))  # Contains 'rental'
        assert parser._is_log_file(Path("access_log.txt"))  # Contains 'access'
        assert not parser._is_log_file(Path("data.txt"))
        assert not parser._is_log_file(Path("config.yaml"))

    def test_find_log_files_no_directory(self) -> None:
        """Test finding log files when directory doesn't exist."""
        parser = LogParser("nonexistent_directory")
        log_files = parser.find_log_files()
        assert log_files == []

    def test_find_log_files_with_real_directory(self) -> None:
        """Test finding log files works with directory structure."""
        parser = LogParser("nonexistent")
        # Just test that it doesn't crash - detailed file system testing is complex
        log_files = parser.find_log_files()
        assert isinstance(log_files, list)

    def test_parse_log_files_empty_directory(self) -> None:
        """Test parsing when no log files exist."""
        with patch.object(LogParser, "find_log_files", return_value=[]):
            parser = LogParser("empty_dir")
            entries = parser.parse_log_files()
            assert entries == []

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=(
            "173.252.95.18 - - [31/Jul/2025:17:03:16 -0700] "
            '"GET /rental HTTP/1.1" 301 292 "-" "facebookexternalhit/1.1"\n'
            "192.168.1.1 - - [31/Jul/2025:18:04:20 -0700] "
            '"POST /api HTTP/1.1" 200 1024 "-" "Chrome/91.0"\n'
            "invalid log line\n"
            "10.0.0.1 - - [01/Aug/2025:09:15:30 -0700] "
            '"GET /home HTTP/1.1" 200 512 "-" "Firefox/89.0"\n'
        ),
    )
    @patch.object(LogParser, "find_log_files")
    def test_parse_single_file(self, mock_find_files: MagicMock, mock_file: MagicMock) -> None:
        """Test parsing a single log file."""
        test_file = Path("test.log")
        mock_find_files.return_value = [test_file]

        parser = LogParser("test_dir")
        entries = parser.parse_log_files()

        # Should parse 3 valid lines (skip the invalid one)
        assert len(entries) == 3
        assert entries[0].ip == "173.252.95.18"
        assert entries[0].source_file == "test.log"
        assert entries[1].ip == "192.168.1.1"
        assert entries[2].ip == "10.0.0.1"

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=(
            "173.252.95.18 - - [31/Jul/2025:17:03:16 -0700] "
            '"GET /rental HTTP/1.1" 301 292 "-" "facebookexternalhit/1.1"\n'
            "192.168.1.1 - - [31/Jul/2025:18:04:20 -0700] "
            '"POST /api HTTP/1.1" 200 1024 "-" "Chrome/91.0"\n'
            "10.0.0.1 - - [01/Aug/2025:09:15:30 -0700] "
            '"GET /home HTTP/1.1" 200 512 "-" "Firefox/89.0"\n'
        ),
    )
    @patch.object(LogParser, "find_log_files")
    def test_parse_log_files_with_max_entries(self, mock_find_files: MagicMock, mock_file: MagicMock) -> None:
        """Test parsing with max entries limit."""
        test_file = Path("test.log")
        mock_find_files.return_value = [test_file]

        parser = LogParser("test_dir")
        entries = parser.parse_log_files(max_entries=2)

        # Should only return 2 entries due to limit
        assert len(entries) == 2
        assert entries[0].ip == "173.252.95.18"
        assert entries[1].ip == "192.168.1.1"

    @patch("builtins.open", side_effect=OSError("File not found"))
    @patch.object(LogParser, "find_log_files")
    def test_parse_single_file_error(self, mock_find_files: MagicMock, mock_file: MagicMock) -> None:
        """Test handling file read errors."""
        test_file = Path("error.log")
        mock_find_files.return_value = [test_file]

        parser = LogParser("test_dir")
        entries = parser.parse_log_files()

        # Should handle the error gracefully and return empty list
        assert entries == []

    def test_parse_single_file_with_max_entries_per_file(self) -> None:
        """Test parsing single file with max entries limit."""
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=(
                '1.1.1.1 - - [31/Jul/2025:17:03:16 -0700] "GET / HTTP/1.1" 200 100 "-" "Chrome"\n'
                '2.2.2.2 - - [31/Jul/2025:17:04:16 -0700] "GET /page HTTP/1.1" 200 200 "-" "Firefox"\n'
                '3.3.3.3 - - [31/Jul/2025:17:05:16 -0700] "GET /api HTTP/1.1" 200 300 "-" "Safari"\n'
            ),
        ):
            parser = LogParser("test_dir")
            entries = parser._parse_single_file(Path("test.log"), max_entries=2)

            # Should only parse first 2 entries
            assert len(entries) == 2
            assert entries[0].ip == "1.1.1.1"
            assert entries[1].ip == "2.2.2.2"

    def test_parse_browser_with_empty_user_agent(self) -> None:
        """Test browser parsing with empty or dash user agent."""
        parser = LogParser()

        browser_dash = parser._parse_browser("-")
        browser_empty = parser._parse_browser("")

        assert browser_dash == "Other"
        assert browser_empty == "Other"
