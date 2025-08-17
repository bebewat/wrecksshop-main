"""
RCON Manager for communicating with Ark servers
Handles server connections, command execution, and status monitoring
"""

import socket
import struct
import time
import logging
import threading
from typing import Dict, Optional, List, Tuple
from datetime import datetime

class RCONManager:
    """Manages RCON connections to Ark servers"""
    
    # RCON packet types
    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0
    
    def __init__(self, app=None):
        """
        Initialize RCON manager
        
        Args:
            app: Main application instance for configuration access
        """
        self.app = app
        self.connections = {}
        self.timeout = 10
        self.retry_attempts = 3
        
        if app and hasattr(app, 'config_manager'):
            self.timeout = app.config_manager.get('rcon_timeout', 10)
            self.retry_attempts = app.config_manager.get('rcon_retry_attempts', 3)
    
    def _create_packet(self, packet_id: int, packet_type: int, body: str) -> bytes:
        """Create RCON packet"""
        try:
            body_encoded = body.encode('utf-8', 'replace')
            packet_size = len(body_encoded) + 10  # 4 + 4 + body + 2 null bytes
            
            packet = struct.pack('<i', packet_size)
            packet += struct.pack('<i', packet_id)
            packet += struct.pack('<i', packet_type)
            packet += body_encoded
            packet += b'\x00\x00'
            
            return packet
        except Exception as e:
            logging.error(f"Failed to create RCON packet: {e}")
            return b''
    
    def _parse_packet(self, data: bytes) -> Tuple[int, int, str]:
        """Parse RCON packet response"""
        try:
            if len(data) < 12:
                return -1, -1, ""
            
            packet_size = struct.unpack('<i', data[:4])[0]
            packet_id = struct.unpack('<i', data[4:8])[0]
            packet_type = struct.unpack('<i', data[8:12])[0]
            
            body_end = 4 + packet_size - 2  # Exclude null terminators
            if body_end > len(data):
                body_end = len(data)
            
            body = data[12:body_end].decode('utf-8', 'replace')
            return packet_id, packet_type, body
            
        except Exception as e:
            logging.error(f"Failed to parse RCON packet: {e}")
            return -1, -1, ""
    
    def connect(self, host: str, port: int, password: str) -> Optional[socket.socket]:
        """
        Connect to RCON server
        
        Args:
            host: Server host/IP
            port: RCON port
            password: RCON password
            
        Returns:
            Socket connection or None if failed
        """
        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Connect to server
            sock.connect((host, port))
            
            # Send authentication packet
            auth_packet = self._create_packet(1, self.SERVERDATA_AUTH, password)
            sock.send(auth_packet)
            
            # Receive authentication response
            response_data = sock.recv(4096)
            packet_id, packet_type, body = self._parse_packet(response_data)
            
            if packet_id == 1 and packet_type == self.SERVERDATA_AUTH_RESPONSE:
                logging.info(f"Successfully authenticated to RCON server {host}:{port}")
                return sock
            else:
                logging.error(f"RCON authentication failed for {host}:{port}")
                sock.close()
                return None
                
        except socket.timeout:
            logging.error(f"RCON connection timeout to {host}:{port}")
            return None
        except socket.error as e:
            logging.error(f"RCON connection error to {host}:{port}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected RCON connection error to {host}:{port}: {e}")
            return None
    
    def send_command(self, server_data: Dict, command: str) -> Optional[str]:
        """
        Send command to RCON server
        
        Args:
            server_data: Server configuration dictionary
            command: Command to execute
            
        Returns:
            Command response or None if failed
        """
        for attempt in range(self.retry_attempts):
            try:
                # Get connection
                connection_key = f"{server_data['host']}:{server_data['port']}"
                sock = self.connections.get(connection_key)
                
                # Create new connection if needed
                if not sock:
                    sock = self.connect(server_data['host'], server_data['port'], server_data['password'])
                    if sock:
                        self.connections[connection_key] = sock
                    else:
                        continue
                
                # Send command packet
                command_packet = self._create_packet(2, self.SERVERDATA_EXECCOMMAND, command)
                sock.send(command_packet)
                
                # Receive response
                response_data = sock.recv(4096)
                packet_id, packet_type, body = self._parse_packet(response_data)
                
                if packet_type == self.SERVERDATA_RESPONSE_VALUE:
                    logging.debug(f"RCON command successful: {command}")
                    return body
                else:
                    logging.warning(f"Unexpected RCON response type: {packet_type}")
                    # Try to reconnect for next attempt
                    self._close_connection(connection_key)
                    
            except socket.error as e:
                logging.error(f"RCON socket error (attempt {attempt + 1}): {e}")
                self._close_connection(connection_key)
                time.sleep(1)  # Wait before retry
                
            except Exception as e:
                logging.error(f"RCON command error (attempt {attempt + 1}): {e}")
                self._close_connection(connection_key)
                time.sleep(1)
        
        logging.error(f"Failed to send RCON command after {self.retry_attempts} attempts")
        return None
    
    def test_connection(self, server_data: Dict) -> bool:
        """
        Test RCON connection to server
        
        Args:
            server_data: Server configuration dictionary
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            sock = self.connect(server_data['host'], server_data['port'], server_data['password'])
            if sock:
                # Test with a simple command
                command_packet = self._create_packet(3, self.SERVERDATA_EXECCOMMAND, "listplayers")
                sock.send(command_packet)
                
                # Try to receive response
                sock.settimeout(5)  # Short timeout for test
                response_data = sock.recv(4096)
                
                sock.close()
                
                # Check if we got a valid response
                packet_id, packet_type, body = self._parse_packet(response_data)
                return packet_type == self.SERVERDATA_RESPONSE_VALUE
            
            return False
            
        except Exception as e:
            logging.error(f"RCON connection test failed: {e}")
            return False
    
    def get_server_info(self, server_data: Dict) -> Dict[str, any]:
        """
        Get server information via RCON
        
        Args:
            server_data: Server configuration dictionary
            
        Returns:
            Dictionary with server information
        """
        info = {
            'online': False,
            'players': 0,
            'max_players': 0,
            'server_name': '',
            'map': '',
            'version': ''
        }
        
        try:
            # Test basic connectivity
            if not self.test_connection(server_data):
                return info
            
            info['online'] = True
            
            # Get player list
            players_response = self.send_command(server_data, "listplayers")
            if players_response:
                # Parse player count from response
                lines = players_response.strip().split('\n')
                # Filter out empty lines and headers
                player_lines = [line for line in lines if line.strip() and not line.startswith('No Players')]
                info['players'] = max(0, len(player_lines) - 1)  # Subtract header line
            
            # Get server info
            info_response = self.send_command(server_data, "serverinfo")
            if info_response:
                # Parse server info (this varies by server)
                info['server_name'] = server_data.get('name', 'Unknown')
            
        except Exception as e:
            logging.error(f"Failed to get server info: {e}")
        
        return info
    
    def give_item_to_player(self, server_data: Dict, player_id: str, item_blueprint: str, 
                           quantity: int = 1, quality: int = 100, force_blueprint: bool = False) -> bool:
        """
        Give item to player via RCON
        
        Args:
            server_data: Server configuration dictionary
            player_id: Steam ID or player name
            item_blueprint: Item blueprint path
            quantity: Number of items to give
            quality: Item quality (0-100)
            force_blueprint: Whether to force blueprint
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Construct give item command
            force_bp = "true" if force_blueprint else "false"
            command = f'GiveItemToPlayer {player_id} "{item_blueprint}" {quantity} {quality} {force_bp}'
            
            response = self.send_command(server_data, command)
            
            if response is not None:
                # Check for success indicators in response
                success_indicators = ["Giving", "gave", "item", "successfully"]
                response_lower = response.lower()
                
                # If response contains success indicators or is empty (some servers don't respond)
                if any(indicator in response_lower for indicator in success_indicators) or not response.strip():
                    logging.info(f"Successfully gave item {item_blueprint} to player {player_id}")
                    return True
                else:
                    logging.warning(f"Uncertain item give result: {response}")
                    return True  # Assume success if no error message
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to give item to player: {e}")
            return False
    
    def send_global_message(self, server_data: Dict, message: str) -> bool:
        """
        Send global message to server
        
        Args:
            server_data: Server configuration dictionary
            message: Message to broadcast
            
        Returns:
            True if successful, False otherwise
        """
        try:
            command = f'broadcast {message}'
            response = self.send_command(server_data, command)
            return response is not None
            
        except Exception as e:
            logging.error(f"Failed to send global message: {e}")
            return False
    
    def send_private_message(self, server_data: Dict, player_id: str, message: str) -> bool:
        """
        Send private message to player
        
        Args:
            server_data: Server configuration dictionary
            player_id: Steam ID or player name
            message: Message to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            command = f'ServerChat {player_id} {message}'
            response = self.send_command(server_data, command)
            return response is not None
            
        except Exception as e:
            logging.error(f"Failed to send private message: {e}")
            return False
    
    def get_online_players(self, server_data: Dict) -> List[Dict]:
        """
        Get list of online players
        
        Args:
            server_data: Server configuration dictionary
            
        Returns:
            List of player dictionaries
        """
        players = []
        
        try:
            response = self.send_command(server_data, "listplayers")
            if response:
                lines = response.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('No Players') and ',' in line:
                        # Parse player info (format may vary)
                        # Typical format: "PlayerName, PlayerID, SteamID"
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) >= 2:
                            player = {
                                'name': parts[0],
                                'id': parts[1] if len(parts) > 1 else '',
                                'steam_id': parts[2] if len(parts) > 2 else ''
                            }
                            players.append(player)
        
        except Exception as e:
            logging.error(f"Failed to get online players: {e}")
        
        return players
    
    def _close_connection(self, connection_key: str):
        """Close and remove connection"""
        try:
            if connection_key in self.connections:
                self.connections[connection_key].close()
                del self.connections[connection_key]
        except:
            pass
    
    def close_all_connections(self):
        """Close all RCON connections"""
        try:
            for connection_key in list(self.connections.keys()):
                self._close_connection(connection_key)
            logging.info("All RCON connections closed")
        except Exception as e:
            logging.error(f"Error closing RCON connections: {e}")
    
    def execute_shop_purchase(self, server_data: Dict, purchase_data: Dict) -> bool:
        """
        Execute shop purchase by giving items to player
        
        Args:
            server_data: Server configuration dictionary
            purchase_data: Purchase information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract purchase information
            player_id = purchase_data.get('player_id', '')
            item_data = purchase_data.get('item_data', {})
            quantity = purchase_data.get('quantity', 1)
            
            if not player_id or not item_data:
                logging.error("Invalid purchase data")
                return False
            
            # Execute give command
            give_command = item_data.get('give_command', '')
            if give_command:
                # Replace placeholders in command
                command = give_command.format(
                    player_id=player_id,
                    blueprint=item_data.get('item_id', ''),
                    quantity=quantity,
                    quality=item_data.get('quality', 100),
                    force_blueprint='false'
                )
                
                response = self.send_command(server_data, command)
                success = response is not None
                
                # Execute additional commands if specified
                additional_commands = item_data.get('additional_commands', '')
                if additional_commands and success:
                    for cmd in additional_commands.split('\n'):
                        cmd = cmd.strip()
                        if cmd:
                            cmd = cmd.format(
                                player_id=player_id,
                                quantity=quantity
                            )
                            self.send_command(server_data, cmd)
                
                return success
            else:
                # Fallback to basic give item command
                return self.give_item_to_player(
                    server_data,
                    player_id,
                    item_data.get('item_id', ''),
                    quantity,
                    item_data.get('quality', 100)
                )
                
        except Exception as e:
            logging.error(f"Failed to execute shop purchase: {e}")
            return False
    
    def monitor_servers(self, servers: List[Dict], callback=None):
        """
        Monitor multiple servers in background thread
        
        Args:
            servers: List of server configurations
            callback: Optional callback function for status updates
        """
        def monitor_thread():
            while True:
                try:
                    for server in servers:
                        try:
                            info = self.get_server_info(server)
                            
                            if callback:
                                callback(server, info)
                            
                            # Update database if app available
                            if self.app and hasattr(self.app, 'database_manager'):
                                status = 'Online' if info['online'] else 'Offline'
                                self.app.database_manager.update_server_status(
                                    server['id'],
                                    status,
                                    datetime.now().isoformat(),
                                    info['players']
                                )
                                
                        except Exception as e:
                            logging.error(f"Error monitoring server {server.get('name', 'Unknown')}: {e}")
                    
                    # Wait before next check
                    time.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    logging.error(f"Error in server monitoring thread: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
        monitor_thread.start()
        logging.info("Server monitoring started")

