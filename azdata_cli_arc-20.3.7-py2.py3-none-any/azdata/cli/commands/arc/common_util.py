# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


# Arc command util
import json
import os
import re

from azdata.cli.commands.arc import constants as dc_constants
from azdata.cli.commands.arc import export_instance_properties as instance_properties
from azdata.cli.commands.arc.constants import (
    INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES,
    INFRASTRUCTURE_PARAMETER_INVALID_VALUE_MSG
)
from azdata.cli.commands.arc.azure import constants as azure_constants
from azdata.cli.core.configuration import Configuration
from azdata.cli.core.deploy import display

from knack.prompting import (
    prompt,
    prompt_y_n,
    NoTTYException
)

############################################################################
# -- Helper functions to validate data controller parameters
############################################################################

def _validate_azure_subscription_id(sid):
    msg = 'Please input a valid Azure subscription ID.'
    if not sid:
        raise ValueError(msg)
    if sid and not re.match(dc_constants.GUID_REGEX, sid):
        msg = "{} is invalid. ".format(sid) + msg
        raise ValueError(msg)


def _validate_azure_resource_location(loc):
    msg = 'Please input a valid Azure location. Supported regions are: ' + ', '.join(dc_constants.SUPPORTED_REGIONS) + '.'
    # If location was not provided or an invalid location was provided
    if not loc or not (loc.lower() in dc_constants.SUPPORTED_REGIONS or loc.lower() in dc_constants.SUPPORTED_EUAP_REGIONS):
        raise ValueError(msg)

def _validate_infrastructure(infrastructure):
    msg = INFRASTRUCTURE_PARAMETER_INVALID_VALUE_MSG
    # If infrastructure was is invalid
    if not infrastructure or not (infrastructure in dc_constants.INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES):
        raise ValueError(msg)

def _validate_resource_group(rg):
    msg = 'Please input a valid Azure resource group'
    if not rg:
        raise ValueError(msg)


def _validate_namespace(ns):
    msg = 'Please enter a valid name for the Kubernetes namespace'
    if not ns:
        raise ValueError(msg)


def _validate_connectivity_type(cn):
    msg = 'Please enter a valid connectivity type. Options are: {}'.format(dc_constants.CONNECTIVITY_TYPES)
    # If conn_type was not provided or an invalid conn_type was provided
    if not cn or cn.lower() not in dc_constants.CONNECTIVITY_TYPES:
        raise ValueError(msg)


def _validate_data_controller_name(name):
    msg = 'Please enter a valid name for the Data Controller'
    if not name:
        raise ValueError(msg)


def _validate_config(profile_name=None, path=None):
    # -- Error if both profile_name and config_profile are specified --
    if profile_name and path:
        raise ValueError("Cannot specify both 'profile-name' and 'path'. Please specify only one.")


def validate_dc_create_params(
        name,
        namespace,
        subscription,
        location,
        resource_group,
        connectivity_mode,
        infrastructure,
        profile_name=None,
        path=None):
    """
    Validates the supplied arguments for 'arc dc create' command
    """
    _validate_config(profile_name, path)
    _validate_namespace(namespace)
    _validate_data_controller_name(name)
    _validate_azure_subscription_id(subscription)
    _validate_connectivity_type(connectivity_mode)
    _validate_resource_group(resource_group)
    _validate_azure_resource_location(location)
    _validate_infrastructure(infrastructure)

# #############################################################################
# Metric/log common functions
# #############################################################################

def get_resource_uri(resource, data_controller):
    resource_kind = resource[instance_properties.KIND]

    if resource_kind in azure_constants.RESOURCE_TYPE_FOR_KIND:
        return azure_constants.RESOURCE_URI.format(
            data_controller[instance_properties.SUBSCRIPTION_ID],
            data_controller[instance_properties.RESOURCE_GROUP],
            azure_constants.RESOURCE_TYPE_FOR_KIND[resource_kind],
            resource[instance_properties.INSTANCE_NAME])
    else:
        display('"{}" instance type "{}" is not supported.'.format(
            resource[instance_properties.INSTANCE_NAME], resource_kind))
        return None


def get_config_file(file, throw_exception=True):
    cli_name = Configuration().CLI_NAME
    config_dir = os.path.expanduser(Configuration().CLI_CONFIG_DIR)
    query_file = os.path.join(config_dir, '{}-{}'.format(cli_name, file))

    query_file_exists = os.path.exists(query_file)
    if not query_file_exists and throw_exception:
        raise ValueError('Please make sure "{}" exists'.format(query_file))
    return query_file


def get_output_file(file_path, force):
    # Check export file exists or not
    msg = 'Please provide a file name with the path: '
    export_file_exists = True
    overwritten = False

    while export_file_exists and not overwritten:
        export_file_exists = os.path.exists(file_path)
        if not force and export_file_exists:
            try:
                yes = prompt_y_n(
                    '{} exists already, do you want to overwrite it?'.format(
                        file_path))
            except NoTTYException as e:
                raise NoTTYException(
                    '{} Please make sure the file does not exist in a non-interactive environment'.format(e))

            overwritten = True if yes else False

            if not overwritten:
                file_path = prompt(msg)
                export_file_exists = True
                overwritten = False
            else:
                os.remove(file_path)
        elif force:
            overwritten = True
            if export_file_exists:
                os.remove(file_path)

    return file_path


def write_file(file_path, data, export_type, data_timestamp=None):
    result = {
        "exportType": export_type,
        "dataTimestamp": data_timestamp,
        "data": data,
    }
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, indent=4)

    output_type = export_type
    display(
        '\t\t{} are exported to {}.'.format(output_type.capitalize(), file_path))

############################################################################
# File I/O
############################################################################

def write_output_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(content, json_file, indent=4)

def get_valid_dc_infrastructures():
    """
    Get the valid sql license types
    """
    return INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES

############################################################################
# Custom Resource Utils
############################################################################

def is_instance_ready(cr):
    """
    Verify that the custom resource instance is ready
    :param cr: Instance to check the readiness of
    :return: True if the instance is ready, False otherwise
    """
    return cr.metadata.generation == cr.status.observed_generation \
        and (cr.status.state is not None and cr.status.state.lower() == 'ready')
