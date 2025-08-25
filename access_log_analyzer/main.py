"""Main FastAPI application for the access log analyzer."""

import json

import plotly
import plotly.express as px
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .analyzer import LogAnalyzer
from .config import settings
from .models import LogEntry, LogSummary
from .parser import LogParser

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
    print(f"Loaded {len(_log_entries)} log entries")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, granularity: str = "hourly") -> HTMLResponse:
    """Main dashboard page.

    Args:
        request: FastAPI request object
        granularity: Time granularity for traffic chart ('hourly' or 'daily')

    Returns:
        HTML response with dashboard
    """
    analyzer = LogAnalyzer(_log_entries)

    # Generate all the plots
    traffic_data = analyzer.get_traffic_over_time(granularity)
    ip_data = analyzer.get_ip_frequency(settings.default_ip_limit)
    browser_data = analyzer.get_browser_stats()

    # Debug what data is being passed to chart
    if granularity == "hourly":
        print(f"DEBUG CHART: dates={traffic_data.dates[:10]}...")
        print(f"DEBUG CHART: counts={traffic_data.counts[:10]}...")
        print(f"DEBUG CHART: len(dates)={len(traffic_data.dates)}, len(counts)={len(traffic_data.counts)}")

    # Create Plotly figures using proper DataFrame API for version 6.3.0
    import pandas as pd
    
    # Traffic chart
    traffic_df = pd.DataFrame({
        'time': traffic_data.dates,
        'count': traffic_data.counts
    })
    fig1 = px.bar(
        traffic_df,
        x='time',
        y='count',
        title=traffic_data.title,
        labels={"time": "Hour" if granularity == "hourly" else "Date", "count": "Request Count"},
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
            range=[-0.5, 23.5]  # Ensure all hours 0-23 are visible
        )

    # IP frequency chart
    ip_df = pd.DataFrame({
        'ip': ip_data.ips,
        'count': ip_data.counts
    })
    fig2 = px.bar(
        ip_df,
        x='count',
        y='ip',
        orientation="h",
        title=ip_data.title,
        labels={"count": "Request Count", "ip": "IP Address"},
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"})

    # Browser distribution chart
    browser_df = pd.DataFrame({
        'browser': browser_data.browsers,
        'count': browser_data.counts
    })
    fig3 = px.pie(
        browser_df,
        values='count',
        names='browser',
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
            "granularity": granularity,
            "total_requests": len(_log_entries),
            "unique_ips": len({entry.ip for entry in _log_entries}),
            "date_range": _get_date_range(),
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


def _get_date_range() -> str:
    """Get the date range of loaded logs.

    Returns:
        Date range string or 'No data' if no logs
    """
    if not _log_entries:
        return "No data"

    dates = [entry.parsed_datetime.date() for entry in _log_entries]
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
