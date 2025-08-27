"""Tests for the main FastAPI application."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from access_log_analyzer.main import _get_date_range, app, load_logs
from access_log_analyzer.models import LogEntry


class TestMainApp:
    """Test cases for the main FastAPI application."""

    def test_load_logs_function(self) -> None:
        """Test the load_logs function."""
        with patch("access_log_analyzer.main.LogParser") as mock_parser_class:
            mock_parser = mock_parser_class.return_value
            mock_parser.parse_log_files.return_value = [
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
                )
            ]

            entries = load_logs()

            assert len(entries) == 1
            assert entries[0].ip == "192.168.1.1"
            mock_parser_class.assert_called_once()
            mock_parser.parse_log_files.assert_called_once()

    def test_get_date_range_with_entries(self) -> None:
        """Test _get_date_range with log entries."""
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
                timestamp="01/Aug/2025:18:04:20 -0700",
                datetime=datetime(2025, 8, 1, 18, 4, 20),
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

        date_range = _get_date_range(entries)
        assert date_range == "2025-07-31 to 2025-08-01"

    def test_get_date_range_empty_entries(self) -> None:
        """Test _get_date_range with empty entries."""
        date_range = _get_date_range([])
        assert date_range == "No data"

    def test_get_date_range_no_entries_parameter(self) -> None:
        """Test _get_date_range with None parameter uses global entries."""
        # This will use the global _log_entries which should be empty initially
        date_range = _get_date_range(None)
        assert date_range == "No data"


class TestMainEndpoints:
    """Test cases for FastAPI endpoints."""

    def setup_method(self) -> None:
        """Setup test client."""
        self.client = TestClient(app)

    @patch(
        "access_log_analyzer.main._log_entries",
        [
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
        ],
    )
    def test_api_logs_endpoint(self) -> None:
        """Test the /api/logs endpoint."""
        response = self.client.get("/api/logs")

        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] == 2
        assert data["unique_ips"] == 2
        assert data["filter_description"] == "Showing all data"
        assert len(data["files_processed"]) == 1

    @patch("access_log_analyzer.main.load_logs")
    @patch("access_log_analyzer.main._log_entries", [])
    def test_api_refresh_endpoint(self, mock_load_logs: MagicMock) -> None:
        """Test the /api/refresh endpoint."""
        mock_load_logs.return_value = [
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
            )
        ]

        response = self.client.get("/api/refresh")

        assert response.status_code == 200
        data = response.json()
        assert "Reloaded 1 log entries" in data["message"]
        mock_load_logs.assert_called_once()

    @patch(
        "access_log_analyzer.main._log_entries",
        [
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
            )
        ],
    )
    def test_dashboard_endpoint(self) -> None:
        """Test the main dashboard endpoint."""
        response = self.client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        # Basic check that it returned HTML
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text


class TestCLIFunction:
    """Test cases for CLI functionality."""

    @patch("uvicorn.run")
    @patch("access_log_analyzer.main.settings")
    def test_cli_function(self, mock_settings: MagicMock, mock_uvicorn_run: MagicMock) -> None:
        """Test the CLI entry point."""
        from access_log_analyzer.main import cli

        mock_settings.host = "127.0.0.1"
        mock_settings.port = 9000
        mock_settings.debug = True

        cli()

        mock_uvicorn_run.assert_called_once_with(
            "access_log_analyzer.main:app",
            host="127.0.0.1",
            port=9000,
            reload=True,
        )
