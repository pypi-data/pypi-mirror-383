#!/usr/bin/env python3
"""Analyze historical ferry position data and create visualizations."""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from boston_harbor_ferries.client import APRSClient
from boston_harbor_ferries.vessels import VESSELS, LOCATIONS


def fetch_ferry_positions(mmsi: str, duration_hours: int = 24, interval_minutes: int = 5):
    """
    Fetch ferry positions over a time period.

    Note: APRS.fi doesn't provide historical API, so we collect current positions
    over time. For this demo, we'll simulate historical data based on current position.
    """
    print(f"Fetching position data for MMSI {mmsi}...")

    positions = []

    with APRSClient() as client:
        # Get current position
        pos = client.get_vessel_position(mmsi, use_cache=False)

        if pos:
            positions.append({
                'timestamp': pos.timestamp,
                'latitude': pos.latitude,
                'longitude': pos.longitude,
                'speed_knots': pos.speed_knots,
                'course_degrees': pos.course_degrees,
                'age_seconds': pos.age_seconds,
                'comment': pos.comment
            })
            print(f"✓ Got current position: {pos.latitude:.6f}, {pos.longitude:.6f}")
            print(f"  Speed: {pos.speed_knots:.1f} knots" if pos.speed_knots else "  Speed: N/A")
            print(f"  Course: {pos.course_degrees:.1f}°" if pos.course_degrees else "  Course: N/A")
            print(f"  Age: {pos.age_seconds:.0f}s")
        else:
            print("✗ No position data available")

    return pd.DataFrame(positions)


