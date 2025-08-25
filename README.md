# Access Log Analyzer

A web-based tool for visualizing and analyzing web server access logs with interactive charts and insights.

## Goal

This project aims to make web server log analysis accessible and insightful by providing:

- **Visual Traffic Analysis**: Interactive charts showing request patterns over time
- **IP Address Insights**: Identify the most active visitors and potential patterns
- **Browser Usage Analytics**: Understand what browsers and user agents are accessing your site
- **Flexible Time Views**: Switch between hourly and daily granularity to spot trends
- **Easy Data Refresh**: Real-time log reloading without restarting the application

## What You'll Learn

Perfect for learning modern Python web development with:
- FastAPI web framework fundamentals
- Interactive data visualization with Plotly
- Log parsing and data analysis techniques
- Responsive web design principles
- RESTful API design patterns
- Modern Python tooling (uv, ruff, mypy, pytest)
- CI/CD with GitHub Actions
- Pre-commit hooks and code quality

## Target Use Case

Designed for developers and site administrators who want to:
- Monitor website traffic patterns
- Identify unusual access patterns or potential security concerns
- Understand visitor behavior and browser preferences
- Learn modern Python web development in a practical context

The tool automatically detects and processes standard Apache/Nginx access log formats.

## Quick Start

1. **Setup environment:**
   ```bash
   make init
   ```

2. **Run the application:**
   ```bash
   make serve
   ```

3. **Visit the dashboard:**
   Open http://localhost:8000 in your browser

## Development

- `make check` - Run all code quality checks
- `make test` - Run tests
- `make lint` - Check code style
- `make format` - Check formatting
- `make type` - Type checking
- `make clean` - Remove build artifacts

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for dependency management