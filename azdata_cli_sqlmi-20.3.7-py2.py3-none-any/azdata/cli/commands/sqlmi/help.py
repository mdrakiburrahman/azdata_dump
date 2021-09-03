# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from knack.help_files import helps
from azdata.cli.commands.sqlmi import _


# pylint: disable=line-too-long
helps['arc sql'] = """
    type: group
    short-summary: {short}
""".format(short=_('Create, delete, and manage SQL resources.'))

# pylint: disable=line-too-long
helps[
    "arc sql mi"
] = """
    type: group
    short-summary: {short}
""".format(
    short=_("Create, delete, and manage SQL managed instance.")
)

# pylint: disable=line-too-long
helps[
    "arc sql endpoint"
] = """
    type: group
    short-summary: {short}
""".format(
    short=_("View and manage SQL endpoints.")
)

helps[
    "arc sql endpoint list"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql endpoint list -n sqlmi1
""".format(
    short=_("List the SQL endpoints."),
    ex1=_("List the endpoints for a SQL managed instance."),
)

# pylint: disable=line-too-long
helps[
    "arc sql mi create"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi create -n sqlmi1
        - name: {ex2}
          text: >
            azdata arc sql mi create -n sqlmi2 --replicas 3
""".format(
    short=_("Create a SQL managed instance."),
    long=_('To set the password of the SQL managed instance, please set the environment variable AZDATA_PASSWORD'),
    ex1=_("Create a SQL managed instance."),
    ex2=_("Create a SQL managed instance with 3 replicas in HA scenario.")
)

# pylint: disable=line-too-long
helps[
    "arc sql mi edit"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi edit --path ./spec.json -n sqlmi1
""".format(
    short=_("Edit the configuration of a SQL managed instance."),
    ex1=_("Edit the configuration of a SQL managed instance."),
)

# pylint: disable=line-too-long
helps[
    "arc sql mi delete"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi delete -n sqlmi1
""".format(
    short=_("Delete a SQL managed instance."),
    ex1=_("Delete a SQL managed instance."),
)

# pylint: disable=line-too-long
helps[
    "arc sql mi show"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi show -n sqlmi1
""".format(
    short=_("Show the details of a SQL managed instance."),
    ex1=_("Show the details of a SQL managed instance."),
)

# pylint: disable=line-too-long
helps[
    "arc sql mi get-mirroring-cert"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi get-mirroring-cert -n sqlmi1 --cert-file fileName1
""".format(
    short=_("Retrieve certificate of availability group mirroring endpoint from sql mi and store in a file."),
    ex1=_("Retrieve certificate of availability group mirroring endpoint from sqlmi1 and store in file fileName1"),
)

# pylint: disable=line-too-long
helps[
    "arc sql mi list"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi list
""".format(
    short=_("List SQL managed instances."), ex1=_("List SQL managed instances."),
)

# pylint: disable=line-too-long
helps['arc sql mi config'] = """
    type: group
    short-summary: {short}
""".format(
    short=_('Configuration commands.'))

# pylint: disable=line-too-long
helps[
    "arc sql mi config init"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi config init --path ./template
""".format(
    short=_("Initializes the CRD and specification files for a SQL managed instance."),
    ex1=_("Initializes the CRD and specification files for a SQL managed instance."),
)

# pylint: disable=line-too-long
helps['arc sql mi config add'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi config add --path custom/spec.json
            --json-values 'spec.storage={val1}'
""".format(
    short=_('Add a value for a json path in a config file.'),
    long=_('Adds the value at the json path in the config file.  All examples '
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Add storage.'),
    val1=_('{"accessMode":"ReadWriteOnce","className":"managed-premium","size":"10Gi"}'))

# pylint: disable=line-too-long
helps['arc sql mi config remove'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi config remove --path custom/spec.json
            --json-path '.spec.storage'
""".format(
    short=_('Remove a value for a json path in a config file.'),
    long=_('Removes the value at the json path in the config file.  All examples '
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Remove storage.'))

# pylint: disable=line-too-long
helps['arc sql mi config replace'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi config replace --path custom/spec.json
            --json-values '$.spec.endpoints[?(@.name=="Controller")].port=30080'
        - name: {ex2}
          text: >
            azdata arc sql mi config replace --path custom/spec.json
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
helps['arc sql mi config patch'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi config patch --path custom/spec.json --patch ./patch.json

                Patch File Example (patch.json):
                    {patch1}
        - name: {ex2}
          text: >
            azdata arc sql mi config patch --path custom/spec.json --patch ./patch.json

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

# pylint: disable=line-too-long
helps['arc sql mi dag'] = """
    type: group
    short-summary: {short}
""".format(
    short=_('Create or Delete a Distributed Availability Group.'))

# pylint: disable=line-too-long
helps['arc sql mi dag create'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi dag create --name=dagCr1 --dag-name=dagName1 --local-name=sqlmi1 --local-primary=true, --remote-name=sqlmi2, remote-url==remotePrimary:5022 --remote-cert-file='./sqlmi2.cer'
""".format(
    short=_('Create a distributed availability group custom resource'),
    long=_('Create a distributed availability group custom resource to create a distributed availability group '),
    ex1=_('Ex 1 - Create a distributed availability group custom resource dagCr1 to create distributed availability group dagName1 '
          'between local sqlmi instance sqlmi1 and remote sqlmi instance sqlmi2. '
          'It requires remote sqlmi primary mirror remotePrimary:5022 and remote sqlmi mirror endpoint certificate file ./sqlmi2.cer.'))

# pylint: disable=line-too-long
helps['arc sql mi dag delete'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi dag delete --name=dagCr1
""".format(
    short=_('Delete a distributed availability group custom resource on a sqlmi instance.'),
    long=_('Delete a distributed availability group custom resource on a sqlmi instance to delete a distributed availability group. '
           'It requires a custom resource name'),
    ex1=_('Ex 1 - delete distributed availability group resources named dagCr1.'))

helps['arc sql mi dag get'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc sql mi dag get --name=dagCr1
""".format(
    short=_('get a distributed availability group custom resource.'),
    long=_('get a distributed availability group custom resource. '
           'It requires a custom resource name'),
    ex1=_('Ex 1 - get distributed availability group resources named dagCr1.'))


