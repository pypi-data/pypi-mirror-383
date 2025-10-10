import logging
from typing import Any

from psycopg import sql
from database_wrapper import DBWrapperAsync

from .db_wrapper_pgsql_mixin import DBWrapperPgSQLMixin
from .connector import PgCursorTypeAsync


class DBWrapperPgSQLAsync(DBWrapperPgSQLMixin, DBWrapperAsync):
    """
    Async database wrapper for postgres

    This is meant to be used in async environments.
    """

    db_cursor: PgCursorTypeAsync | None
    """ Async PostgreSQL cursor object """

    #######################
    ### Class lifecycle ###
    #######################

    # Meta methods
    # We are overriding the __init__ method for the type hinting
    def __init__(
        self,
        db_cursor: PgCursorTypeAsync | None = None,
        logger: logging.Logger | None = None,
    ):
        """
        Initializes a new instance of the DBWrapper class.

        Args:
            db_cursor (PgCursorTypeAsync): The PostgreSQL database cursor object.
            logger (logging.Logger, optional): The logger object. Defaults to None.
        """
        super().__init__(db_cursor, logger)

    ###############
    ### Setters ###
    ###############

    def set_db_cursor(self, db_cursor: PgCursorTypeAsync | None) -> None:
        """
        Updates the database cursor object.

        Args:
            db_cursor (PgCursorTypeAsync): The new database cursor object.
        """
        super().set_db_cursor(db_cursor)

    ######################
    ### Helper methods ###
    ######################

    def log_query(
        self,
        cursor: PgCursorTypeAsync,
        query: sql.SQL | sql.Composed,
        params: tuple[Any, ...],
    ) -> None:
        """
        Logs the given query and parameters.

        Args:
            cursor (Any): The database cursor.
            query (Any): The query to log.
            params (tuple[Any, ...]): The parameters to log.
        """
        query_string = query.as_string(self.db_cursor)
        logging.getLogger().debug(f"Query: {query_string} with params: {params}")
