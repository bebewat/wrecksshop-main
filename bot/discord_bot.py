"""
Discord bot implementation for Ark Survival: Ascended shop system
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
from utils.config import Config
from utils.database import Database
from utils.logger import Logger
from bot.commands import setup_commands
from bot.economy import EconomyManager
from bot.shop import ShopManager

class ArkBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.config = Config()
        self.db = Database()
        self.logger = Logger()
        self.economy = EconomyManager(self.db)
        self.shop = ShopManager(self.db, self.economy)
        self.is_running = False
        
    async def setup_hook(self):
        """Setup hook called when bot starts"""
        await self.db.initialize()
        setup_commands(self)
        
        # Start reward task if enabled
        if self.config.get('reward_interval', 0) > 0:
            self.reward_task.start()
    
    async def on_ready(self):
        """Called when bot is ready"""
        self.logger.info(f'Bot logged in as {self.user.name}')
        self.is_running = True
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="Managing Ark Shop")
        )
    
    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author.bot:
            return
            
        # Log message for debugging
        self.logger.debug(f"Message from {message.author}: {message.content}")
        
        # Process commands
        await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            self.logger.error(f"Command error: {error}")
            await ctx.send(f"❌ An error occurred: {error}")
    
    @tasks.loop(minutes=1)
    async def reward_task(self):
        """Background task to give rewards based on playtime"""
        try:
            interval = self.config.get('reward_interval', 60)
            amount = self.config.get('reward_amount', 10)
            
            # Get active players from RCON servers
            active_players = await self.get_active_players()
            
            for player_id in active_players:
                await self.economy.add_points(player_id, amount, "Playtime reward")
                
        except Exception as e:
            self.logger.error(f"Error in reward task: {e}")
    
    async def get_active_players(self):
        """Get list of active players from all configured servers"""
        # This would integrate with RCON to get active players
        # For now, return empty list
        return []
    
    async def start_bot(self):
        """Start the Discord bot"""
        try:
            token = self.config.get('discord_bot_token')
            if not token:
                raise ValueError("Discord bot token not configured")
            
            await self.start(token)
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the Discord bot"""
        try:
            self.is_running = False
            if self.reward_task.is_running():
                self.reward_task.cancel()
            await self.close()
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
