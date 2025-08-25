"""Log analysis functionality."""

from collections import Counter

import pandas as pd

from .models import BrowserData, FilterParams, IPData, LogEntry, TrafficData


class LogAnalyzer:
    """Analyzes parsed log entries to generate insights."""

    def __init__(self, log_entries: list[LogEntry]) -> None:
        """Initialize with log entries.

        Args:
            log_entries: List of parsed log entries
        """
        self.log_entries = log_entries

    def apply_filters(self, filters: FilterParams) -> list[LogEntry]:
        """Apply filters to log entries.

        Args:
            filters: Filter parameters

        Returns:
            Filtered log entries
        """
        filtered_entries = self.log_entries

        if filters.date:
            try:
                from datetime import datetime

                target_date = datetime.strptime(filters.date, "%Y-%m-%d").date()
                filtered_entries = [entry for entry in filtered_entries if entry.parsed_datetime.date() == target_date]
            except ValueError:
                pass  # Invalid date format, skip filter

        if filters.hour is not None:
            filtered_entries = [entry for entry in filtered_entries if entry.parsed_datetime.hour == filters.hour]

        if filters.ip:
            filtered_entries = [entry for entry in filtered_entries if entry.ip == filters.ip]

        if filters.browser:
            filtered_entries = [entry for entry in filtered_entries if entry.browser == filters.browser]

        return filtered_entries

    def get_traffic_over_time(self, granularity: str = "hourly") -> TrafficData:
        """Generate traffic over time data.

        Args:
            granularity: Either 'hourly' or 'daily'

        Returns:
            Traffic data for visualization
        """
        if not self.log_entries:
            return TrafficData(dates=[], counts=[], title="No data available")

        if granularity == "hourly":
            # Extract hours directly from parsed datetime objects
            hours = [entry.parsed_datetime.hour for entry in self.log_entries]
            df_hours = pd.DataFrame({"hour": hours})
            traffic = df_hours.groupby("hour").size().reset_index(name="count")
            # Ensure all hours 0-23 are represented
            all_hours = pd.DataFrame({"hour": range(24)})
            traffic = all_hours.merge(traffic, on="hour", how="left").fillna(0)
            traffic["count"] = traffic["count"].astype(int)
            title = "Traffic by Hour"
        else:  # daily
            # Convert to pandas DataFrame for easier manipulation
            df = pd.DataFrame([entry.model_dump(by_alias=True) for entry in self.log_entries])
            df["time_bucket"] = pd.to_datetime(df["datetime"]).dt.date
            traffic = df.groupby("time_bucket").size().reset_index(name="count")
            title = "Traffic by Day"

        if granularity == "hourly":
            return TrafficData(
                dates=traffic["hour"].tolist(),
                counts=traffic["count"].tolist(),
                title=title,
            )
        else:
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
