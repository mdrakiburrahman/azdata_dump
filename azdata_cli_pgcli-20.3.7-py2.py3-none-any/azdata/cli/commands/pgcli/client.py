# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.clients.cli_client import CliClient
from azdata.cli.core.configuration import Configuration
from azdata.cli.commands.pgcli.exceptions import PgcliError

import os

__all__ = ["beget"]


def beget(_):
    """Client factory"""
    return PgcliClientMixin()


class PgcliClientMixin(CliClient):
    def __init__(self, check_auth=False, check_eula=True):
        """
        :param check_auth: Set to `True` to have this command enforce
                           authentication before running.
        :param check_auth: Set to `True` to have this command enforce eula
                           acceptance before running.
        """

        super(PgcliClientMixin, self).__init__(
            check_auth=check_auth, check_eula=check_eula
        )

    def run_shell(
        self,
        dbname=None,
        host=None,
        port=None,
        password=None,
        no_password=None,
        single_connection=None,
        username=None,
        pgclirc=None,
        dsn=None,
        row_limit=None,
        less_chatty=None,
        prompt=None,
        prompt_dsn=None,
        list=None,
        auto_vertical_output=None,
        list_dsn=None,
        warn=None,
        no_warn=None,
    ):

        from pgcli.main import cli
        import shlex
        import inspect

        args = locals()
        command = []

        # normalize pgcli config dir location
        default_config_dir = os.path.join(
            Configuration().CLI_CONFIG_DIR, "pgcli", "config"
        )
        psqlrc = os.getenv("PSQLRC")
        pgclirc = pgclirc or os.getenv("PGCLIRC")
        os.environ["PSQLRC"] = psqlrc or default_config_dir
        os.environ["PGCLIRC"] = pgclirc or default_config_dir

        # convert function arguments and values to command  [--arg value]
        for arg in inspect.signature(self.run_shell).parameters:
            if arg in args and args[arg]:
                command.append("--" + arg.replace("_", "-"))
                if not isinstance(args[arg], bool):
                    command.append(args[arg])

        cli(shlex.split(" ".join(command)))

    def run_query(self, host, port, dbname, username, password, query):
        import psycopg2

        connection = None

        try:
            result = []

            connection = psycopg2.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=dbname,
            )
            connection.autocommit = True

            cursor = connection.cursor()
            cursor.execute(query)
            cursor_results = cursor.fetchall()

            for row in cursor_results:
                obj = {}
                for column_index in range(len(cursor_results[0])):
                    column_metadata_name = cursor.description[column_index][0]
                    obj[column_metadata_name] = row[column_index]

                result.append(obj)
            return result
        except (
            psycopg2.errors.SyntaxError,
            psycopg2.OperationalError,
            Exception,
        ) as e:
            raise PgcliError(e)
        finally:
            if connection:
                connection.close()
