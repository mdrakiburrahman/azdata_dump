# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from knack.help_files import helps
from azdata.cli.commands.pgcli import _


# pylint: disable=line-too-long
helps[
    "postgres"
] = """
    type: group
    short-summary: {short}
    long-summary: {long}    
""".format(
    short=_("Postgres query runner and interactive shell."),
    long=_(
        "Postgres query runner and interactive shell which acts as a proxy "
        "to Pgcli, a command line interface for Postgres with "
        "auto-completion and syntax highlighting."
    ),
)

# pylint: disable=line-too-long
helps[
    "postgres shell"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata postgres shell
        - name: {ex2}
          text: >
            azdata postgres shell --dbname <database> --username <username> --host <host>
        - name: {ex3}
          text: >
            azdata postgres shell --dbname postgres://user:passw0rd@example.com:5432/master 
""".format(
    short=_(
        "A command line shell interface for Postgres. See "
        "https://www.pgcli.com/"
    ),
    ex1=_("Example command line to start the interactive experience."),
    ex2=_("Example command line using a provided database and user"),
    ex3=_("Example command line to start using a full connection-string."),
)

helps[
    "postgres query"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata postgres query --host <host> --username <username> -q "SELECT * FROM information_schema.tables"
""".format(
    short=_(
        "The query command allows execution of PostgreSQL commands in a "
        "database session."
    ),
    ex1=_("List all tables in information_schema."),
)
