# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import re
from azdata.cli.core.labels import parse_labels
import azdata.cli.core.deploy as util
from azdata.cli.commands.arc.constants import DIRECT
from azdata.cli.commands.sqlmi.constants import (
    SQLMI_PASSWORD_CHARS,
    SQLMI_PASSWORD_MIN_LENGTH,
    SQLMI_PASSWORD_REQUIRED_GROUPS)
from azdata.cli.commands.sqlmi.exceptions import SqlmiError
from azdata.cli.core.clients.kubernetes_client import K8sApiException
from azdata.cli.core.constants import (
    ARC_GROUP,
    ARC_API_VERSION,
    DATA_CONTROLLER_PLURAL)
from collections import OrderedDict
from urllib3.exceptions import NewConnectionError, MaxRetryError

from azdata.cli.commands.sqlmi.constants import (
    SQLMI_LICENSE_TYPES,
    SQLMI_TIERS,
)

def is_valid_sql_password(pw, user):
    """
    Checks if the provided pw is a valid sql server password i.e. is at least
    eight characters long and contains a char from at least three of these groups
    -Uppercase letters
    -Lowercase letters
    -Base 10 digits
    -Non-alphanumeric characters
    :param pw: the password
    :param user: username for the sql instance
    :return: True if pw meets requirements, False otherwise
    """
    if not pw:
        return False

    if user in pw:
        return False

    if len(pw) < SQLMI_PASSWORD_MIN_LENGTH:
        return False

    lower = 0
    upper = 0
    special = 0
    digit = 0

    for c in pw:
        if c.isdigit():
            digit = 1
        elif c.isalpha():
            if c.isupper():
                upper = 1
            else:
                lower = 1

    special_chars = re.compile(SQLMI_PASSWORD_CHARS)
    if special_chars.search(pw) is not None:
        special = 1

    return (lower + upper + special + digit) >= SQLMI_PASSWORD_REQUIRED_GROUPS


def order_endpoints():
    """
    Order SQL instance `dict` sections to the same order the server API handed us.
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
            ("endpoints", get_endpoints(instance.get("endpoints")))
        ]) for instance in obj]

    def get_arc_sql_endpoints(obj):
        """
        Retrieves all SQL instance endpoints in an ordered dictionary to be used in the BoxLayout.
        :param obj:
        :return:
        """
        return None if "namespace" not in obj else OrderedDict([
            ("clusterName", obj["namespace"]),
            ("instance", get_instances(obj["instances"]))
        ])

    return get_arc_sql_endpoints


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
        # Checks if connectivity mode is valid (only indirect mode is allowed)
        #
        if dcs[0]['spec']['settings']['azure']['connectionMode'] == DIRECT:        
            raise SqlmiError("Performing this action from azdata is only allowed using indirect mode. "
                    "Please use the Azure Portal to perform this action in direct connectivity mode.")

def get_valid_sql_license_types():
    """
    Get the valid sql license types
    """
    return SQLMI_LICENSE_TYPES

def get_valid_sql_tiers():
    """
    Get the valid sql tiers
    """
    return SQLMI_TIERS

def validate_sqlmi_tier(tier):
    """
    returns True if tier is valid
    """

    # tier should have a default value
    if tier is None:
        return False

    # if tier was provided, make sure it's within the allowed values (case insensitive)
    if tier.lower() in (t.lower() for t in get_valid_sql_tiers()):
        return True

    return False

def validate_sqlmi_license_type(license_type):
    """
    returns True if license type is valid
    """
    
    # license_type should have a default value
    if license_type is None:
        return False

    # if license_type was provided, make sure it's within the allowed values (case insensitive)
    if license_type.lower() in (t.lower() for t in get_valid_sql_license_types()):
        return True

    return False

def validate_labels_and_annotations(labels, annotations, service_labels, service_annotations):
    if labels:
        try:
            parse_labels(labels)
        except ValueError as e:
            raise CliError("Labels invalid: {e}")

    if annotations:
        try:
            parse_labels(annotations)
        except ValueError as e:
            raise CliError("Annotations invalid: {e}")

    if service_labels:
        try:
            parse_labels(service_labels)
        except ValueError as e:
            raise CliError("Service labels invalid: {e}")

    if service_annotations:
        try:
            parse_labels(service_annotations)
        except ValueError as e:
            raise CliError("Service annotations invalid: {e}")
