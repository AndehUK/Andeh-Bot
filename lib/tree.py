from __future__ import annotations

# Core Imports
from typing import TYPE_CHECKING

# Third Party Packages
import discord
from discord import app_commands

# Type Imports
if TYPE_CHECKING:
    from bot import AndehBot


class Tree(app_commands.CommandTree):
    """
    Subclass of :class:`discord.app_commands.CommandTree` that adds a dispatch to our
    custom `on_app_command_error` event.
    """

    def __init__(self, client: AndehBot, *, fallback_to_global: bool = True) -> None:
        super().__init__(client=client, fallback_to_global=fallback_to_global)

    async def on_error(
        self, itr: discord.Interaction, error: app_commands.AppCommandError, /
    ) -> None:
        """Coroutine that is called when an app command raises an error"""
        await super().on_error(itr, error)
        return itr.client.dispatch("app_command_error", itr, error)  # Custom bot event
