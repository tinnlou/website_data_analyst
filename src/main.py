#!/usr/bin/env python3
"""
Website Data Analyst - Main Entry Point
Orchestrates the weekly website analytics report generation.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import validate_config, print_config_status
from src.fetchers.ga4_fetcher import GA4Fetcher, test_connection as test_ga4
from src.fetchers.gsc_fetcher import GSCFetcher, test_connection as test_gsc
from src.analyzers.gemini_analyzer import GeminiAnalyzer, test_connection as test_gemini
from src.publishers.notion_publisher import NotionPublisher, test_connection as test_notion


def test_connections():
    """Test all API connections."""
    print("\n🔌 Testing API Connections...\n")
    
    results = {}
    
    print("1. Testing GA4 connection...")
    results['ga4'] = test_ga4()
    print(f"   {'✅ Success' if results['ga4'] else '❌ Failed'}\n")
    
    print("2. Testing Search Console connection...")
    results['gsc'] = test_gsc()
    print(f"   {'✅ Success' if results['gsc'] else '❌ Failed'}\n")
    
    print("3. Testing Gemini connection...")
    results['gemini'] = test_gemini()
    print(f"   {'✅ Success' if results['gemini'] else '❌ Failed'}\n")
    
    print("4. Testing Notion connection...")
    results['notion'] = test_notion()
    print(f"   {'✅ Success' if results['notion'] else '❌ Failed'}\n")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("✅ All connections successful!")
    else:
        print("❌ Some connections failed. Please check your configuration.")
        failed = [k for k, v in results.items() if not v]
        print(f"   Failed: {', '.join(failed)}")
    
    return all_passed


def run_report(dry_run: bool = False, save_data: bool = False, date_range: dict = None):
    """
    Run the complete weekly report generation.
    
    Args:
        dry_run: If True, only fetch data without publishing
        save_data: If True, save raw data to JSON files
        date_range: Optional dict with 'start' and 'end' keys for custom date range
    """
    print("\n" + "=" * 60)
    print("📊 Website Weekly Analytics Report Generator")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display date range
    if date_range:
        print(f"📅 Analysis period: {date_range['start']} to {date_range['end']}")
    else:
        print("📅 Analysis period: Last 7 days (default)")
    print()
    
    # Step 1: Validate configuration
    print("Step 1: Validating configuration...")
    if not print_config_status():
        print("\n❌ Configuration validation failed. Please check your .env file.")
        return False
    print()
    
    # Step 2: Fetch GA4 data
    print("Step 2: Fetching GA4 data...")
    try:
        ga4_fetcher = GA4Fetcher(date_range=date_range)
        ga4_data = ga4_fetcher.fetch_all_data()
    except Exception as e:
        print(f"❌ Failed to fetch GA4 data: {e}")
        return False
    print()
    
    # Step 3: Fetch Search Console data
    print("Step 3: Fetching Search Console data...")
    try:
        gsc_fetcher = GSCFetcher(date_range=date_range)
        gsc_data = gsc_fetcher.fetch_all_data()
    except Exception as e:
        print(f"❌ Failed to fetch Search Console data: {e}")
        return False
    print()
    
    # Save raw data if requested
    if save_data:
        data_dir = PROJECT_ROOT / 'data'
        data_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(data_dir / f'ga4_data_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(ga4_data, f, indent=2, ensure_ascii=False)
        
        with open(data_dir / f'gsc_data_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(gsc_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Raw data saved to data/ directory")
        print()
    
    # Step 4: Generate analysis with Gemini
    print("Step 4: Generating AI analysis...")
    try:
        analyzer = GeminiAnalyzer()
        analysis = analyzer.analyze(ga4_data, gsc_data)
    except Exception as e:
        print(f"❌ Failed to generate analysis: {e}")
        return False
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - Report preview:")
        print("-" * 40)
        print(analysis[:2000])  # Show first 2000 chars
        if len(analysis) > 2000:
            print(f"\n... [truncated, full report is {len(analysis)} characters]")
        print("-" * 40)
        print("\n✅ Dry run completed. Report NOT published to Notion.")
        return True
    
    # Step 5: Publish to Notion
    print("Step 5: Publishing to Notion...")
    try:
        publisher = NotionPublisher()
        period = ga4_data.get('overview', {}).get('period', {}).get('current', {})
        week_start = period.get('start', '')
        week_end = period.get('end', '')
        result = publisher.publish_weekly_report(analysis, week_start, week_end)
    except Exception as e:
        print(f"❌ Failed to publish to Notion: {e}")
        return False
    print()
    
    # Done!
    print("=" * 60)
    print("✅ Weekly report generated successfully!")
    print(f"📝 Notion page: {result['url']}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return True


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Website Weekly Analytics Report Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                    # Run full report generation (last 7 days)
  python src/main.py --dry-run          # Test without publishing
  python src/main.py --test-connections # Test API connections
  python src/main.py --save-data        # Save raw data to JSON
  python src/main.py --period last-month # Analyze last month
  python src/main.py --start-date 2024-12-01 --end-date 2024-12-15  # Custom range
        """
    )
    
    parser.add_argument(
        '--test-connections',
        action='store_true',
        help='Test all API connections and exit'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch data and generate analysis, but do not publish to Notion'
    )
    
    parser.add_argument(
        '--save-data',
        action='store_true',
        help='Save raw API data to JSON files for debugging'
    )
    
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Check configuration status and exit'
    )
    
    # Date range arguments
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for analysis (format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for analysis (format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--period',
        type=str,
        choices=['last-week', 'last-month', 'last-quarter'],
        help='Preset analysis period'
    )
    
    args = parser.parse_args()
    
    if args.check_config:
        print_config_status()
        return
    
    if args.test_connections:
        success = test_connections()
        sys.exit(0 if success else 1)
    
    # Parse date range
    date_range = parse_date_range(args.start_date, args.end_date, args.period)
    
    success = run_report(
        dry_run=args.dry_run, 
        save_data=args.save_data,
        date_range=date_range
    )
    sys.exit(0 if success else 1)


def parse_date_range(start_date: str, end_date: str, period: str) -> dict:
    """
    Parse and validate date range arguments.
    
    Returns:
        Dict with 'start' and 'end' keys, or None for default behavior
    """
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    
    # Preset periods
    if period:
        if period == 'last-week':
            end = today - timedelta(days=1)
            start = end - timedelta(days=6)
        elif period == 'last-month':
            end = today - timedelta(days=1)
            start = end - timedelta(days=29)
        elif period == 'last-quarter':
            end = today - timedelta(days=1)
            start = end - timedelta(days=89)
        return {
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d')
        }
    
    # Custom date range
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end < start:
                print(f"❌ Error: End date ({end_date}) cannot be before start date ({start_date})")
                sys.exit(1)
            
            if end > today:
                print(f"⚠️ Warning: End date ({end_date}) is in the future, using yesterday")
                end = today - timedelta(days=1)
            
            return {
                'start': start.strftime('%Y-%m-%d'),
                'end': end.strftime('%Y-%m-%d')
            }
        except ValueError as e:
            print(f"❌ Error: Invalid date format. Use YYYY-MM-DD. Details: {e}")
            sys.exit(1)
    
    # Default: last 7 days
    return None


if __name__ == '__main__':
    main()

