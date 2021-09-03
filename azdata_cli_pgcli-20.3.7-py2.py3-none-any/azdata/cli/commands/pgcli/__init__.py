# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.i18n import translate
from azdata.cli.core.commands import CliCommandsLoader
from azdata.cli.commands.pgcli.command_table import load_command_table

__all__ = ["_", "COMMAND_LOADER_CLS"]

_ = translate("azdata.cli.commands.pgcli")
"""
To internationalize strings in this CLI command.
See `help.py` for example.
"""


class PgcliCommandsLoader(CliCommandsLoader):
    def __init__(self, cli_ctx=None):
        # pylint: disable=W0611,C0413
        import azdata.cli.commands.pgcli.help  # noqa: F401

        super(PgcliCommandsLoader, self).__init__(cli_ctx=cli_ctx)

    def load_command_table(self, args):
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azdata.cli.commands.pgcli.arguments import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = PgcliCommandsLoader
