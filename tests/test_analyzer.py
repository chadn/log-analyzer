"""Tests for log analysis functionality."""

from datetime import datetime

from access_log_analyzer.analyzer import LogAnalyzer
from access_log_analyzer.models import LogEntry


class TestLogAnalyzer:
    """Test cases for LogAnalyzer."""

    def test_get_traffic_over_time_empty(self) -> None:
        """Test traffic analysis with no data."""
        analyzer = LogAnalyzer([])

        result = analyzer.get_traffic_over_time()

        assert result.title == "No data available"
        assert result.dates == []
        assert result.counts == []

    def test_get_ip_frequency_empty(self) -> None:
        """Test IP frequency analysis with no data."""
        analyzer = LogAnalyzer([])

        result = analyzer.get_ip_frequency()

        assert result.title == "No data available"
        assert result.ips == []
        assert result.counts == []

    def test_get_browser_stats_empty(self) -> None:
        """Test browser stats with no data."""
        analyzer = LogAnalyzer([])

        result = analyzer.get_browser_stats()

        assert result.title == "No data available"
        assert result.browsers == []
        assert result.counts == []

    def test_get_ip_frequency_with_data(self) -> None:
        """Test IP frequency analysis with sample data."""
        entries = [
            LogEntry(
                ip="192.168.1.1",
                timestamp="31/Jul/2025:17:03:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 3, 16),
                method="GET",
                path="/",
                protocol="HTTP/1.1",
                status=200,
                bytes="1024",
                referer="",
                user_agent="Chrome",
                browser="Chrome",
                source_file="test.log",
            ),
            LogEntry(
                ip="192.168.1.1",
                timestamp="31/Jul/2025:17:04:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 4, 16),
                method="GET",
                path="/page",
                protocol="HTTP/1.1",
                status=200,
                bytes="2048",
                referer="",
                user_agent="Chrome",
                browser="Chrome",
                source_file="test.log",
            ),
            LogEntry(
                ip="192.168.1.2",
                timestamp="31/Jul/2025:17:05:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 5, 16),
                method="GET",
                path="/",
                protocol="HTTP/1.1",
                status=200,
                bytes="1024",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        result = analyzer.get_ip_frequency(top_n=10)

        assert len(result.ips) == 2
        assert "192.168.1.1" in result.ips
        assert "192.168.1.2" in result.ips
        assert result.ips[0] == "192.168.1.1"  # Should be first due to higher count
        assert result.counts[0] == 2
        assert result.counts[1] == 1

    def test_get_browser_stats_with_data(self) -> None:
        """Test browser stats with sample data."""
        entries = [
            LogEntry(
                ip="192.168.1.1",
                timestamp="31/Jul/2025:17:03:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 3, 16),
                method="GET",
                path="/",
                protocol="HTTP/1.1",
                status=200,
                bytes="1024",
                referer="",
                user_agent="Chrome",
                browser="Chrome",
                source_file="test.log",
            ),
            LogEntry(
                ip="192.168.1.2",
                timestamp="31/Jul/2025:17:04:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 4, 16),
                method="GET",
                path="/",
                protocol="HTTP/1.1",
                status=200,
                bytes="1024",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
            LogEntry(
                ip="192.168.1.3",
                timestamp="31/Jul/2025:17:05:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 5, 16),
                method="GET",
                path="/",
                protocol="HTTP/1.1",
                status=200,
                bytes="1024",
                referer="",
                user_agent="Chrome",
                browser="Chrome",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        result = analyzer.get_browser_stats()

        assert len(result.browsers) == 2
        assert "Chrome" in result.browsers
        assert "Firefox" in result.browsers
        assert result.title == "Browser Usage Distribution"
