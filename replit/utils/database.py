"""
Database utility for SQLite operations
"""

import sqlite3
import asyncio
import aiosqlite
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "data/bot_database.db"):
        self.db_path = db_path
        self.connection = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def initialize(self) -> None:
        """Initialize database and create tables"""
        try:
            # Create database file if it doesn't exist
            if not os.path.exists(self.db_path):
                await self.create_database()
            
            # Create tables
            await self.create_tables()
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    async def create_database(self) -> None:
        """Create new database file"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
                await db.commit()
        except Exception as e:
            print(f"Error creating database: {e}")
            raise
    
    async def create_tables(self) -> None:
        """Create all required tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Players table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        discord_id TEXT UNIQUE NOT NULL,
                        steam_id TEXT,
                        balance INTEGER DEFAULT 0,
                        tier TEXT DEFAULT 'default',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Shop items table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS shop_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        price INTEGER NOT NULL,
                        ark_command TEXT NOT NULL,
                        category TEXT DEFAULT 'General',
                        enabled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Transactions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_id TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        reason TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Purchase log table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS purchase_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_id TEXT NOT NULL,
                        item_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        total_cost INTEGER NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (item_id) REFERENCES shop_items (id)
                    )
                """)
                
                # Player sessions table (for discounts, etc.)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS player_sessions (
                        discord_id TEXT PRIMARY KEY,
                        discount_percent INTEGER DEFAULT 0,
                        expires_at TIMESTAMP,
                        data TEXT
                    )
                """)
                
                # Admin roles assignments table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS admin_assignments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        discord_id TEXT NOT NULL,
                        role_name TEXT NOT NULL,
                        assigned_by TEXT,
                        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(discord_id, role_name)
                    )
                """)
                
                # Promotional codes table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS promo_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT UNIQUE NOT NULL,
                        type TEXT NOT NULL,
                        value INTEGER NOT NULL,
                        uses INTEGER DEFAULT 0,
                        max_uses INTEGER NOT NULL,
                        expires_at TIMESTAMP,
                        enabled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Promo code usage table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS promo_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code_id INTEGER NOT NULL,
                        player_id TEXT NOT NULL,
                        used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (code_id) REFERENCES promo_codes (id),
                        UNIQUE(code_id, player_id)
                    )
                """)
                
                # Bot statistics table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS bot_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value TEXT NOT NULL,
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Error log table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS error_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_type TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        stack_trace TEXT,
                        context TEXT,
                        occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                await db.execute("CREATE INDEX IF NOT EXISTS idx_players_discord_id ON players(discord_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_transactions_player_id ON transactions(player_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_purchase_log_player_id ON purchase_log(player_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_shop_items_category ON shop_items(category)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_shop_items_enabled ON shop_items(enabled)")
                
                await db.commit()
                
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise
    
    async def execute(self, query: str, params: Tuple = ()) -> int:
        """Execute a query and return the last row id"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch one row as dictionary"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error fetching one row: {e}")
            raise
    
    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as list of dictionaries"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching all rows: {e}")
            raise
    
    async def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute query with multiple parameter sets"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.executemany(query, params_list)
                await db.commit()
        except Exception as e:
            print(f"Error executing many: {e}")
            raise
    
    async def backup_database(self, backup_path: str) -> None:
        """Create database backup"""
        try:
            import shutil
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
        except Exception as e:
            print(f"Error backing up database: {e}")
            raise
    
    async def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table schema information"""
        try:
            query = f"PRAGMA table_info({table_name})"
            return await self.fetch_all(query)
        except Exception as e:
            print(f"Error getting table info: {e}")
            raise
    
    async def get_all_tables(self) -> List[str]:
        """Get list of all tables"""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            rows = await self.fetch_all(query)
            return [row['name'] for row in rows]
        except Exception as e:
            print(f"Error getting all tables: {e}")
            raise
    
    async def vacuum_database(self) -> None:
        """Vacuum database to reclaim space"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("VACUUM")
                await db.commit()
        except Exception as e:
            print(f"Error vacuuming database: {e}")
            raise
    
    async def get_database_size(self) -> int:
        """Get database file size in bytes"""
        try:
            return os.path.getsize(self.db_path)
        except Exception as e:
            print(f"Error getting database size: {e}")
            raise
    
    async def check_database_integrity(self) -> bool:
        """Check database integrity"""
        try:
            result = await self.fetch_one("PRAGMA integrity_check")
            return result['integrity_check'] == 'ok' if result else False
        except Exception as e:
            print(f"Error checking database integrity: {e}")
            raise
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}
            
            # Get table row counts
            tables = await self.get_all_tables()
            for table in tables:
                if not table.startswith('sqlite_'):
                    count_result = await self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                    stats[f"{table}_count"] = count_result['count'] if count_result else 0
            
            # Get database size
            stats['database_size'] = await self.get_database_size()
            
            # Get last activity
            last_transaction = await self.fetch_one(
                "SELECT MAX(timestamp) as last_activity FROM transactions"
            )
            stats['last_activity'] = last_transaction['last_activity'] if last_transaction else None
            
            return stats
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            raise
    
    async def cleanup_old_data(self, days: int = 30) -> None:
        """Clean up old data older than specified days"""
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            # Clean up old sessions
            await self.execute(
                "DELETE FROM player_sessions WHERE expires_at < ?",
                (cutoff_date,)
            )
            
            # Clean up old error logs (keep last 1000)
            await self.execute("""
                DELETE FROM error_log 
                WHERE id NOT IN (
                    SELECT id FROM error_log 
                    ORDER BY occurred_at DESC 
                    LIMIT 1000
                )
            """)
            
            # Clean up old bot stats (keep daily summaries)
            await self.execute("""
                DELETE FROM bot_stats 
                WHERE recorded_at < ? 
                AND id NOT IN (
                    SELECT MIN(id) FROM bot_stats 
                    WHERE recorded_at < ?
                    GROUP BY DATE(recorded_at), metric_name
                )
            """, (cutoff_date, cutoff_date))
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            raise
