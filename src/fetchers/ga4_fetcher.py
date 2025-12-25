"""
GA4 Data Fetcher Module.
Fetches analytics data from Google Analytics 4 using the Data API.
"""

import json
from datetime import datetime, timedelta
from typing import Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy,
)
from google.oauth2 import service_account

from src.config import GOOGLE_CREDENTIALS_PATH, GA4_PROPERTY_ID


class GA4Fetcher:
    """Fetches data from Google Analytics 4."""
    
    def __init__(self, credentials_path: Optional[str] = None, property_id: Optional[str] = None, date_range: dict = None):
        """
        Initialize the GA4 Fetcher.
        
        Args:
            credentials_path: Path to service account JSON file
            property_id: GA4 Property ID (format: properties/XXXXXXXXX or just the number)
            date_range: Optional dict with 'start' and 'end' keys for custom date range
        """
        self.credentials_path = credentials_path or GOOGLE_CREDENTIALS_PATH
        self.property_id = property_id or GA4_PROPERTY_ID
        self.custom_date_range = date_range
        
        # Normalize property ID format
        if self.property_id and not self.property_id.startswith('properties/'):
            self.property_id = f'properties/{self.property_id}'
        
        self.client = self._create_client()
    
    def _create_client(self) -> BetaAnalyticsDataClient:
        """Create authenticated GA4 client."""
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        return BetaAnalyticsDataClient(credentials=credentials)
    
    def _get_date_ranges(self) -> tuple[tuple[str, str], tuple[str, str]]:
        """
        Get date ranges for current period and previous period.
        Returns two tuples: (current_start, current_end), (previous_start, previous_end)
        """
        # Use custom date range if provided
        if self.custom_date_range:
            current_start = datetime.strptime(self.custom_date_range['start'], '%Y-%m-%d').date()
            current_end = datetime.strptime(self.custom_date_range['end'], '%Y-%m-%d').date()
            
            # Calculate previous period (same duration before current)
            period_days = (current_end - current_start).days
            previous_end = current_start - timedelta(days=1)
            previous_start = previous_end - timedelta(days=period_days)
        else:
            # Default: last 7 days
            today = datetime.now().date()
            current_end = today - timedelta(days=1)  # Yesterday
            current_start = current_end - timedelta(days=6)  # 7 days including yesterday
            
            previous_end = current_start - timedelta(days=1)
            previous_start = previous_end - timedelta(days=6)
        
        return (
            (current_start.strftime('%Y-%m-%d'), current_end.strftime('%Y-%m-%d')),
            (previous_start.strftime('%Y-%m-%d'), previous_end.strftime('%Y-%m-%d'))
        )
    
    def fetch_overview_metrics(self) -> dict:
        """
        Fetch key overview metrics comparing current week vs previous week.
        
        Returns:
            Dict with current and previous period data, plus calculated changes.
        """
        current_range, previous_range = self._get_date_ranges()
        
        metrics = [
            Metric(name='activeUsers'),
            Metric(name='sessions'),
            Metric(name='bounceRate'),
            Metric(name='averageSessionDuration'),
            Metric(name='screenPageViews'),
            Metric(name='newUsers'),
            Metric(name='engagementRate'),
        ]
        
        # Fetch current period
        current_request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=current_range[0], end_date=current_range[1])],
            metrics=metrics,
        )
        current_response = self.client.run_report(current_request)
        
        # Fetch previous period
        previous_request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=previous_range[0], end_date=previous_range[1])],
            metrics=metrics,
        )
        previous_response = self.client.run_report(previous_request)
        
        return self._process_overview_response(
            current_response, previous_response,
            current_range, previous_range
        )
    
    def _process_overview_response(self, current, previous, current_range, previous_range) -> dict:
        """Process overview metrics response."""
        metric_names = ['activeUsers', 'sessions', 'bounceRate', 'averageSessionDuration', 
                        'screenPageViews', 'newUsers', 'engagementRate']
        
        current_values = {}
        previous_values = {}
        
        if current.rows:
            for i, name in enumerate(metric_names):
                current_values[name] = float(current.rows[0].metric_values[i].value)
        
        if previous.rows:
            for i, name in enumerate(metric_names):
                previous_values[name] = float(previous.rows[0].metric_values[i].value)
        
        # Calculate percentage changes
        changes = {}
        for name in metric_names:
            curr_val = current_values.get(name, 0)
            prev_val = previous_values.get(name, 0)
            if prev_val > 0:
                changes[name] = round(((curr_val - prev_val) / prev_val) * 100, 2)
            else:
                changes[name] = 0 if curr_val == 0 else 100
        
        return {
            'period': {
                'current': {'start': current_range[0], 'end': current_range[1]},
                'previous': {'start': previous_range[0], 'end': previous_range[1]}
            },
            'current': current_values,
            'previous': previous_values,
            'changes': changes
        }
    
    def fetch_traffic_sources(self, limit: int = 10) -> dict:
        """Fetch traffic source breakdown."""
        current_range, previous_range = self._get_date_ranges()
        
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=current_range[0], end_date=current_range[1])],
            dimensions=[
                Dimension(name='sessionSource'),
                Dimension(name='sessionMedium'),
            ],
            metrics=[
                Metric(name='sessions'),
                Metric(name='activeUsers'),
                Metric(name='bounceRate'),
            ],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='sessions'), desc=True)],
            limit=limit
        )
        
        response = self.client.run_report(request)
        
        sources = []
        for row in response.rows:
            sources.append({
                'source': row.dimension_values[0].value,
                'medium': row.dimension_values[1].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'bounceRate': round(float(row.metric_values[2].value), 2)
            })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'sources': sources
        }
    
    def fetch_top_pages(self, limit: int = 15) -> dict:
        """Fetch top performing pages."""
        current_range, _ = self._get_date_ranges()
        
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=current_range[0], end_date=current_range[1])],
            dimensions=[Dimension(name='pagePath')],
            metrics=[
                Metric(name='screenPageViews'),
                Metric(name='userEngagementDuration'),  # Total engagement time (seconds)
                Metric(name='activeUsers'),  # For calculating per-user engagement
                Metric(name='bounceRate'),
            ],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='screenPageViews'), desc=True)],
            limit=limit
        )
        
        response = self.client.run_report(request)
        
        pages = []
        for row in response.rows:
            engagement_duration = float(row.metric_values[1].value)
            active_users = int(row.metric_values[2].value) or 1  # Avoid division by zero
            avg_engagement_per_user = engagement_duration / active_users  # Seconds per user
            
            pages.append({
                'pagePath': row.dimension_values[0].value,
                'pageViews': int(row.metric_values[0].value),
                'avgEngagementTime': round(avg_engagement_per_user, 2),  # Per-user engagement in seconds
                'bounceRate': round(float(row.metric_values[3].value), 2)
            })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'pages': pages
        }
    
    def fetch_device_breakdown(self) -> dict:
        """Fetch device category breakdown."""
        current_range, _ = self._get_date_ranges()
        
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=current_range[0], end_date=current_range[1])],
            dimensions=[Dimension(name='deviceCategory')],
            metrics=[
                Metric(name='sessions'),
                Metric(name='activeUsers'),
                Metric(name='bounceRate'),
                Metric(name='averageSessionDuration'),
            ],
        )
        
        response = self.client.run_report(request)
        
        devices = []
        total_sessions = sum(int(row.metric_values[0].value) for row in response.rows)
        
        for row in response.rows:
            sessions = int(row.metric_values[0].value)
            devices.append({
                'device': row.dimension_values[0].value,
                'sessions': sessions,
                'percentage': round((sessions / total_sessions) * 100, 2) if total_sessions > 0 else 0,
                'users': int(row.metric_values[1].value),
                'bounceRate': round(float(row.metric_values[2].value), 2),
                'avgSessionDuration': round(float(row.metric_values[3].value), 2)
            })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'devices': devices
        }
    
    def fetch_geo_breakdown(self, limit: int = 10) -> dict:
        """Fetch geographic breakdown by country."""
        current_range, _ = self._get_date_ranges()
        
        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(start_date=current_range[0], end_date=current_range[1])],
            dimensions=[Dimension(name='country')],
            metrics=[
                Metric(name='sessions'),
                Metric(name='activeUsers'),
            ],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='sessions'), desc=True)],
            limit=limit
        )
        
        response = self.client.run_report(request)
        
        countries = []
        total_sessions = sum(int(row.metric_values[0].value) for row in response.rows)
        
        for row in response.rows:
            sessions = int(row.metric_values[0].value)
            countries.append({
                'country': row.dimension_values[0].value,
                'sessions': sessions,
                'percentage': round((sessions / total_sessions) * 100, 2) if total_sessions > 0 else 0,
                'users': int(row.metric_values[1].value),
            })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'countries': countries
        }
    
    def fetch_all_data(self) -> dict:
        """
        Fetch all GA4 data for the weekly report.
        
        Returns:
            Complete GA4 data dictionary with all metrics and dimensions.
        """
        print("📊 Fetching GA4 data...")
        
        data = {
            'source': 'Google Analytics 4',
            'property_id': self.property_id,
            'fetched_at': datetime.now().isoformat(),
            'overview': self.fetch_overview_metrics(),
            'traffic_sources': self.fetch_traffic_sources(),
            'top_pages': self.fetch_top_pages(),
            'devices': self.fetch_device_breakdown(),
            'geo': self.fetch_geo_breakdown(),
        }
        
        print("✅ GA4 data fetched successfully!")
        return data


def test_connection() -> bool:
    """Test GA4 API connection."""
    try:
        fetcher = GA4Fetcher()
        # Just try to fetch basic data
        fetcher.fetch_overview_metrics()
        return True
    except Exception as e:
        print(f"❌ GA4 connection failed: {e}")
        return False


if __name__ == '__main__':
    # Test the fetcher
    import json
    fetcher = GA4Fetcher()
    data = fetcher.fetch_all_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))
