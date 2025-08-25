"""Data models for log parsing and analysis."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """Represents a single parsed log entry."""

    ip: str = Field(description="Client IP address")
    timestamp: str = Field(description="Raw timestamp from log")
    parsed_datetime: datetime = Field(
        description="Parsed datetime object", alias="datetime"
    )
    method: str = Field(description="HTTP method")
    path: str = Field(description="Request path")
    protocol: str = Field(description="HTTP protocol version")
    status: int = Field(description="HTTP status code")
    response_bytes: str = Field(description="Response size in bytes", alias="bytes")
    referer: str = Field(description="HTTP referer")
    user_agent: str = Field(description="User agent string")
    browser: str = Field(description="Parsed browser name")
    source_file: str = Field(description="Source log file name")

    model_config = {"populate_by_name": True}


class TrafficData(BaseModel):
    """Traffic over time data."""

    dates: list[Any] = Field(description="Time points")
    counts: list[int] = Field(description="Request counts")
    title: str = Field(description="Chart title")


class IPData(BaseModel):
    """IP frequency data."""

    ips: list[str] = Field(description="IP addresses")
    counts: list[int] = Field(description="Request counts per IP")
    title: str = Field(description="Chart title")


class BrowserData(BaseModel):
    """Browser usage data."""

    browsers: list[str] = Field(description="Browser names")
    counts: list[int] = Field(description="Usage counts per browser")
    title: str = Field(description="Chart title")


class LogSummary(BaseModel):
    """Summary of log analysis."""

    total_entries: int = Field(description="Total number of log entries")
    unique_ips: int = Field(description="Number of unique IP addresses")
    date_range: str | None = Field(description="Date range of logs")
    files_processed: list[str] = Field(description="List of processed log files")