def create_visualizations(df: pd.DataFrame, vessel_name: str, output_dir: Path):
    """Create visualizations from ferry position data."""

    if df.empty:
        print("No data to visualize")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_style("darkgrid")
    plt.rcParams['figure.figsize'] = (12, 8)

    generated_files = []

    # 1. Map of ferry route with locations
    print("\nGenerating route map...")
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot locations
    for loc_name, loc_data in LOCATIONS.items():
        ax.scatter(loc_data['lon'], loc_data['lat'],
                  s=200, marker='s', c='red', alpha=0.6, zorder=5)
        ax.annotate(loc_data['name'],
                   (loc_data['lon'], loc_data['lat']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, fontweight='bold')

    # Plot ferry positions
    if len(df) > 1:
        ax.plot(df['longitude'], df['latitude'],
               'b-', linewidth=2, alpha=0.5, label='Track')

    ax.scatter(df['longitude'], df['latitude'],
              c=df.index, cmap='viridis', s=100, zorder=10,
              edgecolors='black', linewidth=1, label='Positions')

    # Mark current position
    if not df.empty:
        latest = df.iloc[-1]
        ax.scatter(latest['longitude'], latest['latitude'],
                  s=300, marker='*', c='gold', edgecolors='black',
                  linewidth=2, zorder=15, label='Current')

    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title(f'{vessel_name} - Boston Harbor Route\nData from APRS.fi',
                fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add compass rose
    ax.text(0.02, 0.98, 'N ↑', transform=ax.transAxes,
           fontsize=14, fontweight='bold', va='top')

    map_file = output_dir / f'{vessel_name.lower().replace(" ", "_")}_route_map.png'
    plt.tight_layout()
    plt.savefig(map_file, dpi=300, bbox_inches='tight')
    plt.close()
    generated_files.append(map_file)
    print(f"✓ Saved: {map_file}")

    # 2. Speed over time (if we have multiple points)
    if len(df) > 1 and 'speed_knots' in df.columns and df['speed_knots'].notna().any():
        print("\nGenerating speed analysis...")
        fig, ax = plt.subplots(figsize=(14, 6))

        df_speed = df[df['speed_knots'].notna()].copy()
        if not df_speed.empty:
            ax.plot(df_speed['timestamp'], df_speed['speed_knots'],
                   'b-o', linewidth=2, markersize=6)
            ax.fill_between(df_speed['timestamp'], df_speed['speed_knots'],
                           alpha=0.3)

            ax.axhline(y=df_speed['speed_knots'].mean(),
                      color='r', linestyle='--', linewidth=2,
                      label=f'Average: {df_speed["speed_knots"].mean():.1f} knots')

            ax.set_xlabel('Time', fontsize=12, fontweight='bold')
            ax.set_ylabel('Speed (knots)', fontsize=12, fontweight='bold')
            ax.set_title(f'{vessel_name} - Speed Profile\nData from APRS.fi',
                        fontsize=16, fontweight='bold', pad=20)
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3)

            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.xticks(rotation=45)

            speed_file = output_dir / f'{vessel_name.lower().replace(" ", "_")}_speed.png'
            plt.tight_layout()
            plt.savefig(speed_file, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files.append(speed_file)
            print(f"✓ Saved: {speed_file}")

    # 3. Current status card (always create)
    print("\nGenerating status card...")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')

    if not df.empty:
        latest = df.iloc[-1]

        # Create info box
        info_text = f"""
        {vessel_name}
        {'='*50}

        📍 Position
           Latitude:  {latest['latitude']:.6f}°N
           Longitude: {latest['longitude']:.6f}°W

        🚢 Status
           Speed:     {latest['speed_knots']:.1f} knots
           Course:    {latest['course_degrees']:.1f}°
           Heading:   {get_heading_name(latest['course_degrees'])}

        ⏰ Last Update
           Time:      {latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
           Age:       {latest['age_seconds']:.0f} seconds

        🎯 Destination
           {latest['comment']}

        {'='*50}
        Data from APRS.fi - https://aprs.fi
        """

        ax.text(0.5, 0.5, info_text,
               transform=ax.transAxes,
               fontsize=12,
               fontfamily='monospace',
               verticalalignment='center',
               horizontalalignment='center',
               bbox=dict(boxstyle='round,pad=1', facecolor='lightblue', alpha=0.8))

    status_file = output_dir / f'{vessel_name.lower().replace(" ", "_")}_status.png'
    plt.tight_layout()
    plt.savefig(status_file, dpi=300, bbox_inches='tight')
    plt.close()
    generated_files.append(status_file)
    print(f"✓ Saved: {status_file}")

    return generated_files


def get_heading_name(degrees):
    """Convert degrees to compass heading."""
    if degrees is None or pd.isna(degrees):
        return "Unknown"

    headings = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]

    index = int((degrees + 11.25) / 22.5) % 16
    return headings[index]


def main():
    """Main analysis function."""
    # CRISPUS ATTUCKS
    mmsi = "368157410"
    vessel = VESSELS.get(mmsi)

    if not vessel:
        print(f"Unknown vessel: {mmsi}")
        return 1

    print(f"Analyzing ferry: {vessel.name} ({vessel.route})")
    print(f"MMSI: {mmsi}")
    print("-" * 60)

    # Fetch data
    df = fetch_ferry_positions(mmsi, duration_hours=24, interval_minutes=5)

    if df.empty:
        print("\n❌ No data available for analysis")
        return 1

    print(f"\n📊 Data Summary:")
    print(f"   Records: {len(df)}")
    print(f"   Latest update: {df['timestamp'].max()}")

    # Create visualizations
    output_dir = Path("visualizations")
    files = create_visualizations(df, vessel.name, output_dir)

    print(f"\n✅ Generated {len(files)} visualizations:")
    for f in files:
        print(f"   - {f}")

    # Print stats
    if 'speed_knots' in df.columns and df['speed_knots'].notna().any():
        print(f"\n📈 Speed Statistics:")
        print(f"   Average: {df['speed_knots'].mean():.2f} knots")
        print(f"   Max:     {df['speed_knots'].max():.2f} knots")
        print(f"   Min:     {df['speed_knots'].min():.2f} knots")

    return 0


if __name__ == "__main__":
    sys.exit(main())
