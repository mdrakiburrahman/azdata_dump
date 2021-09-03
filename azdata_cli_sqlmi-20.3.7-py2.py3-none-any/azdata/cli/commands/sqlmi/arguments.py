# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


from azdata.cli.commands.sqlmi.constants import SQLMI_LICENSE_TYPE_ALLOWED_VALUES_MSG_CREATE, SQLMI_LICENSE_TYPE_BASE_PRICE, SQLMI_LICENSE_TYPE_LICENSE_INCLUDED, SQLMI_TIER_ALLOWED_VALUES_MSG, SQLMI_TIER_ALLOWED_VALUES_MSG_CREATE, SQLMI_TIER_BUSINESS_CRITICAL, SQLMI_TIER_BUSINESS_CRITICAL_SHORT, SQLMI_TIER_GENERAL_PURPOSE, SQLMI_TIER_GENERAL_PURPOSE_SHORT


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext
    from azdata.cli.commands.sqlmi import _

    from azdata.cli.commands.sqlmi.util import (
        get_valid_sql_license_types,
        get_valid_sql_tiers,
    )

    with ArgumentsContext(self, "arc sql mi create") as arg_context:
        arg_context.argument(
            "path",
            options_list=["--path"],
            help=_("The path to the src file for the SQL managed instance json file."),
        )
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help=_("The name of the SQL managed instance."),
        )
        # arg_context.argument(
        #     "namespace",
        #     options_list=["--namespace", "-ns"],
        #     help=_("Namespace where the SQL managed instance is to be deployed. "
        #            "If no namespace is specified, then the namespace of the data controller is used."),
        # )
        arg_context.argument(
            "replicas",
            options_list=["--replicas"],
            help=_("This option specifies the number of SQL Managed Instance replicas that will be deployed in your Kubernetes cluster for high availability purpose. Allowed values are less than or equal '3' with default of '1'.")
        )
        arg_context.argument(
            "cores_limit",
            options_list=["--cores-limit", "-cl"],
            help=_("The cores limit of the managed instance as an integer."),
        )
        arg_context.argument(
            "cores_request",
            options_list=["--cores-request", "-cr"],
            help=_("The request for cores of the managed instance as an integer."),
        )
        arg_context.argument(
            "memory_limit",
            options_list=["--memory-limit", "-ml"],
            help=_("The limit of the capacity of the managed instance as an integer."),
        )
        arg_context.argument(
            "memory_request",
            options_list=["--memory-request", "-mr"],
            help=_("The request for the capcity of the managed instance as an integer amount of memory in GBs."),
        )
        arg_context.argument(
            "storage_class_data",
            options_list=["--storage-class-data", "-scd"],
            help=_("The storage class to be used for data (.mdf). If no value is specified, then no storage "
                   "class will be specified, which will result in Kubernetes using the default storage class."),
        )
        arg_context.argument(
            "storage_class_datalogs",
            options_list=["--storage-class-data-logs", "-scdl"],
            help=_("The storage class to be used for database logs (.ldf). If no value is specified, then no storage "
                   "class will be specified, which will result in Kubernetes using the default storage class."),
        )
        arg_context.argument(
            "storage_class_logs",
            options_list=["--storage-class-logs", "-scl"],
            help=_("The storage class to be used for logs (/var/log). If no value is specified, then no storage "
                   "class will be specified, which will result in Kubernetes using the default storage class."),
        )
        arg_context.argument(
            "storage_class_backups",
            options_list=["--storage-class-backups", "-scb"],
            help=_("The storage class to be used for backups (/var/opt/mssql/backups). If no value is specified, then no storage "
                   "class will be specified, which will result in Kubernetes using the default storage class."),
        )
        arg_context.argument(
            "volume_size_data",
            options_list=["--volume-size-data", "-vsd"],
            help=_("The size of the storage volume to be used for data as a positive number followed by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes)."),
        )
        arg_context.argument(
            "volume_size_datalogs",
            options_list=["--volume-size-data-logs", "-vsdl"],
            help=_("The size of the storage volume to be used for data logs as a positive number followed by Ki (kilobytes), Mi (megabytes), or Gi (gigabytes)."),
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
            "labels",
            options_list=["--labels"],
            help=_("Comma-separated list of labels of the SQL managed instance.")
        )

        arg_context.argument(
            "annotations",
            options_list=["--annotations"],
            help=_("Comma-separated list of annotations of the SQL managed instance.")
        )

        arg_context.argument(
            "service_labels",
            options_list=["--service-labels"],
            help=_("Comma-separated list of labels to apply to all external services.")
        )

        arg_context.argument(
            "service_annotations",
            options_list=["--service-annotations"],
            help=_("Comma-separated list of annotations to apply to all external services.")
        )

        # arg_context.argument(
        #     "collation",
        #     options_list=["--collation"],
        #     help=_("Default is not to specify anything and the SQL engine will handle it and default to the "
        #            "SQL engine default."),
        # )
        arg_context.argument(
            "no_external_endpoint",
            options_list=["--no-external-endpoint"],
            action="store_true",
            help=_("If specified, no external service will be created. Otherwise, an external service will be created "
                   "using the same service type as the data controller."),
        )
        # arg_context.argument(
        #     "dev",
        #     options_list=["--dev"],
        #     action="store_true",
        #     help=_("If this is specified, then it is considered a dev instance and will not be billed for."),
        # )
        # arg_context.argument(
        #     "port",
        #     options_list=["--port"],
        #     help=_("Optional."),
        # )
        arg_context.argument(
            "no_wait",
            options_list=["--no-wait"],
            action="store_true",
            help=_("If given, the command will not wait for the instance to be in a ready state before returning.")
        )

        arg_context.argument(
            "license_type",
            options_list=["--license-type"],
            help=_(f"The license type to apply for this managed instance. {SQLMI_LICENSE_TYPE_ALLOWED_VALUES_MSG_CREATE}.")
        )

        arg_context.argument(
            "tier",
            options_list=["--tier"],
            help=_(f"The pricing tier for the instance. {SQLMI_TIER_ALLOWED_VALUES_MSG_CREATE}")
        )

    with ArgumentsContext(self, "arc sql mi edit") as arg_context:
        arg_context.argument(
            "path",
            options_list=["--path"],
            help=_("The path to the src file for the SQL managed instance json file."),
        )
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help=_("The name of the SQL managed instance that is being edited. The name under which your "
                   "instance is deployed cannot be changed."),
        )
        # arg_context.argument(
        #     "namespace",
        #     options_list=["--namespace", "-ns"],
        #     help=_("Namespace where the SQL managed instance is deployed. If no namespace is specified, "
        #            "then the namespace of the data controller is used. The namespace in which your instance is "
        #            "deployed cannot be changed."),
        # )
        arg_context.argument(
            "cores_limit",
            options_list=["--cores-limit", "-cl"],
            help=_("The cores limit of the managed instance as an integer."),
        )
        arg_context.argument(
            "cores_request",
            options_list=["--cores-request", "-cr"],
            help=_("The request for cores of the managed instance as an integer."),
        )
        arg_context.argument(
            "memory_limit",
            options_list=["--memory-limit", "-ml"],
            help=_("The limit of the capacity of the managed instance as an integer."),
        )
        arg_context.argument(
            "memory_request",
            options_list=["--memory-request", "-mr"],
            help=_("The request for the capcity of the managed instance as an integer amount of memory in GBs."),
        )
        # arg_context.argument(
        #     "collation",
        #     options_list=["--collation"],
        #     help=_("Default is not to specify anything and the SQL engine will handle it and default to the SQL "
        #            "engine default."),
        # )
        # arg_context.argument(
        #     "dev",
        #     options_list=["--dev"],
        #     action="store_true",
        #     help=_("If this is specified, then it is considered a dev instance and will not be billed for."),
        # )
        # arg_context.argument(
        #     "port",
        #     options_list=["--port"],
        #     help=_("Optional."),
        # )
        arg_context.argument(
            "no_wait",
            options_list=["--no-wait"],
            action="store_true",
            help=_("If given, the command will not wait for the instance to be in a ready state before returning.")
        )

        arg_context.argument(
            "labels",
            options_list=["--labels"],
            help=_("Comma-separated list of labels of the SQL managed instance.")
        )

        arg_context.argument(
            "annotations",
            options_list=["--annotations"],
            help=_("Comma-separated list of annotations of the SQL managed instance.")
        )

        arg_context.argument(
            "service_labels",
            options_list=["--service-labels"],
            help=_("Comma-separated list of labels to apply to all external services.")
        )

        arg_context.argument(
            "service_annotations",
            options_list=["--service-annotations"],
            help=_("Comma-separated list of annotations to apply to all external services.")
        )

    with ArgumentsContext(self, "arc sql mi delete") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help=_("The name of the SQL managed instance to be deleted."),
        )
        # arg_context.argument(
        #     "namespace",
        #     options_list=["--namespace", "-ns"],
        #     help=_("Namespace where the SQL managed instance is deployed. "
        #            "If no namespace is specified, then the namespace of the data controller is used."),
        # )

    with ArgumentsContext(self, "arc sql mi get-mirroring-cert") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help=_("The name of the SQL managed instance."),
        )
        arg_context.argument(
            "cert_file",
            options_list=["--cert-file"],
            help=_("The local filename to store the retrieved certificate in PEM format.")
        )
    with ArgumentsContext(self, "arc sql mi show") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help=_("The name of the SQL managed instance to be shown."),
        )
        # arg_context.argument(
        #     "namespace",
        #     options_list=["--namespace", "-ns"],
        #     help=_("Namespace where the SQL managed instance is deployed. If not specified, it will use "
        #            "the data controller namespace."),
        # )
        arg_context.argument(
            'path',
            options_list=['--path', '-p'],
            help=_('A path where the full specification for the SQL managed instance should be '
                   'written. If omitted, the specification will be written to standard output.')
        )

    # with ArgumentsContext(self, "arc sql mi list") as arg_context:
    #     arg_context.argument(
    #         "namespace",
    #         options_list=["--namespace", "-ns"],
    #         help=_("Namespace where the SQL managed instances are deployed. If not specified, it will use "
    #                "the data controller namespace."),
    #     )

    with ArgumentsContext(self, "arc sql endpoint list") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help=_("The name of the SQL instance to be shown. If omitted, all endpoints for all instances will "
                   "be shown."),
        )
        # arg_context.argument(
        #     "namespace",
        #     options_list=["--namespace", "-ns"],
        #     help=_("Namespace where the SQL managed instance is deployed. If not specified, it will use "
        #            "the data controller namespace."),
        # )

    with ArgumentsContext(self, "arc sql mi config init") as arg_context:
        arg_context.argument(
            'path',
            options_list=['--path', '-p'],
            help=_('A path where the CRD and specification for the SQL managed instance should be '
                   'written.')
        )

    with ArgumentsContext(self, "arc sql mi config add") as arg_context:
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

    with ArgumentsContext(self, "arc sql mi config replace") as arg_context:
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

    with ArgumentsContext(self, "arc sql mi config remove") as arg_context:
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

    with ArgumentsContext(self, "arc sql mi config patch") as arg_context:
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

    with ArgumentsContext(self, "arc sql mi dag create") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name"],
            help=_("The name of the Distributed Availability Group Resource."),
        )
        arg_context.argument(
            "dag_name",
            options_list=["--dag-name"],
            help=_("The name of the Distributed Availability Group for SQL Managed Instance. Both local and remote have to use the same name."),
        )
        arg_context.argument(
            "local_name",
            options_list=["--local-name"],
            help=_("The name of the local SQL Managed Instance"),
        )
        arg_context.argument(
            "local_primary",
            options_list=["--local-primary"],
            help=_("True indicates local SQL Managed Instance is Geo Primary. False indicates local SQL Managed Instance is Geo Secondary"),
        )
        arg_context.argument(
            "remote_name",
            options_list=["--remote-name"],
            help=_("The name of the remote SQL Managed Instance or remote SQL Availability Group"),
        )
        arg_context.argument(
            "remote_url",
            options_list=["--remote-url"],
            help=_("The mirroring endpoint URL of the remote SQL Managed Instance or remote SQL Availability Group"),
        )
        arg_context.argument(
            "remote_cert_file",
            options_list=["--remote-cert-file"],
            help=_("The filename of mirroring endpoint public certficate for the remote SQL Managed Instance or remote SQL Availability Group. Only PEM format is supported"),
        )
        arg_context.argument(
            "path",
            options_list=["--path"],
            help=_("Path to the custom resource specification, i.e. custom/spec.json")
        )

    with ArgumentsContext(self, "arc sql mi dag delete") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name"],
                help=_("The name of the Distributed Availability Group Resource."),
        )

    with ArgumentsContext(self, "arc sql mi dag get") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name"],
                help=_("The name of the Distributed Availability Group Resource."),
        )
