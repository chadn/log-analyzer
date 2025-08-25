"""Main FastAPI application for the access log analyzer."""

import json
import logging

import pandas as pd
import plotly
import plotly.express as px
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .analyzer import LogAnalyzer
from .config import settings
from .models import FilterParams, LogEntry, LogSummary
from .parser import LogParser

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Access Log Analyzer", version="0.1.0")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state
_log_entries: list[LogEntry] = []


def load_logs() -> list[LogEntry]:
    """Load and parse log files.

    Returns:
        List of parsed log entries
    """
    parser = LogParser(settings.logs_dir)
    return parser.parse_log_files(settings.max_log_entries)


@app.on_event("startup")
async def startup_event() -> None:
    """Load logs on startup."""
    global _log_entries
    _log_entries = load_logs()
    logger.info(f"Loaded {len(_log_entries)} log entries from {settings.logs_dir}")


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    granularity: str = "hourly",
    date: str | None = None,
    hour: int | None = None,
    ip: str | None = None,
    browser: str | None = None,
) -> HTMLResponse:
    """Main dashboard page.

    Args:
        request: FastAPI request object
        granularity: Time granularity for traffic chart ('hourly' or 'daily')
        date: Filter by specific date
        hour: Filter by specific hour
        ip: Filter by specific IP
        browser: Filter by specific browser

    Returns:
        HTML response with dashboard
    """
    # Apply filters
    filters = FilterParams(date=date, hour=hour, ip=ip, browser=browser)
    analyzer = LogAnalyzer(_log_entries)
    filtered_entries = analyzer.apply_filters(filters)
    filtered_analyzer = LogAnalyzer(filtered_entries)

    # Determine granularity based on filters
    if filters.date and not filters.hour:
        # If filtering by date but not hour, show hourly breakdown
        actual_granularity = "hourly"
    elif filters.hour is not None and not filters.date:
        # If filtering by hour but not date, show daily breakdown
        actual_granularity = "daily"
    else:
        # Otherwise use requested granularity
        actual_granularity = granularity

    # Generate all the plots using filtered data
    traffic_data = filtered_analyzer.get_traffic_over_time(actual_granularity)
    ip_data = filtered_analyzer.get_ip_frequency(settings.default_ip_limit)
    browser_data = filtered_analyzer.get_browser_stats()

    # Create filter description
    filter_parts = []
    if filters.date:
        filter_parts.append(f"Date: {filters.date}")
    if filters.hour is not None:
        filter_parts.append(f"Hour: {filters.hour}")
    if filters.ip:
        filter_parts.append(f"IP: {filters.ip}")
    if filters.browser:
        filter_parts.append(f"Browser: {filters.browser}")

    filter_description = "Showing " + (", ".join(filter_parts) if filter_parts else "all data")

    # Log filtering activity for debugging if needed
    if filter_parts:
        logger.debug(f"Applying filters: {filter_description}")
        logger.debug(f"Filtered from {len(_log_entries)} to {len(filtered_entries)} entries")

    logger.debug(f"Generating {actual_granularity} traffic chart with {len(traffic_data.dates)} data points")

    # Create Plotly figures using proper DataFrame API for version 6.3.0

    # Traffic chart
    traffic_df = pd.DataFrame({"time": traffic_data.dates, "count": traffic_data.counts})
    fig1 = px.bar(
        traffic_df,
        x="time",
        y="count",
        title=traffic_data.title,
        labels={
            "time": "Hour" if granularity == "hourly" else "Date",
            "count": "Request Count",
        },
    )
    fig1.update_layout(showlegend=False)

    # Format x-axis for hourly data
    if granularity == "hourly":
        fig1.update_xaxes(
            tickmode="linear",
            tick0=0,
            dtick=2,  # Show every 2 hours
            tickformat="d",  # Show as integers
            title="Hour of Day",
            range=[-0.5, 23.5],  # Ensure all hours 0-23 are visible
        )

    # IP frequency chart
    ip_df = pd.DataFrame({"ip": ip_data.ips, "count": ip_data.counts})
    fig2 = px.bar(
        ip_df,
        x="count",
        y="ip",
        orientation="h",
        title=ip_data.title,
        labels={"count": "Request Count", "ip": "IP Address"},
    )
    # Calculate height based on number of IPs (minimum 400px, 25px per IP)
    ip_chart_height = max(400, len(ip_data.ips) * 25)
    fig2.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=ip_chart_height,
        margin={
            "l": 150,
            "r": 50,
            "t": 50,
            "b": 50,
        },  # Increase left margin for IP labels
    )

    # Browser distribution chart
    browser_df = pd.DataFrame({"browser": browser_data.browsers, "count": browser_data.counts})
    fig3 = px.pie(
        browser_df,
        values="count",
        names="browser",
        title=browser_data.title,
    )

    # Convert to JSON for template
    graphs = {
        "traffic": json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder),
        "ips": json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder),
        "browsers": json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder),
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "graphs": graphs,
            "granularity": actual_granularity,
            "total_requests": len(filtered_entries),
            "unique_ips": len({entry.ip for entry in filtered_entries}),
            "date_range": _get_date_range(filtered_entries),
            "filter_description": filter_description,
            "active_filters": filters.model_dump(),
        },
    )


@app.get("/api/logs")
async def get_logs_data() -> LogSummary:
    """API endpoint to get raw log data summary.

    Returns:
        Summary of log data
    """
    return LogSummary(
        total_entries=len(_log_entries),
        unique_ips=len({entry.ip for entry in _log_entries}),
        date_range=_get_date_range(),
        files_processed=list({entry.source_file for entry in _log_entries}),
        active_filters=FilterParams(date=None, hour=None, ip=None, browser=None),
        filter_description="Showing all data",
    )


@app.get("/api/refresh")
async def refresh_logs() -> dict[str, str]:
    """Refresh log data.

    Returns:
        Status message
    """
    global _log_entries
    _log_entries = load_logs()
    return {"message": f"Reloaded {len(_log_entries)} log entries"}


def _get_date_range(entries: list[LogEntry] | None = None) -> str:
    """Get the date range of loaded logs.

    Args:
        entries: Log entries to analyze, defaults to global entries

    Returns:
        Date range string or 'No data' if no logs
    """
    if entries is None:
        entries = _log_entries

    if not entries:
        return "No data"

    dates = [entry.parsed_datetime.date() for entry in entries]
    return f"{min(dates)} to {max(dates)}"


def cli() -> None:
    """CLI entry point for running the server."""
    import uvicorn

    uvicorn.run(
        "access_log_analyzer.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    cli()
