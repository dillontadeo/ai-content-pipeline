"""
Data storage layer for the AI Content Pipeline.
Handles database operations, content storage, and campaign tracking.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import os


class DataStorage:
    """Manages all data persistence for the content pipeline."""
    
    def __init__(self, db_path: str = 'data/pipeline.db'):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Content table - stores generated blog posts and newsletters
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                blog_title TEXT NOT NULL,
                blog_content TEXT NOT NULL,
                blog_outline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                word_count INTEGER
            )
        ''')
        
        # Newsletter variations table - stores persona-specific newsletters
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS newsletters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER NOT NULL,
                persona TEXT NOT NULL,
                subject_line TEXT NOT NULL,
                body TEXT NOT NULL,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
        # Campaigns table - tracks distribution campaigns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER NOT NULL,
                campaign_name TEXT NOT NULL,
                send_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                hubspot_campaign_id TEXT,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
        # Campaign performance table - stores engagement metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                persona TEXT NOT NULL,
                contacts_sent INTEGER DEFAULT 0,
                opens INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                unsubscribes INTEGER DEFAULT 0,
                open_rate REAL DEFAULT 0.0,
                click_rate REAL DEFAULT 0.0,
                unsubscribe_rate REAL DEFAULT 0.0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        ''')
        
        # Contacts table - stores CRM contact information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                persona TEXT NOT NULL,
                company TEXT,
                hubspot_contact_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance insights table - stores AI-generated insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                insight_text TEXT NOT NULL,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_content(self, topic: str, blog_title: str, blog_content: str, 
                     blog_outline: str, word_count: int) -> int:
        """Save generated blog content."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO content (topic, blog_title, blog_content, blog_outline, word_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (topic, blog_title, blog_content, blog_outline, word_count))
        
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return content_id
    
    def save_newsletter(self, content_id: int, persona: str, subject_line: str, 
                       body: str, word_count: int) -> int:
        """Save generated newsletter variation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO newsletters (content_id, persona, subject_line, body, word_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (content_id, persona, subject_line, body, word_count))
        
        newsletter_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return newsletter_id
    
    def create_campaign(self, content_id: int, campaign_name: str, 
                       hubspot_campaign_id: Optional[str] = None) -> int:
        """Create a new campaign record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns (content_id, campaign_name, hubspot_campaign_id)
            VALUES (?, ?, ?)
        ''', (content_id, campaign_name, hubspot_campaign_id))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return campaign_id
    
    def save_campaign_performance(self, campaign_id: int, persona: str, 
                                 metrics: Dict[str, Any]) -> int:
        """Save campaign performance metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaign_performance 
            (campaign_id, persona, contacts_sent, opens, clicks, unsubscribes,
             open_rate, click_rate, unsubscribe_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id,
            persona,
            metrics.get('contacts_sent', 0),
            metrics.get('opens', 0),
            metrics.get('clicks', 0),
            metrics.get('unsubscribes', 0),
            metrics.get('open_rate', 0.0),
            metrics.get('click_rate', 0.0),
            metrics.get('unsubscribe_rate', 0.0)
        ))
        
        perf_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return perf_id
    
    def save_contact(self, email: str, first_name: str, last_name: str, 
                    persona: str, company: Optional[str] = None,
                    hubspot_contact_id: Optional[str] = None) -> int:
        """Save or update a contact."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if contact exists
        cursor.execute('SELECT id FROM contacts WHERE email = ?', (email,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE contacts 
                SET first_name = ?, last_name = ?, persona = ?, company = ?,
                    hubspot_contact_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (first_name, last_name, persona, company, hubspot_contact_id, email))
            contact_id = existing[0]
        else:
            cursor.execute('''
                INSERT INTO contacts (email, first_name, last_name, persona, company, hubspot_contact_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, first_name, last_name, persona, company, hubspot_contact_id))
            contact_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return contact_id
    
    def save_insight(self, campaign_id: int, insight_text: str, 
                    recommendations: str) -> int:
        """Save AI-generated performance insight."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_insights (campaign_id, insight_text, recommendations)
            VALUES (?, ?, ?)
        ''', (campaign_id, insight_text, recommendations))
        
        insight_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return insight_id
    
    def get_content(self, content_id: int) -> Optional[Dict]:
        """Retrieve content by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_newsletters_for_content(self, content_id: int) -> List[Dict]:
        """Get all newsletter variations for a content piece."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM newsletters WHERE content_id = ?
        ''', (content_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_campaign_performance(self, campaign_id: int) -> List[Dict]:
        """Get performance metrics for a campaign."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM campaign_performance WHERE campaign_id = ?
        ''', (campaign_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaigns with their content."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, co.blog_title, co.topic
            FROM campaigns c
            JOIN content co ON c.content_id = co.id
            ORDER BY c.send_date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_contacts_by_persona(self, persona: str) -> List[Dict]:
        """Get all contacts for a specific persona."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM contacts WHERE persona = ?', (persona,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_historical_performance(self, limit: int = 10) -> List[Dict]:
        """Get historical performance data for analysis."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                cp.*,
                c.campaign_name,
                c.send_date,
                co.blog_title,
                co.topic
            FROM campaign_performance cp
            JOIN campaigns c ON cp.campaign_id = c.id
            JOIN content co ON c.content_id = co.id
            ORDER BY c.send_date DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def export_to_json(self, content_id: int, filepath: str):
        """Export content and newsletters to JSON file."""
        content = self.get_content(content_id)
        newsletters = self.get_newsletters_for_content(content_id)
        
        data = {
            'content': content,
            'newsletters': newsletters,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

