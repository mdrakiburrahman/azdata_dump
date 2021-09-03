# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import json
import os
import base64
import yaml
import sys
import time
import azdata.cli.core.deploy as util
import azdata.cli.core.kubernetes as kubernetes_util

from azdata.cli.core.logging import get_logger
from azdata.cli.core.constants import (
    AZDATA_USERNAME,
    AZDATA_PASSWORD,
    ARC_GROUP,
    ARC_API_VERSION,
    DATA_CONTROLLER_PLURAL)
from azdata.cli.core.labels import parse_labels
from azdata.cli.core.prompt import (prompt, prompt_pass)
from azdata.cli.commands.sqlmi.exceptions import SqlmiError
from azdata.cli.commands.sqlmi.util import (
    is_valid_sql_password, 
    is_valid_connectivity_mode,
    validate_labels_and_annotations,
)
from azdata.cli.core.util import (
    FileUtil,
    is_windows)
from azdata.cli.core.clients.kubernetes_client import (
    K8sApiException)
from azdata.cli.core.models.data_controller_custom_resource import DataControllerCustomResource
from azdata.cli.core.models.custom_resource_definition import CustomResourceDefinition
from azdata.cli.commands.sqlmi.constants import (RESOURCE_KIND, RESOURCE_KIND_PLURAL, API_GROUP, API_VERSION, SQLMI_LICENSE_TYPE_DEFAULT, SQLMI_TIER_DEFAULT)
from azdata.cli.commands.sqlmi.models.sqlmi_cr_model import (SqlmiCustomResource)
from azdata.cli.core.models.constants import(DAG_RESOURCE_KIND, DAG_RESOURCE_KIND_PLURAL, DAG_API_GROUP, DAG_API_VERSION)
from azdata.cli.core.models.dag_cr import (DagCustomResource)
from azdata.cli.core.exceptions import (KubernetesError, CliError, http_status_codes)
from azdata.cli.core.deploy import DeploymentConfigUtil
from humanfriendly.terminal.spinners import AutomaticSpinner
from urllib3.exceptions import NewConnectionError, MaxRetryError
from azdata.cli.core.models.custom_resource import CustomResource
CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5

logger = get_logger(__name__)


