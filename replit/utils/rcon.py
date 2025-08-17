"""
RCON (Remote Console) utility for communicating with Ark servers
"""

import asyncio
import socket
import struct
import random
from typing import Dict, List, Optional, Tuple
from utils.config import Config
from utils.logger import Logger

class RCONProtocol:
    """RCON protocol implementation"""
    
    # Packet types
    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0
    
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.authenticated = False
        self.request_id = 0
    
    def _generate_request_id(self) -> int:
        """Generate unique request ID"""
        self.request_id = random.randint(1, 2147483647)
        return self.request_id
    
    def _pack_packet(self, packet_type: int, body: str) -> bytes:
        """Pack RCON packet"""
        request_id = self._generate_request_id()
        body_bytes = body.encode('utf-8') + b'\x00\x00'
        packet_size = len(body_bytes) + 10
        
        packet = struct.pack('<iii', packet_size, request_id, packet_type)
        packet += body_bytes
        
        return packet
    
    def _unpack_packet(self, data: bytes) -> Tuple[int, int, str]:
        """Unpack RCON packet"""
        if len(data) < 12:
            raise ValueError("Packet too short")
        
        packet_size, request_id, packet_type = struct.unpack('<iii', data[:12])
        body = data[12:packet_size + 4].rstrip(b'\x00').decode('utf-8', errors='ignore')
        
        return request_id, packet_type, body
    
    async def connect(self) -> bool:
        """Connect to RCON server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Authenticate
            auth_packet = self._pack_packet(self.SERVERDATA_AUTH, self.password)
            self.socket.sendall(auth_packet)
            
            # Read response
            response_data = self.socket.recv(4096)
            request_id, packet_type, body = self._unpack_packet(response_data)
            
            if packet_type == self.SERVERDATA_AUTH_RESPONSE and request_id == self.request_id:
                self.authenticated = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"RCON connection error: {e}")
            return False
    
    async def execute_command(self, command: str) -> Optional[str]:
        """Execute command on RCON server"""
        if not self.authenticated:
            if not await self.connect():
                return None
        
        try:
            # Send command
            command_packet = self._pack_packet(self.SERVERDATA_EXECCOMMAND, command)
            self.socket.sendall(command_packet)
            
            # Read response
            response_data = self.socket.recv(4096)
            request_id, packet_type, body = self._unpack_packet(response_data)
            
            if packet_type == self.SERVERDATA_RESPONSE_VALUE:
                return body
            else:
                return None
                
        except Exception as e:
            print(f"RCON command error: {e}")
            return None
    
    def disconnect(self) -> None:
        """Disconnect from RCON server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.authenticated = False

