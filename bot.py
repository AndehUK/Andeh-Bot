from __future__ import annotations

# Core Imports
import traceback
from typing import Any, Tuple

# Third Party Imports
import aiohttp
import discord
from discord.ext import commands
from prisma import Prisma

# Local Imports
from cogs import COGS
from lib.env import Config
from lib.logger import Logger
from lib.regex import RegEx
from lib.tree import Tree


class AndehBot(commands.Bot):
    """The main Discord Bot class"""

    _is_ready: bool
    config: Config
    db: Prisma
    guilds_to_sync: Tuple[int, ...]
    logger: Logger
    regex: RegEx
    session: aiohttp.ClientSession
    sync_on_ready: bool

    def __init__(
        self, *, sync_on_ready: bool = False, guilds_to_sync: Tuple[int, ...] = ()
    ) -> None:
        self._is_ready = False
        self.guilds_to_sync = guilds_to_sync
        self.logger = Logger("AndehBot", console=True)
        self.regex = RegEx()
        self.sync_on_ready = sync_on_ready

        try:
            self.config = Config()
        except ValueError as e:
            self.logger.error(str(e))
            exit(1)

        super().__init__(
            command_prefix="!",
            description="Discord Bot for Andeh's Arsenal",
            intents=discord.Intents.all(),  # All until we know exactly what intents we need
            tree_cls=Tree,
        )

        # Setting this decides who can use owner-only commands such as jsk
        self.owner_ids = {957437570546012240}

    async def setup_hook(self) -> None:
        """
        A coroutine to be called to setup the bot after logging in
        but before we connect to the Discord Websocket.

        Mainly used to load our cogs / extensions.
        """

        try:
            from jishaku.cog import async_setup as jsk
        except ImportError:
            self.logger.error("Jishaku is not installed.")
            exit(1)

        # Jishaku is our debugging tool installed from PyPi
        await jsk(self)
        loaded_cogs = 1

        # Looping through and loading our local extensions (cogs)
        for cog in COGS:
            try:
                await self.load_extension(cog)
                loaded_cogs += 1
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"{type(e)} Exception in loading {cog}\n{tb}")
                continue

        self.logger.info(f"Successfully loaded {loaded_cogs}/{len(COGS)+1} cogs!")

    async def on_ready(self) -> None:
        """
        A coroutine to be called every time the bot connects to the
        Discord Websocket.

        This can be called multiple times if the bot disconnects and
        reconnects, hence why we create the `_is_ready` class variable
        to prevent functionality that should only take place on our first
        start-up from happening again.
        """
        if self._is_ready:
            # Bot has disconnected and reconnected to the Websocket.
            return self.logger.critical("Bot reconnected to Discord Gateway.")

        # Our first time connecting to the Discord Websocket this session
        if self.sync_on_ready and len(self.guilds_to_sync):
            # If we prompted the bot to sync our app commands through command flags
            if -1 in self.guilds_to_sync:
                # Sync all global app commands
                try:
                    global_synced = await self.tree.sync()
                    self.logger.info(f"Synced {len(global_synced)} global commands!")
                except:
                    tb = traceback.format_exc()
                    self.logger.critical(
                        f"Failed to sync global application commands!\n{tb}"
                    )
            for guild_id in [g for g in self.guilds_to_sync if g != -1]:
                # Syncing guild-specific app commands
                try:
                    guild_synced = await self.tree.sync(
                        guild=discord.Object(guild_id, type=discord.Guild)
                    )
                    self.logger.info(
                        f"Synced {len(guild_synced)} commands for guild ({guild_id})"
                    )
                except:
                    tb = traceback.format_exc()
                    self.logger.critical(
                        f"Failed to sync commands for guild ({guild_id})\n{tb}"
                    )

        # The bot is now fully setup and ready!
        self._is_ready = True
        self.logger.info(f"{self.user} is now online!")

    async def start(self, *args: Any, reconnect: bool = True) -> None:
        """
        Logs in the client with the specified credentials and calls the :meth:`setup_hook` method
        then creates a websocket connection and lets the websocket listen to messages / events
        from Discord.
        """
        self.logger.info("Starting Bot...")
        async with aiohttp.ClientSession() as self.session, Prisma() as self.db:
            # Initialises our ClientSession and Database connection as bot variables.
            try:
                await super().start(self.config.bot_token, reconnect=True)
            finally:
                self.logger.info("Shutdown Bot.")
