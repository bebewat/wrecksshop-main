"""
Economy management system for point-based transactions
"""

import asyncio
from datetime import datetime

class EconomyManager:
    def __init__(self, database):
        self.db = database
    
    async def get_balance(self, player_id):
        """Get player's point balance"""
        try:
            query = "SELECT balance FROM players WHERE discord_id = ?"
            result = await self.db.fetch_one(query, (player_id,))
            
            if result:
                return result['balance']
            else:
                # Create new player entry
                await self.create_player(player_id)
                return 0
                
        except Exception as e:
            raise Exception(f"Error getting balance: {e}")
    
    async def create_player(self, player_id, starting_balance=0):
        """Create new player entry"""
        try:
            query = """
                INSERT OR IGNORE INTO players (discord_id, balance, created_at)
                VALUES (?, ?, datetime('now'))
            """
            await self.db.execute(query, (player_id, starting_balance))
            
        except Exception as e:
            raise Exception(f"Error creating player: {e}")
    
    async def add_points(self, player_id, amount, reason=""):
        """Add points to player balance"""
        try:
            # Ensure player exists
            await self.create_player(player_id)
            
            # Add points
            query = "UPDATE players SET balance = balance + ? WHERE discord_id = ?"
            await self.db.execute(query, (amount, player_id))
            
            # Log transaction
            await self.log_transaction(player_id, amount, "credit", reason)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error adding points: {e}")
    
    async def spend_points(self, player_id, amount, reason=""):
        """Spend points from player balance"""
        try:
            # Check balance first
            balance = await self.get_balance(player_id)
            
            if balance < amount:
                return False
            
            # Deduct points
            query = "UPDATE players SET balance = balance - ? WHERE discord_id = ?"
            await self.db.execute(query, (amount, player_id))
            
            # Log transaction
            await self.log_transaction(player_id, -amount, "debit", reason)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error spending points: {e}")
    
    async def transfer_points(self, sender_id, receiver_id, amount):
        """Transfer points between players"""
        try:
            # Check sender balance
            sender_balance = await self.get_balance(sender_id)
            
            if sender_balance < amount:
                return False
            
            # Ensure both players exist
            await self.create_player(sender_id)
            await self.create_player(receiver_id)
            
            # Execute transfer
            await self.spend_points(sender_id, amount, f"Transfer to {receiver_id}")
            await self.add_points(receiver_id, amount, f"Transfer from {sender_id}")
            
            return True
            
        except Exception as e:
            raise Exception(f"Error transferring points: {e}")
    
    async def log_transaction(self, player_id, amount, transaction_type, reason=""):
        """Log transaction to database"""
        try:
            query = """
                INSERT INTO transactions (player_id, amount, type, reason, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            """
            await self.db.execute(query, (player_id, amount, transaction_type, reason))
            
        except Exception as e:
            raise Exception(f"Error logging transaction: {e}")
    
    async def get_leaderboard(self, limit=10):
        """Get top players by balance"""
        try:
            query = """
                SELECT discord_id, balance 
                FROM players 
                ORDER BY balance DESC 
                LIMIT ?
            """
            results = await self.db.fetch_all(query, (limit,))
            return [(row['discord_id'], row['balance']) for row in results]
            
        except Exception as e:
            raise Exception(f"Error getting leaderboard: {e}")
    
    async def get_transaction_history(self, player_id, limit=20):
        """Get player's transaction history"""
        try:
            query = """
                SELECT amount, type, reason, timestamp
                FROM transactions 
                WHERE player_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            transactions = await self.db.fetch_all(query, (player_id, limit))
            return transactions
            
        except Exception as e:
            raise Exception(f"Error getting transaction history: {e}")
    
    async def apply_discount(self, player_id, discount_percent):
        """Apply discount to next purchase (stored in session)"""
        try:
            query = """
                INSERT OR REPLACE INTO player_sessions (discord_id, discount_percent, expires_at)
                VALUES (?, ?, datetime('now', '+1 hour'))
            """
            await self.db.execute(query, (player_id, discount_percent))
            
        except Exception as e:
            raise Exception(f"Error applying discount: {e}")
    
    async def get_active_discount(self, player_id):
        """Get player's active discount"""
        try:
            query = """
                SELECT discount_percent 
                FROM player_sessions 
                WHERE discord_id = ? AND expires_at > datetime('now')
            """
            result = await self.db.fetch_one(query, (player_id,))
            return result['discount_percent'] if result else 0
            
        except Exception as e:
            raise Exception(f"Error getting discount: {e}")
