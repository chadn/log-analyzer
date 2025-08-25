"""Log analysis functionality."""

from collections import Counter

import pandas as pd

from .models import BrowserData, IPData, LogEntry, TrafficData


class LogAnalyzer:
    """Analyzes parsed log entries to generate insights."""

    def __init__(self, log_entries: list[LogEntry]) -> None:
        """Initialize with log entries.

        Args:
            log_entries: List of parsed log entries
        """
        self.log_entries = log_entries

    def get_traffic_over_time(self, granularity: str = "hourly") -> TrafficData:
        """Generate traffic over time data.

        Args:
            granularity: Either 'hourly' or 'daily'

        Returns:
            Traffic data for visualization
        """
        if not self.log_entries:
            return TrafficData(dates=[], counts=[], title="No data available")

        # Convert to pandas DataFrame for easier manipulation
        df = pd.DataFrame([entry.model_dump(by_alias=True) for entry in self.log_entries])

        if granularity == "hourly":
            df["time_bucket"] = pd.to_datetime(df["datetime"]).dt.floor("h")
            title = "Traffic by Hour"
        else:  # daily
            df["time_bucket"] = pd.to_datetime(df["datetime"]).dt.date
            title = "Traffic by Day"

        traffic = df.groupby("time_bucket").size().reset_index(name="count")

        return TrafficData(
            dates=traffic["time_bucket"].tolist(),
            counts=traffic["count"].tolist(),
            title=title,
        )

    def get_ip_frequency(self, top_n: int = 20) -> IPData:
        """Generate IP address frequency data.

        Args:
            top_n: Number of top IPs to return

        Returns:
            IP frequency data for visualization
        """
        if not self.log_entries:
            return IPData(ips=[], counts=[], title="No data available")

        ip_counts = Counter(entry.ip for entry in self.log_entries)
        top_ips = ip_counts.most_common(top_n)

        return IPData(
            ips=[ip for ip, _ in top_ips],
            counts=[count for _, count in top_ips],
            title=f"Top {top_n} IP Addresses",
        )

    def get_browser_stats(self) -> BrowserData:
        """Generate browser usage statistics.

        Returns:
            Browser usage data for visualization
        """
        if not self.log_entries:
            return BrowserData(browsers=[], counts=[], title="No data available")

        browser_counts = Counter(entry.browser for entry in self.log_entries)

        return BrowserData(
            browsers=list(browser_counts.keys()),
            counts=list(browser_counts.values()),
            title="Browser Usage Distribution",
        )
