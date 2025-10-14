"""FastMCP server for DART MCP tools."""

from __future__ import annotations

import os
import sys
from datetime import datetime

import pandas as pd

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fallback for systems without MCP installed
    class FastMCP:
        def __init__(self, name):
            self.name = name
            self.tools = []
        
        def tool(self):
            def decorator(func):
                self.tools.append(func)
                return func
            return decorator
        
        def run(self, transport="stdio"):
            print("MCP server would run here, but MCP package not available")
            print("Available tools:", [tool.__name__ for tool in self.tools])

from . import gtfs

mcp = FastMCP("dart")


@mcp.tool()
async def next_trains(
    origin: str, destination: str, when_iso: str | None = None
) -> str:
    """Return the next few scheduled DART bus departures.

    Args:
        origin: Stop name (e.g. 'DART Central Station').
                Supports common abbreviations like 'DART' for DART Central Station, 'DT' for downtown.
                If stop is not found, use list_stations() to see all available options.
        destination: Route name (e.g. 'University', 'Fairgrounds', 'Maury St').
                     This represents the bus route destination, not a specific stop.
                     If route is not found, use list_routes() to see all available routes.
        when_iso: Optional ISO-8601 datetime (local time). Default: now.

    Note: This is a bus system with one central station and multiple routes.
    Use list_stations() for stops and list_routes() for destinations.
    """
    try:
        # Parse the target time
        if when_iso:
            try:
                when_dt = datetime.fromisoformat(when_iso.replace("Z", "+00:00"))
                # Convert to local time if needed
                if when_dt.tzinfo is not None:
                    # Convert to naive datetime assuming Central time
                    when_dt = when_dt.replace(tzinfo=None)
            except ValueError:
                return (
                    f"Invalid datetime format: {when_iso}. Please use ISO-8601 format."
                )
        else:
            when_dt = datetime.now()

        target_date = when_dt.date()
        seconds_since_midnight = (
            when_dt.hour * 3600 + when_dt.minute * 60 + when_dt.second
        )

        # Find station IDs with enhanced error handling
        data = gtfs.get_default_data()
        try:
            origin_id = gtfs.find_station(origin, data)
        except ValueError:
            available_stations = gtfs.list_all_stations(data)
            # Try to find close matches
            close_matches = [
                s
                for s in available_stations
                if origin.lower() in s.lower()
                or s.lower().startswith(origin.lower()[:3])
            ]
            error_msg = f"Origin station '{origin}' not found."
            if close_matches:
                error_msg += (
                    f" Did you mean one of these? {', '.join(close_matches[:5])}"
                )
            else:
                error_msg += " Use list_stations() to see all available stations."
            return error_msg

        # Get station name for display
        origin_name = gtfs.get_station_name(origin_id, data)

        # For bus systems, we'll show routes departing from the central station
        # Filter trips by destination route name
        available_routes = data.trips["trip_headsign"].dropna().unique()
        matching_routes = [
            route for route in available_routes
            if destination.lower() in route.lower()
        ]
        
        if not matching_routes:
            error_msg = f"Destination route '{destination}' not found."
            error_msg += f" Use list_routes() to see all available routes."
            return error_msg

        # Find next buses for the matching route
        route_trips = data.trips[data.trips["trip_headsign"].isin(matching_routes)]
        if route_trips.empty:
            return f"No buses found for route '{destination}'."

        # Get active service IDs for the target date
        service_ids = gtfs.get_active_service_ids(target_date, data)
        if not service_ids:
            return f"No service available on {target_date.strftime('%A, %B %d, %Y')}."

        # Filter to active trips
        active_trips = route_trips[route_trips["service_id"].isin(service_ids)]
        if active_trips.empty:
            return f"No active buses for route '{destination}' on {target_date.strftime('%A, %B %d, %Y')}."

        # Get stop times for the origin station
        origin_platforms = gtfs.get_platform_stops_for_station(origin_id, data)
        if not origin_platforms:
            return f"No platform stops found for {origin_name}."

        # Get stop times for these trips from the origin
        stop_times = data.stop_times[
            (data.stop_times["trip_id"].isin(active_trips["trip_id"])) &
            (data.stop_times["stop_id"].isin(origin_platforms))
        ].copy()

        if stop_times.empty:
            return f"No departures found from {origin_name} for route '{destination}'."

        # Convert departure times to seconds and filter
        stop_times["dep_seconds"] = stop_times["departure_time"].apply(gtfs.time_to_seconds)
        stop_times = stop_times.dropna(subset=["dep_seconds"])
        
        # Filter to departures after the specified time
        upcoming = stop_times[stop_times["dep_seconds"] >= seconds_since_midnight]
        
        if upcoming.empty:
            return f"No more buses today from {origin_name} to {destination}."

        # Sort by departure time and limit results
        upcoming = upcoming.sort_values("dep_seconds").head(5)

        # Join with trips to get trip information
        upcoming = upcoming.merge(
            active_trips[["trip_id", "trip_headsign", "trip_short_name"]], on="trip_id"
        )

        # Format results
        lines = []
        for _, row in upcoming.iterrows():
            dep_time = row["departure_time"]
            train_name = row["trip_short_name"] if pd.notna(row["trip_short_name"]) else row["trip_id"]
            headsign = row["trip_headsign"] or ""
            
            line = f"• Bus {train_name}: {dep_time}"
            if headsign:
                line += f" (to {headsign})"
            lines.append(line)

        date_str = target_date.strftime("%A, %B %d, %Y")
        current_time_str = when_dt.strftime("%I:%M %p")
        header = (
            f"Next DART bus departures from {origin_name} to {destination} "
            f"on {date_str}:\n(Current time: {current_time_str})\n\n"
        )
        return header + "\n".join(lines)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def list_stations() -> str:
    """List all available DART bus stops.

    This tool is useful when you need to find the exact stop names, especially if
    the next_trains() tool returns a "Station not found" error. Stop names are
    case-insensitive and support some common abbreviations like 'DART' and 'DT'.

    Returns a formatted list of all DART bus stops that can be used as origin
    or destination in the next_trains() tool.
    """
    try:
        stations = gtfs.list_all_stations(gtfs.get_default_data())
        stations_list = "\n".join([f"• {station}" for station in stations])
        return f"Available DART bus stops:\n{stations_list}\n\nNote: Stop names support common abbreviations like 'DART' for DART Central Station and 'DT' for downtown."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def list_routes() -> str:
    """List all available DART bus routes.

    This tool shows all the bus routes available in the DART system.
    These route names can be used as destinations in the next_trains() tool.

    Returns a formatted list of all DART bus routes.
    """
    try:
        data = gtfs.get_default_data()
        routes = data.trips["trip_headsign"].dropna().unique()
        routes_list = "\n".join([f"• {route}" for route in sorted(routes)])
        return f"Available DART bus routes:\n{routes_list}\n\nNote: Use these route names as destinations in the next_trains() tool."
    except Exception as e:
        return f"Error: {str(e)}"


def main() -> None:
    """Main entry point for the MCP server."""
    # Only load GTFS data when not in test mode
    if os.getenv("PYTEST_CURRENT_TEST") is None and "pytest" not in sys.modules:
        try:
            data = gtfs.get_default_data()
            stations_count = len(data.stations)
            # Use stderr for logging to avoid interfering with MCP protocol on stdout
            print(
                f"Loaded GTFS data successfully. Found {stations_count} stations.",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"Error loading GTFS data: {e}", file=sys.stderr)
            sys.exit(1)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
