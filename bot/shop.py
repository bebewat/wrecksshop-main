"""
Shop management system for the Ark Discord bot
"""

import asyncio
from utils.rcon import RCONManager
from data.item_library import ITEM_LIBRARY

class ShopManager:
    def __init__(self, database, economy_manager):
        self.db = database
        self.economy = economy_manager
        self.rcon = RCONManager()
    
    async def get_shop_items(self, page=1, items_per_page=10):
        """Get paginated shop items"""
        try:
            offset = (page - 1) * items_per_page
            
            query = """
                SELECT id, name, description, price, ark_command, category, enabled
                FROM shop_items 
                WHERE enabled = 1 
                ORDER BY category, name 
                LIMIT ? OFFSET ?
            """
            
            items = await self.db.fetch_all(query, (items_per_page, offset))
            return items
            
        except Exception as e:
            raise Exception(f"Error getting shop items: {e}")
    
    async def get_item(self, item_id):
        """Get a specific shop item"""
        try:
            query = "SELECT * FROM shop_items WHERE id = ? AND enabled = 1"
            item = await self.db.fetch_one(query, (item_id,))
            return item
            
        except Exception as e:
            raise Exception(f"Error getting item: {e}")
    
    async def purchase_item(self, player_id, item_id, quantity=1):
        """Process item purchase"""
        try:
            # Get item details
            item = await self.get_item(item_id)
            if not item:
                return False
            
            total_cost = item['price'] * quantity
            
            # Check and deduct points
            success = await self.economy.spend_points(player_id, total_cost, 
                                                    f"Purchased {quantity}x {item['name']}")
            
            if not success:
                return False
            
            # Execute RCON command to give item in-game
            await self.give_item_ingame(player_id, item['ark_command'], quantity)
            
            # Log purchase
            await self.log_purchase(player_id, item_id, quantity, total_cost)
            
            return True
            
        except Exception as e:
            # Refund points if RCON command failed
            await self.economy.add_points(player_id, total_cost, "Purchase refund - command failed")
            raise Exception(f"Error processing purchase: {e}")
    
    async def give_item_ingame(self, player_id, ark_command, quantity):
        """Execute RCON command to give item to player in-game"""
        try:
            # Get player's Steam ID from database
            steam_id = await self.get_player_steam_id(player_id)
            
            if not steam_id:
                # If no Steam ID, we can't give the item in-game
                # This should be handled by requiring Steam ID linking
                raise Exception("Player Steam ID not found")
            
            # Format the command with quantity and Steam ID
            command = ark_command.format(steam_id=steam_id, quantity=quantity)
            
            # Execute command on all configured servers
            await self.rcon.execute_command_all_servers(command)
            
        except Exception as e:
            raise Exception(f"Error giving item in-game: {e}")
    
    async def get_player_steam_id(self, player_id):
        """Get player's linked Steam ID"""
        try:
            query = "SELECT steam_id FROM players WHERE discord_id = ?"
            result = await self.db.fetch_one(query, (player_id,))
            return result['steam_id'] if result else None
            
        except Exception as e:
            raise Exception(f"Error getting Steam ID: {e}")
    
    async def log_purchase(self, player_id, item_id, quantity, total_cost):
        """Log purchase to database"""
        try:
            query = """
                INSERT INTO purchase_log (player_id, item_id, quantity, total_cost, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            """
            await self.db.execute(query, (player_id, item_id, quantity, total_cost))
            
        except Exception as e:
            raise Exception(f"Error logging purchase: {e}")
    
    async def add_shop_item(self, name, description, price, ark_command, category="General"):
        """Add new item to shop"""
        try:
            query = """
                INSERT INTO shop_items (name, description, price, ark_command, category, enabled)
                VALUES (?, ?, ?, ?, ?, 1)
            """
            
            item_id = await self.db.execute(query, (name, description, price, ark_command, category))
            return item_id
            
        except Exception as e:
            raise Exception(f"Error adding shop item: {e}")
    
    async def update_shop_item(self, item_id, **kwargs):
        """Update shop item"""
        try:
            # Build dynamic update query
            fields = []
            values = []
            
            for field, value in kwargs.items():
                if field in ['name', 'description', 'price', 'ark_command', 'category', 'enabled']:
                    fields.append(f"{field} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(item_id)
            query = f"UPDATE shop_items SET {', '.join(fields)} WHERE id = ?"
            
            await self.db.execute(query, values)
            return True
            
        except Exception as e:
            raise Exception(f"Error updating shop item: {e}")
    
    async def delete_shop_item(self, item_id):
        """Delete shop item"""
        try:
            query = "DELETE FROM shop_items WHERE id = ?"
            await self.db.execute(query, (item_id,))
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting shop item: {e}")
    
    async def get_categories(self):
        """Get all item categories"""
        try:
            query = "SELECT DISTINCT category FROM shop_items ORDER BY category"
            categories = await self.db.fetch_all(query)
            return [cat['category'] for cat in categories]
            
        except Exception as e:
            raise Exception(f"Error getting categories: {e}")
