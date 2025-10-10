"""CLI for Boston Harbor ferry tracking."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .client import APRSClient
from .vessels import VESSELS, ROUTES


console = Console()


@click.group()
@click.version_option()
def main():
    """Boston Harbor ferry tracker using APRS.fi.

    Track Seaport Ferry vessels in real-time.

    Data provided by aprs.fi - https://aprs.fi
    """
    pass


@main.command()
def list_vessels():
    """List all known Boston Harbor ferries."""
    table = Table(title="Boston Harbor Commuter Ferries", show_header=True)

    table.add_column("MMSI", style="cyan")
    table.add_column("Vessel Name", style="green bold")
    table.add_column("Route", style="yellow")
    table.add_column("Operator", style="blue")
    table.add_column("Capacity", style="magenta")

    for mmsi, vessel in VESSELS.items():
        table.add_row(
            mmsi,
            vessel.name,
            vessel.route,
            vessel.operator,
            str(vessel.capacity) if vessel.capacity else "N/A",
        )

    console.print()
    console.print(table)
    console.print()
    console.print("[dim]Data source: aprs.fi - https://aprs.fi[/dim]")


@main.command()
def routes():
    """Show ferry routes and schedules."""
    for route_name, route in ROUTES.items():
        console.print()
        console.print(Panel(
            f"[bold]{route_name}[/bold]\n\n"
            f"Stops:\n" + "\n".join(f"  • {stop}" for stop in route.stops) + "\n\n"
            f"Travel time: ~{route.travel_time_minutes} minutes",
            title=route_name,
            border_style="blue",
        ))


@main.command()
@click.argument("mmsi")
@click.option("--no-cache", is_flag=True, help="Force fresh data from API")
def track(mmsi: str, no_cache: bool):
    """Track a specific ferry by MMSI number.

    Example: harbor-ferry track 368157410
    """
    if mmsi not in VESSELS:
        console.print(f"[red]Error:[/red] Unknown MMSI {mmsi}", file=sys.stderr)
        console.print("\nKnown vessels:", file=sys.stderr)
        for known_mmsi, vessel in VESSELS.items():
            console.print(f"  {known_mmsi}: {vessel.name}", file=sys.stderr)
        sys.exit(1)

    vessel = VESSELS[mmsi]

    with console.status(f"[bold green]Fetching position for {vessel.name}..."):
        with APRSClient() as client:
            position = client.get_vessel_position(mmsi, use_cache=not no_cache)

    if position is None:
        console.print(f"[yellow]No recent position data for {vessel.name}[/yellow]")
        sys.exit(0)

    # Format output
    status_text = Text()
    status_text.append(f"{vessel.name}\n", style="bold green")
    status_text.append(f"MMSI: {mmsi}\n", style="cyan")
    status_text.append(f"Route: {vessel.route}\n\n", style="yellow")

    status_text.append("Position:\n", style="bold")
    status_text.append(f"  Latitude:  {position.latitude:.6f}°N\n")
    status_text.append(f"  Longitude: {position.longitude:.6f}°W\n")

    if position.speed_knots is not None:
        status_text.append(f"  Speed:     {position.speed_knots:.1f} knots\n")

    if position.course_degrees is not None:
        status_text.append(f"  Course:    {position.course_degrees}°\n")

    status_text.append(f"\nLast update: {position.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim")
    status_text.append(f"Data age: {position.age_seconds:.0f} seconds\n", style="dim")

    if position.comment:
        status_text.append(f"\nComment: {position.comment}\n", style="italic")

    console.print()
    console.print(Panel(status_text, title="Ferry Position", border_style="green"))
    console.print()
    console.print("[dim]Data from aprs.fi - https://aprs.fi[/dim]")


@main.command()
@click.option("--no-cache", is_flag=True, help="Force fresh data from API")
def track_all(no_cache: bool):
    """Track all Boston Harbor ferries."""
    with console.status("[bold green]Fetching all ferry positions..."):
        with APRSClient() as client:
            positions = client.get_all_ferries(use_cache=not no_cache)

    if not positions:
        console.print("[yellow]No ferry position data available[/yellow]")
        sys.exit(0)

    table = Table(title="Boston Harbor Ferry Positions", show_header=True)

    table.add_column("Vessel", style="green bold")
    table.add_column("Route", style="yellow")
    table.add_column("Latitude", style="cyan")
    table.add_column("Longitude", style="cyan")
    table.add_column("Speed", style="magenta")
    table.add_column("Age", style="dim")

    for pos in sorted(positions, key=lambda p: p.vessel.name):
        speed = f"{pos.speed_knots:.1f} kn" if pos.speed_knots else "N/A"
        age = f"{pos.age_seconds:.0f}s"

        table.add_row(
            pos.vessel.name,
            pos.vessel.route,
            f"{pos.latitude:.6f}°",
            f"{pos.longitude:.6f}°",
            speed,
            age,
        )

    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]Showing {len(positions)} of {len(VESSELS)} known ferries[/dim]")
    console.print("[dim]Data from aprs.fi - https://aprs.fi[/dim]")


@main.command()
def cache_info():
    """Show cache statistics."""
    with APRSClient() as client:
        stats = client.get_cache_stats()

    console.print()
    console.print(Panel(
        f"Cache size: {stats['size']} entries\n"
        f"Cache path: {stats['path']}\n"
        f"TTL: {stats['ttl_seconds']} seconds",
        title="Cache Statistics",
        border_style="blue",
    ))


@main.command()
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
def clear_cache():
    """Clear all cached ferry data."""
    with APRSClient() as client:
        client.clear_cache()

    console.print("[green]Cache cleared successfully[/green]")


@main.command()
def test_api():
    """Test API connectivity and verify configuration."""
    from .config import get_settings
    import httpx

    settings = get_settings()

    console.print()
    console.print(Panel(
        f"[bold]API Configuration Test[/bold]\n\n"
        f"API Key: {settings.api_key[:8]}...{settings.api_key[-4:]}\n"
        f"User-Agent: {settings.user_agent}\n"
        f"Base URL: {settings.api_base_url}\n"
        f"Cache TTL: {settings.cache_ttl_seconds}s\n"
        f"Rate limit: {settings.max_requests_per_minute}/min",
        title="Configuration",
        border_style="blue",
    ))

    # Test a simple API call
    console.print()
    with console.status("[bold green]Testing API connection..."):
        try:
            # Use a known good callsign for testing (W1AW is ARRL HQ)
            url = f"{settings.api_base_url}/get"
            headers = {"User-Agent": settings.user_agent}
            params = {
                "name": "W1AW",
                "what": "loc",
                "apikey": settings.api_key,
                "format": "json",
            }

            response = httpx.get(url, headers=headers, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "ok":
                    console.print("[green]✓ API connection successful![/green]")
                    console.print(f"[green]✓ API key is valid[/green]")
                    console.print(f"[green]✓ User-Agent accepted[/green]")
                    console.print()
                    console.print("[dim]Test query: W1AW (ARRL HQ)[/dim]")
                    if data.get("found"):
                        console.print(f"[dim]Found {data['found']} result(s)[/dim]")
                elif data.get("result") == "fail":
                    console.print(f"[red]✗ API error: {data.get('description', 'Unknown error')}[/red]")
                    sys.exit(1)
            else:
                console.print(f"[red]✗ HTTP {response.status_code}: {response.text}[/red]")
                sys.exit(1)

        except httpx.TimeoutException:
            console.print("[red]✗ API request timed out[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            sys.exit(1)

    console.print()
    console.print("[bold green]All tests passed! Your configuration is working correctly.[/bold green]")
    console.print()


if __name__ == "__main__":
    main()
