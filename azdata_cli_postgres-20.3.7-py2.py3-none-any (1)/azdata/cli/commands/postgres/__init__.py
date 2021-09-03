# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.i18n import translate
from azdata.cli.core.commands import CliCommandsLoader

_ = translate('azdata.cli.commands.postgres')
import azdata.cli.commands.postgres.help  # pylint: disable=W0611,C0413

__all__ = ['_', 'COMMAND_LOADER_CLS']


class PostgresCommandsLoader(CliCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(PostgresCommandsLoader, self).__init__(cli_ctx=cli_ctx)

    def load_command_table(self, args):
        from azdata.cli.commands.postgres.command_table import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azdata.cli.commands.postgres.arguments import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = PostgresCommandsLoader