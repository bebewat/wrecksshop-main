"""
Point System Manager for handling player rewards and point transactions
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class PointSystem:
    """Manages player points, rewards, and transactions"""
    
    def __init__(self, database_manager):
        """
        Initialize point system
        
        Args:
            database_manager: Database manager instance
        """
        self.db_manager = database_manager
        self.reward_lock = threading.Lock()
        self.active_players = {}  # Track active players for rewards
        self.reward_tiers = self._load_reward_tiers()
    
    def _load_reward_tiers(self) -> List[Dict]:
        """Load reward tiers from configuration"""
        try:
            if hasattr(self.db_manager, 'config_manager'):
                return self.db_manager.config_manager.get('reward_tiers', [])
            return []
        except Exception as e:
            logging.error(f"Failed to load reward tiers: {e}")
            return []
    
    def get_user_points(self, discord_id: str) -> int:
        """
        Get user's current point balance
        
        Args:
            discord_id: Discord user ID
            
        Returns:
            Current point balance
        """
        try:
            user = self.db_manager.get_user_by_discord_id(discord_id)
            if user:
                return user['points']
            else:
                # Create new user with 0 points
                return 0
        except Exception as e:
            logging.error(f"Failed to get user points for {discord_id}: {e}")
            return 0
    
    def add_points(self, discord_id: str, amount: int, reason: str = "Points added") -> bool:
        """
        Add points to user account
        
        Args:
            discord_id: Discord user ID
            amount: Points to add
            reason: Reason for adding points
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if amount <= 0:
                logging.warning(f"Attempted to add non-positive points: {amount}")
                return False
            
            # Ensure user exists
            user = self.db_manager.get_user_by_discord_id(discord_id)
            if not user:
                # Create user with default values
                self.db_manager.create_user(discord_id, f"User_{discord_id[-4:]}")
            
            # Add points
            success = self.db_manager.update_user_points(discord_id, amount, reason)
            
            if success:
                logging.info(f"Added {amount} points to {discord_id}: {reason}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to add points to {discord_id}: {e}")
            return False
    
    def remove_points(self, discord_id: str, amount: int, reason: str = "Points deducted") -> bool:
        """
        Remove points from user account
        
        Args:
            discord_id: Discord user ID
            amount: Points to remove
            reason: Reason for removing points
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if amount <= 0:
                logging.warning(f"Attempted to remove non-positive points: {amount}")
                return False
            
            # Check if user has enough points
            current_points = self.get_user_points(discord_id)
            if current_points < amount:
                logging.warning(f"User {discord_id} has insufficient points: {current_points} < {amount}")
                return False
            
            # Remove points
            success = self.db_manager.update_user_points(discord_id, -amount, reason)
            
            if success:
                logging.info(f"Removed {amount} points from {discord_id}: {reason}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to remove points from {discord_id}: {e}")
            return False
    
    def transfer_points(self, from_discord_id: str, to_discord_id: str, amount: int, 
                       from_name: str = "", to_name: str = "") -> bool:
        """
        Transfer points between users
        
        Args:
            from_discord_id: Source user Discord ID
            to_discord_id: Target user Discord ID
            amount: Points to transfer
            from_name: Source user display name
            to_name: Target user display name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if amount <= 0:
                logging.warning(f"Attempted to transfer non-positive points: {amount}")
                return False
            
            if from_discord_id == to_discord_id:
                logging.warning("Cannot transfer points to self")
                return False
            
            # Check source user has enough points
            from_points = self.get_user_points(from_discord_id)
            if from_points < amount:
                logging.warning(f"Source user {from_discord_id} has insufficient points: {from_points} < {amount}")
                return False
            
            # Ensure both users exist
            to_user = self.db_manager.get_user_by_discord_id(to_discord_id)
            if not to_user:
                self.db_manager.create_user(to_discord_id, to_name or f"User_{to_discord_id[-4:]}")
            
            with self.reward_lock:
                # Remove from source
                if not self.remove_points(from_discord_id, amount, f"Transfer to {to_name or to_discord_id}"):
                    return False
                
                # Add to target
                if not self.add_points(to_discord_id, amount, f"Transfer from {from_name or from_discord_id}"):
                    # Rollback - add points back to source
                    self.add_points(from_discord_id, amount, f"Rollback transfer to {to_name or to_discord_id}")
                    return False
            
            logging.info(f"Successfully transferred {amount} points from {from_discord_id} to {to_discord_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to transfer points: {e}")
            return False
    
    def get_user_transactions(self, discord_id: str, limit: int = 50) -> List[Dict]:
        """
        Get user's transaction history
        
        Args:
            discord_id: Discord user ID
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        try:
            return self.db_manager.get_user_transactions(discord_id, limit)
        except Exception as e:
            logging.error(f"Failed to get transactions for {discord_id}: {e}")
            return []
    
    def get_leaderboard(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get points leaderboard
        
        Args:
            limit: Number of top users to return
            
        Returns:
            List of (discord_id, points) tuples
        """
        try:
            return self.db_manager.get_leaderboard(limit)
        except Exception as e:
            logging.error(f"Failed to get leaderboard: {e}")
            return []
    
    def calculate_reward_amount(self, discord_id: str, base_amount: int) -> int:
        """
        Calculate reward amount based on user tier
        
        Args:
            discord_id: Discord user ID
            base_amount: Base reward amount
            
        Returns:
            Calculated reward amount
        """
        try:
            # Get user's tier multiplier
            multiplier = self._get_user_tier_multiplier(discord_id)
            
            # Apply multiplier
            reward_amount = int(base_amount * multiplier)
            
            # Apply any additional bonuses
            reward_amount = self._apply_bonus_multipliers(discord_id, reward_amount)
            
            return max(1, reward_amount)  # Minimum 1 point
            
        except Exception as e:
            logging.error(f"Failed to calculate reward for {discord_id}: {e}")
            return base_amount
    
    def _get_user_tier_multiplier(self, discord_id: str) -> float:
        """Get user's tier multiplier based on roles/status"""
        try:
            # Default multiplier
            multiplier = 1.0
            
            # Check reward tiers
            for tier in self.reward_tiers:
                requirements = tier.get('requirements', [])
                
                # For now, just return the highest tier multiplier
                # In a full implementation, this would check Discord roles, donation status, etc.
                if self._check_tier_requirements(discord_id, requirements):
                    tier_multiplier = tier.get('multiplier', 1.0)
                    if tier_multiplier > multiplier:
                        multiplier = tier_multiplier
            
            return multiplier
            
        except Exception as e:
            logging.error(f"Failed to get tier multiplier for {discord_id}: {e}")
            return 1.0
    
    def _check_tier_requirements(self, discord_id: str, requirements: List[str]) -> bool:
        """Check if user meets tier requirements"""
        try:
            # Basic implementation - in a full version this would check:
            # - Discord roles
            # - Donation status from Tip4Serv
            # - Admin status
            # - Play time
            # - etc.
            
            if not requirements:
                return True  # No requirements = everyone qualifies
            
            # For now, return True for basic tier
            return True
            
        except Exception as e:
            logging.error(f"Failed to check tier requirements for {discord_id}: {e}")
            return False
    
    def _apply_bonus_multipliers(self, discord_id: str, amount: int) -> int:
        """Apply any bonus multipliers"""
        try:
            # Check for special events, bonuses, etc.
            # This could include:
            # - Weekend bonuses
            # - First login bonus
            # - Streak bonuses
            # - Special event multipliers
            
            return amount  # No bonuses for now
            
        except Exception as e:
            logging.error(f"Failed to apply bonus multipliers for {discord_id}: {e}")
            return amount
    
    def process_playtime_rewards(self) -> int:
        """
        Process playtime rewards for active players
        
        Returns:
            Number of players who received rewards
        """
        try:
            rewarded_count = 0
            
            # Get reward configuration
            if hasattr(self.db_manager, 'config_manager'):
                base_amount = self.db_manager.config_manager.get('reward_amount', 10)
                reward_interval = self.db_manager.config_manager.get('reward_interval', 30)
            else:
                base_amount = 10
                reward_interval = 30
            
            # For now, this is a simplified implementation
            # In a full version, this would:
            # 1. Check which players are currently online on servers
            # 2. Track their playtime
            # 3. Give rewards based on actual playtime
            
            # Check for users who haven't received rewards recently
            cutoff_time = datetime.now() - timedelta(minutes=reward_interval)
            
            # This is a placeholder - would need integration with server monitoring
            # to track actual online players
            
            logging.info(f"Processed playtime rewards for {rewarded_count} players")
            return rewarded_count
            
        except Exception as e:
            logging.error(f"Failed to process playtime rewards: {e}")
            return 0
    
    def give_reward(self, discord_id: str, username: str = "", reason: str = "Playtime reward") -> bool:
        """
        Give reward to specific user
        
        Args:
            discord_id: Discord user ID
            username: User's display name
            reason: Reason for reward
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get base reward amount
            if hasattr(self.db_manager, 'config_manager'):
                base_amount = self.db_manager.config_manager.get('reward_amount', 10)
            else:
                base_amount = 10
            
            # Calculate actual reward amount
            reward_amount = self.calculate_reward_amount(discord_id, base_amount)
            
            # Ensure user exists
            user = self.db_manager.get_user_by_discord_id(discord_id)
            if not user:
                self.db_manager.create_user(discord_id, username or f"User_{discord_id[-4:]}")
            
            # Check if user already received reward recently
            if self._check_recent_reward(discord_id):
                logging.debug(f"User {discord_id} already received recent reward")
                return False
            
            # Give reward
            success = self.add_points(discord_id, reward_amount, reason)
            
            if success:
                # Update last reward time
                self._update_last_reward_time(discord_id)
                logging.info(f"Gave {reward_amount} point reward to {discord_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to give reward to {discord_id}: {e}")
            return False
    
    def _check_recent_reward(self, discord_id: str) -> bool:
        """Check if user received reward recently"""
        try:
            user = self.db_manager.get_user_by_discord_id(discord_id)
            if not user or not user.get('last_reward'):
                return False
            
            # Get reward interval
            if hasattr(self.db_manager, 'config_manager'):
                reward_interval = self.db_manager.config_manager.get('reward_interval', 30)
            else:
                reward_interval = 30
            
            last_reward = datetime.fromisoformat(user['last_reward'])
            cutoff_time = datetime.now() - timedelta(minutes=reward_interval)
            
            return last_reward > cutoff_time
            
        except Exception as e:
            logging.error(f"Failed to check recent reward for {discord_id}: {e}")
            return False
    
    def _update_last_reward_time(self, discord_id: str) -> bool:
        """Update user's last reward time"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET last_reward = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            ''', (discord_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Failed to update last reward time for {discord_id}: {e}")
            return False
    
    def get_point_statistics(self) -> Dict[str, any]:
        """Get point system statistics"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Total points in circulation
            cursor.execute('SELECT COALESCE(SUM(points), 0) FROM users')
            total_points = cursor.fetchone()[0]
            
            # Total points earned
            cursor.execute('SELECT COALESCE(SUM(total_earned), 0) FROM users')
            total_earned = cursor.fetchone()[0]
            
            # Total points spent
            cursor.execute('SELECT COALESCE(SUM(total_spent), 0) FROM users')
            total_spent = cursor.fetchone()[0]
            
            # Active users (with points > 0)
            cursor.execute('SELECT COUNT(*) FROM users WHERE points > 0')
            active_users = cursor.fetchone()[0]
            
            # Recent transactions (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM point_transactions 
                WHERE created_at >= datetime('now', '-1 day')
            ''')
            recent_transactions = cursor.fetchone()[0]
            
            return {
                'total_points_circulation': total_points,
                'total_points_earned': total_earned,
                'total_points_spent': total_spent,
                'active_users': active_users,
                'recent_transactions': recent_transactions
            }
            
        except Exception as e:
            logging.error(f"Failed to get point statistics: {e}")
            return {}
    
    def validate_transaction(self, discord_id: str, amount: int, transaction_type: str) -> Tuple[bool, str]:
        """
        Validate a point transaction before processing
        
        Args:
            discord_id: Discord user ID
            amount: Transaction amount
            transaction_type: Type of transaction
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if amount <= 0:
                return False, "Transaction amount must be positive"
            
            # Check daily limits
            if hasattr(self.db_manager, 'config_manager'):
                max_daily_rewards = self.db_manager.config_manager.get('max_daily_rewards', 1000)
                max_transfer = self.db_manager.config_manager.get('max_points_per_transfer', 10000)
            else:
                max_daily_rewards = 1000
                max_transfer = 10000
            
            if transaction_type == 'transfer' and amount > max_transfer:
                return False, f"Transfer amount exceeds maximum of {max_transfer} points"
            
            if transaction_type == 'reward':
                # Check daily reward limit
                today_rewards = self._get_daily_rewards(discord_id)
                if today_rewards + amount > max_daily_rewards:
                    return False, f"Daily reward limit of {max_daily_rewards} points would be exceeded"
            
            return True, ""
            
        except Exception as e:
            logging.error(f"Failed to validate transaction: {e}")
            return False, "Transaction validation failed"
    
    def _get_daily_rewards(self, discord_id: str) -> int:
        """Get total rewards received today"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COALESCE(SUM(points_change), 0) 
                FROM point_transactions 
                WHERE discord_id = ? 
                AND transaction_type = 'earned' 
                AND DATE(created_at) = DATE('now')
                AND points_change > 0
            ''', (discord_id,))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            logging.error(f"Failed to get daily rewards for {discord_id}: {e}")
            return 0
    
    def cleanup_old_transactions(self, days_to_keep: int = 90) -> int:
        """
        Clean up old transaction records
        
        Args:
            days_to_keep: Number of days of transactions to keep
            
        Returns:
            Number of records deleted
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            cursor.execute('''
                DELETE FROM point_transactions 
                WHERE created_at < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logging.info(f"Cleaned up {deleted_count} old transaction records")
            return deleted_count
            
        except Exception as e:
            logging.error(f"Failed to cleanup old transactions: {e}")
            return 0