def arc_sql_mi_create(
        client,
        name,
        path=None,
        # namespace=None,
        replicas=None,
        cores_limit=None,
        cores_request=None,
        memory_limit=None,
        memory_request=None,
        storage_class_data=None,
        storage_class_logs=None,
        storage_class_datalogs=None,
        storage_class_backups=None,
        volume_size_data=None,
        volume_size_logs=None,
        volume_size_datalogs=None,
        volume_size_backups=None,
        no_external_endpoint=None,
        labels=None,
        annotations=None,
        service_labels=None,
        service_annotations=None,
        # dev=None,
        # port=None,
        no_wait=False,
        license_type=None,
        tier=None):
    """
    Create a SQL managed instance.
    :param client:
    :param path: The path to the src file for the SQL managed instance json file.
    :param name: The name of the Azure SQL managed instance.
    :param namespace: Namespace where the Azure SQL managed instance is to be deployed.
    :param replicas: If specified, the instance will deploy the number of replicas, default to 1.
    :param cores_limit: The cores limit of the managed instance as an integer.
    :param cores_request: The request for cores of the managed instance as an integer.
    :param memory_limit: The limit of the capacity of the managed instance as an integer.
    :param memory_request: The request for the capacity of the managed instance as an integer amount of memory in GBs.
    :param storage_class_data: The storage classes to be used for data
    :param storage_class_logs: The storage classes to be used for logs (/var/log).
    :param storage_class_datalogs: The storage class to be used for data-logs (/var/opt/mssql/data-log)
    :param storage_class_backups: The storage classes to be used for logs (/var/opt/mssql/backups).
    :param volume_size_data: The volume size for the storage classes to be used for data.
    :param volume_size_logs: The volume size for the storage classes to be used for logs.
    :param volume_size_datalogs: The volume size for the storage classes to be used for data logs.
    :param volume_size_backups: The volume size for the storage classes to be used for backups.
    :param no_external_endpoint: If not specified, an external service is created using the same service type as dc.
    :param dev: If this is specified, then it is considered a dev instance and will not be billed for.
    :param labels: If specified, applies the set of labels to the resource's metadata.
    :param annotations: If specified, applies the set of annotations to the resource's metadata.
    :param service_labels: If specified, applies the set of labels to all external service specifications.
    :param service_annotations: If specified, applies the set of annotations to all external service specifications.
    :param port: Optional. Default is 31433.
    :param no_wait: If given, the command won't wait for the deployment to be ready before returning.
    :return:
    """
    args = locals()
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        #
        namespace = client.profile.active_context.namespace

        # Determine source for the resource spec preferring path first
        #
        if not path:
            # TODO: Use mutating web hooks to set these default values
            #
            spec_object = {
                "apiVersion": API_GROUP + '/' + API_VERSION,
                "kind": RESOURCE_KIND,
                "metadata": {},
                "spec": {
                  "tier": SQLMI_TIER_DEFAULT,
                  "licenseType": SQLMI_LICENSE_TYPE_DEFAULT,
                  "storage": {
                    "data": {
                        "volumes": [
                            {
                                "size": "5Gi"
                            }
                        ]
                    },
                    "logs": {
                        "volumes": [
                            {
                                "size": "5Gi"
                            }
                        ]
                    },
                  }
                }
              }

        # Otherwise, use the provided src file.
        #
        else:
            spec_object = FileUtil.read_json(path)

        # Decode base spec and apply args. Must patch namespace in separately since it's not parameterized in this func
        #
        cr = CustomResource.decode(SqlmiCustomResource, spec_object)
        cr.metadata.namespace = namespace
        cr.apply_args(**args)
        cr.validate(client.apis.kubernetes)

        # Temporarily uses env to set dev mode as --dev parameter is disabled
        is_dev = os.environ.get("SQL_MI_IS_DEVELOPMENT")
        if is_dev:
            cr.spec.dev = True

        if replicas:
            try:
                if int(replicas) != 3 and int(replicas)!=2 and int(replicas) != 1:
                    raise CliError('Count of replica nodes must be 1-3.')
                cr.spec.replicas = int(replicas)
            except ValueError as e:
                raise CliError(e)

        validate_labels_and_annotations(labels, annotations, service_labels, service_annotations)

        custom_object_exists = util.retry(lambda: client.apis.kubernetes.namespaced_custom_object_exists(
            name, namespace,
            group=API_GROUP,
            version=API_VERSION,
            plural=RESOURCE_KIND_PLURAL),
                                          retry_count=CONNECTION_RETRY_ATTEMPTS,
                                          retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                          retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))
        if custom_object_exists:
            raise ValueError("Arc SQL managed instance `{}` already exists in namespace `{}`.".format(name, namespace))

        if not no_external_endpoint:
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
                raise CliError("No data controller exists in namespace `{}`. Cannot set external endpoint argument."
                               .format(namespace))
            else:
                is_valid_connectivity_mode(client)
                dc_cr = CustomResource.decode(DataControllerCustomResource, dcs[0])
                cr.spec.services.primary.serviceType = dc_cr.get_controller_service().serviceType

        # Create login secret
        #
        secret_name = name + "-login-secret"

        secret_exists = util.retry(lambda: client.apis.kubernetes.secret_exists(cr.metadata.namespace, secret_name),
                                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                                   retry_delay=RETRY_INTERVAL, retry_method="secret exists",
                                   retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

        if not secret_exists:

            # Username
            username = os.environ.get(AZDATA_USERNAME)
            if not username:
                if sys.stdin.isatty():
                    username = prompt("Arc SQL managed instance username:")
                else:
                    raise ValueError("Please provide an Arc SQL managed instance password through the env "
                                     "variable AZDATA_USERNAME.")
            else:
                client.stdout("Using AZDATA_USERNAME environment variable for `{}` username.".format(name))

            while username == "sa" or username == "":
                if username == "sa":
                    username = prompt("The login 'sa' is not allowed.  Please use a different login.")
                if username == "":
                    username = prompt("Login username required. Please enter a login.")

            # Password
            pw = os.environ.get(AZDATA_PASSWORD)
            if not pw:
                if sys.stdin.isatty():
                    while not pw:
                        pw = prompt_pass("Arc SQL managed instance password:", True)
                        if not is_valid_sql_password(pw, "sa"):
                            client.stdout("\nError: SQL Server passwords must be at least 8 characters long, cannot "
                                            "contain the username, and must contain characters from three of the"
                                            " following four sets: Uppercase letters, Lowercase letters, Base 10 digits,"
                                            "and Symbols. Please try again.\n")
                            pw = None
                else:
                    raise ValueError("Please provide an Arc SQL managed instance password through the env "
                                     "variable AZDATA_PASSWORD.")
            else:
                client.stdout("Using AZDATA_PASSWORD environment variable for `{}` password.".format(name))

            secrets = dict()
            encoding = "utf-8"
            secrets["secretName"] = secret_name
            secrets["base64Username"] = base64.b64encode(
                bytes(username, encoding)).decode(encoding)
            secrets["base64Password"] = base64.b64encode(
                bytes(pw, encoding)).decode(encoding)
            temp = util.get_config_from_template(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates", "useradmin-login.yaml.tmpl"),
                secrets)
            mssql_secret = yaml.safe_load(temp)

            try:
                util.retry(
                    lambda: client.apis.kubernetes.create_secret(cr.metadata.namespace, mssql_secret, ignore_conflict=True),
                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                    retry_delay=RETRY_INTERVAL, retry_method="create secret",
                    retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

            except K8sApiException as e:
                if e.status != http_status_codes.conflict:
                    raise

        # Create custom resource
        #
        util.retry(lambda: client.apis.kubernetes.create_namespaced_custom_object(cr=cr, plural=RESOURCE_KIND_PLURAL, ignore_conflict=True),
                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                   retry_delay=RETRY_INTERVAL, retry_method="create namespaced custom object",
                   retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

        if no_wait:
            client.stdout(
                "Deployed {0} in namespace `{1}`. Please use `azdata arc sql mi show -n {0}` to check its status."
                    .format(cr.metadata.name, cr.metadata.namespace))
        else:
            response = client.apis.kubernetes.get_namespaced_custom_object(
                cr.metadata.name, cr.metadata.namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
            )
            deployed_cr = CustomResource.decode(SqlmiCustomResource, response)
            if not is_windows():
                with AutomaticSpinner('Deploying {0} in namespace `{1}`'.format(cr.metadata.name, cr.metadata.namespace),
                                      show_time=True):
                    while not _is_instance_ready(deployed_cr):
                        time.sleep(5)
                        response = util.retry(lambda: client.apis.kubernetes.get_namespaced_custom_object(
                                                        cr.metadata.name, cr.metadata.namespace,
                                                        group=API_GROUP,
                                                        version=API_VERSION,
                                                        plural=RESOURCE_KIND_PLURAL),
                                              retry_count=CONNECTION_RETRY_ATTEMPTS,
                                              retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                              retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

                        deployed_cr = CustomResource.decode(SqlmiCustomResource, response)
            else:
                client.stdout('Deploying {0} in namespace `{1}`'.format(name, namespace))
                while not _is_instance_ready(deployed_cr):
                    time.sleep(5)
                    response = util.retry(lambda: client.apis.kubernetes.get_namespaced_custom_object(
                                                    cr.metadata.name, cr.metadata.namespace,
                                                    group=API_GROUP,
                                                    version=API_VERSION,
                                                    plural=RESOURCE_KIND_PLURAL),
                                          retry_count=CONNECTION_RETRY_ATTEMPTS,
                                          retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                          retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

                    deployed_cr = CustomResource.decode(SqlmiCustomResource, response)

            client.stdout('{0} is Ready'.format(cr.metadata.name))

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except ValueError as e:
        raise CliError(e)
    except Exception as e:
        raise CliError(e)

def arc_sql_mi_edit(
        client,
        name,
        # namespace=None,
        path=None,
        cores_limit=None,
        cores_request=None,
        memory_limit=None,
        memory_request=None,
        labels=None,
        annotations=None,
        service_labels=None,
        service_annotations=None,
        # dev=None,
        # port=None,
        no_wait=False):
    """
    Edit the configuration of a SQL managed instance.
    :param client:
    :param path: The path to the src file for the SQL managed instance json file.
    :param name: The name of the Azure SQL managed instance.
    :param namespace: Namespace where the Azure SQL managed instance is to be deployed.
    :param cores_limit: The cores limit of the managed instance as an integer.
    :param cores_request: The request for cores of the managed instance as an integer.
    :param memory_limit: The limit of the capacity of the managed instance as an integer.
    :param memory_request: The request for the capcity of the managed instance as an integer amount of memory in GBs.
    :param labels: If specified, applies the set of labels to the resource's metadata.
    :param annotations: If specified, applies the set of annotations to the resource's metadata.
    :param service_labels: If specified, applies the set of labels to all external service specifications.
    :param service_annotations: If specified, applies the set of annotations to all external service specifications.
    :param dev: If this is specified, then it is considered a dev instance and will not be billed for.
    :param port: Optional. Default is 31433.
    :param no_wait: If given, the command won't wait for the deployment to be ready before returning.
    :return:
    """
    args = locals()
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        if path:
            # Read src file for edit
            json_object = FileUtil.read_json(path)
        else:
            json_object = client.apis.kubernetes.get_namespaced_custom_object(
                name=name, namespace=namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL)

        validate_labels_and_annotations(labels, annotations, service_labels, service_annotations)

        cr = CustomResource.decode(SqlmiCustomResource, json_object)
        cr.apply_args(**args)
        cr.validate(client.apis.kubernetes)

        # Patch CR
        client.apis.kubernetes.patch_namespaced_custom_object(cr=cr, plural=RESOURCE_KIND_PLURAL)

        if no_wait:
            client.stdout(
                "Updated {0} in namespace `{1}`. Please use `azdata arc sql mi show -n {0} to check its status."
                    .format(cr.metadata.name, cr.metadata.namespace))
        else:
            response = client.apis.kubernetes.get_namespaced_custom_object(
                cr.metadata.name, cr.metadata.namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
            )
            deployed_cr = CustomResource.decode(SqlmiCustomResource, response)
            if not is_windows():
                with AutomaticSpinner('Updating {0} in namespace `{1}`'.format(cr.metadata.name, cr.metadata.namespace),
                                      show_time=True):
                    while not _is_instance_ready(deployed_cr):
                        time.sleep(5)
                        response = client.apis.kubernetes.get_namespaced_custom_object(
                            cr.metadata.name, cr.metadata.namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
                        )
                        deployed_cr = CustomResource.decode(SqlmiCustomResource, response)
            else:
                client.stdout('Updating {0} in namespace `{1}`'.format(name, namespace))
                while not _is_instance_ready(deployed_cr):
                    time.sleep(5)
                    response = client.apis.kubernetes.get_namespaced_custom_object(
                        cr.metadata.name, cr.metadata.namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
                    )
                    deployed_cr = CustomResource.decode(SqlmiCustomResource, response)

            client.stdout('{0} is Ready'.format(cr.metadata.name))

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CliError(e)

def _is_instance_ready(cr):
    """
    Verify that the SQL Mi instance is ready
    :param cr: Instance to check the readiness of
    :return: True if the instance is ready, False otherwise
    """
    return cr.metadata.generation == cr.status.observed_generation \
        and (cr.status.state is not None and cr.status.state.lower() == 'ready')

def arc_sql_mi_delete(client, name):
    """
    Delete a SQL managed instance.
    :param client:
    :param name: Name of the SQL managed instance.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        is_valid_connectivity_mode(client)

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        client.apis.kubernetes.delete_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group=API_GROUP,
            version=API_VERSION,
            plural=RESOURCE_KIND_PLURAL
        )

        client.stdout("Deleted {} from namespace {}".format(name, namespace))

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_sql_mi_show(client, name, path=None):
    """
    Show the details of a SQL managed instance.
    :param client:
    :param name: Name of the SQL managed instance.
    :param path: A path where the full specification for the SQL managed instance should be written.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        response = client.apis.kubernetes.get_namespaced_custom_object(
            name, namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
        )

        if path:
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, "{}.json".format(name))
            with open(path, "w") as outfile:
                json.dump(response, outfile, indent=4)
            client.stdout("{0} specification written to {1}".format(name, path))
        else:
            return response

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CliError(e)

def arc_sql_mi_getmirroringcert(
        client,
        name,
        cert_file):

    args = locals()
    try:
        util.check_and_set_kubectl_context()
        is_valid_connectivity_mode(client)
        namespace = client.profile.active_context.namespace

        json_object = client.apis.kubernetes.get_namespaced_custom_object(
            name=name, namespace=namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL)
        if not (cert_file):
            raise CliError('cert_file cannot be null')

        cr = CustomResource.decode(SqlmiCustomResource, json_object)
        cr.apply_args(**args)
        cr.validate(client.apis.kubernetes)

        cr = CustomResource.decode(SqlmiCustomResource, json_object)
        if cr.spec.replicas > 1:
            config_map = kubernetes_util.get_config_map(namespace, 'sql-config-{0}'.format(name))
            data_pem = config_map.data["sql-mirroring-cert"]
            client.stdout('result write to file {0}: {1}'.format(cert_file, data_pem))

            file = open(cert_file,"w")
            file.write(data_pem)
            file.close()
        else:
            raise CliError('More than 1 replica needed MIAA HA scenario.')
    except Exception as e:
        raise CliError(e)

def arc_sql_mi_list(client):
    """
    List SQL managed instances.
    :param client:
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        response = client.apis.kubernetes.list_namespaced_custom_object(
            namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
        )

        items = response.get("items")

        result = []

        # Temporary, need to discuss what the intended structure is across partners
        #
        for item in items:
            cr = CustomResource.decode(SqlmiCustomResource, item)
            result.append(
                {"name": cr.metadata.name,
                 "primaryEndpoint": cr.status.primaryEndpoint,
                 "replicas": cr.status.readyReplicas,
                 "state": cr.status.state})

        return result

    except KubernetesError as e:
        raise SqlmiError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_sql_endpoint_list(client, name=None):
    """
    List endpoints for the given SQL managed instance(s).
    :param client:
    :param name: Name of the SQL managed instance.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        custom_resources = []

        if name:
            response = client.apis.kubernetes.get_namespaced_custom_object(
                name, namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
            )
            cr = CustomResource.decode(SqlmiCustomResource, response)
            if cr is None:
                raise CliError("SQL managed instance {} not found.".format(name))
            custom_resources.append(cr)
        else:
            response = client.apis.kubernetes.list_namespaced_custom_object(
                namespace, group=API_GROUP, version=API_VERSION, plural=RESOURCE_KIND_PLURAL
            )

            items = response.get("items")

            for item in items:
                cr = CustomResource.decode(SqlmiCustomResource, item)
                if cr:
                    custom_resources.append(cr)

        arc_sql_endpoints = {"namespace": namespace}
        instances = []

        # Loop through the specified custom resources and retrieve their endpoints from their status
        for cr in custom_resources:
            endpoints = []

            if cr.status:
                descrip_str = "description"
                endpoint_str = "endpoint"

                # Connection string
                ext_endpoint = cr.status.primaryEndpoint
                if ext_endpoint:
                    connection_str = ext_endpoint
                else:
                    connection_str = "Not yet available"
                endpoints.append({descrip_str: "SQL Managed Instance", endpoint_str: connection_str})

                # Logs
                logs_endpoint = cr.status.log_search_dashboard
                endpoints.append({descrip_str: "Log Search Dashboard", endpoint_str: logs_endpoint})

                # Metrics
                metrics_endpoint = cr.status.metrics_dashboard
                endpoints.append({descrip_str: "Metrics Dashboard", endpoint_str: metrics_endpoint})

                # Readable Secondary Endpoint
                secondary_service_endpoint = cr.status.secondaryServiceEndpoint
                if secondary_service_endpoint:
                    endpoints.append({descrip_str: "SQL Managed Instance Readable Secondary Replicas", endpoint_str: secondary_service_endpoint})

            instances.append({"name": cr.metadata.name, "endpoints": endpoints})

        arc_sql_endpoints["instances"] = instances

        return arc_sql_endpoints

    except KubernetesError as e:
        raise CliError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_sql_mi_config_init(client, path):
    """
    Returns a package of crd.json and spec-template.json.
    :param client:
    :param path:
    :return:
    """
    try:
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

        if not is_windows():
            with AutomaticSpinner("Fetching {0} template".format(RESOURCE_KIND),
                                  show_time=True):
                crd_response = client.apis.controller.resource_crd_get(RESOURCE_KIND)
                spec_response = client.apis.controller.resource_spec_get(RESOURCE_KIND)
        else:
            crd_response = client.apis.controller.resource_crd_get(RESOURCE_KIND)
            spec_response = client.apis.controller.resource_spec_get(RESOURCE_KIND)

        crd_pretty = json.dumps(crd_response, indent=4)
        spec_pretty = json.dumps(spec_response, indent=4)

        with open(os.path.join(path, "crd.json"), "w") as output:
            output.write(crd_pretty)

        with open(os.path.join(path, "spec.json"), "w") as output:
            output.write(spec_pretty)

        client.stdout("{0} template created in directory: {1}".format(RESOURCE_KIND, path))

    except Exception as e:
        raise CliError(e)


def arc_sql_mi_config_add(client, path, json_values):
    """
    Add new key and value to the given config file
    :param client:
    :param path:
    :param json_values:
    :return:
    """
    try:
        config_object = DeploymentConfigUtil.config_add(path, json_values)
        DeploymentConfigUtil.write_config_file(path, config_object)
    except Exception as e:
        raise CliError(e)


def arc_sql_mi_config_replace(client, path, json_values):
    """
    Replace the value of a given key in the given config file
    :param client:
    :param path:
    :param json_values:
    :return:
    """
    try:
        config_object = DeploymentConfigUtil.config_replace(path, json_values)
        DeploymentConfigUtil.write_config_file(path, config_object)
    except Exception as e:
        raise CliError(e)


def arc_sql_mi_config_remove(client, path, json_path):
    """
    Remove a key from the given config file
    :param client:
    :param path:
    :param json_path:
    :return:
    """
    try:
        config_object = DeploymentConfigUtil.config_remove(path, json_path)
        DeploymentConfigUtil.write_config_file(path, config_object)
    except Exception as e:
        raise CliError(e)


def arc_sql_mi_config_patch(client, path, patch_file):
    """
    Patch a given file against the given config file
    :param client:
    :param path:
    :param patch_file:
    :return:
    """
    try:
        config_object = DeploymentConfigUtil.config_patch(path, patch_file)
        DeploymentConfigUtil.write_config_file(path, config_object)
    except Exception as e:
        raise CliError(e)

def CustomResourceFuntion(client, cr):
    state = None
    results = None

    if client.apis.kubernetes.namespaced_custom_object_exists(
            cr.metadata.name,
            cr.metadata.namespace,
            group=DAG_API_GROUP,
            version=DAG_API_VERSION,
            plural=DAG_RESOURCE_KIND_PLURAL):
        raise ValueError("Rest API DAG Function API `{}` already exists in namespace `{}`.".format(cr.metadata.name, cr.metadata.namespace))
    
    # Create custom resource
    #
    util.retry(lambda: client.apis.kubernetes.create_namespaced_custom_object(cr=cr, plural=DAG_RESOURCE_KIND_PLURAL, ignore_conflict=True),
               retry_count=CONNECTION_RETRY_ATTEMPTS,
               retry_delay=RETRY_INTERVAL, retry_method="create namespaced custom object",
               retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))
    
    client.stdout('waiting...')
    state = None
    if not is_windows():
        with AutomaticSpinner('Deploying {0} in namespace `{1}`'.format(cr.metadata.name, cr.metadata.namespace),
                              show_time=True):
            while state != 'succeeded' and state != 'failed' or state is None:
                time.sleep(5)
                response = util.retry(lambda: client.apis.kubernetes.get_namespaced_custom_object(
                                                cr.metadata.name, cr.metadata.namespace,
                                                group=DAG_API_GROUP,
                                                version=DAG_API_VERSION,
                                                plural=DAG_RESOURCE_KIND_PLURAL),
                                      retry_count=CONNECTION_RETRY_ATTEMPTS,
                                      retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                      retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))
    
                deployed_cr = CustomResource.decode(DagCustomResource, response)
                state = deployed_cr.status.state
                results = deployed_cr.status.results
                if state is not None:
                    state = state.lower()
    else:
        client.stdout('Deploying {0} in namespace `{1}`'.format(name, namespace))
        while state != 'succeeded' and state != 'failed' or state is None:
            time.sleep(5)
            response = util.retry(lambda: client.apis.kubernetes.get_namespaced_custom_object(
                                            cr.metadata.name, cr.metadata.namespace,
                                            group=DAG_API_GROUP,
                                            version=DAG_API_VERSION,
                                            plural=DAG_RESOURCE_KIND_PLURAL),
                                  retry_count=CONNECTION_RETRY_ATTEMPTS,
                                  retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                  retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))
    
            deployed_cr = CustomResource.decode(DagCustomResource, response)
            state = deployed_cr.status.state
            results = deployed_cr.status.results
            if state is not None:
                state = state.lower()
    
    client.stdout('{0} is Ready'.format(cr.metadata.name))
    
    return state,results

"""
Create Distributed Availability Group between two sql mi instances.
:param client:
:param path:  The path to the src file for the SQL DAG json file.
:param name: The name of the DAG Custom Resource.
:param dag_name: The name of the DAG Name.
:param local_name: The name of the local SQL MI instance name.
:param local_primary: True or False: True indicates local SQL MI Instance is primary.
:param remote_name: The name of the remote SQL MI instance name.
:param remote_cert_file: the file name for remote SQL MI mirroring endpoint certficate.
:return:
"""
def arc_sql_mi_dag_create(
        client,
        name,
        dag_name,
        local_name,
        local_primary,
        remote_name,
        remote_url,
        remote_cert_file,
        path=None):

    args = locals()
    try:
        util.check_and_set_kubectl_context()
        is_valid_connectivity_mode(client)
        namespace = client.profile.active_context.namespace

        # Determine source for the resource spec preferring path first
        #
        if not path:
            # TODO: Use mutating web hooks to set these default values
            #
            spec_object = {
                "apiVersion": DAG_API_GROUP + '/' + DAG_API_VERSION,
                "kind": DAG_RESOURCE_KIND,
                "metadata": {
                    "name": name
                },
                "spec": {
                    "input": {
                        "dagName" : dag_name,
                        "localName": local_name,
                        "remoteName": remote_name,
                        "remoteEndpoint": remote_url,
                        "remotePublicCert" : "",
                        "isLocalPrimary" : local_primary
                    }
                }
            }

        # Otherwise, use the provided src file.
        #
        else:
            spec_object = FileUtil.read_json(path)

        # Decode base spec and apply args. Must patch namespace in separately since it's not parameterized in this func
        #
        cr = CustomResource.decode(DagCustomResource, spec_object)
        cr.metadata.namespace = namespace
        cr.validate(client.apis.kubernetes)

        file = open(remote_cert_file,"r")
        remotePublicCert = file.read()
        file.close()

        cr.spec.input.remotePublicCert = remotePublicCert
        
        client.stdout('create_namespaced_custom_object {0}'.format(cr._to_dict()))

        state, results = CustomResourceFuntion(client, cr)

        if state != 'succeeded':
            raise CliError('Create Distributed AG return state({0}), result({1})'.format(state,results))

    except Exception as e:
        raise CliError(e)

"""
Delete Distributed Availability Group by deleting DAG custom resource.
:param client:
:param name: The name of the DAG Custom Resource.
:return:
"""
def arc_sql_mi_dag_delete(
        client,
        name):

    args = locals()
    try:
        util.check_and_set_kubectl_context()
        is_valid_connectivity_mode(client)
        namespace = client.profile.active_context.namespace

        if not (name):
            raise CliError('name {0} cannot be null'.format(name))

        client.apis.kubernetes.delete_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group=DAG_API_GROUP,
            version=DAG_API_VERSION,
            plural=DAG_RESOURCE_KIND_PLURAL
        )
        client.stdout("Deleted dag {} from namespace {}".format(name, namespace))

    except Exception as e:
        raise CliError(e)


"""
Get custom resource spec for a Distributed Availability Group
:param client:
:param name: The name of the DAG Custom Resource.
:return:
"""
def arc_sql_mi_dag_get(
        client,
        name):
    try:
        util.check_and_set_kubectl_context()
        is_valid_connectivity_mode(client)
        namespace = client.profile.active_context.namespace
        response = client.apis.kubernetes.get_namespaced_custom_object(
            name, namespace, group=DAG_API_GROUP, version=DAG_API_VERSION, plural=DAG_RESOURCE_KIND_PLURAL
        )
        cr = CustomResource.decode(DagCustomResource, response)
        client.stdout("input: {}".format(json.dumps(cr.spec.input._to_dict(),indent=4)))
        client.stdout("status: {}".format(json.dumps(cr.status._to_dict(),indent=4)))
    except Exception as e:
        raise CliError(e)
