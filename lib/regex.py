# Core Imports
import re
from functools import cached_property


class RegEx:
    """Class containing commonly-used regex patterns"""

    @cached_property
    def url_regex(self) -> re.Pattern[str]:
        """Regex Pattern that looks for a URL"""
        return re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
