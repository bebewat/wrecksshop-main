"""
Shop Manager for handling item purchases and shop operations
"""

import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

class ShopManager:
    """Manages shop operations, purchases, and item availability"""
    
    def __init__(self, database_manager, point_system):
        """
        Initialize shop manager
        
        Args:
            database_manager: Database manager instance
            point_system: Point system instance
        """
        self.db_manager = database_manager
        self.point_system = point_system
        self.discount_cache = {}
        self.purchase_cooldowns = {}  # Track purchase cooldowns
        self.logger = logging.getLogger('arkbot.shop')
    
    def get_available_items(self, category: str = None, user_id: str = None) -> List[Dict]:
        """
        Get available shop items
        
        Args:
            category: Filter by category (optional)
            user_id: User ID for permission checks (optional)
            
        Returns:
            List of available item dictionaries
        """
        try:
            # Get base items from database
            items = self.db_manager.get_shop_items(active_only=True)
            
            # Filter by category if specified
            if category:
                items = [item for item in items if item.get('category', '').lower() == category.lower()]
            
            # Apply user-specific filters
            if user_id:
                items = self._filter_items_for_user(items, user_id)
            
            # Apply current discounts
            items = self._apply_discounts_to_items(items, user_id)
            
            # Sort items
            items.sort(key=lambda x: (x.get('category', ''), x.get('name', '')))
            
            return items
            
        except Exception as e:
            self.logger.error(f"Failed to get available items: {e}")
            return []
    
    def get_item(self, item_id: str) -> Optional[Dict]:
        """
        Get specific item by ID
        
        Args:
            item_id: Item ID or database ID
            
        Returns:
            Item dictionary or None if not found
        """
        try:
            return self.db_manager.get_shop_item(item_id)
        except Exception as e:
            self.logger.error(f"Failed to get item {item_id}: {e}")
            return None
    
    def process_purchase(self, user_id: str, item_id: str, quantity: int, 
                        player_name: str, server_id: str = None) -> Tuple[bool, str]:
        """
        Process item purchase
        
        Args:
            user_id: Discord user ID
            item_id: Item ID to purchase
            quantity: Number of items to purchase
            player_name: Player's in-game name
            server_id: Target server ID (optional)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate input
            if quantity <= 0:
                return False, "Quantity must be positive"
            
            # Get item information
            item = self.get_item(item_id)
            if not item:
                return False, "Item not found"
            
            if item.get('status') != 'Active':
                return False, "Item is not available for purchase"
            
            # Check stock
            stock = item.get('stock', -1)
            if stock != -1 and stock < quantity:
                return False, f"Insufficient stock (available: {stock})"
            
            # Check user requirements
            requirements_ok, req_message = self._check_purchase_requirements(user_id, item, quantity)
            if not requirements_ok:
                return False, req_message
            
            # Check cooldown
            cooldown_ok, cooldown_message = self._check_purchase_cooldown(user_id, item)
            if not cooldown_ok:
                return False, cooldown_message
            
            # Calculate final price with discounts
            base_price = item['price'] * quantity
            final_price, discount_info = self._calculate_final_price(base_price, item, user_id)
            
            # Check user points
            user_points = self.point_system.get_user_points(user_id)
            if user_points < final_price:
                return False, f"Insufficient points. Need: {final_price}, Have: {user_points}"
            
            # Process the purchase transaction
            success, message = self.db_manager.process_purchase(
                user_id, item_id, quantity, player_name
            )
            
            if success:
                # Apply discount if any
                if discount_info:
                    self._log_discount_usage(user_id, item, discount_info, base_price, final_price)
                
                # Set cooldown
                self._set_purchase_cooldown(user_id, item)
                
                # Log successful purchase
                self.logger.info(f"Purchase successful: {player_name} bought {quantity}x {item['name']} for {final_price} points")
                
                return True, f"Successfully purchased {quantity}x {item['name']} for {final_price} points"
            else:
                return False, message
                
        except Exception as e:
            self.logger.error(f"Failed to process purchase: {e}")
            return False, f"Purchase failed: {str(e)}"
    
    def _filter_items_for_user(self, items: List[Dict], user_id: str) -> List[Dict]:
        """Filter items based on user permissions and requirements"""
        try:
            filtered_items = []
            
            for item in items:
                # Check level requirement
                level_req = item.get('level_requirement', 1)
                user_level = self._get_user_level(user_id)
                if user_level < level_req:
                    continue
                
                # Check role requirements
                required_roles = item.get('required_roles', '')
                if required_roles and not self._check_user_roles(user_id, required_roles):
                    continue
                
                # Check stock availability
                stock = item.get('stock', -1)
                if stock == 0:
                    continue
                
                filtered_items.append(item)
            
            return filtered_items
            
        except Exception as e:
            self.logger.error(f"Failed to filter items for user: {e}")
            return items
    
    def _get_user_level(self, user_id: str) -> int:
        """Get user's level (placeholder implementation)"""
        try:
            # In a full implementation, this would check:
            # - Discord roles
            # - In-game level
            # - Admin status
            # - etc.
            return 100  # Default to max level for now
        except:
            return 1
    
    def _check_user_roles(self, user_id: str, required_roles: str) -> bool:
        """Check if user has required roles"""
        try:
            if not required_roles.strip():
                return True  # No requirements
            
            # In a full implementation, this would check Discord roles
            return True  # Allow all for now
            
        except Exception as e:
            self.logger.error(f"Failed to check user roles: {e}")
            return False
    
    def _check_purchase_requirements(self, user_id: str, item: Dict, quantity: int) -> Tuple[bool, str]:
        """Check if user meets purchase requirements"""
        try:
            # Check level requirement
            level_req = item.get('level_requirement', 1)
            user_level = self._get_user_level(user_id)
            if user_level < level_req:
                return False, f"Requires level {level_req} (you are level {user_level})"
            
            # Check role requirements
            required_roles = item.get('required_roles', '')
            if required_roles and not self._check_user_roles(user_id, required_roles):
                return False, f"Requires roles: {required_roles}"
            
            # Check daily purchase limits (if implemented)
            daily_limit = item.get('daily_limit', 0)
            if daily_limit > 0:
                daily_purchases = self._get_daily_purchases(user_id, item['id'])
                if daily_purchases + quantity > daily_limit:
                    return False, f"Daily limit exceeded (limit: {daily_limit}, purchased today: {daily_purchases})"
            
            return True, ""
            
        except Exception as e:
            self.logger.error(f"Failed to check purchase requirements: {e}")
            return False, "Requirements check failed"
    
    def _check_purchase_cooldown(self, user_id: str, item: Dict) -> Tuple[bool, str]:
        """Check if item is on cooldown for user"""
        try:
            cooldown_minutes = item.get('cooldown', 0)
            if cooldown_minutes <= 0:
                return True, ""  # No cooldown
            
            cooldown_key = f"{user_id}:{item['id']}"
            last_purchase = self.purchase_cooldowns.get(cooldown_key)
            
            if last_purchase:
                time_since = datetime.now() - last_purchase
                cooldown_remaining = timedelta(minutes=cooldown_minutes) - time_since
                
                if cooldown_remaining.total_seconds() > 0:
                    minutes_remaining = int(cooldown_remaining.total_seconds() / 60) + 1
                    return False, f"Item on cooldown for {minutes_remaining} more minutes"
            
            return True, ""
            
        except Exception as e:
            self.logger.error(f"Failed to check purchase cooldown: {e}")
            return True, ""  # Allow purchase if check fails
    
    def _set_purchase_cooldown(self, user_id: str, item: Dict):
        """Set purchase cooldown for user"""
        try:
            cooldown_minutes = item.get('cooldown', 0)
            if cooldown_minutes > 0:
                cooldown_key = f"{user_id}:{item['id']}"
                self.purchase_cooldowns[cooldown_key] = datetime.now()
        except Exception as e:
            self.logger.error(f"Failed to set purchase cooldown: {e}")
    
    def _apply_discounts_to_items(self, items: List[Dict], user_id: str = None) -> List[Dict]:
        """Apply current discounts to items"""
        try:
            discounted_items = []
            
            for item in items:
                discounted_item = item.copy()
                
                # Calculate discounted price
                final_price, discount_info = self._calculate_final_price(item['price'], item, user_id)
                
                if final_price != item['price']:
                    discounted_item['original_price'] = item['price']
                    discounted_item['price'] = final_price
                    discounted_item['discount_info'] = discount_info
                
                discounted_items.append(discounted_item)
            
            return discounted_items
            
        except Exception as e:
            self.logger.error(f"Failed to apply discounts: {e}")
            return items
    
    def _calculate_final_price(self, base_price: int, item: Dict, user_id: str = None) -> Tuple[int, Optional[Dict]]:
        """Calculate final price with discounts applied"""
        try:
            # Get applicable discounts
            discounts = self._get_applicable_discounts(item, user_id)
            
            if not discounts:
                return base_price, None
            
            final_price = base_price
            applied_discounts = []
            
            for discount in discounts:
                if discount['type'] == 'Percentage':
                    discount_amount = int(final_price * (discount['value'] / 100))
                else:  # Fixed amount
                    discount_amount = min(discount['value'], final_price)
                
                final_price -= discount_amount
                applied_discounts.append({
                    'name': discount['name'],
                    'type': discount['type'],
                    'value': discount['value'],
                    'amount_saved': discount_amount
                })
                
                # If not stackable, only apply first discount
                if not discount.get('stackable', False):
                    break
            
            final_price = max(1, final_price)  # Minimum 1 point
            
            discount_info = {
                'discounts': applied_discounts,
                'total_saved': base_price - final_price
            } if applied_discounts else None
            
            return final_price, discount_info
            
        except Exception as e:
            self.logger.error(f"Failed to calculate final price: {e}")
            return base_price, None
    
    def _get_applicable_discounts(self, item: Dict, user_id: str = None) -> List[Dict]:
        """Get discounts applicable to item and user"""
        try:
            # In a full implementation, this would:
            # 1. Get active discounts from database
            # 2. Check discount conditions (time, usage limits, etc.)
            # 3. Filter by target type (all items, category, specific items)
            # 4. Check user-specific conditions (roles, level, etc.)
            
            # For now, return empty list (no discounts)
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get applicable discounts: {e}")
            return []
    
    def _log_discount_usage(self, user_id: str, item: Dict, discount_info: Dict, 
                           original_price: int, final_price: int):
        """Log discount usage for analytics"""
        try:
            # In a full implementation, this would log to discount_usage table
            self.logger.info(f"Discount applied: {user_id} saved {original_price - final_price} points on {item['name']}")
        except Exception as e:
            self.logger.error(f"Failed to log discount usage: {e}")
    
    def _get_daily_purchases(self, user_id: str, item_id: int) -> int:
        """Get number of times user purchased item today"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COALESCE(SUM(quantity), 0) 
                FROM purchases 
                WHERE discord_id = ? 
                AND item_id = ? 
                AND DATE(created_at) = DATE('now')
            ''', (user_id, item_id))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            self.logger.error(f"Failed to get daily purchases: {e}")
            return 0
