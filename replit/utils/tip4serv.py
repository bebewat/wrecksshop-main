"""
Tip4Serv integration utility for handling donations and webhooks
"""

import requests
import json
import hashlib
import hmac
import time
from typing import Dict, Optional, Any
from utils.config import Config
from utils.logger import Logger

class Tip4ServManager:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.base_url = "https://api.tip4serv.com"
        
    def get_api_credentials(self) -> tuple:
        """Get API credentials from config"""
        secret = self.config.get('tip4serv_secret', '')
        token = self.config.get('tip4serv_token', '')
        return secret, token
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature from Tip4Serv"""
        try:
            secret, _ = self.get_api_credentials()
            if not secret:
                self.logger.error("Tip4Serv secret not configured")
                return False
            
            # Calculate expected signature
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    def process_donation_webhook(self, webhook_data: Dict[str, Any]) -> Optional[Dict]:
        """Process incoming donation webhook"""
        try:
            # Extract donation information
            donation_info = {
                'transaction_id': webhook_data.get('transaction_id'),
                'donor_name': webhook_data.get('donor_name'),
                'donor_email': webhook_data.get('donor_email'),
                'amount': webhook_data.get('amount', 0),
                'currency': webhook_data.get('currency', 'USD'),
                'message': webhook_data.get('message', ''),
                'timestamp': webhook_data.get('timestamp', int(time.time())),
                'custom_data': webhook_data.get('custom_data', {})
            }
            
            # Log donation
            self.logger.info(f"Donation received: {donation_info['donor_name']} - ${donation_info['amount']}")
            
            # Calculate bonus points based on donation amount
            bonus_points = self.calculate_donation_bonus(donation_info['amount'])
            donation_info['bonus_points'] = bonus_points
            
            return donation_info
            
        except Exception as e:
            self.logger.error(f"Error processing donation webhook: {e}")
            return None
    
    def calculate_donation_bonus(self, amount: float) -> int:
        """Calculate bonus points for donation amount"""
        try:
            # Default conversion: $1 = 100 points
            base_points = int(amount * 100)
            
            # Bonus tiers
            if amount >= 50:
                bonus_multiplier = 1.5  # 50% bonus for $50+
            elif amount >= 25:
                bonus_multiplier = 1.3  # 30% bonus for $25+
            elif amount >= 10:
                bonus_multiplier = 1.2  # 20% bonus for $10+
            elif amount >= 5:
                bonus_multiplier = 1.1  # 10% bonus for $5+
            else:
                bonus_multiplier = 1.0  # No bonus under $5
            
            total_points = int(base_points * bonus_multiplier)
            
            self.logger.info(f"Donation bonus calculated: ${amount} = {total_points} points")
            return total_points
            
        except Exception as e:
            self.logger.error(f"Error calculating donation bonus: {e}")
            return 0
    
    async def award_donation_points(self, donation_info: Dict, discord_id: str = None) -> bool:
        """Award points for donation"""
        try:
            from bot.economy import EconomyManager
            from utils.database import Database
            
            # Initialize database and economy manager
            db = Database()
            await db.initialize()
            economy = EconomyManager(db)
            
            # Determine recipient
            if discord_id:
                # Direct Discord user ID provided
                recipient_id = discord_id
            else:
                # Try to find user by email or custom data
                recipient_id = await self.find_user_by_donation_info(donation_info)
                if not recipient_id:
                    self.logger.warning(f"Could not find Discord user for donation: {donation_info['donor_email']}")
                    return False
            
            # Award points
            points = donation_info.get('bonus_points', 0)
            if points > 0:
                reason = f"Donation bonus: ${donation_info['amount']} - {donation_info['transaction_id']}"
                await economy.add_points(recipient_id, points, reason)
                
                self.logger.info(f"Awarded {points} points to {recipient_id} for donation")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error awarding donation points: {e}")
            return False
    
    async def find_user_by_donation_info(self, donation_info: Dict) -> Optional[str]:
        """Find Discord user by donation information"""
        try:
            from utils.database import Database
            
            db = Database()
            
            # Check custom data for Discord ID
            custom_data = donation_info.get('custom_data', {})
            if 'discord_id' in custom_data:
                return custom_data['discord_id']
            
            # Check if email is linked to a Discord account
            email = donation_info.get('donor_email')
            if email:
                # This would query a user_links table if it exists
                query = "SELECT discord_id FROM user_links WHERE email = ?"
                result = await db.fetch_one(query, (email,))
                if result:
                    return result['discord_id']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding user by donation info: {e}")
            return None
    
    def get_donation_history(self, limit: int = 50) -> List[Dict]:
        """Get donation history from Tip4Serv API"""
        try:
            secret, token = self.get_api_credentials()
            if not token:
                self.logger.error("Tip4Serv token not configured")
                return []
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'order': 'desc'
            }
            
            response = requests.get(
                f"{self.base_url}/donations",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('donations', [])
            else:
                self.logger.error(f"Error fetching donation history: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting donation history: {e}")
            return []
    
    def get_donation_stats(self) -> Dict:
        """Get donation statistics"""
        try:
            secret, token = self.get_api_credentials()
            if not token:
                return {}
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/stats",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Error fetching donation stats: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting donation stats: {e}")
            return {}
    
    def create_donation_goal(self, title: str, target_amount: float, description: str = "") -> bool:
        """Create a donation goal"""
        try:
            secret, token = self.get_api_credentials()
            if not token:
                return False
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'title': title,
                'target_amount': target_amount,
                'description': description,
                'currency': 'USD'
            }
            
            response = requests.post(
                f"{self.base_url}/goals",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                self.logger.info(f"Donation goal created: {title}")
                return True
            else:
                self.logger.error(f"Error creating donation goal: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating donation goal: {e}")
            return False
    
    def send_thank_you_message(self, donation_info: Dict) -> bool:
        """Send thank you message for donation"""
        try:
            # This would integrate with email service or notification system
            donor_name = donation_info.get('donor_name', 'Anonymous')
            amount = donation_info.get('amount', 0)
            points = donation_info.get('bonus_points', 0)
            
            message = f"""
