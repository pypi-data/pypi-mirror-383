"""
Database layer for prompt library system.

SQLite database with tables for prompts, versions, performance metrics, and ratings.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from contextlib import contextmanager


class PromptDatabase:
    """SQLite database manager for prompt library."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to ~/.kagglerboze/prompts.db
        """
        if db_path is None:
            db_dir = Path.home() / '.kagglerboze'
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / 'prompts.db')

        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Prompts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    domain TEXT NOT NULL,
                    task TEXT NOT NULL,
                    template TEXT NOT NULL,
                    variables TEXT,
                    tags TEXT,
                    author TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_official BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            """)

            # Versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    template TEXT NOT NULL,
                    changes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    FOREIGN KEY (prompt_id) REFERENCES prompts(id),
                    UNIQUE(prompt_id, version)
                )
            """)

            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    version TEXT,
                    dataset TEXT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    recorded_by TEXT,
                    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
                )
            """)

            # Ratings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts(id),
                    UNIQUE(prompt_id, user_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_domain ON prompts(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_task ON prompts(task)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_versions_prompt ON versions(prompt_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_prompt ON performance_metrics(prompt_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ratings_prompt ON ratings(prompt_id)")

    def insert_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """
        Insert new prompt.

        Args:
            prompt_data: Dictionary with prompt fields

        Returns:
            Prompt ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO prompts (
                    id, name, description, domain, task, template,
                    variables, tags, author, is_official
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_data['id'],
                prompt_data['name'],
                prompt_data.get('description', ''),
                prompt_data['domain'],
                prompt_data['task'],
                prompt_data['template'],
                json.dumps(prompt_data.get('variables', [])),
                json.dumps(prompt_data.get('tags', [])),
                prompt_data.get('author', 'system'),
                prompt_data.get('is_official', False)
            ))

            return prompt_data['id']

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get prompt by ID.

        Args:
            prompt_id: Prompt ID

        Returns:
            Prompt dictionary or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def search_prompts(
        self,
        domain: Optional[str] = None,
        task: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        is_official: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Search prompts by criteria.

        Args:
            domain: Filter by domain
            task: Filter by task
            tags: Filter by tags (any match)
            author: Filter by author
            is_official: Filter by official status

        Returns:
            List of matching prompts
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM prompts WHERE is_active = 1"
            params = []

            if domain:
                query += " AND domain = ?"
                params.append(domain)

            if task:
                query += " AND task = ?"
                params.append(task)

            if author:
                query += " AND author = ?"
                params.append(author)

            if is_official is not None:
                query += " AND is_official = ?"
                params.append(is_official)

            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = [self._row_to_dict(row) for row in rows]

            # Filter by tags if provided
            if tags:
                results = [
                    p for p in results
                    if any(tag in json.loads(p['tags']) for tag in tags)
                ]

            return results

    def insert_version(self, version_data: Dict[str, Any]) -> int:
        """
        Insert new version.

        Args:
            version_data: Dictionary with version fields

        Returns:
            Version ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO versions (
                    prompt_id, version, template, changes, created_by
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                version_data['prompt_id'],
                version_data['version'],
                version_data['template'],
                version_data.get('changes', ''),
                version_data.get('created_by', 'system')
            ))

            return cursor.lastrowid

    def get_versions(self, prompt_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions for a prompt.

        Args:
            prompt_id: Prompt ID

        Returns:
            List of versions
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM versions WHERE prompt_id = ? ORDER BY created_at DESC",
                (prompt_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def insert_performance_metric(self, metric_data: Dict[str, Any]) -> int:
        """
        Insert performance metric.

        Args:
            metric_data: Dictionary with metric fields

        Returns:
            Metric ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO performance_metrics (
                    prompt_id, version, dataset, metric_name, metric_value,
                    metadata, recorded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metric_data['prompt_id'],
                metric_data.get('version'),
                metric_data.get('dataset', 'unknown'),
                metric_data['metric_name'],
                metric_data['metric_value'],
                json.dumps(metric_data.get('metadata', {})),
                metric_data.get('recorded_by', 'system')
            ))

            return cursor.lastrowid

    def get_performance_metrics(
        self,
        prompt_id: str,
        metric_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get performance metrics for a prompt.

        Args:
            prompt_id: Prompt ID
            metric_name: Optional metric name filter

        Returns:
            List of metrics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if metric_name:
                cursor.execute("""
                    SELECT * FROM performance_metrics
                    WHERE prompt_id = ? AND metric_name = ?
                    ORDER BY recorded_at DESC
                """, (prompt_id, metric_name))
            else:
                cursor.execute("""
                    SELECT * FROM performance_metrics
                    WHERE prompt_id = ?
                    ORDER BY recorded_at DESC
                """, (prompt_id,))

            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def insert_rating(self, rating_data: Dict[str, Any]) -> int:
        """
        Insert or update rating.

        Args:
            rating_data: Dictionary with rating fields

        Returns:
            Rating ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO ratings (
                    prompt_id, user_id, rating, comment
                ) VALUES (?, ?, ?, ?)
            """, (
                rating_data['prompt_id'],
                rating_data['user_id'],
                rating_data['rating'],
                rating_data.get('comment', '')
            ))

            return cursor.lastrowid

    def get_ratings(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get rating statistics for a prompt.

        Args:
            prompt_id: Prompt ID

        Returns:
            Dictionary with average rating and count
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(*) as count
                FROM ratings
                WHERE prompt_id = ?
            """, (prompt_id,))

            row = cursor.fetchone()
            return {
                'avg_rating': row['avg_rating'] or 0.0,
                'count': row['count']
            }

    def get_top_prompts(self, domain: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top-rated prompts.

        Args:
            domain: Optional domain filter
            limit: Maximum number of results

        Returns:
            List of top prompts with ratings
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT p.*, AVG(r.rating) as avg_rating, COUNT(r.id) as rating_count
                FROM prompts p
                LEFT JOIN ratings r ON p.id = r.prompt_id
                WHERE p.is_active = 1
            """
            params = []

            if domain:
                query += " AND p.domain = ?"
                params.append(domain)

            query += """
                GROUP BY p.id
                HAVING COUNT(r.id) > 0
                ORDER BY avg_rating DESC, rating_count DESC
                LIMIT ?
            """
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary."""
        d = dict(row)

        # Parse JSON fields
        if 'variables' in d and d['variables']:
            d['variables'] = json.loads(d['variables'])
        if 'tags' in d and d['tags']:
            d['tags'] = json.loads(d['tags'])
        if 'metadata' in d and d['metadata']:
            d['metadata'] = json.loads(d['metadata'])

        return d
