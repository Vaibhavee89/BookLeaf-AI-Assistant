"""Local SQLite database client as fallback for Supabase."""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)

# Database file location
DB_PATH = Path(__file__).parent.parent.parent.parent / "local_data" / "bookleaf.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class LocalDBClient:
    """SQLite client that mimics Supabase interface."""

    def __init__(self):
        """Initialize the local database client."""
        self.db_path = str(DB_PATH)
        self._init_database()
        logger.info("local_db_initialized", path=self.db_path)

    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Authors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Identities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identities (
                id TEXT PRIMARY KEY,
                author_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                platform_identifier TEXT NOT NULL,
                normalized_identifier TEXT,
                confidence_score REAL DEFAULT 1.0,
                matching_method TEXT,
                matching_metadata TEXT,
                verified BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES authors(id)
            )
        """)

        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                author_id TEXT,
                identity_id TEXT,
                platform TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES authors(id),
                FOREIGN KEY (identity_id) REFERENCES identities(id)
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence_score REAL,
                intent TEXT,
                entities TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Knowledge documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                document_type TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Knowledge embeddings table (simplified - no vector search)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_text TEXT NOT NULL,
                chunk_index INTEGER,
                embedding TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES knowledge_documents(id)
            )
        """)

        # Escalations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS escalations (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                message_id TEXT,
                reason TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                assigned_to TEXT,
                resolution_notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        """)

        # Query analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_analytics (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                query_text TEXT NOT NULL,
                intent TEXT,
                confidence_score REAL,
                response_time_ms INTEGER,
                llm_model TEXT,
                success BOOLEAN,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_identities_author_id ON identities(author_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_identities_platform ON identities(platform, platform_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_author_id ON conversations(author_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations(status)")

        conn.commit()
        conn.close()

        logger.info("local_db_schema_initialized")

    def table(self, table_name: str):
        """Get table interface (mimics Supabase)."""
        return LocalTable(self, table_name)


class LocalTable:
    """Table interface that mimics Supabase table operations."""

    def __init__(self, client: LocalDBClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self._query = {}
        self._filters = []

    def insert(self, data: Dict[str, Any]):
        """Insert data into table."""
        conn = self.client._get_connection()
        cursor = conn.cursor()

        # Add ID if not present
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())

        # Convert dict/list fields to JSON
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                processed_data[key] = json.dumps(value)
            else:
                processed_data[key] = value

        columns = ', '.join(processed_data.keys())
        placeholders = ', '.join(['?' for _ in processed_data])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

        try:
            cursor.execute(query, list(processed_data.values()))
            conn.commit()

            # Fetch the inserted row
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (data['id'],))
            result = cursor.fetchone()
            conn.close()

            return LocalResponse([self._row_to_dict(result)])
        except Exception as e:
            conn.close()
            logger.error("insert_failed", table=self.table_name, error=str(e))
            return LocalResponse(None, error=str(e))

    def select(self, *columns):
        """Select columns from table."""
        self._query['columns'] = columns if columns else ['*']
        return self

    def eq(self, column: str, value: Any):
        """Add equality filter."""
        self._filters.append(('=', column, value))
        return self

    def neq(self, column: str, value: Any):
        """Add not equal filter."""
        self._filters.append(('!=', column, value))
        return self

    def gt(self, column: str, value: Any):
        """Add greater than filter."""
        self._filters.append(('>', column, value))
        return self

    def gte(self, column: str, value: Any):
        """Add greater than or equal filter."""
        self._filters.append(('>=', column, value))
        return self

    def lt(self, column: str, value: Any):
        """Add less than filter."""
        self._filters.append(('<', column, value))
        return self

    def lte(self, column: str, value: Any):
        """Add less than or equal filter."""
        self._filters.append(('<=', column, value))
        return self

    def like(self, column: str, pattern: str):
        """Add LIKE filter."""
        self._filters.append(('LIKE', column, pattern))
        return self

    def ilike(self, column: str, pattern: str):
        """Add case-insensitive LIKE filter."""
        self._filters.append(('LIKE', f"LOWER({column})", pattern.lower()))
        return self

    def order(self, column: str, desc: bool = False):
        """Add order by clause."""
        self._query['order'] = (column, 'DESC' if desc else 'ASC')
        return self

    def limit(self, count: int):
        """Add limit clause."""
        self._query['limit'] = count
        return self

    def single(self):
        """Execute and return single result."""
        result = self.execute()
        if result.data and len(result.data) > 0:
            result.data = result.data[0]
        else:
            result.data = None
        return result

    def update(self, data: Dict[str, Any]):
        """Update records."""
        conn = self.client._get_connection()
        cursor = conn.cursor()

        # Add updated_at timestamp
        data['updated_at'] = datetime.utcnow().isoformat()

        # Convert dict/list fields to JSON
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                processed_data[key] = json.dumps(value)
            else:
                processed_data[key] = value

        set_clause = ', '.join([f"{k} = ?" for k in processed_data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause}"
        params = list(processed_data.values())

        # Add filters
        if self._filters:
            where_clause, filter_params = self._build_where_clause()
            query += f" WHERE {where_clause}"
            params.extend(filter_params)

        try:
            cursor.execute(query, params)
            conn.commit()

            # Return updated rows
            select_query = f"SELECT * FROM {self.table_name}"
            if self._filters:
                select_query += f" WHERE {where_clause}"

            cursor.execute(select_query, filter_params if self._filters else [])
            results = cursor.fetchall()
            conn.close()

            return LocalResponse([self._row_to_dict(row) for row in results])
        except Exception as e:
            conn.close()
            logger.error("update_failed", table=self.table_name, error=str(e))
            return LocalResponse(None, error=str(e))

    def delete(self):
        """Delete records."""
        conn = self.client._get_connection()
        cursor = conn.cursor()

        query = f"DELETE FROM {self.table_name}"
        params = []

        # Add filters
        if self._filters:
            where_clause, params = self._build_where_clause()
            query += f" WHERE {where_clause}"

        try:
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return LocalResponse([])
        except Exception as e:
            conn.close()
            logger.error("delete_failed", table=self.table_name, error=str(e))
            return LocalResponse(None, error=str(e))

    def execute(self):
        """Execute the query."""
        conn = self.client._get_connection()
        cursor = conn.cursor()

        columns = ', '.join(self._query.get('columns', ['*']))
        query = f"SELECT {columns} FROM {self.table_name}"
        params = []

        # Add filters
        if self._filters:
            where_clause, params = self._build_where_clause()
            query += f" WHERE {where_clause}"

        # Add order by
        if 'order' in self._query:
            column, direction = self._query['order']
            query += f" ORDER BY {column} {direction}"

        # Add limit
        if 'limit' in self._query:
            query += f" LIMIT {self._query['limit']}"

        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            return LocalResponse([self._row_to_dict(row) for row in results])
        except Exception as e:
            conn.close()
            logger.error("query_failed", table=self.table_name, error=str(e))
            return LocalResponse(None, error=str(e))

    def _build_where_clause(self):
        """Build WHERE clause from filters."""
        clauses = []
        params = []

        for operator, column, value in self._filters:
            if operator == 'LIKE' and 'LOWER' in column:
                clauses.append(f"{column} LIKE ?")
            else:
                clauses.append(f"{column} {operator} ?")
            params.append(value)

        return ' AND '.join(clauses), params

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary."""
        if row is None:
            return None

        result = dict(row)

        # Parse JSON fields
        for key, value in result.items():
            if isinstance(value, str):
                # Try to parse as JSON
                if value.startswith('{') or value.startswith('['):
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                # Convert boolean strings
                elif value == '0':
                    result[key] = False
                elif value == '1':
                    result[key] = True

        return result


class LocalResponse:
    """Response object that mimics Supabase response."""

    def __init__(self, data: Optional[List[Dict[str, Any]]] = None, error: Optional[str] = None):
        self.data = data
        self.error = error

    def execute(self):
        """Execute (for chaining compatibility)."""
        return self


# Global instance
local_db = LocalDBClient()
