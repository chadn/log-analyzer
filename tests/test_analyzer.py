"""Tests for log analysis functionality."""

from datetime import datetime

from access_log_analyzer.analyzer import LogAnalyzer
from access_log_analyzer.models import FilterParams, LogEntry


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

    def test_get_traffic_over_time_hourly(self) -> None:
        """Test hourly traffic analysis with sample data."""
        entries = [
            LogEntry(
                ip="192.168.1.1",
                timestamp="31/Jul/2025:08:15:30 -0700",
                datetime=datetime(2025, 7, 31, 8, 15, 30),
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
                timestamp="31/Jul/2025:08:45:22 -0700",
                datetime=datetime(2025, 7, 31, 8, 45, 22),
                method="GET",
                path="/page",
                protocol="HTTP/1.1",
                status=200,
                bytes="2048",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
            LogEntry(
                ip="192.168.1.3",
                timestamp="31/Jul/2025:14:22:11 -0700",
                datetime=datetime(2025, 7, 31, 14, 22, 11),
                method="GET",
                path="/api",
                protocol="HTTP/1.1",
                status=200,
                bytes="512",
                referer="",
                user_agent="Chrome",
                browser="Chrome",
                source_file="test.log",
            ),
            LogEntry(
                ip="192.168.1.4",
                timestamp="01/Aug/2025:14:33:44 -0700",
                datetime=datetime(2025, 8, 1, 14, 33, 44),
                method="GET",
                path="/data",
                protocol="HTTP/1.1",
                status=200,
                bytes="1536",
                referer="",
                user_agent="Safari",
                browser="Safari",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        result = analyzer.get_traffic_over_time(granularity="hourly")

        assert result.title == "Traffic by Hour"
        assert len(result.dates) == 24  # All hours 0-23 should be present
        assert len(result.counts) == 24

        # Check specific hours that should have data
        hour_8_index = result.dates.index(8)
        hour_14_index = result.dates.index(14)

        assert result.counts[hour_8_index] == 2  # Two entries at hour 8
        assert result.counts[hour_14_index] == 2  # Two entries at hour 14 (different days, same hour)

        # Check that unused hours have 0 count
        hour_0_index = result.dates.index(0)
        assert result.counts[hour_0_index] == 0

    def test_apply_filters_date_valid(self) -> None:
        """Test applying a valid date filter."""
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
                timestamp="01/Aug/2025:17:03:16 -0700",
                datetime=datetime(2025, 8, 1, 17, 3, 16),
                method="GET",
                path="/page",
                protocol="HTTP/1.1",
                status=200,
                bytes="2048",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        filters = FilterParams(date="2025-07-31", hour=None, ip=None, browser=None)
        filtered = analyzer.apply_filters(filters)

        assert len(filtered) == 1
        assert filtered[0].ip == "192.168.1.1"

    def test_apply_filters_date_invalid(self) -> None:
        """Test applying an invalid date filter (should be ignored)."""
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
        ]

        analyzer = LogAnalyzer(entries)
        filters = FilterParams(date="invalid-date", hour=None, ip=None, browser=None)
        filtered = analyzer.apply_filters(filters)

        # Invalid date should be ignored, all entries returned
        assert len(filtered) == 1

    def test_apply_filters_hour(self) -> None:
        """Test applying an hour filter."""
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
                timestamp="31/Jul/2025:18:03:16 -0700",
                datetime=datetime(2025, 7, 31, 18, 3, 16),
                method="GET",
                path="/page",
                protocol="HTTP/1.1",
                status=200,
                bytes="2048",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        filters = FilterParams(date=None, hour=17, ip=None, browser=None)
        filtered = analyzer.apply_filters(filters)

        assert len(filtered) == 1
        assert filtered[0].ip == "192.168.1.1"

    def test_apply_filters_ip(self) -> None:
        """Test applying an IP filter."""
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
                timestamp="31/Jul/2025:17:03:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 3, 16),
                method="GET",
                path="/page",
                protocol="HTTP/1.1",
                status=200,
                bytes="2048",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        filters = FilterParams(date=None, hour=None, ip="192.168.1.2", browser=None)
        filtered = analyzer.apply_filters(filters)

        assert len(filtered) == 1
        assert filtered[0].ip == "192.168.1.2"

    def test_apply_filters_browser(self) -> None:
        """Test applying a browser filter."""
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
                timestamp="31/Jul/2025:17:03:16 -0700",
                datetime=datetime(2025, 7, 31, 17, 3, 16),
                method="GET",
                path="/page",
                protocol="HTTP/1.1",
                status=200,
                bytes="2048",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        filters = FilterParams(date=None, hour=None, ip=None, browser="Firefox")
        filtered = analyzer.apply_filters(filters)

        assert len(filtered) == 1
        assert filtered[0].browser == "Firefox"

    def test_apply_filters_combined(self) -> None:
        """Test applying multiple filters together."""
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
                timestamp="31/Jul/2025:18:03:16 -0700",
                datetime=datetime(2025, 7, 31, 18, 3, 16),
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
        ]

        analyzer = LogAnalyzer(entries)
        filters = FilterParams(date="2025-07-31", hour=17, ip="192.168.1.1", browser="Chrome")
        filtered = analyzer.apply_filters(filters)

        assert len(filtered) == 1
        assert filtered[0].parsed_datetime.hour == 17

    def test_get_traffic_over_time_daily(self) -> None:
        """Test daily traffic analysis with sample data."""
        entries = [
            LogEntry(
                ip="192.168.1.1",
                timestamp="31/Jul/2025:08:15:30 -0700",
                datetime=datetime(2025, 7, 31, 8, 15, 30),
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
                timestamp="31/Jul/2025:14:22:11 -0700",
                datetime=datetime(2025, 7, 31, 14, 22, 11),
                method="GET",
                path="/page",
                protocol="HTTP/1.1",
                status=200,
                bytes="2048",
                referer="",
                user_agent="Firefox",
                browser="Firefox",
                source_file="test.log",
            ),
            LogEntry(
                ip="192.168.1.3",
                timestamp="01/Aug/2025:09:33:44 -0700",
                datetime=datetime(2025, 8, 1, 9, 33, 44),
                method="GET",
                path="/api",
                protocol="HTTP/1.1",
                status=200,
                bytes="512",
                referer="",
                user_agent="Chrome",
                browser="Chrome",
                source_file="test.log",
            ),
        ]

        analyzer = LogAnalyzer(entries)
        result = analyzer.get_traffic_over_time(granularity="daily")

        assert result.title == "Traffic by Day"
        assert len(result.dates) == 2  # Two different days
        assert len(result.counts) == 2

        # Should have 2 entries for July 31 and 1 for August 1
        # Note: dates should be in chronological order
        assert result.counts[0] == 2  # July 31
        assert result.counts[1] == 1  # August 1
