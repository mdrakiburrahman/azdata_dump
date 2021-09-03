# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.commands import CliCommandGroup
from azdata.cli.commands.sqlmi.client import (beget, beget_no_check_auth)
from knack.output import format_table
from azdata.cli.commands.sqlmi.util import hierarchical_output


def load_command_table(self, _):
    operations = "azdata.cli.commands.sqlmi.custom#{}"

    with CliCommandGroup(
            self, "arc sql mi", operations, client_factory=beget
    ) as g:
        g.command("create", "arc_sql_mi_create")
        g.command("delete", "arc_sql_mi_delete")
        g.command("show", "arc_sql_mi_show")
        g.command('get-mirroring-cert', 'arc_sql_mi_getmirroringcert', output=hierarchical_output)
        g.command("list", "arc_sql_mi_list", output=format_table)
        g.command("edit", "arc_sql_mi_edit")

    with CliCommandGroup(
            self, 'arc sql endpoint', operations, client_factory=beget
    ) as g:
        g.command('list', 'arc_sql_endpoint_list', output=hierarchical_output)

    with CliCommandGroup(
            self, 'arc sql mi config', operations, client_factory=beget
    ) as g:
        g.command('init', 'arc_sql_mi_config_init')

    with CliCommandGroup(
            self, 'arc sql mi config', operations, client_factory=beget_no_check_auth
    ) as g:
        g.command('patch', 'arc_sql_mi_config_patch')
        g.command('add', 'arc_sql_mi_config_add')
        g.command('replace', 'arc_sql_mi_config_replace')
        g.command('remove', 'arc_sql_mi_config_remove')

    with CliCommandGroup(
            self, 'arc sql mi dag', operations, client_factory=beget
    ) as g:
        g.command('create', 'arc_sql_mi_dag_create', output=hierarchical_output)
        g.command('delete', 'arc_sql_mi_dag_delete', output=hierarchical_output)
        g.command('get', 'arc_sql_mi_dag_get', output=hierarchical_output)
