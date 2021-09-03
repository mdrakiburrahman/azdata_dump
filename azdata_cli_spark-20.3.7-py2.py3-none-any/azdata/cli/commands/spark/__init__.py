# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.i18n import translate
from azdata.cli.core.commands import CliCommandsLoader

# pylint: disable=unused-import
_ = translate('azdata.cli.commands.spark')
import azdata.cli.commands.spark.help


class SparkCommandsLoader(CliCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(SparkCommandsLoader, self).__init__(cli_ctx=cli_ctx)

    def load_command_table(self, args):
        from azdata.cli.commands.spark.command_table import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azdata.cli.commands.spark.arguments import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = SparkCommandsLoader