class RCONManager:
    """Manager for multiple RCON connections"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.connections = {}
    
    def get_servers(self) -> List[Dict]:
        """Get configured RCON servers"""
        return self.config.get('rcon_servers', [])
    
    async def get_connection(self, server_name: str) -> Optional[RCONProtocol]:
        """Get RCON connection for server"""
        try:
            servers = self.get_servers()
            server_config = None
            
            for server in servers:
                if server.get('name') == server_name:
                    server_config = server
                    break
            
            if not server_config:
                return None
            
            # Check if connection exists and is valid
            if server_name in self.connections:
                connection = self.connections[server_name]
                if connection.authenticated:
                    return connection
            
            # Create new connection
            connection = RCONProtocol(
                server_config['host'],
                server_config['port'],
                server_config['password']
            )
            
            if await connection.connect():
                self.connections[server_name] = connection
                return connection
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting RCON connection for {server_name}: {e}")
            return None
    
    async def execute_command(self, server_name: str, command: str) -> Optional[str]:
        """Execute command on specific server"""
        try:
            connection = await self.get_connection(server_name)
            if connection:
                result = await connection.execute_command(command)
                self.logger.info(f"RCON command executed on {server_name}: {command}")
                return result
            else:
                self.logger.error(f"Failed to connect to RCON server: {server_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error executing RCON command on {server_name}: {e}")
            return None
    
    async def execute_command_all_servers(self, command: str) -> Dict[str, Optional[str]]:
        """Execute command on all configured servers"""
        results = {}
        servers = self.get_servers()
        
        for server in servers:
            server_name = server.get('name')
            if server_name:
                result = await self.execute_command(server_name, command)
                results[server_name] = result
        
        return results
    
    def test_connection(self, host: str, port: int, password: str) -> bool:
        """Test RCON connection"""
        try:
            connection = RCONProtocol(host, port, password)
            
            # Create async event loop for testing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(connection.connect())
                if result:
                    connection.disconnect()
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"RCON connection test failed: {e}")
            return False
    
    async def get_server_info(self, server_name: str) -> Optional[Dict]:
        """Get server information"""
        try:
            # Get server info using RCON commands
            connection = await self.get_connection(server_name)
            if not connection:
                return None
            
            # Execute info commands
            server_info = {}
            
            # Get server version
            version_result = await connection.execute_command("version")
            if version_result:
                server_info['version'] = version_result.strip()
            
            # Get player count
            players_result = await connection.execute_command("listplayers")
            if players_result:
                # Parse player list (format may vary)
                lines = players_result.split('\n')
                player_count = len([line for line in lines if line.strip() and 'Player' in line])
                server_info['player_count'] = player_count
            
            # Get server name
            name_result = await connection.execute_command("getservername")
            if name_result:
                server_info['server_name'] = name_result.strip()
            
            return server_info
            
        except Exception as e:
            self.logger.error(f"Error getting server info for {server_name}: {e}")
            return None
    
    async def get_online_players(self, server_name: str) -> List[Dict]:
        """Get list of online players"""
        try:
            connection = await self.get_connection(server_name)
            if not connection:
                return []
            
            # Get player list
            players_result = await connection.execute_command("listplayers")
            if not players_result:
                return []
            
            players = []
            lines = players_result.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and 'Player' in line:
                    # Parse player information
                    # Format may vary by server, this is a basic parser
                    parts = line.split(',')
                    if len(parts) >= 2:
                        player_info = {
                            'name': parts[0].replace('Player:', '').strip(),
                            'steam_id': parts[1].strip() if len(parts) > 1 else '',
                            'online_time': parts[2].strip() if len(parts) > 2 else ''
                        }
                        players.append(player_info)
            
            return players
            
        except Exception as e:
            self.logger.error(f"Error getting online players for {server_name}: {e}")
            return []
    
    async def broadcast_message(self, message: str, server_name: Optional[str] = None) -> bool:
        """Broadcast message to server(s)"""
        try:
            command = f'broadcast "{message}"'
            
            if server_name:
                # Broadcast to specific server
                result = await self.execute_command(server_name, command)
                return result is not None
            else:
                # Broadcast to all servers
                results = await self.execute_command_all_servers(command)
                return any(result is not None for result in results.values())
                
        except Exception as e:
            self.logger.error(f"Error broadcasting message: {e}")
            return False
    
    async def give_item_to_player(self, steam_id: str, item_command: str, 
                                quantity: int = 1, server_name: Optional[str] = None) -> bool:
        """Give item to player on server(s)"""
        try:
            # Format the command with player Steam ID and quantity
            command = item_command.format(steam_id=steam_id, quantity=quantity)
            
            if server_name:
                # Give item on specific server
                result = await self.execute_command(server_name, command)
                return result is not None
            else:
                # Give item on all servers
                results = await self.execute_command_all_servers(command)
                return any(result is not None for result in results.values())
                
        except Exception as e:
            self.logger.error(f"Error giving item to player {steam_id}: {e}")
            return False
    
    async def kick_player(self, steam_id: str, reason: str = "", 
                         server_name: Optional[str] = None) -> bool:
        """Kick player from server(s)"""
        try:
            command = f'kickplayer {steam_id}'
            if reason:
                command += f' "{reason}"'
            
            if server_name:
                result = await self.execute_command(server_name, command)
                return result is not None
            else:
                results = await self.execute_command_all_servers(command)
                return any(result is not None for result in results.values())
                
        except Exception as e:
            self.logger.error(f"Error kicking player {steam_id}: {e}")
            return False
    
    def disconnect_all(self) -> None:
        """Disconnect all RCON connections"""
        for connection in self.connections.values():
            try:
                connection.disconnect()
            except:
                pass
        self.connections.clear()
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all RCON connections"""
        results = {}
        servers = self.get_servers()
        
        for server in servers:
            server_name = server.get('name')
            if server_name:
                try:
                    connection = await self.get_connection(server_name)
                    if connection:
                        # Test with a simple command
                        result = await connection.execute_command("version")
                        results[server_name] = result is not None
                    else:
                        results[server_name] = False
                except Exception:
                    results[server_name] = False
        
        return results
