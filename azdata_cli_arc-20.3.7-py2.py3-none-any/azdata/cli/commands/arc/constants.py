# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os

ARC_NAME = 'arc'
"""
Command group constant
"""

DATA_CONTROLLER_CUSTOM_RESOURCE = 'datacontroller'
"""
Name of control plane custom resource
"""

EXPORT_TASK_CUSTOM_RESOURCE = 'export'
"""
Name of export task custom resource
"""

CONTROLLER_LABEL = 'controller'
"""
Name of the controller app label
"""

CONTROLLER_SVC = 'controller-svc-external'
"""
Name of external controller service
"""

MGMT_PROXY = 'mgmtproxy-svc-external'
"""
Name of management proxy service
"""

MONITOR_PLURAL = 'monitors'
"""
Plural name for Monitor custom resource.
"""

MONITOR_RESOURCE = 'monitorstack'
"""
Monitor resource.
"""

BASE = os.path.dirname(os.path.realpath(__file__))
"""
Base directory
"""

CONFIG_DIR = os.path.join(BASE, 'deployment-configs')
"""
Config directory
"""

TEMPLATE_DIR = os.path.join(BASE, 'templates')
"""
Custom resource definition directory
"""

DATA_CONTROLLER_CRD = os.path.join(TEMPLATE_DIR, 'data_controller_crd.yaml')
"""
File location for control plane CRD.
"""

MONITOR_CRD = os.path.join(TEMPLATE_DIR, 'monitor_crd.yaml')
"""
File location for monitor CRD.
"""

POSTGRES_CRD = os.path.join(TEMPLATE_DIR, 'postgres_crd.yaml')
"""
File location for postgres CRD.
"""

SQLMI_CRD = os.path.join(TEMPLATE_DIR, 'sqlmi_crd.yaml')
"""
File location for sqlmi CRD.
"""

SQLMI_RESTORE_TASK_CRD = os.path.join(TEMPLATE_DIR, 'sqlmi_restore_task_crd.yaml')
"""
File location for sqlmi restore CRD.
"""

DAG_CRD = os.path.join(TEMPLATE_DIR, 'dag_crd.yaml')
"""
File location for distributed AG CRD.
"""


EXPORT_TASK_CRD = os.path.join(TEMPLATE_DIR, 'export-crd.yaml')
"""
File location for export task CRD.
"""

ARC_WEBHOOK_SPEC_TEMPLATE = os.path.join(TEMPLATE_DIR, 'test-hook.yaml')
"""
Template for the arc webhook
"""

HELP_DIR = os.path.join(CONFIG_DIR, 'help')
"""
Help config directory
"""

CONTROL_CONFIG_FILENAME = 'control.json'
"""
Control config file name
"""

CONFIG_FILES = [CONTROL_CONFIG_FILENAME]
"""
Array of config file names from profiles
"""

LAST_BILLING_USAGE_FILE = "usage-{}.json"
"""
Name of last usage file exported before deleting data controller
"""

LAST_USAGE_UPLOAD_FLAG = "end_usage"
"""
Key of flag in usage file indicating last usage upload
"""

EXPORT_TASK_RESOURCE_KIND = "ExportTask"
"""
Defines the export resource kind name.
"""

EXPORT_TASK_RESOURCE_KIND_PLURAL = "exporttasks"
"""
Defines the export resource kind plural name.
"""

TASK_API_GROUP = "tasks.arcdata.microsoft.com"
"""
Defines the API group.
"""

MAX_POLLING_ATTEMPTS = 12
"""
Max retry attepts to get custom resource status
"""

EXPORT_COMPLETED_STATE = "Completed"
"""
Export completed state
"""

DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE = 28
"""
Default metric query window in minute
"""

DEFAULT_LOG_QUERY_WINDOW_IN_DAY = 14
"""
Default log query window in day
"""

DEFAULT_USAGE_QUERY_WINDOW_IN_DAY = 62
"""
Default usage query window in day
"""

DEFAULT_QUERY_WINDOW = {
    'metrics': DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE,
    'logs': DEFAULT_LOG_QUERY_WINDOW_IN_DAY,
    'usage': DEFAULT_USAGE_QUERY_WINDOW_IN_DAY
}

"""
Default query window for three types of data
"""

############################################################################
# Data Controller constants
############################################################################

GUID_REGEX = r'[0-9a-f]{8}\-([0-9a-f]{4}\-){3}[0-9a-f]{12}'
"""
Used to validate subscription IDs
"""

DIRECT="direct"
"""
Direct connection mode
"""

INDIRECT="indirect"
"""
Indirect connection mode
"""

CONNECTIVITY_TYPES = [DIRECT, INDIRECT]
"""
Supported connectivity types for data controller
"""

SUPPORTED_REGIONS = ['eastus', 'eastus2', 'centralus', 'westeurope', 'southeastasia', 'westus2', 'japaneast', 'australiaeast', 'koreacentral', 'northeurope', 'uksouth', 'francecentral']
"""
Supported Azure regions for data controller. This list does not include EUAP regions.
"""

SUPPORTED_EUAP_REGIONS = ['eastus2euap', 'centraluseuap', 'eastasia']
"""
Supported Azure EUAP regions for data controller.
"""

INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES = set(["aws", "gcp", "azure", "alibaba", "onpremises", "other"])
INFRASTRUCTURE_PARAMETER_DEFAULT_VALUE = "other"
INFRASTRUCTURE_PARAMETER_INVALID_VALUE_MSG = 'Please input a valid infrastructure. Supported values are: ' + ', '.join(INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES) + '.'