Thank you for your donation, {donor_name}!

Donation Amount: ${amount}
Bonus Points Awarded: {points}
Transaction ID: {donation_info.get('transaction_id', 'N/A')}

Your support helps keep our Ark servers running and improves the gaming experience for everyone!
"""
            
            self.logger.info(f"Thank you message prepared for {donor_name}")
            # In a real implementation, this would send an email or Discord DM
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending thank you message: {e}")
            return False
    
    def validate_webhook_data(self, data: Dict) -> bool:
        """Validate webhook data structure"""
        try:
            required_fields = ['transaction_id', 'amount', 'donor_name']
            
            for field in required_fields:
                if field not in data:
                    self.logger.error(f"Missing required field in webhook: {field}")
                    return False
            
            # Validate amount
            amount = data.get('amount')
            if not isinstance(amount, (int, float)) or amount <= 0:
                self.logger.error("Invalid donation amount")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating webhook data: {e}")
            return False
    
    def get_api_status(self) -> Dict:
        """Check Tip4Serv API status"""
        try:
            response = requests.get(
                f"{self.base_url}/status",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'status': 'online',
                    'response_time': response.elapsed.total_seconds(),
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {'status': 'timeout'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def test_webhook_setup(self) -> bool:
        """Test webhook configuration"""
        try:
            secret, token = self.get_api_credentials()
            
            if not secret or not token:
                self.logger.error("Tip4Serv credentials not properly configured")
                return False
            
            # Test signature verification
            test_payload = '{"test": true}'
            test_signature = hmac.new(
                secret.encode('utf-8'),
                test_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if self.verify_webhook_signature(test_payload, test_signature):
                self.logger.info("Webhook signature verification test passed")
                return True
            else:
                self.logger.error("Webhook signature verification test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error testing webhook setup: {e}")
            return False
