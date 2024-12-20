from importlib import resources

from duckdb import DuckDBPyConnection, DuckDBPyRelation, connect

import challenge.sql


def get_connection() -> DuckDBPyConnection:
    con = connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    return con


def run_ddb_query(
    fname: str, con: DuckDBPyConnection, params: object | None = None
) -> DuckDBPyRelation:
    inp_file = resources.files(challenge.sql) / fname
    query = inp_file.read_text()
    return con.sql(query, params=params)
