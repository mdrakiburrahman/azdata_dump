# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.i18n import translate
from azdata.cli.core.commands import CliCommandsLoader

_ = translate('azdata.cli.commands.arc')
import azdata.cli.commands.arc.help  # pylint: disable=W0611,C0413

__all__ = ['_', 'COMMAND_LOADER_CLS']


class ArcCommandsLoader(CliCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(ArcCommandsLoader, self).__init__(cli_ctx=cli_ctx)

    def load_command_table(self, args):
        from azdata.cli.commands.arc.command_table import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azdata.cli.commands.arc.arguments import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ArcCommandsLoader