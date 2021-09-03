# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import azdata.cli.core.deploy as util
from azdata.cli.commands.sqlmi.exceptions import CliError
from azdata.cli.core.clients.kubernetes_client import K8sApiException
from azdata.cli.commands.arc.constants import DIRECT
from azdata.cli.core.constants import (
    ARC_GROUP,
    ARC_API_VERSION,
    DATA_CONTROLLER_PLURAL)
from collections import OrderedDict
from urllib3.exceptions import NewConnectionError, MaxRetryError


def order_endpoints():
    """
    Order postgres server instance `dict` sections to the same order the server API handed us.
    NOTE: This is redundant in Python 3.7 however needed for earlier versions.

    :return: A well defined `OrderedDict` of the given SQL instance endpoints.
    """

    def get_endpoints(endpoints):
        """
        Creates ordered dictionaries for the given endpoints to be used in the BoxLayout.
        :param endpoints:
        :return:
        """
        def new_endpoint(e):
            return OrderedDict([
                ("description", e["description"]),
                ("endpoint", e["endpoint"]),
                ("options", [])
            ])

        return [new_endpoint(endpoint) for endpoint in endpoints]

    def get_instances(obj):
        """
        Returns all instances and their endpoints.
        :param obj:
        :return:
        """
        obj = obj if obj else []
        return [OrderedDict([
            ("instanceName", instance["name"]),
            ("engine", instance["engine"]),
            ("endpoints", get_endpoints(instance.get("endpoints")))
        ]) for instance in obj]

    def get_arc_postgres_endpoints(obj):
        """
        Retrieves all postgres server endpoints in an ordered dictionary to be used in the BoxLayout.
        :param obj:
        :return:
        """
        return None if "namespace" not in obj else OrderedDict([
            ("clusterName", obj["namespace"]),
            ("instance", get_instances(obj["instances"]))
        ])

    return get_arc_postgres_endpoints


def hierarchical_output(command_result):
    """
    Callback for formatting complex custom-output.
    :parm_am command_result: The command's high-level result object.
    :return: Complex BoxLayout otherwise flat json.
    """
    from azdata.cli.core.layout import BoxLayout

    try:
        raw_result = command_result.result
        result = order_endpoints()(raw_result)

        return BoxLayout(result, config={
            'headers': {
                'left': {
                    'label': '',
                    'id': None
                },
                'right': {
                    'label': '',
                    'id': None
                }
            },
            'identifiers': []
        }, bdc_config=True)
    except Exception as e:  # -- fallback --
        from knack.output import format_json
    return format_json(command_result)

def is_valid_connectivity_mode(client):
    CONNECTION_RETRY_ATTEMPTS = 12
    RETRY_INTERVAL = 5
    
    namespace = client.profile.active_context.namespace

    response = util.retry(lambda: client.apis.kubernetes.list_namespaced_custom_object(
                                    namespace,
                                    group=ARC_GROUP,
                                    version=ARC_API_VERSION,
                                    plural=DATA_CONTROLLER_PLURAL),
                            retry_count=CONNECTION_RETRY_ATTEMPTS,
                            retry_delay=RETRY_INTERVAL,
                            retry_method="list namespaced custom object",
                            retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

    dcs = response.get("items")
    if not dcs:
        raise CliError("No data controller exists in namespace `{}`."
                        .format(namespace))
    else:
        if dcs[0]['spec']['settings']['azure']['connectionMode'] == DIRECT:        
            raise CliError("Performing this action from azdata is only allowed using indirect mode. "
                    "Please use the Azure Portal to perform this action in direct connectivity mode.")
