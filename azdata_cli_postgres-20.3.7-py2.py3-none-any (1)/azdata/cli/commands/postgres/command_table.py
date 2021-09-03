# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.commands import CliCommandGroup
from azdata.cli.commands.postgres import client
from azdata.cli.commands.postgres.validators import *
from azdata.cli.commands.postgres.util import hierarchical_output
from knack.output import format_table


def load_command_table(self, _):
    # ------------------------------------------------------------------------------
    # Server Commands
    # ------------------------------------------------------------------------------
    with CliCommandGroup(self, 'arc postgres server', 'azdata.cli.commands.postgres.custom#{}',
                         client_factory=client.beget) as g:
        g.command('create', 'arc_postgres_server_create')
        g.command('delete', 'arc_postgres_server_delete')
        g.command('show', 'arc_postgres_server_show')
        g.command('list', 'arc_postgres_server_list', output=format_table)
        g.command('edit', 'arc_postgres_server_edit')
        # g.command('restart', 'arc_postgres_server_restart')

    with CliCommandGroup(self, 'arc postgres server config', 'azdata.cli.commands.postgres.custom#{}',
                         client_factory=client.beget) as g:
        g.command('init', 'arc_postgres_server_config_init')

    with CliCommandGroup(self, 'arc postgres server config', 'azdata.cli.commands.postgres.custom#{}',
                         client_factory=client.beget_no_check_auth) as g:
        g.command('patch', 'arc_postgres_server_config_patch')
        g.command('add', 'arc_postgres_server_config_add')
        g.command('replace', 'arc_postgres_server_config_replace')
        g.command('remove', 'arc_postgres_server_config_remove')

    # ------------------------------------------------------------------------------
    # Endpoint Commands
    # ------------------------------------------------------------------------------
    with CliCommandGroup(self, 'arc postgres', 'azdata.cli.commands.postgres.custom#{}',
                         client_factory=client.beget) as g:
        g.command('endpoint list', 'arc_postgres_endpoint_list', output=hierarchical_output)

    # ------------------------------------------------------------------------------
    # Backup Commands
    # ------------------------------------------------------------------------------
    with CliCommandGroup(self, 'arc postgres backup', 'azdata.cli.commands.postgres.custom#{}',
                      client_factory=client.beget) as g:
        g.command('create', 'arc_postgres_backup_create')
        g.command('delete', 'arc_postgres_backup_delete', validator=validate_backup_delete)
        g.command('restore', 'arc_postgres_backup_restore')
        g.command('list', 'arc_postgres_backup_list', output=format_table)

    # ------------------------------------------------------------------------------
    # Database Commands - Unimplemented
    # ------------------------------------------------------------------------------
    # with CliCommandGroup(self, 'arc postgres database', 'azdata.cli.commands.postgres.custom#{}',
    #                   client_factory=client.beget) as g:
    #     g.command('create', 'arc_postgres_database_create')
    #     g.command('delete', 'arc_postgres_database_delete')
    #     g.command('show', 'arc_postgres_database_show')
    #     g.command('list', 'arc_postgres_database_list')
    #     g.command('edit', 'arc_postgres_database_edit')

    # ------------------------------------------------------------------------------
    # Role Commands - Unimplemented
    # ------------------------------------------------------------------------------
    # with CliCommandGroup(self, 'arc postgres role', 'azdata.cli.commands.postgres.custom#{}',
    #                   client_factory=client.beget) as g:
    #     g.command('create', 'arc_postgres_role_create')
    #     g.command('delete', 'arc_postgres_role_delete')
    #     g.command('show', 'arc_postgres_role_show')
    #     g.command('list', 'arc_postgres_role_list')

    # ------------------------------------------------------------------------------
    # User Commands - Unimplemented
    # ------------------------------------------------------------------------------
    # with CliCommandGroup(self, 'arc postgres user', 'azdata.cli.commands.postgres.custom#{}',
    #                   client_factory=client.beget) as g:
    #     g.command('create', 'arc_postgres_user_create')
    #     g.command('delete', 'arc_postgres_user_delete')
    #     g.command('show', 'arc_postgres_user_show')
    #     g.command('list', 'arc_postgres_user_list')
    #     g.command('edit', 'arc_postgres_user_edit')

    # ------------------------------------------------------------------------------
    # Volume Commands - Unimplemented
    # ------------------------------------------------------------------------------
    # with CliCommandGroup(self, 'arc postgres volume', 'azdata.cli.commands.postgres.custom#{}',
    #                   client_factory=client.beget) as g:
    #     g.command('delete', 'arc_postgres_volume_delete')
    #     g.command('show', 'arc_postgres_volume_show')
    #     g.command('list', 'arc_postgres_volume_list')