# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.exceptions import CliError
from azdata.cli.core.util import (
    FileUtil,
    is_windows)
from azdata.cli.core.exceptions import http_status_codes
from azdata.cli.core.clients.kubernetes_client import (
    K8sApiException)
from azdata.cli.core.models.data_controller_custom_resource import DataControllerCustomResource
from azdata.cli.core.models.custom_resource_definition import CustomResourceDefinition
from azdata.cli.core.models.custom_resource import CustomResource
from azdata.cli.core.constants import (
    AZDATA_PASSWORD,
    MGMT_PROXY,
    ARC_GROUP,
    ARC_API_VERSION,
    DATA_CONTROLLER_PLURAL)
from azdata.cli.core.prompt import (prompt, prompt_pass, prompt_y_n)
from azdata.cli.commands.postgres.constants import (
    RESOURCE_KIND,
    COMMAND_UNIMPLEMENTED,
    API_VERSION,
    API_GROUP,
    DEFAULT_ENGINE_VERSION)
from azdata.cli.commands.postgres.util import is_valid_connectivity_mode
from .models.postgres_cr_model import PostgresqlCustomResource
from azdata.cli.core.exceptions import KubernetesError
from azdata.cli.core.deploy import DeploymentConfigUtil
from collections import OrderedDict
from dateutil import parser, tz
from enum import Enum
from humanfriendly.terminal.spinners import AutomaticSpinner
from knack.prompting import NoTTYException
from kubernetes import client as k8sClient

import azdata.cli.core.deploy as util
import copy
import datetime
import json
import time
import os
import re
import base64
import pathlib
import yaml
import sys
from azdata.cli.core.logging import get_logger
from urllib3.exceptions import NewConnectionError, MaxRetryError

CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5

logger = get_logger(__name__)


class progress_state(str, Enum):
    active = 'active'
    done = 'done'
    failed = 'failed'
    pending = 'pending'

# ------------------------------------------------------------------------------
# Server Commands
# ------------------------------------------------------------------------------

