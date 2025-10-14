"""Module for database adapter handling."""

from ..adapt_handler.adapt_handler import AdaptHandler


class BisslogDB(AdaptHandler):
    """Database adapter handler.

    This class extends `AdaptHandler` to provide a standardized way
    to interact with the main database.

    Inherits
    --------
    AdaptHandler : Provides adapter handling capabilities."""


# Global instance of the database adapter
bisslog_db = BisslogDB("main-database")
