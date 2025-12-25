"""
Google Search Console Data Fetcher Module.
Fetches search performance data from Google Search Console API.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from googleapiclient.discovery import build
from google.oauth2 import service_account
import httplib2

from src.config import GOOGLE_CREDENTIALS_PATH, GSC_SITE_URL


class GSCFetcher:
    """Fetches data from Google Search Console."""
    
    def __init__(self, credentials_path: Optional[str] = None, site_url: Optional[str] = None, date_range: dict = None):
        """
        Initialize the GSC Fetcher.
        
        Args:
            credentials_path: Path to service account JSON file
            site_url: Site URL registered in Search Console
            date_range: Optional dict with 'start' and 'end' keys for custom date range
        """
        self.credentials_path = credentials_path or GOOGLE_CREDENTIALS_PATH
        self.site_url = site_url or GSC_SITE_URL
        self.custom_date_range = date_range
        self.service = self._create_service()
    
    def _create_service(self):
        """Create authenticated Search Console service with proxy support."""
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        
        # Configure proxy if available
        proxy_url = os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY')
        if proxy_url:
            # Parse proxy URL (format: http://host:port)
            proxy_url = proxy_url.replace('http://', '').replace('https://', '')
            if ':' in proxy_url:
                proxy_host, proxy_port = proxy_url.split(':')
                proxy_info = httplib2.ProxyInfo(
                    httplib2.socks.PROXY_TYPE_HTTP,
                    proxy_host,
                    int(proxy_port)
                )
                http = httplib2.Http(proxy_info=proxy_info)
                # Create authorized http with credentials
                from google_auth_httplib2 import AuthorizedHttp
                authed_http = AuthorizedHttp(credentials, http=http)
                return build('searchconsole', 'v1', http=authed_http)
        
        return build('searchconsole', 'v1', credentials=credentials)
    
    def _get_date_ranges(self) -> tuple[tuple[str, str], tuple[str, str]]:
        """
        Get date ranges for current period and previous period.
        Note: Search Console data has a 2-3 day delay.
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
            # Default: last 7 days with 3-day buffer for data delay
            today = datetime.now().date()
            current_end = today - timedelta(days=3)
            current_start = current_end - timedelta(days=6)
            
            previous_end = current_start - timedelta(days=1)
            previous_start = previous_end - timedelta(days=6)
        
        return (
            (current_start.strftime('%Y-%m-%d'), current_end.strftime('%Y-%m-%d')),
            (previous_start.strftime('%Y-%m-%d'), previous_end.strftime('%Y-%m-%d'))
        )
    
    def _execute_query(self, start_date: str, end_date: str, 
                       dimensions: list = None, row_limit: int = 1000) -> dict:
        """Execute a Search Console query."""
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': dimensions or [],
            'rowLimit': row_limit
        }
        
        response = self.service.searchanalytics().query(
            siteUrl=self.site_url,
            body=request
        ).execute()
        
        return response
    
    def fetch_overview_metrics(self) -> dict:
        """
        Fetch key overview metrics comparing current week vs previous week.
        
        Returns:
            Dict with current and previous period data, plus calculated changes.
        """
        current_range, previous_range = self._get_date_ranges()
        
        # Fetch current period (no dimensions = aggregate data)
        current_response = self._execute_query(
            current_range[0], current_range[1], 
            dimensions=[]
        )
        
        # Fetch previous period
        previous_response = self._execute_query(
            previous_range[0], previous_range[1],
            dimensions=[]
        )
        
        # Extract metrics
        def extract_metrics(response):
            if 'rows' in response and response['rows']:
                row = response['rows'][0]
                return {
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),  # Convert to percentage
                    'position': round(row.get('position', 0), 2)
                }
            return {'clicks': 0, 'impressions': 0, 'ctr': 0, 'position': 0}
        
        current_metrics = extract_metrics(current_response)
        previous_metrics = extract_metrics(previous_response)
        
        # Calculate changes
        changes = {}
        for key in current_metrics:
            curr_val = current_metrics[key]
            prev_val = previous_metrics[key]
            
            if key == 'position':
                # Lower position is better, so invert the change
                changes[key] = round(prev_val - curr_val, 2) if prev_val > 0 else 0
            elif prev_val > 0:
                changes[key] = round(((curr_val - prev_val) / prev_val) * 100, 2)
            else:
                changes[key] = 0 if curr_val == 0 else 100
        
        return {
            'period': {
                'current': {'start': current_range[0], 'end': current_range[1]},
                'previous': {'start': previous_range[0], 'end': previous_range[1]}
            },
            'current': current_metrics,
            'previous': previous_metrics,
            'changes': changes
        }
    
    def fetch_top_queries(self, limit: int = 20) -> dict:
        """Fetch top search queries."""
        current_range, previous_range = self._get_date_ranges()
        
        # Current period queries
        current_response = self._execute_query(
            current_range[0], current_range[1],
            dimensions=['query'],
            row_limit=limit
        )
        
        # Previous period queries for comparison
        previous_response = self._execute_query(
            previous_range[0], previous_range[1],
            dimensions=['query'],
            row_limit=100  # Get more to find matches
        )
        
        # Build previous period lookup
        previous_lookup = {}
        if 'rows' in previous_response:
            for row in previous_response['rows']:
                query = row['keys'][0]
                previous_lookup[query] = {
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'position': round(row.get('position', 0), 2)
                }
        
        queries = []
        if 'rows' in current_response:
            for row in current_response['rows']:
                query = row['keys'][0]
                prev_data = previous_lookup.get(query, {})
                
                current_clicks = row.get('clicks', 0)
                current_position = round(row.get('position', 0), 2)
                prev_clicks = prev_data.get('clicks', 0)
                prev_position = prev_data.get('position', 0)
                
                queries.append({
                    'query': query,
                    'clicks': current_clicks,
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),
                    'position': current_position,
                    'clicksChange': current_clicks - prev_clicks,
                    'positionChange': round(prev_position - current_position, 2) if prev_position > 0 else 0,
                    'isNew': query not in previous_lookup
                })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'queries': queries
        }
    
    def fetch_top_pages(self, limit: int = 15) -> dict:
        """Fetch top performing pages."""
        current_range, _ = self._get_date_ranges()
        
        response = self._execute_query(
            current_range[0], current_range[1],
            dimensions=['page'],
            row_limit=limit
        )
        
        pages = []
        if 'rows' in response:
            for row in response['rows']:
                pages.append({
                    'page': row['keys'][0],
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),
                    'position': round(row.get('position', 0), 2)
                })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'pages': pages
        }
    
    def fetch_device_breakdown(self) -> dict:
        """Fetch device category breakdown."""
        current_range, _ = self._get_date_ranges()
        
        response = self._execute_query(
            current_range[0], current_range[1],
            dimensions=['device'],
            row_limit=10
        )
        
        devices = []
        total_clicks = sum(row.get('clicks', 0) for row in response.get('rows', []))
        
        if 'rows' in response:
            for row in response['rows']:
                clicks = row.get('clicks', 0)
                devices.append({
                    'device': row['keys'][0],
                    'clicks': clicks,
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),
                    'position': round(row.get('position', 0), 2),
                    'percentage': round((clicks / total_clicks) * 100, 2) if total_clicks > 0 else 0
                })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'devices': devices
        }
    
    def fetch_country_breakdown(self, limit: int = 10) -> dict:
        """Fetch country breakdown."""
        current_range, _ = self._get_date_ranges()
        
        response = self._execute_query(
            current_range[0], current_range[1],
            dimensions=['country'],
            row_limit=limit
        )
        
        countries = []
        total_clicks = sum(row.get('clicks', 0) for row in response.get('rows', []))
        
        if 'rows' in response:
            for row in response['rows']:
                clicks = row.get('clicks', 0)
                countries.append({
                    'country': row['keys'][0],
                    'clicks': clicks,
                    'impressions': row.get('impressions', 0),
                    'ctr': round(row.get('ctr', 0) * 100, 2),
                    'position': round(row.get('position', 0), 2),
                    'percentage': round((clicks / total_clicks) * 100, 2) if total_clicks > 0 else 0
                })
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'countries': countries
        }
    
    def fetch_query_opportunities(self, limit: int = 10) -> dict:
        """
        Find queries with high impressions but low CTR (optimization opportunities).
        """
        current_range, _ = self._get_date_ranges()
        
        response = self._execute_query(
            current_range[0], current_range[1],
            dimensions=['query'],
            row_limit=100  # Get more to filter
        )
        
        opportunities = []
        if 'rows' in response:
            # Filter for high impression, low CTR queries
            for row in response['rows']:
                impressions = row.get('impressions', 0)
                ctr = row.get('ctr', 0)
                position = row.get('position', 0)
                
                # Criteria: High impressions, but CTR below 3% and position in top 20
                if impressions >= 50 and ctr < 0.03 and position <= 20:
                    opportunities.append({
                        'query': row['keys'][0],
                        'impressions': impressions,
                        'clicks': row.get('clicks', 0),
                        'ctr': round(ctr * 100, 2),
                        'position': round(position, 2),
                        'potentialClicks': round(impressions * 0.05)  # Estimated if CTR improved to 5%
                    })
            
            # Sort by potential impact (impressions)
            opportunities.sort(key=lambda x: x['impressions'], reverse=True)
            opportunities = opportunities[:limit]
        
        return {
            'period': {'start': current_range[0], 'end': current_range[1]},
            'opportunities': opportunities
        }
    
    def fetch_all_data(self) -> dict:
        """
        Fetch all Search Console data for the weekly report.
        
        Returns:
            Complete GSC data dictionary with all metrics and dimensions.
        """
        print("🔍 Fetching Search Console data...")
        
        data = {
            'source': 'Google Search Console',
            'site_url': self.site_url,
            'fetched_at': datetime.now().isoformat(),
            'overview': self.fetch_overview_metrics(),
            'top_queries': self.fetch_top_queries(),
            'top_pages': self.fetch_top_pages(),
            'devices': self.fetch_device_breakdown(),
            'countries': self.fetch_country_breakdown(),
            'opportunities': self.fetch_query_opportunities(),
        }
        
        print("✅ Search Console data fetched successfully!")
        return data


def test_connection() -> bool:
    """Test Search Console API connection."""
    try:
        fetcher = GSCFetcher()
        # Just try to fetch basic data
        fetcher.fetch_overview_metrics()
        return True
    except Exception as e:
        print(f"❌ Search Console connection failed: {e}")
        return False


if __name__ == '__main__':
    # Test the fetcher
    import json
    fetcher = GSCFetcher()
    data = fetcher.fetch_all_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))
