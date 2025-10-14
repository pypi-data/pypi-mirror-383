import logging
import textwrap
import typing

import psycopg2
import psycopg2.extras
import psycopg2.pool


class PostgresDatabase:
    def __init__(self, dsn: str, minconn: int = 1, maxconn: int = 1) -> None:
        self.log = logging.getLogger(__name__)
        self.p = psycopg2.pool.ThreadedConnectionPool(
            minconn, maxconn, dsn, cursor_factory=psycopg2.extras.DictCursor
        )
        psycopg2.extras.register_uuid()

    def b(self, sql: str, records: list[dict]) -> None:
        """Batch execute a query"""
        cnx = self.p.getconn()
        try:
            with cnx:
                with cnx.cursor() as cur:
                    self.log.debug(f"Batch query with {len(records)} parameter sets")
                    self.log.debug(textwrap.dedent(sql))
                    psycopg2.extras.execute_batch(cur, sql, records)
        finally:
            self.p.putconn(cnx)

    def q(self, sql: str, params: dict | None = None) -> list[dict]:
        """Execute a query and return all rows"""
        if params is None:
            params = {}
        cnx = self.p.getconn()
        try:
            with cnx:
                with cnx.cursor() as c:
                    self.log.debug(textwrap.dedent(c.mogrify(sql, params).decode()))
                    c.execute(sql, params)
                    return c.fetchall()
        finally:
            self.p.putconn(cnx)

    def q_one(self, sql: str, params: dict | None = None) -> dict | None:
        """Execute a query and return the first row, or None if there are no rows"""
        for r in self.q(sql, params):
            return r
        return None

    def q_val(self, sql: str, params: dict | None = None) -> typing.Any:  # noqa: ANN401
        """Execute a query and return the value in the first column of the first row,
        or None if there are no rows"""
        for r in self.q(sql, params):
            return r[0]
        return None

    def u(self, sql: str, params: dict | None = None) -> int:
        """Execute a statement and return the number of rows affected"""
        if params is None:
            params = {}
        cnx = self.p.getconn()
        try:
            with cnx:
                with cnx.cursor() as c:
                    self.log.debug(textwrap.dedent(c.mogrify(sql, params).decode()))
                    c.execute(sql, params)
                    return c.rowcount
        finally:
            self.p.putconn(cnx)
