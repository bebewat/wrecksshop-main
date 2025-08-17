# WrecksShop - Ark Survival: Ascended Discord Bot

## Project Overview
WrecksShop is a comprehensive Discord bot for managing in-game item shops for Ark Survival: Ascended servers. The bot features a Python-based GUI application that compiles to a standalone .exe for easy management.

## Core Features
- Discord bot integration with shop management
- RCON server communication for Ark servers
- Point-based economy system with playtime rewards
- SQL database integration for persistent data
- Tip4Serv integration for donation handling
- Comprehensive GUI for all management functions

## Architecture
- **Frontend**: Python tkinter GUI (compiles to .exe)
- **Backend**: Discord.py bot with asyncio
- **Database**: SQLite/PostgreSQL support
- **Game Integration**: RCON protocol for Ark servers
- **External APIs**: Tip4Serv integration

## GUI Structure
### Main Tabs
- Config: Bot tokens, channels, reward settings
- Servers: RCON server management
- SQL Databases: Database configuration
- Shop: Item management and categories
- Library: GitHub item/dino data integration
- Admin Roles: Permission management
- Discounts: Role and event-based discounts
- Control: Bot status and operations

### Persistent Bottom Menu
- Start/Stop: Bot toggle controls
- Logs: Activity logging and error tracking
- GitHub: Repository link
- Discord: Support server link

## Technical Stack
- Python 3.11+
- discord.py for bot functionality
- tkinter for GUI
- aiorcon for Ark RCON communication
- SQLAlchemy for database ORM
- requests for external API calls
- PyInstaller for .exe compilation

## Development Status
- Project initialized
- Basic structure planned
- Ready for implementation

## User Preferences
- Bot name: WrecksShop
- Branding: Purple/teal color scheme with dinosaur theme
- Deployment: Standalone .exe application
- Target: Ark Survival: Ascended servers

## Recent Changes
- 2025-08-17: Project created and documented
- Logo provided: WrecksShop branding with dinosaur theme