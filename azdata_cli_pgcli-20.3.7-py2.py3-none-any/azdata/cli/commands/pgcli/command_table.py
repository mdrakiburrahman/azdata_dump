# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.commands import CliCommandGroup
from azdata.cli.commands.pgcli.client import beget


def load_command_table(self, _):
    operations = "azdata.cli.commands.pgcli.custom#{}"

    with CliCommandGroup(
        self, "postgres", operations, client_factory=beget
    ) as g:
        g.command("shell", "postgres_shell", is_preview=True)

    with CliCommandGroup(
        self, "postgres", operations, client_factory=beget
    ) as g:
        g.command("query", "postgres_query", output="table", is_preview=True)
