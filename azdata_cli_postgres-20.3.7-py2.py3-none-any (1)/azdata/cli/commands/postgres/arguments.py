# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext
    from azdata.cli.commands.postgres import _

    # ------------------------------------------------------------------------------
    # Server Commands
    # ------------------------------------------------------------------------------

    with ArgumentsContext(self, 'arc postgres server create') as arg_context:
        arg_context.argument(
            'path',
            options_list=['--path'],
            help=_('The path to the source json file for the Azure Arc enabled PostgreSQL Hyperscale'
                    ' server group. This is optional.')
        )
        arg_context.argument(
            'name',
            options_list=['--name', '-n'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
        # )
        arg_context.argument(
            "replicas",
            options_list=["--replicas", '-r'],
            help=_("The number of replicas to be deployed for high availability purpose with default of '1'.")
        )
        arg_context.argument(
            'cores_limit',
            options_list=['--cores-limit', '-cl'],
            help=_('The maximum number of CPU cores for Azure Arc enabled PostgreSQL Hyperscale server group'
                    ' that can be used per node. Fractional cores are supported.'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'cores_request',
            options_list=['--cores-request', '-cr'],
            help=_('The minimum number of CPU cores that must be available per node to schedule the service. '
                   'Fractional cores are supported.'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'memory_limit',
            options_list=['--memory-limit', '-ml'],
            help=_('The memory limit of the Azure Arc enabled PostgreSQL Hyperscale server group as a number'
                    ' followed by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes).'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'memory_request',
            options_list=['--memory-request', '-mr'],
            help=_('The memory request of the Azure Arc enabled PostgreSQL Hyperscale server group as a'
                    ' number followed by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes).'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'storage_class_data',
            options_list=['--storage-class-data', '-scd'],
            help=_('The storage class to be used for data persistent volumes.')
        )
        arg_context.argument(
            'storage_class_logs',
            options_list=['--storage-class-logs', '-scl'],
            help=_('The storage class to be used for logs persistent volumes.')
        )
        arg_context.argument(
            'storage_class_backups',
            options_list=['--storage-class-backups', '-scb'],
            help=_('The storage class to be used for backup persistent volumes.')
        )
        arg_context.argument(
            'volume_claim_mounts',
            options_list=['--volume-claim-mounts', '-vcm'],
            help=_('A comma-separated list of volume claim mounts. A volume claim mount is a pair of an existing persistent volume claim '
                '(in the same namespace) and volume type (and optional metadata depending on the volume type) separated by colon.'
                'The persistent volume will be mounted in each pod for the PostgreSQL server group. '
                'The mount path may depend on the volume type.')
        )
        arg_context.argument(
            "volume_size_data",
            options_list=["--volume-size-data", "-vsd"],
            help=_("The size of the storage volume to be used for data as a positive number followed by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes)."),
        )
        arg_context.argument(
            "volume_size_logs",
            options_list=["--volume-size-logs", "-vsl"],
            help=_("The size of the storage volume to be used for logs as a positive number followed by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes)."),
        )
        arg_context.argument(
            "volume_size_backups",
            options_list=["--volume-size-backups", "-vsb"],
            help=_("The size of the storage volume to be used for backups as a positive number followed by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes)."),
        )
        arg_context.argument(
            'workers',
            options_list=['--workers', '-w'],
            help=_("The number of worker nodes to provision in a server group. "
                    "In Preview, reducing the number of worker nodes is not supported. Refer to documentation for additional details.")
        )
        arg_context.argument(
            'extensions',
            options_list=('--extensions'),
            help='A comma-separated list of the Postgres extensions that should be loaded on startup. Please refer to the postgres documentation for supported values.'
        )
        arg_context.argument(
            'engine_version',
            type=int,
            options_list=['--engine-version', '-ev'],
            help=_('Must be 11 or 12. The default value is 12.')
        )
        arg_context.argument(
            'engine_settings',
            options_list=('--engine-settings', '-es'),
            help="A comma separated list of Postgres engine settings in the format 'key1=val1, key2=val2'."
        )
        arg_context.argument(
            "no_external_endpoint",
            options_list=["--no-external-endpoint"],
            action="store_true",
            help=_("If specified, no external service will be created. Otherwise, an external service will be created "
                   "using the same service type as the data controller."),
        )
        # arg_context.argument(
        #     'dev',
        #     options_list=['--dev'],
        #     action='store_true',
        #     help=_('If this is specified, then it is considered a dev instance and will not be billed for.')
        # )
        arg_context.argument(
            "port",
            options_list=["--port"],
            help=_("Optional."),
        )
        arg_context.argument(
            "no_wait",
            options_list=["--no-wait"],
            action="store_true",
            help=_("If given, the command will not wait for the instance to be in a ready state before returning.")
        )
        arg_context.argument(
            'coordinator_engine_settings',
            options_list=('--coordinator-engine-settings', '-ces'),
            help=_("A comma separated list of Postgres engine settings in the format 'key1=val1, key2=val2' to be applied to 'coordinator' node role."
                  " When node role specific settings are specified, default settings will be ignored and overridden with the settings provided here.")
        )
        arg_context.argument(
            'worker_engine_settings',
            options_list=('--worker-engine-settings', '-wes'),
            help=_("A comma separated list of Postgres engine settings in the format 'key1=val1, key2=val2' to be applied to 'worker' node role."
                  " When node role specific settings are specified, default settings will be ignored and overridden with the settings provided here.")
        )
    with ArgumentsContext(self, 'arc postgres server edit') as arg_context:
        arg_context.argument(
            'path',
            options_list=['--path'],
            help=_('The path to the source json file for the Azure Arc enabled PostgreSQL Hyperscale server group. This is optional.')
        )
        arg_context.argument(
            'name',
            options_list=['--name', '-n'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group that is being edited. The name under which your instance '
                   'is deployed cannot be changed.')
        )
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed. If no namespace is specified, then the '
        #            'namespace of the data controller is used. The namespace in which your instance is deployed '
        #            'cannot be changed.')
        # )
        arg_context.argument(
            "replicas",
            options_list=["--replicas", '-r'],
            help=_("The number of replicas to be deployed for high availability purpose with default of '1'.")
        )
        arg_context.argument(
            'cores_limit',
            options_list=['--cores-limit', '-cl'],
            help=_('The maximum number of CPU cores for Azure Arc enabled PostgreSQL Hyperscale server group that can be used per node,'
                    ' fractional cores are supported. To remove the cores_limit, specify its value as empty string.'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'cores_request',
            options_list=['--cores-request', '-cr'],
            help=_('The minimum number of CPU cores that must be available per node to schedule the service, fractional cores'
                    ' are supported. To remove the cores_request, specify its value as empty string.'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'memory_limit',
            options_list=['--memory-limit', '-ml'],
            help=_('The memory limit for Azure Arc enabled PostgreSQL Hyperscale server group as a number followed'
                    ' by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes). To remove the memory_limit, specify its value as empty string.'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'memory_request',
            options_list=['--memory-request', '-mr'],
            help=_('The memory request for Azure Arc enabled PostgreSQL Hyperscale server group as a number followed by'
                    ' Ki (kilobytes), Mi (megabytes), or Gi (gigabytes). To remove the memory_request, specify its value as empty string.'
                    ' Optionally a comma-separated list of roles with values can be specified in format <role>=<value>. Valid roles are: "coordinator" or "c", "worker" or "w".'
                    ' If no roles are specified, settings will apply to all nodes of the PostgreSQL Hyperscale server group.')
        )
        arg_context.argument(
            'workers',
            options_list=['--workers', '-w'],
            help=_('The number of worker nodes to provision in a server group.'
                    ' In Preview, reducing the number of worker nodes is not supported. Refer to documentation for additional details.')
        )
        arg_context.argument(
            'extensions',
            options_list=('--extensions'),
            help='A comma-separated list of the Postgres extensions that should be loaded on startup. Please refer to the postgres documentation for supported values.'
        )
        arg_context.argument(
            'engine_version',
            type=int,
            options_list=
            [
                arg_context.deprecate(
                    target='--engine-version',
                    hide=False
                ),                
                arg_context.deprecate(
                    target='-ev',
                    hide=False
                ),                
            ],
            help=_('Engine version cannot be changed. --engine-version can be used in conjunction with --name to '
                   'identify a PostgreSQL Hyperscale server group when two server groups of different engine version '
                   'have the same name. --engine-version is optional and when used to identify a server group, it must be 11 or 12.')
        )        
        # arg_context.argument(
        #     'dev',
        #     options_list=['--dev'],
        #     action='store_true',
        #     help=_('If this is specified, then it is considered a dev instance and will not be billed for.')
        # )
        arg_context.argument(
            "port",
            options_list=["--port"],
            help=_("Optional."),
        )
        arg_context.argument(
            'admin_password',
            options_list=['--admin-password'],
            action='store_true',
            help=_("If given, the Azure Arc enabled PostgreSQL Hyperscale server group's admin password will be set to the value of the "
                   "AZDATA_PASSWORD environment variable if present and a prompted value otherwise.")
        )
        arg_context.argument(
            "no_wait",
            options_list=["--no-wait"],
            action="store_true",
            help=_("If given, the command will not wait for the instance to be in a ready state before returning.")
        )
        arg_context.argument(
            'engine_settings',
            options_list=('--engine-settings', '-es'),
            help=_("A comma separated list of Postgres engine settings in the format 'key1=val1, key2=val2'. The provided settings will be merged with the existing settings."
                 " To remove a setting, provide an empty value like 'removedKey='."
                 " If you change an engine setting that requires a restart, the service will be restarted to apply the settings immediately.")
        )
        arg_context.argument(
            'replace_engine_settings',
            options_list=('--replace-engine-settings', '-res'),
            action='store_true',
            help='When specified with --engine-settings, will replace all existing custom engine settings with new set of settings and values.'
        )
        arg_context.argument(
            'coordinator_engine_settings',
            options_list=('--coordinator-engine-settings', '-ces'),
            help=_("A comma separated list of Postgres engine settings in the format 'key1=val1, key2=val2' to be applied to 'coordinator' node role."
                  " When node role specific settings are specified, default settings will be ignored and overridden with the settings provided here.")
        )
        arg_context.argument(
            'worker_engine_settings',
            options_list=('--worker-engine-settings', '-wes'),
            help=_("A comma separated list of Postgres engine settings in the format 'key1=val1, key2=val2' to be applied to 'worker' node role."
                  " When node role specific settings are specified, default settings will be ignored and overridden with the settings provided here.")
        )

    with ArgumentsContext(self, 'arc postgres server delete') as arg_context:
        arg_context.argument(
            'name',
            options_list=['--name', '-n'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed. '
        #            'If no namespace is specified, then the namespace of the data controller is used.')
        # )
        arg_context.argument(
            'engine_version',
            type=int,
            options_list=
            [
                arg_context.deprecate(
                    target='--engine-version',
                    hide=False
                ),                
                arg_context.deprecate(
                    target='-ev',
                    hide=False
                ),                
            ],
            help=_('--engine-version can be used in conjunction with --name to identify a PostgreSQL Hyperscale server '
                   'group when two server groups of different engine version have the same name. --engine-version is '
                   'optional and when used to identify a server group, it must be 11 or 12.')
        )        
        arg_context.argument(
            "force",
            options_list=("--force", "-f"),
            action="store_true",
            help=_("Force delete the Azure Arc enabled PostgreSQL Hyperscale server group without confirmation."))

    with ArgumentsContext(self, 'arc postgres server show') as arg_context:
        arg_context.argument(
            'name',
            options_list=['--name', '-n'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed. If not specified, it will use '
        #            'the data controller namespace.')
        # )
        arg_context.argument(
            'engine_version',
            type=int,
            options_list=
            [
                arg_context.deprecate(
                    target='--engine-version',
                    hide=False
                ),                
                arg_context.deprecate(
                    target='-ev',
                    hide=False
                ),                
            ],
            help=_('--engine-version can be used in conjunction with --name to identify a PostgreSQL Hyperscale server '
                   'group when two server groups of different engine version have the same name. --engine-version is '
                   'optional and when used to identify a server group, it must be 11 or 12.')
        )        
        arg_context.argument(
            'path',
            options_list=['--path', '-p'],
            help=_('A path where the full specification for the Azure Arc enabled PostgreSQL Hyperscale server group should be '
                   'written. If omitted, the specification will be written to standard output.')
        )

    # with ArgumentsContext(self, 'arc postgres server list') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server groups are deployed. If not specified, it will use '
    #                'the data controller namespace.')
    #     )

    with ArgumentsContext(self, 'arc postgres endpoint list') as arg_context:
        arg_context.argument(
            'name',
            options_list=['--name', '-n'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed. If not specified, it will use '
        #            'the data controller namespace.')
        # )
        arg_context.argument(
            'engine_version',
            type=int,
            options_list=
            [
                arg_context.deprecate(
                    target='--engine-version',
                    hide=False
                ),                
                arg_context.deprecate(
                    target='-ev',
                    hide=False
                ),                
            ],
            help=_('--engine-version can be used in conjunction with --name to identify a PostgreSQL Hyperscale server '
                   'group when two server groups of different engine version have the same name. --engine-version is '
                   'optional and when used to identify a server group, it must be 11 or 12.')
        )        

    with ArgumentsContext(self, "arc postgres server config init") as arg_context:
        arg_context.argument(
            'path',
            options_list=['--path', '-p'],
            help=_('A path where the CRD and specification for the Azure Arc enabled PostgreSQL Hyperscale server group should be '
                   'written.')
        )
        arg_context.argument(
            'engine_version',
            type=int,
            options_list=
            [
                arg_context.deprecate(
                    target='--engine-version',
                    hide=False
                ),                
                arg_context.deprecate(
                    target='-ev',
                    hide=False
                ),                
            ],
            help=_('Must be 11 or 12. The default value is 12.')
        )        

    with ArgumentsContext(self, "arc postgres server config add") as arg_context:
        arg_context.argument(
            "path",
            options_list=("--path", "-p"),
            help=_("Path to the custom resource specification, i.e. custom/spec.json")
        )

        arg_context.argument(
            "json_values",
            options_list=("--json-values", "-j"),
            help=_("A key value pair list of json paths to values: key1.subkey1=value1,key2.subkey2=value2. "
                   "You may provide inline json values such as: "
                   "key=\'{\"kind\":\"cluster\",\"name\":\"test-cluster\"}\' or provide a file path, such as"
                   " key=./values.json. Add does NOT support conditionals.  "
                   "If the inline value you are providing is a key "
                   "value pair itself with \"=\" and \",\" please escape those characters.  "
                   "For example, key1=\"key2\=val2\,key3\=val3\". "
                   "Please see http://jsonpatch.com/ for "
                   "examples of how your path should look.  If you would like to access an array, you must do so "
                   "by indicating the index, such as key.0=value")
        )

    with ArgumentsContext(self, "arc postgres server config replace") as arg_context:
        arg_context.argument(
            "path",
            options_list=("--path", "-p"),
            help=_("Path to the custom resource specification, i.e. custom/spec.json")
        )

        arg_context.argument(
            "json_values",
            options_list=("--json-values", "-j"),
            help=_("A key value pair list of json paths to values: key1.subkey1=value1,key2.subkey2=value2. "
                   "You may provide inline json values such as: "
                   "key=\'{\"kind\":\"cluster\",\"name\":\"test-cluster\"}\' or provide a file path, such as"
                   " key=./values.json. Replace supports conditionals through the jsonpath library.  To use this, "
                   "start your path with a $. This will allow you to do a conditional "
                   "such as -j $.key1.key2[?(@.key3==\"someValue\"].key4=value. "
                   "If the inline value you are providing is a key "
                   "value pair itself with \"=\" and \",\" please escape those characters.  "
                   "For example, key1=\"key2\=val2\,key3\=val3\". "
                   "You may see examples below. "
                   "For additional help, please see: https://jsonpath.com/")
        )

    with ArgumentsContext(self, "arc postgres server config remove") as arg_context:
        arg_context.argument(
            "path",
            options_list=("--path", "-p"),
            help=_("Path to the custom resource specification, i.e. custom/spec.json")
        )

        arg_context.argument(
            "json_path",
            options_list=("--json-path", "-j"),
            help=_("A list of json paths based on the jsonpatch library that indicates which values you would like "
                   "removed, such as: key1.subkey1,key2.subkey2. Remove does NOT support conditionals. "
                   "Please see http://jsonpatch.com/ for "
                   "examples of how your path should look.  If you would like to access an array, you must do so "
                   "by indicating the index, such as key.0=value")
        )

    with ArgumentsContext(self, "arc postgres server config patch") as arg_context:
        arg_context.argument(
            "path",
            options_list=("--path", "-p"),
            help=_("Path to the custom resource specification, i.e. custom/spec.json")
        )

        arg_context.argument(
            "patch_file",
            options_list=("--patch-file"),
            help=_("Path to a patch json file that is based off the jsonpatch library: http://jsonpatch.com/. "
                   "You must start your patch json file with a key called \"patch\", whose value is an array "
                   "of patch operations you intend to make. "
                   "For the path of a patch operation, you may use dot notation, such as key1.key2 for most operations."
                   " If you would like to do a replace operation, and you are replacing a value in an array that "
                   "requires a conditional, please use the jsonpath notation by beginning your path with a $. "
                   "This will allow you to do a conditional such as $.key1.key2[?(@.key3==\"someValue\"].key4. "
                   "Please see the examples below. For additional help with conditionals, "
                   "please see: https://jsonpath.com/.")
        )

    # with ArgumentsContext(self, 'arc postgres server restart') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server groups are deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )

    # ------------------------------------------------------------------------------
    # Database Commands
    # ------------------------------------------------------------------------------

    # with ArgumentsContext(self, 'arc postgres database create') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the database.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group_name',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    #     arg_context.argument(
    #         'owner',
    #         options_list=['--owner'],
    #         help=_('An optional name of a user that should own the database. By default, the database will be owned '
    #                'by the administrative user.')
    #     )
    #
    #     arg_context.argument(
    #         'sharded',
    #         options_list=['--sharded'],
    #         help=_('An optional boolean that indicates whether the database should support sharding. The default is '
    #                'true if the service has multiple workers and false if not.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres database delete') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the database.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group_name',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres database edit') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the database.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group_name',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    #     arg_context.argument(
    #         'owner',
    #         options_list=['--owner'],
    #         help=_('An optional name of a user that should own the database. By default, the database will be owned '
    #                'by the administrative user.')
    #     )
    #
    #     arg_context.argument(
    #         'sharded',
    #         options_list=['--sharded'],
    #         help=_('An optional boolean that indicates whether the database should support sharding. The default is '
    #                'true if the service has multiple workers and false if not.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres database list') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group_name',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres database show') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the database.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group_name',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )

    # ------------------------------------------------------------------------------
    # Backup Commands
    # ------------------------------------------------------------------------------

    with ArgumentsContext(self, 'arc postgres backup create') as arg_context:
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
        # )
    
        arg_context.argument(
            'backup_name',
            options_list=['--name', '-n'],
            help=_('Name of the backup. This parameter is optional.')
        )
    
        arg_context.argument(
            'server_name',
            options_list=['--server-name', '-sn'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )

        arg_context.argument(
            'incremental',
            options_list=['--incremental', '-i'],
            action='store_true',
            help='If given, the command will take an incremental backup. The default is to take a full backup.'
        )

        arg_context.argument(
            'no_wait',
            options_list=['--no-wait'],
            action='store_true',
            help='If given, the command will not wait for the backup to complete before returning.'
        )

    # with ArgumentsContext(self, 'arc postgres server backup delete') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    
    #     arg_context.argument(
    #         'backup_id',
    #         options_list=['--backup-id', '-id'],
    #         help=_('ID of the backup. This parameter is mutually exclusive with --name.')
    #     )
    
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the backup. This parameter is mutually exclusive with --backup-id.')
    #     )
    
    #     arg_context.argument(
    #         'tier',
    #         options_list=['--tier'],
    #         help=_('The ordinal of the backup tier where the backup is deleted from. If omitted or "all", the backup '
    #                'will be deleted from all tiers.')
    #     )
    
    #     arg_context.argument(
    #         'max',
    #         options_list=['--max'],
    #         help=_('A comma-separated list of trim specifications that determine when backups should be deleted. '
    #                'If unspecified, the defaults from the database service are used.')
    #     )
    
    #     arg_context.argument(
    #         'min',
    #         options_list=['--min'],
    #         help=_('A comma-separated list of trim specifications that determine how many backups should be '
    #                'retained. This takes precedence over --max. If unspecified, the defaults from the database '
    #                'service are used.')
    #     )

    with ArgumentsContext(self, 'arc postgres backup restore') as arg_context:
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
        # )
    
        arg_context.argument(
            'backup_id',
            options_list=['--backup-id', '-id'],
            help=_('ID of the backup. If not specified, the most recent backup taken will be restored.')
        )

        arg_context.argument(
            'server_name',
            options_list=['--server-name', '-sn'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )

        arg_context.argument(
            'source_server_name',
            options_list=['--source-server-name', '-ssn'],
            help=_('Name of the source Azure Arc enabled PostgreSQL Hyperscale server group. '
                   'If not provided, the backup will be restored in place on the server group identified by --server-name.')
        )

        arg_context.argument(
            'restore_time',
            options_list=('--time', '-t'),
            help='The point in time to restore to, given either as a timestamp or a number and suffix (m for minutes, h for hours, d for days, and w for weeks). '
                'E.g. 1.5h goes back 90 minutes. If specifed, --source-server-name must be given to restore the backup from a separate '
                'Azure Arc enabled PostgreSQL Hyperscale server group.'
        )

    with ArgumentsContext(self, 'arc postgres backup list') as arg_context:
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
        # )
        arg_context.argument(
            'server_name',
            options_list=['--server-name', '-sn'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )

    with ArgumentsContext(self, 'arc postgres backup delete') as arg_context:
        # arg_context.argument(
        #     'namespace',
        #     options_list=['--namespace', '-ns'],
        #     help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
        # )

        arg_context.argument(
            'server_name',
            options_list=['--server-name', '-sn'],
            help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
        )

        arg_context.argument(
            'backup_name',
            options_list=['--name', '-n'],
            help=_('Name of the backup. This parameter is mutually exclusive with -id.')
        )

        arg_context.argument(
            'backup_id',
            options_list=['-id'],
            help=_('ID of the backup to be deleted. This parameter is mutually exclusive with --name.')
        )

    # ------------------------------------------------------------------------------
    # Role Commands
    # ------------------------------------------------------------------------------

    # with ArgumentsContext(self, 'arc postgres role create') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the role.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres role delete') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the role.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres role list') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres role show') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the role.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )

    # ------------------------------------------------------------------------------
    # User Commands
    # ------------------------------------------------------------------------------
    # with ArgumentsContext(self, 'arc postgres user create') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the user.')
    #     )
    #
    #     arg_context.argument(
    #         'password',
    #         options_list=['--password', '-p'],
    #         help=_('An optional password for the user. If omitted, a password will be generated.')
    #     )
    #
    #     arg_context.argument(
    #         'roles',
    #         options_list=['--roles', '-r'],
    #         help=_('An optional comma-separated list of roles that the user should belong to. '
    #                'If omitted, the user will not belong to any roles.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres user delete') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the user.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres user edit') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the user.')
    #     )
    #
    #     arg_context.argument(
    #         'password',
    #         options_list=['--password', '-p'],
    #         help=_('An optional password for the user. If omitted, a password will be generated.')
    #     )
    #
    #     arg_context.argument(
    #         'roles',
    #         options_list=['--roles', '-r'],
    #         help=_('An optional comma-separated list of roles that the user should belong to. '
    #                'If omitted, the user will not belong to any roles.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres user list') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres user show') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'name',
    #         options_list=['--name', '-n'],
    #         help=_('Name of the user.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    # ------------------------------------------------------------------------------
    # Volume Commands
    # ------------------------------------------------------------------------------

    # with ArgumentsContext(self, 'arc postgres volume delete') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group. If omitted, all deleted server groups with inactive volumes '
    #                'will be included.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres volume list') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )
    #
    # with ArgumentsContext(self, 'arc postgres volume show') as arg_context:
    #     arg_context.argument(
    #         'namespace',
    #         options_list=['--namespace', '-ns'],
    #         help=_('Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.')
    #     )
    #
    #     arg_context.argument(
    #         'server_group',
    #         options_list=['--server-group-name', '-sn'],
    #         help=_('Name of the Azure Arc enabled PostgreSQL Hyperscale server group.')
    #     )