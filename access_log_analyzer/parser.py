"""Log file parsing functionality."""

import logging
import re
from datetime import datetime
from pathlib import Path

from .models import LogEntry

logger = logging.getLogger(__name__)

# Apache/Nginx common log format regex (with referer and user-agent)
COMMON_LOG_PATTERN = re.compile(
    r"(?P<host>\S+) - - \[(?P<timestamp>[^\]]+)\] "
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d+) (?P<bytes>\S+) "(?P<referer>[^"]*)" '
    r'"(?P<user_agent>[^"]*)"'
)

# Combined log format (NCSA format) - without referer and user-agent
NCSA_LOG_PATTERN = re.compile(
    r"(?P<host>\S+) - - \[(?P<timestamp>[^\]]+)\] "
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r"(?P<status>\d+) (?P<bytes>\S+)"
)

# List of patterns to try in order
LOG_PATTERNS = [COMMON_LOG_PATTERN, NCSA_LOG_PATTERN]


class LogParser:
    """Parses web server access logs."""

    def __init__(self, logs_dir: str = "logs") -> None:
        """Initialize the log parser.

        Args:
            logs_dir: Directory containing log files
        """
        self.logs_dir = Path(logs_dir)

    def find_log_files(self) -> list[Path]:
        """Find all log files in the logs directory.

        Returns:
            List of log file paths
        """
        if not self.logs_dir.exists():
            return []

        log_files = []
        for file_path in self.logs_dir.iterdir():
            if file_path.is_file() and self._is_log_file(file_path):
                log_files.append(file_path)

        return sorted(log_files)

    def _is_log_file(self, file_path: Path) -> bool:
        """Check if a file appears to be a log file.

        Args:
            file_path: Path to check

        Returns:
            True if file appears to be a log file
        """
        return any(ext in file_path.name.lower() for ext in ["log", "rental", "access"])

    def parse_log_line(self, line: str) -> LogEntry | None:
        """Parse a single log line using multiple format patterns.

        Args:
            line: Raw log line

        Returns:
            Parsed LogEntry or None if parsing fails
        """
        stripped_line = line.strip()

        # Try each pattern until one matches
        match = None
        for pattern in LOG_PATTERNS:
            match = pattern.match(stripped_line)
            if match:
                break

        if not match:
            return None

        data = match.groupdict()

        # Parse timestamp
        try:
            # Format: 31/Jul/2025:17:03:16 -0700 or 01/Jul/1995:00:00:01 -0400
            dt_str = data["timestamp"].split(" ")[0]  # Remove timezone for simplicity
            parsed_datetime = datetime.strptime(dt_str, "%d/%b/%Y:%H:%M:%S")
        except ValueError:
            return None

        # Handle optional fields (may not exist in all formats)
        referer = data.get("referer", "-")
        user_agent = data.get("user_agent", "-")

        # Parse browser from user agent (default to "Unknown" if no user agent)
        browser = self._parse_browser(user_agent) if user_agent != "-" else "Unknown"

        return LogEntry(
            ip=data["host"],  # Can be IP address or hostname
            timestamp=data["timestamp"],
            datetime=parsed_datetime,  # Using alias for compatibility
            method=data["method"],
            path=data["path"],
            protocol=data["protocol"],
            status=int(data["status"]),
            bytes=data["bytes"],  # Using alias for compatibility
            referer=referer,
            user_agent=user_agent,
            browser=browser,
            source_file="",  # Will be set by caller
        )

    def _parse_browser(self, user_agent: str) -> str:
        """Extract browser name from user agent string.

        Args:
            user_agent: User agent string

        Returns:
            Browser name
        """
        ua_lower = user_agent.lower()

        if "chrome" in ua_lower:
            return "Chrome"
        elif "firefox" in ua_lower:
            return "Firefox"
        elif "safari" in ua_lower and "chrome" not in ua_lower:
            return "Safari"
        elif "facebook" in ua_lower:
            return "Facebook Bot"
        elif "bot" in ua_lower or "crawler" in ua_lower:
            return "Bot/Crawler"
        else:
            return "Other"

    def parse_log_files(self, max_entries: int | None = None) -> list[LogEntry]:
        """Parse all log files and return entries.

        Args:
            max_entries: Maximum number of entries to parse

        Returns:
            List of parsed log entries
        """
        entries = []
        log_files = self.find_log_files()

        logger.info(f"Found {len(log_files)} log files in {self.logs_dir}")

        for log_file in log_files:
            file_entries = self._parse_single_file(log_file, max_entries)
            entries.extend(file_entries)
            logger.info(f"Parsed {len(file_entries)} entries from {log_file.name}")

            if max_entries and len(entries) >= max_entries:
                logger.info(f"Reached max entries limit ({max_entries}), stopping parsing")
                break

        final_count = len(entries[:max_entries]) if max_entries else len(entries)
        logger.info(f"Successfully parsed {final_count} total log entries")

        return entries[:max_entries] if max_entries else entries

    def _parse_single_file(self, log_file: Path, max_entries: int | None = None) -> list[LogEntry]:
        """Parse a single log file.

        Args:
            log_file: Path to log file
            max_entries: Maximum entries to parse from this file

        Returns:
            List of parsed entries from this file
        """
        entries: list[LogEntry] = []

        try:
            with open(log_file, encoding="utf-8", errors="ignore") as f:
                for _line_num, line in enumerate(f, 1):
                    if max_entries and len(entries) >= max_entries:
                        break

                    entry = self.parse_log_line(line)
                    if entry:
                        entry.source_file = log_file.name
                        entries.append(entry)
        except Exception as e:
            logger.error(f"Error reading {log_file}: {e}", exc_info=True)

        return entries
