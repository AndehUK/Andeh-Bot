# Core Imports
import os
import shutil

# Third Party Imports
import dotenv

DEFAULT_TOKEN = "YOUR_BOT_TOKEN"
DEFAULT_DB_URL = "mysql://username:password@host:3306/database"

if not os.path.exists(".env"):
    shutil.copy(".example.env", ".env")

dotenv.load_dotenv()


class Config:
    """Type-safe environment configuration"""

    bot_token: str
    database_url: str

    def __init__(self) -> None:
        if not os.environ["BOT_TOKEN"] or os.environ["BOT_TOKEN"] == DEFAULT_TOKEN:
            raise ValueError("BOT_TOKEN is not set")
        elif (
            not os.environ["DATABASE_URL"]
            or os.environ["DATABASE_URL"] == DEFAULT_DB_URL
        ):
            raise ValueError("DATABASE_URL is not set")

        self.bot_token = os.environ["BOT_TOKEN"]
        self.database_url = os.environ["DATABASE_URL"]

    def reload(self) -> None:
        dotenv.load_dotenv()
        self.__init__()
