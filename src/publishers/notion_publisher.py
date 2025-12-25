"""
Notion Publisher Module.
Publishes analysis reports to Notion as new pages.
"""

from datetime import datetime
from typing import Optional
from notion_client import Client

from src.config import NOTION_TOKEN, NOTION_PARENT_PAGE_ID


class NotionPublisher:
    """Publishes reports to Notion."""
    
    def __init__(self, token: str = None, parent_page_id: str = None):
        """
        Initialize the Notion Publisher.
        
        Args:
            token: Notion integration token
            parent_page_id: Parent page ID where reports will be created
        """
        self.token = token or NOTION_TOKEN
        self.parent_page_id = parent_page_id or NOTION_PARENT_PAGE_ID
        self.client = Client(auth=self.token)
    
    def _markdown_to_notion_blocks(self, markdown: str) -> list:
        """
        Convert markdown text to Notion blocks.
        This is a simplified converter for common markdown elements.
        """
        blocks = []
        lines = markdown.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            # Headers
            if line.startswith('# '):
                blocks.append({
                    'type': 'heading_1',
                    'heading_1': {
                        'rich_text': [{'type': 'text', 'text': {'content': line[2:].strip()}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'type': 'text', 'text': {'content': line[3:].strip()}}]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    'type': 'heading_3',
                    'heading_3': {
                        'rich_text': [{'type': 'text', 'text': {'content': line[4:].strip()}}]
                    }
                })
            # Horizontal rule
            elif line.strip() == '---':
                blocks.append({'type': 'divider', 'divider': {}})
            # Bullet points
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                content = line.strip()[2:]
                blocks.append({
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': self._parse_inline_formatting(content)
                    }
                })
            # Numbered list
            elif line.strip() and line.strip()[0].isdigit() and '. ' in line:
                content = line.split('. ', 1)[1] if '. ' in line else line
                blocks.append({
                    'type': 'numbered_list_item',
                    'numbered_list_item': {
                        'rich_text': self._parse_inline_formatting(content)
                    }
                })
            # Table (simplified - convert to text)
            elif line.strip().startswith('|'):
                # Collect all table lines
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                i -= 1  # Adjust for the loop increment
                
                # Create a code block for the table
                table_text = '\n'.join(table_lines)
                blocks.append({
                    'type': 'code',
                    'code': {
                        'rich_text': [{'type': 'text', 'text': {'content': table_text}}],
                        'language': 'plain text'
                    }
                })
            # Quote blocks
            elif line.strip().startswith('>'):
                content = line.strip()[1:].strip()
                blocks.append({
                    'type': 'quote',
                    'quote': {
                        'rich_text': [{'type': 'text', 'text': {'content': content}}]
                    }
                })
            # Regular paragraph
            else:
                # Combine consecutive paragraph lines
                paragraph_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('-') and not lines[i].startswith('*') and not lines[i].startswith('|') and not lines[i].startswith('>') and lines[i].strip() != '---':
                    paragraph_lines.append(lines[i])
                    i += 1
                i -= 1  # Adjust for the loop increment
                
                content = ' '.join(paragraph_lines)
                if content.strip():
                    blocks.append({
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': self._parse_inline_formatting(content)
                        }
                    })
            
            i += 1
        
        return blocks
    
    def _parse_inline_formatting(self, text: str) -> list:
        """Parse inline markdown formatting (bold, italic, etc.)."""
        # Simplified: just return as plain text
        # A full implementation would parse **bold**, *italic*, `code`, etc.
        
        # Truncate if too long (Notion has a 2000 char limit per rich text)
        if len(text) > 1900:
            text = text[:1900] + '...'
        
        return [{'type': 'text', 'text': {'content': text}}]
    
    def publish(self, title: str, content: str, icon: str = "📊") -> dict:
        """
        Publish a report to Notion as a new page.
        
        Args:
            title: Page title
            content: Markdown content of the report
            icon: Emoji icon for the page
            
        Returns:
            Dict with page ID and URL
        """
        print("📝 Publishing report to Notion...")
        
        # Convert markdown to Notion blocks
        blocks = self._markdown_to_notion_blocks(content)
        
        # Split blocks into chunks (Notion API limit: 100 blocks per request)
        block_chunks = [blocks[i:i+100] for i in range(0, len(blocks), 100)]
        
        # Create the page with first chunk
        page = self.client.pages.create(
            parent={'page_id': self.parent_page_id},
            icon={'type': 'emoji', 'emoji': icon},
            properties={
                'title': {
                    'title': [{'type': 'text', 'text': {'content': title}}]
                }
            },
            children=block_chunks[0] if block_chunks else []
        )
        
        page_id = page['id']
        
        # Append remaining blocks if any
        for chunk in block_chunks[1:]:
            self.client.blocks.children.append(block_id=page_id, children=chunk)
        
        # Get page URL
        page_url = page.get('url', f"https://notion.so/{page_id.replace('-', '')}")
        
        print(f"✅ Report published successfully!")
        print(f"   URL: {page_url}")
        
        return {
            'page_id': page_id,
            'url': page_url
        }
    
    def publish_weekly_report(self, content: str, week_start: str = None, week_end: str = None) -> dict:
        """
        Publish a weekly analytics report.
        
        Args:
            content: Markdown content of the report
            week_start: Start date of the period
            week_end: End date of the period (optional)
            
        Returns:
            Dict with page ID and URL
        """
        if not week_start:
            week_start = datetime.now().strftime('%Y-%m-%d')
        
        # Include date range in title
        if week_end:
            title = f"网站分析报告 {week_start} ~ {week_end}"
        else:
            title = f"网站周报分析 - {week_start}"
        
        return self.publish(title, content, icon="📈")


def test_connection() -> bool:
    """Test Notion API connection."""
    try:
        publisher = NotionPublisher()
        # Try to retrieve the parent page
        publisher.client.pages.retrieve(page_id=publisher.parent_page_id)
        return True
    except Exception as e:
        print(f"❌ Notion connection failed: {e}")
        return False


if __name__ == '__main__':
    # Test the publisher
    test_content = """# Test Report

## Summary
This is a test report.

- Point 1
- Point 2
- Point 3

---

## Details

Some detailed information here.
"""
    
    publisher = NotionPublisher()
    result = publisher.publish("Test Report", test_content)
    print(result)