def arc_postgres_server_create(client,
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
                               storage_class_backups=None,
                               volume_claim_mounts=None,
                               extensions=None,
                               volume_size_data=None,
                               volume_size_logs=None,
                               volume_size_backups=None,
                               workers=None,
                               engine_version=DEFAULT_ENGINE_VERSION,
                               no_external_endpoint=None,
                               # dev=None,
                               port=None,
                               no_wait=False,
                               engine_settings=None,
                               coordinator_engine_settings=None,
                               worker_engine_settings=None):
    """
    Create an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param path: The src filepath of the postgres resource.
    :param name: The name of the Azure Arc enabled PostgreSQL Hyperscale server group.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.
    :param replicas: If specified, the instance will deploy the number of replicas, default to 1.
    :param cores_limit: The limit of cores of the managed instance in integer number of vcores.
    :param cores_request: The request for cores of the managed instance in integer number of vcores.
    :param memory_limit: The limit of the capacity of the managed instance in integer amount of memory in GBs.
    :param memory_request: The request for the capacity of the managed instance in integer amount of memory in GBs.
    :param storage_class_data: The storage classes to be used for data persistent volumes.
    :param storage_class_logs: The storage classes to be used for logs persistent volumes.
    :param storage_class_backups: The storage classes to be used for backups persistent volumes.
    :param volume_claim_mounts: A comma-separated list of volume claim mounts.
    :param volume_size_data: The volume size for the storage classes to be used for data.
    :param volume_size_logs: The volume size for the storage classes to be used for logs.
    :param volume_size_backups: The volume size for the storage classes to be used for backups.
    :param extensions: A comma-separated list of Postgres extensions that should be enabled.
    :param workers: The number of worker nodes to provision in a sharded cluster, or zero for single-node Postgres.
    :param no_external_endpoint: If not specified, an external service is created using the same service type as the dc.
    :param dev: If this is specified, then it is considered a dev instance and will not be billed for.
    :param port: Optional parameter for the service port.
    :param no_wait: If given, the command won't wait until the deployment is ready before returning.
    :param engine_settings: If given, sets the engine properties
    :param coordinator_engine_settings: If given, sets the engine settings on coordinator node
    :param worker_engine_settings: If given, sets the engine settings on worker node
    :return:
    """
    args = locals()
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        crd = _get_postgres_crd()

        # Initialize the custom resource's spec
        #
        if not path:
            # If no config file was provided, use this default spec.
            # TODO: Use mutating web hooks to set these default values.
            #
            spec_object = {
                "apiVersion": API_GROUP + '/' + API_VERSION,
                "kind": RESOURCE_KIND,
                "metadata": {},
                "spec": {
                  "scheduling": {
                    "default" : {
                      "resources" : {
                        "requests" : {
                          "memory": "256Mi"
                        }
                      }
                    }
                  },
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
                    "backups": {
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
        else:
            spec_object = FileUtil.read_json(path)

        cr = CustomResource.decode(PostgresqlCustomResource, spec_object)
        args['engine_version'] = engine_version
        cr.apply_args(**args)
        cr.metadata.namespace = namespace

        resource_kind_plural = crd.spec.names.plural

        # Temporarily uses env to set dev mode as --dev parameter is disabled
        is_dev = os.environ.get("PG_IS_DEVELOPMENT")
        if is_dev:
            cr.spec.dev = True

        # TODO possibly add this as a post-validation step
        if cr.spec.scale.shards and cr.spec.scale.shards > 0:
            if 'citus' not in cr.spec.engine.extensions:
                cr.spec.engine.extensions.insert(0, 'citus')

        # TODO possibly add this as a post-validation step
        if cr.spec.scale.replicas and cr.spec.scale.replicas > 1:
            if 'citus' not in cr.spec.engine.extensions:
                cr.spec.engine.extensions.insert(0, 'citus')

        cr.validate(client.apis.kubernetes)

        custom_object_exists = util.retry(lambda: client.apis.kubernetes.namespaced_custom_object_exists(
                                                    cr.metadata.name, cr.metadata.namespace,
                                                    group=API_GROUP,
                                                    version=API_VERSION,
                                                    plural=resource_kind_plural),
                                        retry_count=CONNECTION_RETRY_ATTEMPTS,
                                        retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                        retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

        if custom_object_exists:
            raise ValueError("Postgres Server `{}` already exists in namespace `{}`.".format(name, namespace))

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

        secret_name = name + "-login-secret"

        secret_exists = util.retry(lambda: client.apis.kubernetes.secret_exists(cr.metadata.namespace, secret_name),
                                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                                   retry_delay=RETRY_INTERVAL, retry_method="secret exists",
                                   retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

        if not secret_exists:
            pw = os.environ.get(AZDATA_PASSWORD)
            if not pw:
                if sys.stdin.isatty():
                    pw = prompt_pass("Postgres Server password:", confirm=True, allow_empty=False)
                else:
                    raise ValueError("Please provide a Postgres Server password through the env "
                                     "variable AZDATA_PASSWORD.")
            else:
                client.stdout("Using AZDATA_PASSWORD environment variable for `{}` password.".format(name))

            model = {"secretName": secret_name}
            encoding = "utf-8"
            model["base64Username"] = base64.b64encode(
                bytes("postgres", encoding)).decode(encoding)
            model["base64Password"] = base64.b64encode(
                bytes(pw, encoding)).decode(encoding)
            temp = util.get_config_from_template(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates", "postgres-login.yaml.tmpl"),
                model)
            postgres_secret = yaml.safe_load(temp)

            util.retry(
                lambda: client.apis.kubernetes.create_secret(cr.metadata.namespace, postgres_secret, ignore_conflict=True),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL, retry_method="create secret",
                retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

        util.retry(lambda: client.apis.kubernetes.create_namespaced_custom_object(cr=cr, plural=resource_kind_plural, ignore_conflict=True),
                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                   retry_delay=RETRY_INTERVAL, retry_method="create namespaced custom object",
                   retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

        if no_wait:
            client.stdout(
                "Deployed {0} in namespace `{1}`. "
                "Please use `azdata arc postgres server show -n {0}` to check its status."
                    .format(cr.metadata.name, cr.metadata.namespace))
        else:
            state = None
            if not is_windows():
                with AutomaticSpinner('Deploying {0} in namespace `{1}`'.format(cr.metadata.name, cr.metadata.namespace),
                                      show_time=True):
                    while state != 'ready' or state is None:
                        time.sleep(5)
                        response = util.retry(lambda: client.apis.kubernetes.get_namespaced_custom_object(
                                                cr.metadata.name,
                                                cr.metadata.namespace,
                                                group=API_GROUP,
                                                version=API_VERSION,
                                                plural=resource_kind_plural),
                                              retry_count=CONNECTION_RETRY_ATTEMPTS,
                                              retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                              retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

                        deployed_cr = CustomResource.decode(PostgresqlCustomResource, response)
                        state = deployed_cr.status.state
                        if state is not None:
                            state = state.lower()
            else:
                client.stdout('Deploying {0} in namespace `{1}`'.format(name, namespace))
                while state != 'ready' or state is None:
                    time.sleep(5)
                    response = util.retry(lambda: client.apis.kubernetes.get_namespaced_custom_object(
                                            cr.metadata.name,
                                            cr.metadata.namespace,
                                            group=API_GROUP,
                                            version=API_VERSION,
                                            plural=resource_kind_plural),
                                          retry_count=CONNECTION_RETRY_ATTEMPTS,
                                          retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
                                          retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

                    deployed_cr = CustomResource.decode(PostgresqlCustomResource, response)
                    state = deployed_cr.status.state
                    if state is not None:
                        state = state.lower()

            client.stdout('{0} is Ready'.format(cr.metadata.name))

    except KubernetesError as e:
        raise CliError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_postgres_server_edit(
        client,
        name,
        # namespace=None,
        replicas=None,
        path=None,
        workers=None,
        engine_version=None, # TODO: Remove engine_version override when engine_version is removed from CLI.
        cores_limit=None,
        cores_request=None,
        memory_limit=None,
        memory_request=None,
        extensions=None,
        # dev=None,
        port=None,
        no_wait=False,
        engine_settings=None,
        replace_engine_settings=None,
        coordinator_engine_settings=None,
        worker_engine_settings=None,
        admin_password=False):
    """
    Edit the configuration of an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param name: The name of the Azure Arc enabled PostgreSQL Hyperscale server group you would like to edit.
    :param path: The path to the source json file for the Azure Arc enabled PostgreSQL Hyperscale server group. This is optional.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.
    :param replicas: If specified, the instance will deploy the number of replicas
    :param workers: The number of worker nodes to provision in a sharded cluster, or zero for single-node Postgres.
    :param engine_version: Deprecated.
    :param cores_limit: The limit of cores of the managed instance in integer number of vcores.
    :param cores_request: The request for cores of the managed instance in integer number of vcores.
    :param memory_limit: The limit of the capacity of the managed instance in integer amount of memory in GBs.
    :param memory_request: The request for the capacity of the managed instance in integer amount of memory in GBs.
    :param extensions: A comma-separated list of Postgres extensions that should be enabled.
    :param dev: If this is specified, then it is considered a dev instance and will not be billed for.
    :param port: Optional parameter for the service port.
    :param no_wait: If given, the command won't wait for the deployment to be ready before returning.
    :param engine_settings: If given, sets the engine properties
    :param replace_engine_settings: If given, replaces all existing engine settings
    :param coordinator_engine_settings: If given, sets the engine settings on coordinator node
    :param worker_engine_settings: If given, sets the engine settings on worker node
    :param admin_password: The admin password for Postgres.
    :return:
    """
    args = locals()
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        # Get the Postgres resource
        old_cr, crd = _get_postgres_custom_object(client, name, namespace)
        if old_cr is None:
            raise CliError("Azure Arc enabled PostgreSQL Hyperscale server "
                            "group {} not found.".format(name))

        if path:
            # Load the spec from a file if provided
            body = FileUtil.read_json(path)
        else:
            # Otherwise clone the existing resource so we can validate against it
            body = copy.deepcopy(old_cr.encode())

        cr = CustomResource.decode(PostgresqlCustomResource, body)
        # TODO: Remove this manual override for engine_version when it's removed from CLI.
        # Currently engine_version parameter is marked as deprecated but not removed from CLI.
        # It has to be set to the current engine version in the custom resource spec.
        # Otherwise the postgres CR model will try to apply it (with the default None value) from args and fail.
        args['engine_version'] = cr.spec.engine.version
        cr.apply_args(**args)

        # TODO possibly add this as a post-validation step
        if cr.spec.scale.shards and cr.spec.scale.shards > 0:
            if 'citus' not in cr.spec.engine.extensions:
                cr.spec.engine.extensions.insert(0, 'citus')

        # Run validations that examine multiple custom resource properties
        #
        cr.validate(client.apis.kubernetes)

        # TODO: Validations on the spec should happen on the backend.
        # Until we have webhook validation configured, we'll do them here.
        # https://sqlhelsinki.visualstudio.com/aris/_workitems/edit/16349
        if cr.spec.scale.replicas and old_cr.spec.scale.replicas:
            if cr.spec.scale.replicas < old_cr.spec.scale.replicas:
                raise CliError("The number of replicas cannot be decreased.")

        # TODO: Validations on the spec should happen on the backend.
        # Until we have webhook validation configured, we'll do them here.
        # https://sqlhelsinki.visualstudio.com/aris/_workitems/edit/16349
        if cr.spec.scale.replicas == 0:
            raise CliError("The number of replicas cannot be zero.")

        # TODO possibly add this as a post-validation step
        if cr.spec.scale.replicas and cr.spec.scale.replicas > 1:
            if 'citus' not in cr.spec.engine.extensions:
                cr.spec.engine.extensions.insert(0, 'citus')

        # Update the admin password if requested
        if admin_password:
            pw = os.environ.get(AZDATA_PASSWORD)
            if not pw:
                if sys.stdin.isatty():
                    pw = prompt_pass('Postgres Server password:', confirm=True, allow_empty=False)
                else:
                    raise ValueError('Please provide a Postgres Server password '
                                     'through the AZDATA_PASSWORD environment variable.')

            client.stdout('Updating password')
            client.apis.kubernetes.patch_secret(namespace, name+'-login-secret', {'stringData': {'password': pw}})

        # Replace CR
        client.apis.kubernetes.replace_namespaced_custom_object(cr=cr, plural=crd.plural)

        if no_wait:
            client.stdout(
                "Updated {0} in namespace `{1}`. "
                "Please use `azdata arc postgres server show -n {0} to check its status."
                    .format(cr.metadata.name, cr.metadata.namespace))
        else:
            response = client.apis.kubernetes.get_namespaced_custom_object(
                cr.metadata.name, cr.metadata.namespace, group=API_GROUP, version=API_VERSION, plural=crd.plural
            )
            deployed_cr = CustomResource.decode(PostgresqlCustomResource, response)

            if not is_windows():
                with AutomaticSpinner('Updating {0} in namespace `{1}`'.format(cr.metadata.name, cr.metadata.namespace),
                                      show_time=True):
                    while not _is_instance_ready(deployed_cr):
                        time.sleep(5)
                        response = client.apis.kubernetes.get_namespaced_custom_object(
                            cr.metadata.name, cr.metadata.namespace, group=API_GROUP, version=API_VERSION, plural=crd.plural
                        )
                        deployed_cr = CustomResource.decode(PostgresqlCustomResource, response)

            else:
                client.stdout('Updating {0} in namespace `{1}`'.format(name, namespace))
                while not _is_instance_ready(deployed_cr):
                    time.sleep(5)
                    response = client.apis.kubernetes.get_namespaced_custom_object(
                        cr.metadata.name, cr.metadata.namespace, group=API_GROUP, version=API_VERSION, plural=crd.plural
                    )
                    deployed_cr = CustomResource.decode(PostgresqlCustomResource, response)

            client.stdout('{0} is Ready'.format(cr.metadata.name))

    except KubernetesError as e:
        raise CliError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_postgres_server_delete(client, name, engine_version=None, force=False):
    """
    Delete an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param name: Name of the Azure Arc enabled PostgreSQL Hyperscale server group..
    :param engine_version: Deprecated.
    :param force: A boolean indicating whether to delete the Azure Arc enabled PostgreSQL Hyperscale server group without confirmation.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        is_valid_connectivity_mode(client)

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        cr, crd = _get_postgres_custom_object(client, name, namespace)
        if cr is None:
            raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {} not found.".format(name))

        try:
            yes = force or prompt_y_n("Do you want to delete Azure Arc enabled PostgreSQL Hyperscale server group {}?".format(name))
        except NoTTYException:
            raise CliError("Please specify --force in non-interactive mode.")

        if not yes:
            client.stdout("Azure Arc enabled PostgreSQL Hyperscale server group {} not deleted.".format(name))
            return

        client.apis.kubernetes.delete_namespaced_custom_object(name=name, namespace=namespace, crd=crd)

        client.stdout("Deleted Azure Arc enabled PostgreSQL Hyperscale server group {} from namespace {}".format(name, namespace))

        client.stdout('Note: Deleting a server group does not remove its associated storage. Reach out to your Kubernetes administrator or '+
            'read documentation article "Delete an Azure Arc enabled PostgreSQL Hyperscale server group" for possible next steps.')

    except KubernetesError as e:
        raise CliError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_postgres_server_show(client, name, engine_version=None, path=None):
    """
    Show the details of an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param name: Name of the Azure Arc enabled PostgreSQL Hyperscale server group.
    :param engine_version: Deprecated.
    :param path: A path to a json file where the full specification for the Azure Arc enabled PostgreSQL Hyperscale server group should be written.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        (cr, _) = _get_postgres_custom_object(client, name, namespace, raw=True)
        if cr is None:
            raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {} not found.".format(name))
        
        if path:
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, "{}.json".format(name))
            with open(path, "w") as outfile:
                json.dump(cr, outfile, indent=4)
            client.stdout("{0} specification written to {1}".format(name, path))
        else:
            return cr

    except KubernetesError as e:
        raise CliError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_postgres_server_list(client):
    """
    List Azure Arc enabled PostgreSQL Hyperscale server groups.
    :param client:
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        crd = _get_postgres_crd()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        response = client.apis.kubernetes.list_namespaced_custom_object(
            namespace, group=API_GROUP, version=API_VERSION, plural=crd.spec.names.plural)
        # Temporary, need to discuss with PMs what standardized output we"d like for all partners
        items = response.get("items")

        result = []
        items.sort(key=lambda i:i["kind"] + "\n" + i["metadata"]["name"])
        for item in items:
            cr = CustomResource.decode(PostgresqlCustomResource, item)
            result.append(
                {"name": cr.metadata.name,
                 "workers": cr.spec.scale.shards,  # defaults to 0
                 "replicas": cr.spec.scale.replicas,  # defaults to 1
                 "state": cr.status.state})

        return result

    except KubernetesError as e:
        raise CliError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_postgres_endpoint_list(client, name=None, engine_version=None):
    """
    List Azure Arc enabled PostgreSQL Hyperscale server groups.
    :param client:
    :param name: Name of the Azure Arc enabled PostgreSQL Hyperscale server group.
    :param engine_version: Deprecated.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        custom_resources = []

        if name:
            (cr, _) = _get_postgres_custom_object(client, name, namespace)
            if cr is None:
                raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {} not found.".format(name))
            custom_resources.append(cr)
        else:
            crd = _get_postgres_crd()

            response = client.apis.kubernetes.list_namespaced_custom_object(
                namespace, group=API_GROUP, version=API_VERSION, plural=crd.spec.names.plural)
            items = response.get("items")

            for item in items:
                cr = CustomResource.decode(PostgresqlCustomResource, item)
                if cr:
                    custom_resources.append(cr)

        arc_postgres_endpoints = {"namespace": namespace}
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
                    connection_str = "postgresql://postgres:<replace with password>@{}".format(ext_endpoint)
                else:
                    connection_str = "Not yet available"
                endpoints.append({descrip_str: "PostgreSQL Instance", endpoint_str: connection_str})

                # Logs
                logs_endpoint = cr.status.log_search_dashboard
                endpoints.append({descrip_str: "Log Search Dashboard", endpoint_str: logs_endpoint})

                # Metrics
                metrics_endpoint = cr.status.metrics_dashboard
                endpoints.append({descrip_str: "Metrics Dashboard", endpoint_str: metrics_endpoint})

            instances.append({"name": cr.metadata.name, "engine": cr.kind, "endpoints": endpoints})

        arc_postgres_endpoints["instances"] = instances

        return arc_postgres_endpoints

    except KubernetesError as e:
        raise CliError(e.message)
    except Exception as e:
        raise CliError(e)


def arc_postgres_server_config_init(client, path, engine_version=None):
    """
    Returns a package of crd.json and spec-template.json.
    :param client:
    :param path:
    :param engine_version: Deprecated.
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


def arc_postgres_server_config_add(client, path, json_values):
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


def arc_postgres_server_config_replace(client, path, json_values):
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


def arc_postgres_server_config_remove(client, path, json_path):
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


def arc_postgres_server_config_patch(client, path, patch_file):
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

def arc_postgres_backup_create(client, server_name, backup_name=None, incremental=False, no_wait=False):
    """
    Create a backup of an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param server_name: Name of the Azure Arc enabled PostgreSQL Hyperscale server group.
    :param backup_name: Name of the backup. This parameter is optional.
    :param incremental: Whether the backup should be incremental. This parameter is optional.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace
        (cr, _) = _get_postgres_custom_object(client, server_name, namespace)
        if cr == None:
            raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {0} not found.".format(server_name))

        server_group_id = cr.metadata.uid
        resource_kind = cr.kind
        if no_wait:
            backup = util.retry(lambda: client.apis.controller.postgres_server_backup_create(
                    resource_kind=resource_kind,
                    namespace=namespace,
                    server_group_id=server_group_id,
                    backup_name=backup_name,
                    incremental=incremental),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="backup create",
                retry_on_exceptions=(NewConnectionError, MaxRetryError))
            client.stdout("Created backup{0}. Please use `azdata arc postgres server list` to check its status."
                    .format('' if backup_name is None else " " + backup_name))
        else:
            if not is_windows():
                with AutomaticSpinner("Creating backup{0}"
                        .format('' if backup_name is None else " " + backup_name), show_time=True):
                    backup = util.retry(lambda: client.apis.controller.postgres_server_backup_create(
                            resource_kind=resource_kind,
                            namespace=namespace,
                            server_group_id=server_group_id,
                            backup_name=backup_name,
                            incremental=incremental),
                        retry_count=CONNECTION_RETRY_ATTEMPTS,
                        retry_delay=RETRY_INTERVAL,
                        retry_method="backup create",
                        retry_on_exceptions=(NewConnectionError, MaxRetryError))
                    backup = util.retry(lambda: _wait_for_backup_state_change(
                            lambda: client.apis.controller.postgres_server_backup_show(
                                resource_kind=resource_kind,
                                namespace=namespace,
                                server_group_id=server_group_id,
                                backup_id=backup.ID)),
                        retry_count=CONNECTION_RETRY_ATTEMPTS,
                        retry_delay=RETRY_INTERVAL,
                        retry_method="backup show",
                        retry_on_exceptions=(NewConnectionError, MaxRetryError))
            else:
                backup = util.retry(lambda: client.apis.controller.postgres_server_backup_create(
                        resource_kind=resource_kind,
                        namespace=namespace,
                        server_group_id=server_group_id,
                        backup_name=backup_name,
                        incremental=incremental),
                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                    retry_delay=RETRY_INTERVAL,
                    retry_method="backup create",
                    retry_on_exceptions=(NewConnectionError, MaxRetryError))
                backup = util.retry(lambda: _wait_for_backup_state_change(
                        lambda: client.apis.controller.postgres_server_backup_show(
                            resource_kind=resource_kind,
                            namespace=namespace,
                            server_group_id=server_group_id,
                            backup_id=backup.ID)),
                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                    retry_delay=RETRY_INTERVAL,
                    retry_method="backup show",
                    retry_on_exceptions=(NewConnectionError, MaxRetryError))
        return _format_backup(backup)
    except Exception as e:
        raise CliError(e)

def arc_postgres_backup_restore(client, server_name, backup_id=None, source_server_name=None, restore_time=None):
    """
    Restore a backup of an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param server_name: Name of the target Azure Arc enabled PostgreSQL Hyperscale server group.
    :param backup_id: ID of the backup.
    :param source_server_name: Name of the source Azure Arc enabled PostgreSQL Hyperscale server group.
    :param restore_time: Restore time (for point-in-time restore).
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        (cr, _) = _get_postgres_custom_object(client, server_name, namespace)
        if cr == None:
            raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {0} not found.".format(server_name))

        server_group_id = cr.metadata.uid
        resource_kind = cr.kind
        source_server_group_id = None
        if source_server_name:
            backup_vcm_found = False
            if cr.spec.storage.volumeClaimMounts:
                backup_vcm = [m for m in cr.spec.storage.volumeClaimMounts if m['volumeType'] == 'backup']
                backup_vcm_found = len(backup_vcm) > 0
            if not backup_vcm_found:
                raise CliError('Azure Arc enabled PostgreSQL Hyperscale server group {0} is not configured '
                    'to use shared persistent volume claim for backup/restore.'.format(server_name))

            (source_cr, _) = _get_postgres_custom_object(client, source_server_name, namespace, None)
            if source_cr == None:
                raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {0} not found.".format(source_server_name))

            backup_vcm_found = False
            if source_cr.spec.storage.volumeClaimMounts:
                source_backup_vcm = [m for m in source_cr.spec.storage.volumeClaimMounts if m['volumeType'] == 'backup']
                backup_vcm_found = len(source_backup_vcm) > 0
            if not backup_vcm_found:
                raise CliError('Azure Arc enabled PostgreSQL Hyperscale server group {0} is not configured '
                    'to use shared persistent volume claim for backup/restore.'.format(source_server_name))
            
            if backup_vcm[0]['volumeClaimName'] != source_backup_vcm[0]['volumeClaimName']:
                raise CliError('Azure Arc enabled PostgreSQL Hyperscale server group {0} and {1}'
                    'do not have the same persistent volume claim.'.format(server_name, source_server_name))
                    
            source_server_group_id = source_cr.metadata.uid
        elif cr.spec.engine.version == 11:
            raise CliError("In place restore is not supported for PostgreSQL version 11.\n"
                "Restore from a different server by using the --source-server-name argument.")

        if restore_time is not None:
            restore_time = _parse_restore_time(restore_time)
        
        status = util.retry(lambda: client.apis.controller.postgres_server_backup_restore(
                resource_kind=resource_kind,
                namespace=namespace,
                server_group_id=server_group_id,
                backup_id=backup_id,
                source_server_group_id=source_server_group_id,
                time=restore_time),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="backup restore",
            retry_on_exceptions=(NewConnectionError, MaxRetryError))

        def _wait_for_restore():
            startTime = time.time()
            result = util.retry(lambda: _wait_for_backup_state_change(
                    lambda: client.apis.controller.postgres_server_backup_restore_status(
                        resource_kind=resource_kind,
                        namespace=namespace,
                        server_group_id=server_group_id)),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="backup restore status",
                retry_on_exceptions=(NewConnectionError, MaxRetryError))

            if result.progress.lower() == progress_state.done:
                # if the restore completes very quickly, it's possible that Kubernetes hasn't run the health check to notice that the pods
                # are no longer ready or that the Dusky controller hasn't updated the state based on the pods yet, so ensure we wait at least
                # 15 seconds since the restore began, unless we see the service leave the Running state sooner. (the health check interval is
                # 10 seconds, and we'll give the controller 5 seconds...)
                delay = 2.5
                while True: # wait for the service to become unready or for 15 seconds to have elapsed
                    (cr, _) = _get_postgres_custom_object(client, server_name, namespace, None)
                    if cr is None or cr.status.state != 'Ready': break
                    initialDelay = 15 - (time.time()-startTime) - delay
                    if initialDelay <= 0: break
                    time.sleep(5 if initialDelay > 5 else initialDelay)
                while cr: # and wait for the service to become ready again if desired
                    time.sleep(delay)
                    (cr, _) = _get_postgres_custom_object(client, server_name, namespace, None)
                    if cr is None or cr.status.state == 'Ready': break
                    if delay < 10: delay *= 2

            return _format_restore(result)

        if not is_windows():
            if backup_id:
                if restore_time:
                    message = "Restoring to '{0}' with backup ID '{1}'".format(restore_time, backup_id)
                else:
                    message = "Restoring backup ID '{0}'".format(backup_id)
            elif restore_time:
                message = "Restoring to '{0}'".format(restore_time)
            else:
                message = "Restoring the most recent backup"
            with AutomaticSpinner(message, show_time=True):
                return _wait_for_restore()
        else:
            return _wait_for_restore()
        
    except Exception as e:
        raise CliError(e)

def arc_postgres_backup_list(client, server_name):
    """
    Show all backups for an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param server_name: The name of the server group.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        (cr, _) = _get_postgres_custom_object(client, server_name, namespace)
        if cr == None:
            raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {0} not found."
                            " No backup was retrieved.".format(server_name))

        backups = util.retry(lambda: client.apis.controller.postgres_server_backup_list(
                resource_kind=cr.kind,
                namespace=namespace,
                server_group_id=cr.metadata.uid),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="backup list",
            retry_on_exceptions=(NewConnectionError, MaxRetryError))
        if not backups:
            logger.warn("No backups were found for PostgreSQL Hyperscale server group '{}'.".format(server_name))

        return [_format_backup(b) for b in backups]
    except Exception as e:
        raise CliError(e)

def arc_postgres_backup_delete(client, server_name, backup_name=None, backup_id=None):
    """
    Delete the backup for an Azure Arc enabled PostgreSQL Hyperscale server group.
    :param client:
    :param server_name: The name of the server group.
    :param backup_name: The name of the backup to be deleted.
    :param backup_id: The id of the backup to be deleted.
    :return:
    """
    try:
        util.check_and_set_kubectl_context()

        # TODO: Support user supplied namespace when the backend supports it
        namespace = client.profile.active_context.namespace

        (cr, _) = _get_postgres_custom_object(client, server_name, namespace)
        if cr == None:
            raise CliError("Azure Arc enabled PostgreSQL Hyperscale server group {0} not found.".format(server_name))

        not_found = "Backup '{}' was not found for PostgreSQL Hyperscale server group '{}'.".format(backup_name or backup_id, server_name)

        if backup_name is not None:
            backup_id = _get_backup_id_by_name(client, cr.kind, namespace, cr.metadata.uid, backup_name)
            if backup_id is None:
                logger.warn(not_found)
                return

        backup = util.retry(lambda: client.apis.controller.postgres_server_backup_delete(
                resource_kind=cr.kind,
                namespace=namespace,
                server_group_id=cr.metadata.uid,
                backup_id=backup_id),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="backup delete",
            retry_on_exceptions=(NewConnectionError, MaxRetryError))

        # util.retry returns True if the function it retries returns None
        if backup == True:
            logger.warn(not_found)
        else:
            return _format_backup(backup)
    except Exception as e:
        raise CliError(e)

# Returns the id of the backup with the given name if it exists.
# Raises an exception if there are multiple backups with the given name.
# Returns None if no backup was found with the given name.
def _get_backup_id_by_name(client, resource_kind, namespace, server_id, backup_name) -> str:
    backups = util.retry(lambda: client.apis.controller.postgres_server_backup_list(
                resource_kind=resource_kind,
                namespace=namespace,
                server_group_id=server_id),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="backup list",
            retry_on_exceptions=(NewConnectionError, MaxRetryError))
    backups = [b for b in backups if b.backup.name == backup_name]

    if len(backups) == 0:
        return None
    elif len(backups) > 1:
        raise ValueError("There are multiple backups named '%s'. Use -id parameter instead." % backup_name)

    return backups[0].ID

def _format_backup(resp):
    result = OrderedDict()
    result['name'] = resp.backup.name
    result['ID'] = resp.ID
    result['Type'] = resp.backup.type
    result['state'] = resp.progress
    result['timestamp'] = resp.timestamp
    result['size'] = resp.backup.size
    if not resp.status.result:
        result['error'] = resp.status.message
    return result

def _format_restore(resp):
    result = OrderedDict()
    result['ID'] = resp.ID
    result['state'] = resp.progress
    if not resp.status.result:
        result['error'] = resp.status.message
    return result

# def arc_postgres_server_restart(client, name, namespace=None):
#     """
#     Restart an Azure Arc enabled PostgreSQL Hyperscale server group.
#     :param client:
#     :param name: Name of the Azure Arc enabled PostgreSQL Hyperscale server group.
#     :param namespace: Namespace where the Azure Arc enabled PostgreSQL Hyperscale server groups are deployed.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)


# ------------------------------------------------------------------------------
# Database Commands - Unimplemented
# ------------------------------------------------------------------------------

# def arc_postgres_database_create(client, namespace, name, server_group_name, sharded=False, owner=None):
#     """
#     Create a database within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the database.
#     :param server_group_name: Name of the PostgreSQL server group.
#     :param sharded: An optional boolean that indicates whether the database should support sharding.
#     :param owner: An optional name of a user that should own the database.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)


# def arc_postgres_database_delete(client, namespace, name, server_group_name):
#     """
#     Delete a database from a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the database.
#     :param server_group_name: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_database_show(client, namespace, name, server_group_name):
#     """
#     Show the details of a PostgreSQL database.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the database.
#     :param server_group_name: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_database_edit(client, namespace, name, server_group_name, sharded=False, owner=None):
#     """
#     Edit the configuration of a database within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the database.
#     :param server_group_name: Name of the PostgreSQL server group.
#     :param sharded: An optional boolean that indicates whether the database should support sharding.
#     :param owner: An optional name of a user that should own the database.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_database_list(client, namespace, server_group_name):
#     """
#     List databases within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param server_group_name: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
#
# # ------------------------------------------------------------------------------
# # Role Commands - Unimplemented
# # ------------------------------------------------------------------------------
#
# def arc_postgres_role_create(client, namespace, name, server_group):
#     """
#     Create a role within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the role.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_role_delete(client, namespace, name, server_group):
#     """
#     Delete a role from a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the role.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_role_list(client, namespace, server_group):
#     """
#     List roles within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_role_show(client, namespace, name, server_group):
#     """
#     Show the details of a PostgreSQL role.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the role.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# # ------------------------------------------------------------------------------
# # User Commands - Unimplemented
# # ------------------------------------------------------------------------------
#
# def arc_postgres_user_create(client, namespace, name, password, roles, server_group):
#     """
#     Create a user within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the user.
#     :param password: An optional password for the user. If omitted, a password will be generated.
#     :param roles: An optional comma-separated list of roles that the user should belong to.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_user_edit(client, namespace, name, password, roles, server_group):
#     """
#     Edit the configuration of a user within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the user.
#     :param password: An optional password for the user. If omitted, a password will be generated.
#     :param roles: An optional comma-separated list of roles that the user should belong to.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_user_delete(client, namespace, name, server_group):
#     """
#     Delete a user from a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the user.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_user_list(client, namespace, server_group):
#     """
#     List users within a PostgreSQL server group.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_user_show(client, namespace, name, server_group):
#     """
#     Show the details of a PostgreSQL user.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param name: Name of the user.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# # ------------------------------------------------------------------------------
# # Volume Commands - Unimplemented
# # ------------------------------------------------------------------------------
#
# def arc_postgres_volume_delete(client, namespace, server_group=None):
#     """
#     Delete all inactive volume claims associated with one or all deleted PostgreSQL server groups.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_volume_list(client, namespace, server_group):
#     """
#     List volume claims of one or all PostgreSQL server groups.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)
#
#
# def arc_postgres_volume_show(client, namespace, server_group):
#     """
#     Show the details of a PostgreSQL volume.
#     :param client:
#     :param namespace: Namespace where the PostgreSQL server group is deployed.
#     :param server_group: Name of the PostgreSQL server group.
#     :return:
#     """
#     try:
#         client.stdout(COMMAND_UNIMPLEMENTED)
#     except Exception as e:
#         raise CliError(e)


def _get_postgres_crd():
    """
    Returns the postgresql CRD.
    :return:
    """
    api = k8sClient.ApiextensionsV1Api()
    crds = api.list_custom_resource_definition()
    for crd in crds.items:
        if crd.spec.names.kind == RESOURCE_KIND:
            return crd
    raise CliError("Unable to locate PostgreSQL custom resource definition.")


def _get_postgres_custom_object(client, name, namespace, raw=False):
    """
    Returns the custom object and the corresponding CRD as a tuple for the Azure Arc enabled PostgreSQL Hyperscale server group identified by name and engine version.
    It's possible to create multipe Azure Arc enabled PostgreSQL Hyperscale server groups with the same name but different engine version.
    Name and engine version can uniquely identify an Azure Arc enabled PostgreSQL Hyperscale server group in a namespace.
    :param client:
    :param name: The name of the instance.
    :param namespace: Namespace where the Azure Arc enabled PostgreSQL Hyperscale server group is deployed.
    :param raw: If True this function does not decode the json into a custom resource and returns the raw json instead
    :return: None will be returned if the Azure Arc enabled PostgreSQL Hyperscale server group cannot be found.
             CliError will be raised if there are multiple Azure Arc enabled PostgreSQL Hyperscale server groups found.
    """

    crd = CustomResourceDefinition(_get_postgres_crd().to_dict())

    try:
        result = client.apis.kubernetes.get_namespaced_custom_object(name=name, namespace=namespace, crd=crd)
        cr = CustomResource.decode(PostgresqlCustomResource, result)
        return (result if raw else cr), crd
    except K8sApiException as e:
        if e.status == http_status_codes.not_found:
            pass
    return None, None


def _wait_for_backup_state_change(func, *funcargs, **kwargs):
    delay = kwargs.get("delay", 5)
    while True:
        time.sleep(delay)
        result = func(*funcargs)
        if result.progress.lower() not in (progress_state.active, progress_state.pending):
            break
        delay *= 2
        if delay > 60:
            delay = 60
    return result

def _parse_restore_time(time):
    if re.match(r"^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)[mMhHdDwW]$", time) is not None:
        return time
    else:
        t = parser.parse(time)
        if t.tzinfo is None:
            t = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond, tz.tzlocal())
        return t.astimezone(tz.tzutc())


def _is_instance_ready(cr):
    return cr.metadata.generation == cr.status.observed_generation \
        and (cr.status.state is not None and cr.status.state.lower() == 'ready')