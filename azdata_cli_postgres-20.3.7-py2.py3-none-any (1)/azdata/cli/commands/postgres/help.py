# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from knack.help_files import helps
from azdata.cli.commands.postgres import _

# pylint: disable=line-too-long
helps['arc postgres'] = """
    type: group
    short-summary: {short}
""".format(short=_('Create, delete, and managed Azure Arc enabled PostgreSQL Hyperscale server groups.'))

# ------------------------------------------------------------------------------
# Server Commands
# ------------------------------------------------------------------------------

helps['arc postgres server'] = """
    type: group
    short-summary: {short}
""".format(short=_('Manage Azure Arc enabled PostgreSQL Hyperscale server groups.'))

helps['arc postgres server create'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server create -n pg1
        - name: {ex2}
          text: >
            azdata arc postgres server create -n pg1 --engine-settings "key1=val1"

            azdata arc postgres server create -n pg1 --engine-settings 'key2=val2'
        - name: {ex3}
          text: >
            azdata arc postgres server create -n pg1 --volume-claim-mounts backup-pvc:backup
        - name: {ex4}
          text: >
            azdata arc postgres server create -n pg1 --memory-limit "coordinator=2Gi,w=1Gi" --workers 1
""".format(
    short=_('Create an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    long=_('To set the password of the server group, please set the environment variable AZDATA_PASSWORD'),
    ex1=_('Create an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex2=_('Create an Azure Arc enabled PostgreSQL Hyperscale server group '
            'with engine settings. Both below examples are valid.'),
    ex3=_('Create a PostgreSQL server group with volume claim mounts.'),
    ex4=_('Create a PostgreSQL server group with specific memory-limit for different node roles.'))

helps['arc postgres server edit'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server edit --src ./spec.json -n pg1
        - name: {ex2}
          text: >
            azdata arc postgres server edit -n pg1 --coordinator-engine-settings 'key2=val2'
        - name: {ex3}
          text: >
            azdata arc postgres server edit -n pg1 --engine-settings 'key1=val1' --replace-engine-settings
""".format(
    short=_('Edit the configuration of an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex1=_('Edit the configuration of an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex2=_('Edit an Azure Arc enabled PostgreSQL Hyperscale server group with engine settings for the coordinator node.'),
    ex3=_('Edits an Azure Arc enabled PostgreSQL Hyperscale server group and replaces existing ' 
            'engine settings with new setting key1=val1.'))

helps['arc postgres server delete'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server delete -n pg1
""".format(
    short=_('Delete an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex1=_('Delete an Azure Arc enabled PostgreSQL Hyperscale server group.'))

helps['arc postgres server show'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server show -n pg1
""".format(
    short=_('Show the details of an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex1=_('Show the details of an Azure Arc enabled PostgreSQL Hyperscale server group.'))

helps['arc postgres server list'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server list
""".format(
    short=_('List Azure Arc enabled PostgreSQL Hyperscale server groups.'),
    ex1=_('List Azure Arc enabled PostgreSQL Hyperscale server groups.'))

# helps['arc postgres server restart'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres server restart
# """.format(
#     short=_('Restart an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Restart an Azure Arc enabled PostgreSQL Hyperscale server group.'))

helps['arc postgres endpoint'] = """
    type: group
    short-summary: {short}
""".format(short=_('Manage Azure Arc enabled PostgreSQL Hyperscale server group endpoints.'))

helps['arc postgres endpoint list'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres endpoint list -n postgres01
""".format(
    short=_('List Azure Arc enabled PostgreSQL Hyperscale server group endpoints.'),
    ex1=_('List Azure Arc enabled PostgreSQL Hyperscale server group endpoints.'))

# pylint: disable=line-too-long
helps['arc postgres server config'] = """
    type: group
    short-summary: {short}
""".format(
    short=_('Configuration commands.'))

# pylint: disable=line-too-long
helps[
    "arc postgres server config init"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server config init --path ./template
""".format(
    short=_("Initializes the CRD and specification files for an Azure " 
              "Arc enabled PostgreSQL Hyperscale server group."),
    ex1=_("Initializes the CRD and specification files for an Azure " 
              "Arc enabled PostgreSQL Hyperscale server group."),
)

# pylint: disable=line-too-long
helps['arc postgres server config add'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server config add --path custom/spec.json
            --json-values 'spec.storage={val1}'
""".format(
    short=_('Add a value for a json path in a config file.'),
    long=_('Adds the value at the json path in the config file.  All examples '
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Add storage.'),
    val1=_('{"accessMode":"ReadWriteOnce","className":"managed-premium","size":"10Gi"}'))

# pylint: disable=line-too-long
helps['arc postgres server config remove'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server config remove --path custom/spec.json
            --json-path '.spec.storage'
""".format(
    short=_('Remove a value for a json path in a config file.'),
    long=_('Removes the value at the json path in the config file.  All examples '
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Remove storage.'))

# pylint: disable=line-too-long
helps['arc postgres server config replace'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server config replace --path custom/spec.json
            --json-values '$.spec.endpoints[?(@.name=="Controller")].port=30080'
        - name: {ex2}
          text: >
            azdata arc postgres server config replace --path custom/spec.json
            --json-values '{val2}'
""".format(
    short=_('Replace a value for a json path in a config file.'),
    long=_('Replaces the value at the json path in the config file.  All examples'
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Replace the port of a single endpoint.'),
    ex2=_('Ex 2 - Replace storage.'),
    val2=_('spec.storage={"accessMode":"ReadWriteOnce","className":"managed-premium","size":"10Gi"}'))

# pylint: disable=line-too-long
helps['arc postgres server config patch'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres server config patch --path custom/spec.json --patch ./patch.json

                Patch File Example (patch.json):
                    {patch1}
        - name: {ex2}
          text: >
            azdata arc postgres server config patch --path custom/spec.json --patch ./patch.json

                Patch File Example (patch.json):
                    {patch2}
""".format(
    short=_('Patches a config file based on a json patch file.'),
    long=_('Patches the config file according to the given patch file. '
           'Please consult http://jsonpatch.com/ for a better understanding of how the paths should be composed. '
           'The replace operation can use conditionals in its path due to the jsonpath library https://jsonpath.com/. '
           'All patch json files must start with a key of \"patch\" that has an array of patches with their '
           'corresponding op (add, replace, remove), path, and value. '
           'The \"remove\" op does not require a value, just a path. '
           'Please see the examples below.'),
    ex1=_('Ex 1 - Replace the port of a single endpoint with patch file.'),
    patch1=_('{"patch":[{"op":"replace","path":"$.spec.endpoints[?(@.name==\'Controller\')].port",'
              '"value":30080}]}'),
    ex2=_('Ex 2 - Replace storage with patch file.'),
    patch2=_('{"patch":[{"op":"replace","path":".spec.storage",'
             '"value":{"accessMode":"ReadWriteMany","className":"managed-premium","size":"10Gi"}}]}'))

# ------------------------------------------------------------------------------
# Database Commands
# ------------------------------------------------------------------------------

# helps['arc postgres database'] = """
#     type: group
#     short-summary: {short}
# """.format(short=_('Manage Azure Arc enabled PostgreSQL Hyperscale server group databases.'))
#
# helps['arc postgres database create'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres database create
# """.format(
#     short=_('Create a database within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Create a database within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres database delete'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres database delete
# """.format(
#     short=_('Delete a database from an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Delete a database from an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres database edit'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres database edit
# """.format(
#     short=_('Edit the configuration of a database within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Edit the configuration of a database within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres database list'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres database list
# """.format(
#     short=_('List databases within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('List databases within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres database show'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres database show
# """.format(
#     short=_('Show the details of a PostgreSQL database.'),
#     ex1=_('Show the details of a PostgreSQL database.'))

# ------------------------------------------------------------------------------
# Backup Commands
# ------------------------------------------------------------------------------

helps['arc postgres backup'] = """
    type: group
    short-summary: {short}
""".format(short=_('Manage Azure Arc enabled PostgreSQL Hyperscale server group backups.'))

helps['arc postgres backup create'] = """
    type: command
    short-summary: {short}
    examples:
        - name: Creates a backup for service 'pg'.
          text: >
            azdata arc postgres backup create -sn pg
        - name: Creates a named backup for service 'pg'.
          text: >
            azdata arc postgres backup create -sn pg -n backup1
""".format(
    short=_('Create a backup of an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex1=_('Create a backup of an Azure Arc enabled PostgreSQL Hyperscale server group.'))

helps['arc postgres backup delete'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres backup delete -sn pg -id e07dd3940e374bd9acbc86869cbc123d
""".format(
    short=_('Delete a backup of an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex1=_('Delete a backup of an Azure Arc enabled PostgreSQL Hyperscale server group.'))

helps['arc postgres backup list'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc postgres backup list -sn pg
""".format(
    short=_('List backups of an Azure Arc enabled PostgreSQL Hyperscale server group.'),
    ex1=_('List backups of an Azure Arc enabled PostgreSQL Hyperscale server group.'))

helps['arc postgres backup restore'] = """
    type: command
    short-summary: {short}
    examples:
        - name: Restore a backup by ID
          text: azdata arc postgres backup restore -sn pg -id 123e4567e89b12d3a456426655440000
        - name: Restore a backup by time (point-in-time restore)
          text: azdata arc postgres backup restore -sn pg-dst -ssn pg-src --time \"2020-11-18 17:25:34Z\"
        - name: Restore a backup by time span (point-in-time restore)
          text: azdata arc postgres backup restore -sn pg-dst -ssn pg-src --time 1d
""".format(
    short=_('Restore a backup of an Azure Arc enabled PostgreSQL Hyperscale server group.'))

# helps['arc postgres backup restorestatus'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: Get the recent restore status for service 'pg' by ID.
#           text: >
#             azdata arc postgres backup restorestatus -sn pg -id 123e4567e89b12d3a456426655440000
# """.format(
#     short=_('Get the status of the most recent restore operation, if any.'),
#     ex1=_('Get the status of the most recent restore operation, if any.'))

# helps['arc postgres backup show'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: Gets a backup for service 'pg' by ID
#           text: >
#             azdata arc postgres backup show -sn pg -id 123e4567e89b12d3a456426655440000
# """.format(
#     short=_('Show details about a backup of a PostgreSQL server group.'),
#     ex1=_('Show details about a backup of a PostgreSQL server group.'))

# ------------------------------------------------------------------------------
# Endpoint Commands
# ------------------------------------------------------------------------------

# helps['arc postgres endpoint'] = """
#     type: group
#     short-summary: {short}
# """.format(short=_('View endpoints of Azure Arc enabled PostgreSQL Hyperscale server groups.'))
#
# helps['arc postgres endpoint list'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres endpoint list
# """.format(
#     short=_('Lists the endpoints of Azure Arc enabled PostgreSQL Hyperscale server groups.'),
#     ex1=_('Lists the endpoints of Azure Arc enabled PostgreSQL Hyperscale server groups.'))

# ------------------------------------------------------------------------------
# Role Commands
# ------------------------------------------------------------------------------

# helps['arc postgres role'] = """
#     type: group
#     short-summary: {short}
# """.format(short=_('Manage Azure Arc enabled PostgreSQL Hyperscale server group roles.'))
#
# helps['arc postgres role create'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres role create
# """.format(
#     short=_('Create a role within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Create a role within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres role delete'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres role delete
# """.format(
#     short=_('Delete a role within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Delete a role within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres role list'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres role list
# """.format(
#     short=_('List roles within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('List roles within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres role show'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres role show
# """.format(
#     short=_('Show the details of a PostgreSQL role.'),
#     ex1=_('Show the details of a PostgreSQL role.'))

# ------------------------------------------------------------------------------
# User Commands
# ------------------------------------------------------------------------------

# helps['arc postgres user'] = """
#     type: group
#     short-summary: {short}
# """.format(short=_('Manage Azure Arc enabled PostgreSQL Hyperscale server group users.'))
#
# helps['arc postgres user create'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres user create
# """.format(
#     short=_('Create a user within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Create a user within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres user delete'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres user delete
# """.format(
#     short=_('Delete a user within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Delete a user within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres user edit'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres user edit
# """.format(
#     short=_('Edit the configuration of a user within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('Edit the configuration of a user within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres user list'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres user list
# """.format(
#     short=_('List users within an Azure Arc enabled PostgreSQL Hyperscale server group.'),
#     ex1=_('List users within an Azure Arc enabled PostgreSQL Hyperscale server group.'))
#
# helps['arc postgres user show'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres user show
# """.format(
#     short=_('Show the details of a PostgreSQL user.'),
#     ex1=_('Show the details of a PostgreSQL user.'))

# ------------------------------------------------------------------------------
# Volume Commands
# ------------------------------------------------------------------------------

# helps['arc postgres volume'] = """
#     type: group
#     short-summary: {short}
# """.format(short=_('Manage Azure Arc enabled PostgreSQL Hyperscale server group volume claims.'))
#
# helps['arc postgres volume delete'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres volume delete
# """.format(
#     short=_('Delete all inactive volume claims associated with one or all deleted Azure Arc enabled PostgreSQL Hyperscale server groups.'),
#     ex1=_('Delete all inactive volume claims associated with one or all deleted Azure Arc enabled PostgreSQL Hyperscale server groups.'))
#
# helps['arc postgres volume list'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres volume list
# """.format(
#     short=_('List volume claims of one or all Azure Arc enabled PostgreSQL Hyperscale server groups.'),
#     ex1=_('List volume claims of one or all Azure Arc enabled PostgreSQL Hyperscale server groups.'))
#
# helps['arc postgres volume show'] = """
#     type: command
#     short-summary: {short}
#     examples:
#         - name: {ex1}
#           text: >
#             azdata arc postgres volume show
# """.format(
#     short=_('Show the details of a PostgreSQL volume.'),
#     ex1=_('Show the details of a PostgreSQL volume.'))
