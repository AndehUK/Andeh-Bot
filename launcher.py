# Core Imports
import asyncio
import os
from typing import Tuple

# Third Party Packages
import click
import dotenv

# Local Imports
from bot import AndehBot


@click.command()
@click.option("--sync", is_flag=True, help="Flag to trigger app command syncing")
@click.option(
    "--guilds",
    multiple=True,
    type=int,
    default=(-1,),
    show_default=True,
    help="Provide one or more guild IDs to sync app commands to. Default is -1 (Global commands).",
)
def cli(sync: bool, guilds: Tuple[int, ...]) -> None:
    """
    CLI built into our launcher command that allows us to specify whether we want to
    sync our app commands on launch.
    """
    asyncio.run(main(sync, guilds))


async def main(sync: bool, guilds: Tuple[int, ...]) -> None:
    # Load our environment variables
    dotenv.load_dotenv()

    # Initialise and start our bot instance
    bot = AndehBot(sync_on_ready=sync, guilds_to_sync=guilds)
    await bot.start(os.environ["BOT_TOKEN"])


if __name__ == "__main__":
    cli()
