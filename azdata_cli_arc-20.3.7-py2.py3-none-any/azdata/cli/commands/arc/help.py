# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from knack.help_files import helps
from azdata.cli.core.deploy import get_environment_list_by_target

"""Help documentation for `control` commands."""

from knack.help_files import helps
from azdata.cli.commands.arc import _

helps['arc'] = """
    type: group
    short-summary: {short}
""".format(short=_('Commands for using Azure Arc for Azure data services.'))

helps['arc dc'] = """
    type: group
    short-summary: {short}
""".format(short=_('Create, delete, and manage data controllers.'))

helps['arc dc create'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc create
""".format(
    short=_('Create data controller.'),
    long=_('Create data controller - kube config is required on your system along with the '
           'following environment variables {0}.'.format(get_environment_list_by_target('cluster'))),
    ex1=_('Data controller deployment.'))

helps['arc dc delete'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc delete
""".format(
    short=_('Delete data controller.'),
    long=_('Delete data controller - kube config is required on your system.'
           .format(get_environment_list_by_target('cluster'))),
    ex1=_('Data controller deployment.'))

helps['arc dc endpoint'] = """
    type: group
    short-summary: {short}
""".format(
    short=_('Endpoint commands.'))

helps['arc dc endpoint list'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc endpoint list
""".format(
    short=_('List the data controller endpoint.'),
    long=_('List the data controller endpoint.'
           .format(get_environment_list_by_target('cluster'))),
    ex1=_('Lists all available data controller endpoints.'))

helps['arc dc status'] = """
    type: group
    short-summary: {short}
""".format(
    short=_('Status commands.'))

helps['arc dc status show'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc status show --namespace <ns>
""".format(
    short=_('Shows the status of the data controller.'),
    long=_('Shows the status of the data controller.'
           .format(get_environment_list_by_target('cluster'))),
    ex1=_('Shows the status of the data controller in a particular namespace.'))

helps['arc dc config'] = """
    type: group
    short-summary: {short}
""".format(
    short=_('Configuration commands.'))

helps['arc dc config init'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc config init
        - name: {ex2}
          text: >
            azdata arc dc config init --source azure-arc-kubeadm --path custom
""".format(
    short=_('Initializes a data controller configuration profile that can be used with control create.'),
    long=_('Initializes a data controller configuration  profile that can be used with control create. '
           'The specific source of the configuration profile can be specified in the arguments.'),
    ex1=_('Guided data controller config init experience - you will receive prompts for needed values.'),
    ex2=_('arc dc config init with arguments, creates a configuration profile of aks-dev-test in ./custom.'))

helps['arc dc config list'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc config list
        - name: {ex2}
          text: >
            azdata arc dc config list --config-profile aks-dev-test
""".format(
    short=_('Lists available configuration profile choices.'),
    long=_('Lists available configuration profile choices for use in `arc dc config init`'),
    ex1=_('Shows all available configuration profile names.'),
    ex2=_('Shows json of a specific configuration profile.'))

helps['arc dc config add'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc config add --path custom/control.json
            --json-values 'spec.storage={val1}'
""".format(
    short=_('Add a value for a json path in a config file.'),
    long=_('Adds the value at the json path in the config file.  All examples '
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Add data controller storage.'),
    val1=_('{"accessMode":"ReadWriteOnce","className":"managed-premium","size":"10Gi"}'))

helps['arc dc config remove'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc config remove --path custom/control.json
            --json-path '.spec.storage'
""".format(
    short=_('Remove a value for a json path in a config file.'),
    long=_('Removes the value at the json path in the config file.  All examples '
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Remove data controller storage.'))

helps['arc dc config replace'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc config replace --path custom/control.json
            --json-values '$.spec.endpoints[?(@.name=="Controller")].port=30080'
        - name: {ex2}
          text: >
            azdata arc dc config replace --path custom/control.json
            --json-values '{val2}'
""".format(
    short=_('Replace a value for a json path in a config file.'),
    long=_('Replaces the value at the json path in the config file.  All examples'
           'below are given in Bash.  If using another command line, please be aware that you may need to escape'
           'quotations appropriately.  Alternatively, you may use the patch file functionality.'),
    ex1=_('Ex 1 - Replace the port of a single endpoint (Data Controller Endpoint).'),
    ex2=_('Ex 2 - Replace data controller storage.'),
    val2=_('spec.storage={"accessMode":"ReadWriteOnce","className":"managed-premium","size":"10Gi"}'))

helps['arc dc config patch'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc dc config patch --path custom/control.json --patch ./patch.json

                Patch File Example (patch.json):
                    {patch1}
        - name: {ex2}
          text: >
            azdata arc dc config patch --path custom/control.json --patch ./patch.json

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
    ex1=_('Ex 1 - Replace the port of a single endpoint (Data Controller Endpoint) with patch file.'),
    patch1=_('{"patch":[{"op":"replace","path":"$.spec.endpoints[?(@.name==\'Controller\')].port",'
              '"value":30080}]}'),
    ex2=_('Ex 2 - Replace data controller storage with patch file.'),
    patch2=_('{"patch":[{"op":"replace","path":".spec.storage",'
             '"value":{"accessMode":"ReadWriteMany","className":"managed-premium","size":"10Gi"}}]}'))

helps['arc dc debug'] = """
    type: group
    short-summary: {short}
""".format(
    short=_('Debug commands.'))

helps['arc dc debug copy-logs'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
    short=_('Copy logs.'),
    long=_('Copy the debug logs from the data controller - Kubernetes configuration is required on your system.'))

helps['arc dc debug dump'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
    short=_('Trigger memory dump.'),
    long=_('Trigger memory dump and copy it out from container - Kubernetes configuration is required on your system.'))

helps['arc dc export'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
    short=_('Export metrics, logs or usage.'),
    long=_('Export metrics, logs or usage to a file.'))

helps['arc dc upload'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
    short=_('Upload exported data file.'),
    long=_('Upload data file exported from a data controller to Azure.'))

helps['arc resource-kind'] = """
    type: group
    short-summary: {short}
""".format(short=_('Resource-kind commands to define and template custom resources on your cluster.'))

helps['arc resource-kind list'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata arc resource-kind list
""".format(
    short=_('Lists the available custom resource kinds for Arc that can be defined and created.'),
    long=_('Lists the available custom resource kinds for Arc that can be defined and created. After listing, you'
           ' can proceed to getting the template file needed to define or create that custom resource.'),
    ex1=_('Example command for listing the available custom resource kinds for Arc.'))

helps['arc resource-kind get'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata arc resource-kind get --kind sqldb
""".format(
    short=_('Gets the Arc resource-kind\'s template file.'),
    ex1=_('Example command for getting an Arc resource-kind\'s CRD template file.'))

helps['arc resource'] = """
    type: group
    short-summary: {short}
""".format(short=_('Resource commands to create and manage custom resources on your cluster.'))
