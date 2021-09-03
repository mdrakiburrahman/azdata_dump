# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.exceptions import CliError, ApiError
from azdata.cli.core.logging import get_logger
from azdata.cli.core.prompt import prompt
from azdata.cli.commands.pgcli.exceptions import PgcliError
from azdata.cli.commands.pgcli.util import (
    prompt_postgres_username,
    prompt_postgres_password,
)
from knack.prompting import NoTTYException

import os
import io

logger = get_logger(__name__)


def postgres_shell(
    client,
    dbname=None,
    host=None,
    port=None,
    password=None,
    no_password=None,
    single_connection=None,
    username=None,
    pgclirc=None,
    dsn=None,
    list_dsn=None,
    row_limit=None,
    less_chatty=None,
    prompt=None,
    prompt_dsn=None,
    list=None,
    auto_vertical_output=None,
    warn=None,
    no_warn=None,
):
    """
    ```sh
    azdata postgres shell <interactive>
    ```
    """
    try:
        if not username:
            username = os.getenv("PGUSER")
            username = username or prompt_postgres_username()

        # assert password
        if not os.getenv("PGPASSWORD") and (not no_password and not password):
            os.environ["PGPASSWORD"] = prompt_postgres_password()
            no_password = True  # no second prompt from pglci

        client.run_shell(
            dbname=dbname,
            host=host,
            port=port,
            password=password,
            no_password=no_password,
            single_connection=single_connection,
            username=username,
            pgclirc=pgclirc,
            dsn=dsn,
            list_dsn=list_dsn,
            row_limit=row_limit,
            less_chatty=less_chatty,
            prompt=prompt,
            prompt_dsn=prompt_dsn,
            list=list,
            auto_vertical_output=auto_vertical_output,
            warn=warn,
            no_warn=no_warn,
        )

    except io.UnsupportedOperation as ex:
        raise NoTTYException("Command must be ran in interactive mode.")
    except NoTTYException as ex:
        raise CliError(ex)
    except PgcliError as ex:
        raise CliError(ex)


def postgres_query(
    client, query, host="localhost", dbname=None, port=5432, username=None
):
    """
    ```sh
    azdata postgres query -q "SELECT * FROM x" <interactive>
    azdata postgres query --username admin
                          --dbname database-name
                          --host localhost
                          -q "SELECT * FROM x"
    ```
    """
    try:
        if not username:
            username = os.getenv("PGUSER")
            username = username or prompt_postgres_username()

        # assert password
        if not os.getenv("PGPASSWORD"):
            password = prompt_postgres_password()

        return client.run_query(host, port, dbname, username, password, query)
    except NoTTYException as ex:
        raise CliError(ex)
    except ApiError:
        msg = (
            'Could not translate host name from "endpoint" to address: '
            "nodename nor servname provided, or not known."
        )
        raise CliError(msg)
    except PgcliError as ex:
        raise CliError(ex)
