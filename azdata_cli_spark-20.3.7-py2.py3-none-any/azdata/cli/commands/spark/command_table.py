# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from knack.commands import CommandGroup
from azdata.cli.commands.spark import client


def load_command_table(self, _):
    with CommandGroup(self, 'bdc spark', 'azdata.cli.commands.spark.custom#{}',
                      client_factory=client.beget) as g:
        g.command('session create', 'spark_session_create')
        g.command('session list', 'spark_session_list')
        g.command('session info', 'spark_session_info')
        g.command('session log', 'spark_session_log')
        g.command('session state', 'spark_session_state')
        g.command('session delete', 'spark_session_delete')
        g.command('statement list', 'spark_statement_list')
        g.command('statement create', 'spark_statement_create')
        g.command('statement info', 'spark_statement_info')
        g.command('statement cancel', 'spark_statement_cancel')
        g.command('batch create', 'spark_batch_create')
        g.command('batch list', 'spark_batch_list')
        g.command('batch info', 'spark_batch_info')
        g.command('batch log', 'spark_batch_log')
        g.command('batch state', 'spark_batch_state')
        g.command('batch delete', 'spark_batch_delete')


