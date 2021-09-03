# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext
    from azdata.cli.commands.pgcli import _

    with ArgumentsContext(self, "postgres shell") as arg_context:
        arg_context.argument(
            "host",
            options_list=["--host"],  # removed -h, --version, --help
            help=_("Host address of the postgres database."),
        )
        arg_context.argument(
            "port",
            options_list=["--port", "-p"],
            type=int,
            help=_("Port number at which the postgres instance is listening."),
        )
        arg_context.argument(
            "username",
            options_list=["--username", "-u"],
            help=_("Username to connect to the postgres database."),
        )
        arg_context.argument(
            "password",
            action="store_true",
            options_list=["--password", "-w"],
            help=_("Force password prompt."),
        )
        arg_context.argument(
            "no_password",
            action="store_true",
            options_list=["--no-password"],
            help=_("Never prompt for password."),
        )
        arg_context.argument(
            "single_connection",
            action="store_true",
            options_list=["--single-connection"],
            help=_("Do not use a separate connection for completions."),
        )
        arg_context.argument(
            "dbname",
            options_list=["--dbname", "-d"],
            help=_("Database name to connect to."),
        )
        arg_context.argument(
            "pgclirc",
            options_list=["--pgclirc"],
            help=_("Location of pgclirc file."),
        )
        arg_context.argument(
            "dsn",
            options_list=["--dsn"],
            help=_(
                "Use DSN configured into the [alias_dsn] section of pgclirc "
                "file."
            ),
        )
        arg_context.argument(
            "list_dsn",
            action="store_true",
            options_list=["--list-dsn"],
            help=_(
                "List of DSN configured into the [alias_dsn] section of "
                "pgclirc file."
            ),
        )
        arg_context.argument(
            "row_limit",
            options_list=["--row-limit"],
            type=int,
            help=_(
                "Set threshold for row limit prompt. Use 0 to disable prompt."
            ),
        )
        arg_context.argument(
            "less_chatty",
            action="store_true",
            options_list=["--less-chatty"],
            help=_("Skip intro on startup and goodbye on exit."),
        )
        arg_context.argument(
            "prompt",
            options_list=["--prompt"],
            help=_('Prompt format (Default: "\\u@\h:\d> ").'),
        )
        arg_context.argument(
            "prompt_dsn",
            options_list=["--prompt-dsn"],
            help=_(
                "Prompt format for connections using DSN aliases (Default: "
                '"\\u@\h:\d> ").'
            ),
        )
        arg_context.argument(
            "list",
            action="store_true",
            options_list=["--list", "-l"],
            help=_("List available databases, then exit."),
        )
        arg_context.argument(
            "auto_vertical_output",
            action="store_true",
            options_list=["--auto-vertical-output"],
            help=_(
                "Automatically switch to vertical output mode if the result "
                "is wider than the terminal width."
            ),
        )
        arg_context.argument(
            "warn",
            action="store_true",
            options_list=["--warn"],
            help=_("Warn before running a destructive query."),
        )
        arg_context.argument(
            "no_warn",
            action="store_true",
            options_list=["--no-warn"],
            help=_("Warn before running a destructive query."),
        )

    with ArgumentsContext(self, "postgres query") as arg_context:
        arg_context.argument(
            "dbname",
            options_list=["--dbname", "-d"],
            required=False,
            help=_("Database to run query in."),
        )
        arg_context.argument(
            "query",
            options_list=["--q", "-q"],
            help=_("PostgreSQL query to execute."),
        )
        arg_context.argument(
            "host",
            options_list=["--host"],
            help=_("Host address of the postgres database."),
        )
        arg_context.argument(
            "port",
            options_list=["--port", "-p"],
            type=int,
            help=_("Port number at which the postgres instance is listening."),
        )
        arg_context.argument(
            "username",
            options_list=["--username", "-u"],
            help=_("Username to connect to the postgres database."),
        )
