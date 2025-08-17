"""
Discord bot commands for the Ark shop system
"""

import discord
from discord.ext import commands
import asyncio

def setup_commands(bot):
    """Setup all bot commands"""
    
    @bot.command(name='balance', aliases=['bal', 'points'])
    async def balance(ctx, member: discord.Member = None):
        """Check point balance"""
        target = member or ctx.author
        
        try:
            balance = await bot.economy.get_balance(str(target.id))
            embed = discord.Embed(
                title="💰 Point Balance",
                description=f"{target.display_name} has **{balance:,}** points",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            bot.logger.error(f"Error getting balance: {e}")
            await ctx.send("❌ Error retrieving balance.")
    
    @bot.command(name='shop')
    async def shop(ctx, page: int = 1):
        """Display the shop"""
        try:
            items = await bot.shop.get_shop_items(page=page)
            
            if not items:
                await ctx.send("🛒 The shop is currently empty.")
                return
            
            embed = discord.Embed(
                title="🛒 Ark Item Shop",
                description="Use `!buy <item_id>` to purchase items",
                color=0x0099ff
            )
            
            for item in items:
                embed.add_field(
                    name=f"{item['name']} (ID: {item['id']})",
                    value=f"💰 {item['price']:,} points\n📝 {item['description']}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error displaying shop: {e}")
            await ctx.send("❌ Error loading shop.")
    
    @bot.command(name='buy')
    async def buy(ctx, item_id: int, quantity: int = 1):
        """Buy an item from the shop"""
        try:
            player_id = str(ctx.author.id)
            
            # Check if item exists
            item = await bot.shop.get_item(item_id)
            if not item:
                await ctx.send("❌ Item not found.")
                return
            
            # Check balance
            balance = await bot.economy.get_balance(player_id)
            total_cost = item['price'] * quantity
            
            if balance < total_cost:
                await ctx.send(f"❌ Insufficient points. You need {total_cost:,} points but have {balance:,}.")
                return
            
            # Process purchase
            success = await bot.shop.purchase_item(player_id, item_id, quantity)
            
            if success:
                embed = discord.Embed(
                    title="✅ Purchase Successful!",
                    description=f"You purchased {quantity}x {item['name']} for {total_cost:,} points",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Purchase failed. Please try again.")
                
        except Exception as e:
            bot.logger.error(f"Error processing purchase: {e}")
            await ctx.send("❌ Error processing purchase.")
    
    @bot.command(name='give')
    @commands.has_permissions(administrator=True)
    async def give_points(ctx, member: discord.Member, amount: int, *, reason="Admin grant"):
        """Give points to a player (Admin only)"""
        try:
            await bot.economy.add_points(str(member.id), amount, reason)
            
            embed = discord.Embed(
                title="💰 Points Given",
                description=f"Gave {amount:,} points to {member.display_name}",
                color=0x00ff00
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error giving points: {e}")
            await ctx.send("❌ Error giving points.")
    
    @bot.command(name='transfer', aliases=['send'])
    async def transfer_points(ctx, member: discord.Member, amount: int):
        """Transfer points to another player"""
        try:
            sender_id = str(ctx.author.id)
            receiver_id = str(member.id)
            
            if sender_id == receiver_id:
                await ctx.send("❌ You cannot transfer points to yourself.")
                return
            
            # Check sender balance
            balance = await bot.economy.get_balance(sender_id)
            if balance < amount:
                await ctx.send(f"❌ Insufficient points. You have {balance:,} points.")
                return
            
            # Process transfer
            success = await bot.economy.transfer_points(sender_id, receiver_id, amount)
            
            if success:
                embed = discord.Embed(
                    title="💸 Points Transferred",
                    description=f"Transferred {amount:,} points to {member.display_name}",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Transfer failed.")
                
        except Exception as e:
            bot.logger.error(f"Error transferring points: {e}")
            await ctx.send("❌ Error processing transfer.")
    
    @bot.command(name='leaderboard', aliases=['lb', 'top'])
    async def leaderboard(ctx):
        """Show points leaderboard"""
        try:
            top_players = await bot.economy.get_leaderboard(limit=10)
            
            if not top_players:
                await ctx.send("📊 No players found.")
                return
            
            embed = discord.Embed(
                title="🏆 Points Leaderboard",
                color=0xffd700
            )
            
            for i, (player_id, balance) in enumerate(top_players, 1):
                try:
                    user = bot.get_user(int(player_id))
                    name = user.display_name if user else f"User {player_id}"
                except:
                    name = f"User {player_id}"
                
                embed.add_field(
                    name=f"{i}. {name}",
                    value=f"{balance:,} points",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error showing leaderboard: {e}")
            await ctx.send("❌ Error loading leaderboard.")
