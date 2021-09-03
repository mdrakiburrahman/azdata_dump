# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from knack.commands import CommandGroup
from knack.output import format_table
from azdata.cli.commands.arc.client import (beget, beget_no_check_auth)
from azdata.cli.commands.arc.validators import *
from knack.output import format_table


def load_command_table(self, _):
    # Hide `bdc` command for the immediate.

    with CommandGroup(self, 'arc dc',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget_no_check_auth) as g:
        g.command('create', 'dc_create')

    with CommandGroup(self, 'arc dc',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget) as g:
        g.command('endpoint list', 'dc_endpoint_list', output=format_table)

    with CommandGroup(self, 'arc dc',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget) as g:
        g.command('config show', 'dc_config_show')

    with CommandGroup(self, 'arc dc',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget) as g:
        g.command('status show', 'dc_status_show')

    with CommandGroup(self, 'arc dc',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget_no_check_auth) as g:
        g.command('delete', 'dc_delete')

    with CommandGroup(self, 'arc dc',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget) as g:
        g.command('export', 'dc_export')

    with CommandGroup(self, 'arc dc',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget_no_check_auth) as g:
        g.command('upload', 'dc_upload')

    with CommandGroup(self, 'arc dc config',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget_no_check_auth) as g:
        g.command('list', 'dc_config_list')
        g.command('init', 'dc_config_init')

    with CommandGroup(self, 'arc dc config',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget_no_check_auth) as g:
        g.command('patch', 'dc_config_patch')
        g.command('add', 'dc_config_add')
        g.command('replace', 'dc_config_replace')
        g.command('remove', 'dc_config_remove')

    with CommandGroup(self, 'arc dc debug',
                      'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget_no_check_auth) as g:
        g.command('copy-logs', 'dc_debug_copy_logs', validator=validate_copy_logs)
        g.command('dump', 'dc_debug_dump')

    with CommandGroup(self, 'arc', 'azdata.cli.commands.arc.custom#{}',
                      client_factory=beget) as g:
        g.command('resource-kind list', 'arc_resource_kind_list')
        g.command('resource-kind get', 'arc_resource_kind_get')
