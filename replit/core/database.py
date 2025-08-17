"""
Database management for the Ark Bot Manager
Handles SQLite operations for users, items, transactions, and configuration
"""

import sqlite3
import logging
import os
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

class DatabaseManager:
    """Manages database operations for the bot"""
    
    def __init__(self, config_manager):
        """
        Initialize database manager
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.db_file = config_manager.get('database_file', 'arkbot.db')
        self.connection_pool = {}
        self.lock = threading.Lock()
        
        # Ensure database directory exists
        db_dir = os.path.dirname(os.path.abspath(self.db_file))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection for current thread"""
        thread_id = threading.get_ident()
        
        if thread_id not in self.connection_pool:
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable dict-like row access
            self.connection_pool[thread_id] = conn
        
        return self.connection_pool[thread_id]
    
    def initialize_database(self) -> bool:
        """
        Initialize database with required tables
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    display_name TEXT,
                    points INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    last_reward TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Point transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS point_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    discord_id TEXT NOT NULL,
                    points_change INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Shop items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shop_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    item_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    stock INTEGER DEFAULT -1,
                    description TEXT,
                    give_command TEXT,
                    additional_commands TEXT,
                    level_requirement INTEGER DEFAULT 1,
                    required_roles TEXT,
                    cooldown INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Purchases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    discord_id TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    price INTEGER NOT NULL,
                    total_cost INTEGER NOT NULL,
                    status TEXT DEFAULT 'Completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (item_id) REFERENCES shop_items (id)
                )
            ''')
            
            # RCON servers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rcon_servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    password TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'Unknown',
                    players INTEGER DEFAULT 0,
                    last_check TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Admin roles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    level INTEGER NOT NULL,
                    description TEXT,
                    color TEXT,
                    permissions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Admin users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    discord_id TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT DEFAULT 'Active',
                    last_seen TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (role) REFERENCES admin_roles (name)
                )
            ''')
            
            # Discounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    value REAL NOT NULL,
                    target_type TEXT NOT NULL,
                    target_details TEXT,
                    description TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    usage_limit INTEGER,
                    user_limit INTEGER,
                    current_uses INTEGER DEFAULT 0,
                    stackable BOOLEAN DEFAULT 0,
                    announce BOOLEAN DEFAULT 1,
                    auto_apply BOOLEAN DEFAULT 1,
                    code TEXT,
                    min_purchase REAL DEFAULT 0,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Discount usage log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discount_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discount_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    discord_id TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    original_price INTEGER NOT NULL,
                    discounted_price INTEGER NOT NULL,
                    saved_amount INTEGER NOT NULL,
                    usage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discount_id) REFERENCES discounts (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Log entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    user_id TEXT
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users (discord_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON point_transactions (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_discord_id ON point_transactions (discord_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shop_items_status ON shop_items (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_discounts_status ON discounts (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries (timestamp)')
            
            # Insert default admin role if none exists
            cursor.execute('SELECT COUNT(*) FROM admin_roles')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO admin_roles (name, level, description, permissions)
                    VALUES (?, ?, ?, ?)
                ''', ('Admin', 100, 'Administrator with full access', 
                      json.dumps(['*'])))
            
            conn.commit()
            logging.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            return False
    
    # User Management
    def get_user_by_discord_id(self, discord_id: str) -> Optional[Dict]:
        """Get user by Discord ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logging.error(f"Failed to get user {discord_id}: {e}")
            return None
    
    def create_user(self, discord_id: str, username: str, display_name: str = None) -> bool:
        """Create new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (discord_id, username, display_name, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (discord_id, username, display_name or username))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Failed to create user {discord_id}: {e}")
            return False
    
    def update_user_points(self, discord_id: str, points_change: int, reason: str) -> bool:
        """Update user points and log transaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get or create user
            user = self.get_user_by_discord_id(discord_id)
            if not user:
                return False
            
            # Update points
            new_points = max(0, user['points'] + points_change)
            cursor.execute('''
                UPDATE users 
                SET points = ?, 
                    total_earned = total_earned + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            ''', (new_points, max(0, points_change), discord_id))
            
            # Log transaction
            cursor.execute('''
                INSERT INTO point_transactions 
                (user_id, discord_id, points_change, reason, transaction_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user['id'], discord_id, points_change, reason, 
                  'earned' if points_change > 0 else 'spent'))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Failed to update points for {discord_id}: {e}")
            return False
    
    def get_user_points(self, discord_id: str) -> int:
        """Get user's current points"""
        user = self.get_user_by_discord_id(discord_id)
        return user['points'] if user else 0
    
    def get_user_transactions(self, discord_id: str, limit: int = 50) -> List[Dict]:
        """Get user's transaction history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM point_transactions 
                WHERE discord_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (discord_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Failed to get transactions for {discord_id}: {e}")
            return []
    
    def get_leaderboard(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get points leaderboard"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT discord_id, points, username
                FROM users 
                WHERE points > 0
                ORDER BY points DESC 
                LIMIT ?
            ''', (limit,))
            
            return [(row['discord_id'], row['points']) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Failed to get leaderboard: {e}")
            return []
    
    # Shop Management
    def add_shop_item(self, item_data: Dict) -> bool:
        """Add item to shop"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO shop_items 
                (name, item_id, category, price, stock, description, 
                 give_command, additional_commands, level_requirement, 
                 required_roles, cooldown, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_data['name'], item_data['item_id'], item_data['category'],
                item_data['price'], item_data.get('stock', -1), 
                item_data.get('description', ''),
                item_data.get('give_command', ''), 
                item_data.get('additional_commands', ''),
                item_data.get('level_requirement', 1),
                item_data.get('required_roles', ''),
                item_data.get('cooldown', 0),
                item_data.get('status', 'Active')
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Failed to add shop item: {e}")
            return False
    
    def get_shop_items(self, active_only: bool = True) -> List[Dict]:
        """Get shop items"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM shop_items'
            if active_only:
                query += " WHERE status = 'Active'"
            query += ' ORDER BY category, name'
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Failed to get shop items: {e}")
            return []
    
    def get_shop_item(self, item_id: str) -> Optional[Dict]:
        """Get shop item by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM shop_items WHERE id = ? OR item_id = ?', 
                          (item_id, item_id))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logging.error(f"Failed to get shop item {item_id}: {e}")
            return None
    
    def process_purchase(self, discord_id: str, item_id: str, quantity: int, player_name: str) -> Tuple[bool, str]:
        """Process item purchase"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user
            user = self.get_user_by_discord_id(discord_id)
            if not user:
                return False, "User not found"
            
            # Get item
            item = self.get_shop_item(item_id)
            if not item:
                return False, "Item not found"
            
            if item['status'] != 'Active':
                return False, "Item is not available"
            
            # Check stock
            if item['stock'] != -1 and item['stock'] < quantity:
                return False, f"Insufficient stock (available: {item['stock']})"
            
            total_cost = item['price'] * quantity
            
            # Check user points
            if user['points'] < total_cost:
                return False, f"Insufficient points (need: {total_cost}, have: {user['points']})"
            
            # Update user points
            cursor.execute('''
                UPDATE users 
                SET points = points - ?, 
                    total_spent = total_spent + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            ''', (total_cost, total_cost, discord_id))
            
            # Update item stock
            if item['stock'] != -1:
                cursor.execute('''
                    UPDATE shop_items 
                    SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (quantity, item['id']))
            
            # Record purchase
            cursor.execute('''
                INSERT INTO purchases 
                (user_id, discord_id, player_name, item_id, item_name, 
                 quantity, price, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user['id'], discord_id, player_name, item['id'], 
                  item['name'], quantity, item['price'], total_cost))
            
            # Log transaction
            cursor.execute('''
                INSERT INTO point_transactions 
                (user_id, discord_id, points_change, reason, transaction_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user['id'], discord_id, -total_cost, 
                  f"Purchased {quantity}x {item['name']}", 'purchase'))
            
            conn.commit()
            return True, "Purchase completed successfully"
            
        except Exception as e:
            logging.error(f"Failed to process purchase: {e}")
            return False, f"Purchase failed: {e}"
    
    def get_recent_purchases(self, limit: int = 50) -> List[Dict]:
        """Get recent purchases"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM purchases 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Failed to get recent purchases: {e}")
            return []
    
    # Server Management
    def add_server(self, server_data: Dict) -> bool:
        """Add RCON server"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rcon_servers (name, host, port, password, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (server_data['name'], server_data['host'], server_data['port'],
                  server_data['password'], server_data.get('description', '')))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Failed to add server: {e}")
            return False
    
    def get_all_servers(self) -> List[Dict]:
        """Get all RCON servers"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM rcon_servers ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Failed to get servers: {e}")
            return []
    
    def get_server_by_name(self, name: str) -> Optional[Dict]:
        """Get server by name"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM rcon_servers WHERE name = ?', (name,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logging.error(f"Failed to get server {name}: {e}")
            return None
    
    def update_server_status(self, server_id: int, status: str, last_check: str, players: int = 0) -> bool:
        """Update server status"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE rcon_servers 
                SET status = ?, last_check = ?, players = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, last_check, players, server_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Failed to update server status: {e}")
            return False
    
    # Statistics
    def get_daily_statistics(self) -> Dict[str, Any]:
        """Get daily statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().date()
            
            # Commands today (from log entries)
            cursor.execute('''
                SELECT COUNT(*) FROM log_entries 
                WHERE DATE(timestamp) = ? AND message LIKE '%command%'
            ''', (today,))
            commands_today = cursor.fetchone()[0]
            
            # Points awarded today
            cursor.execute('''
                SELECT COALESCE(SUM(points_change), 0) FROM point_transactions 
                WHERE DATE(created_at) = ? AND points_change > 0
            ''', (today,))
            points_awarded = cursor.fetchone()[0]
            
            # Purchases today
            cursor.execute('''
                SELECT COUNT(*) FROM purchases 
                WHERE DATE(created_at) = ?
            ''', (today,))
            purchases_today = cursor.fetchone()[0]
            
            # Active users (users with activity in last 24 hours)
            cursor.execute('''
                SELECT COUNT(DISTINCT discord_id) FROM point_transactions 
                WHERE created_at >= datetime('now', '-1 day')
            ''', ())
            active_users = cursor.fetchone()[0]
            
            return {
                'commands_today': commands_today,
                'points_awarded': points_awarded,
                'purchases_today': purchases_today,
                'active_users': active_users
            }
            
        except Exception as e:
            logging.error(f"Failed to get daily statistics: {e}")
            return {}
    
    def get_shop_statistics(self) -> Dict[str, Any]:
        """Get shop statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total and active items
            cursor.execute('SELECT COUNT(*) FROM shop_items')
            total_items = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM shop_items WHERE status = 'Active'")
            active_items = cursor.fetchone()[0]
            
            # Total sales and revenue
            cursor.execute('SELECT COUNT(*), COALESCE(SUM(total_cost), 0) FROM purchases')
            row = cursor.fetchone()
            total_sales = row[0]
            total_revenue = row[1]
            
            # Top category
            cursor.execute('''
                SELECT category, COUNT(*) as count FROM purchases 
                JOIN shop_items ON purchases.item_id = shop_items.id 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            top_category = row[0] if row else 'N/A'
            
            # Best seller
            cursor.execute('''
                SELECT item_name, COUNT(*) as count FROM purchases 
                GROUP BY item_name 
                ORDER BY count DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            best_seller = row[0] if row else 'N/A'
            
            return {
                'total_items': total_items,
                'active_items': active_items,
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'top_category': top_category,
                'best_seller': best_seller
            }
            
        except Exception as e:
            logging.error(f"Failed to get shop statistics: {e}")
            return {}
    
    def close_connections(self):
        """Close all database connections"""
        try:
            with self.lock:
                for conn in self.connection_pool.values():
                    conn.close()
                self.connection_pool.clear()
            logging.info("Database connections closed")
        except Exception as e:
            logging.error(f"Error closing database connections: {e}")
    
    # Admin Management (stub methods for future implementation)
    def get_admin_roles(self) -> List[Dict]:
        """Get all admin roles"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM admin_roles ORDER BY level DESC')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Failed to get admin roles: {e}")
            return []
    
    def add_admin_role(self, role_data: Dict) -> bool:
        """Add admin role"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO admin_roles (name, level, description, color, permissions)
                VALUES (?, ?, ?, ?, ?)
            ''', (role_data['name'], role_data['level'], role_data.get('description', ''),
                  role_data.get('color', ''), json.dumps(role_data.get('permissions', []))))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Failed to add admin role: {e}")
            return False
    
    # Discount Management (stub methods)
    def get_all_discounts(self) -> List[Dict]:
        """Get all discounts"""
        return []
    
    def add_discount(self, discount_data: Dict) -> bool:
        """Add discount"""
        return True
    
    # Additional stub methods for GUI compatibility
    def get_all_shop_items(self) -> List[Dict]:
        """Alias for get_shop_items"""
        return self.get_shop_items(active_only=False)
    
    def get_recent_log_entries(self, limit: int = 100) -> List[Dict]:
        """Get recent log entries"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM log_entries ORDER BY timestamp DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Failed to get log entries: {e}")
            return []
