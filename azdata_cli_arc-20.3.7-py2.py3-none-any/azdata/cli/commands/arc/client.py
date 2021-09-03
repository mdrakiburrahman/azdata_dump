# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from .azure.azure_resource_client import AzureResourceClient
from azdata.cli.commands.arc import data_controller_properties
from azdata.cli.commands.arc.azure import constants as azure_constants
from azdata.cli.commands.arc.constants import (
    ARC_WEBHOOK_SPEC_TEMPLATE,
    POSTGRES_CRD,
    SQLMI_CRD,
    MONITOR_CRD,
    MONITOR_PLURAL,
    MONITOR_RESOURCE)
from azdata.cli.core.clients.cli_client import CliClient
from azdata.cli.core.models.custom_resource_definition import CustomResourceDefinition
from azdata.cli.core.models.monitor_custom_resource import MonitorCustomResource
from http import HTTPStatus
from azdata.cli.core.configuration import Configuration
from azdata.cli.core.constants import (
    ARC_NAMESPACE_LABEL,
    ARC_WEBHOOK_PREFIX,
    AZDATA_PASSWORD,
    AZDATA_USERNAME,
    DOMAIN_SERVICE_ACCOUNT_USERNAME,
    DOMAIN_SERVICE_ACCOUNT_PASSWORD,
    DOCKER_USERNAME,
    DOCKER_PASSWORD,
    REGISTRY_USERNAME,
    REGISTRY_PASSWORD)
from azdata.cli.core.clients.controller_client import ControllerClient
from azdata.cli.core.constants import (ARC_GROUP, ARC_API_VERSION, DATA_CONTROLLER_PLURAL)
from azdata.cli.core.models.data_controller_custom_resource import DataControllerCustomResource
from azdata.cli.core.models.custom_resource import CustomResource
from azdata.cli.core.exceptions import (CliError, ControllerError, KubernetesError, http_status_codes)
from azdata.cli.core.enums import ContextType
from azdata.cli.core.deploy import (display, get_config_from_template)
from azdata.cli.commands.arc.common_util import (
    is_instance_ready
)
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ConnectionError
from azdata.cli.core.logging import get_logger
from azdata.cli.commands.arc.constants import (TEMPLATE_DIR, CONTROLLER_LABEL, CONTROLLER_SVC, DIRECT)
from azdata.cli.core.models.custom_resource import CustomResource

from kubernetes.client.rest import ApiException as K8sApiException
from kubernetes import client as k8sClient
import azdata.cli.core.deploy as util
import azdata.cli.core.kubernetes as kubernetes_util
from datetime import (datetime, timedelta)
import time
import os
import yaml
import base64
import pydash as _

CONNECTION_RETRY_ATTEMPTS = 12
DELETE_CLUSTER_TIMEOUT_SECONDS = 300
RETRY_INTERVAL = 5
UPDATE_INTERVAL = (15 * 60) / RETRY_INTERVAL
logger = get_logger(__name__)
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def beget(_):
    """Client factory"""
    return ArcClientMixin()


def beget_no_check_auth(_):
    """Client factory - no check on authentication"""
    return ArcClientMixin(False)


def beget_no_check_auth_or_eula(_):
    """Client factory - no check on authentication or eula"""
    return ArcClientMixin(False, False)


class ArcClientMixin(CliClient):
    def __init__(self, check_auth=True, check_eula=True):
        super(ArcClientMixin, self).__init__(check_auth, check_eula)
        self.cluster_name = None
        self._azure_resource_client = AzureResourceClient()

    @property
    def azure_resource_client(self):
        return self._azure_resource_client

    def dc_create(self, crd: dict, cr: DataControllerCustomResource):
        """
        Create a data controller
        :param crd:
        :param cr:
        :return:
        """
        # Set up the private registry if the docker environment variables are set
        #
        if (os.environ.get(DOCKER_USERNAME) and os.environ.get(DOCKER_PASSWORD)) or \
                (os.environ.get(REGISTRY_USERNAME) and os.environ.get(REGISTRY_PASSWORD)):
            util.retry(lambda: kubernetes_util.setup_private_registry(
                cr.metadata.namespace, cr.spec.docker.registry, secret_name=cr.spec.credentials.dockerRegistry,
                ignore_conflict=True),
                       retry_count=CONNECTION_RETRY_ATTEMPTS,
                       retry_delay=RETRY_INTERVAL, retry_method="set up docker private registry",
                       retry_on_exceptions=(NewConnectionError, MaxRetryError))

        # Create the bootstrapper, if it needs to be created
        #
        util.retry(lambda: self.create_bootstrapper(cr),
                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                   retry_delay=RETRY_INTERVAL,
                   retry_method="create bootstrapper",
                   retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

        util.retry(lambda: self.apis.kubernetes.create_namespaced_custom_object(cr=cr, plural=crd.plural,
                                                                                ignore_conflict=True),
                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                   retry_delay=RETRY_INTERVAL,
                   retry_method="create namespaced custom object",
                   retry_on_exceptions=(NewConnectionError, MaxRetryError, KubernetesError))

        i = 0

        # Check if the external controller service exists
        #
        while not util.retry(lambda: self.apis.kubernetes.service_ready(cr.metadata.namespace, CONTROLLER_SVC),
                             retry_count=CONNECTION_RETRY_ATTEMPTS,
                             retry_delay=RETRY_INTERVAL,
                             retry_method="service ready",
                             retry_on_exceptions=(NewConnectionError, MaxRetryError)):
            # Log to console once every 5 minutes if controller service is not ready
            #
            if i != 0 and i % 60 == 0:
                display("Waiting for data controller service to be ready after %d "
                        "minutes." % ((i * RETRY_INTERVAL) / 60))

            time.sleep(RETRY_INTERVAL)
            i = i + 1

        # Check if controller is running
        #
        while not util.retry(lambda: self.apis.kubernetes.pod_is_running(cr.metadata.namespace, CONTROLLER_LABEL),
                             retry_count=CONNECTION_RETRY_ATTEMPTS,
                             retry_delay=RETRY_INTERVAL,
                             retry_method="pod is running",
                             retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException)):
            # Log to console once every 5 minutes if controller is not running
            #
            if i != 0 and i % 60 == 0:
                display("Waiting for data controller to be running after %d "
                        "minutes." % ((i * RETRY_INTERVAL) / 60))

            time.sleep(RETRY_INTERVAL)
            i = i + 1

        service = util.retry(lambda: self.apis.kubernetes.get_service(cr.metadata.namespace, CONTROLLER_SVC),
                             retry_count=CONNECTION_RETRY_ATTEMPTS,
                             retry_delay=RETRY_INTERVAL,
                             retry_method="get service",
                             retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

        controller_endpoint = util.retry(
            lambda: self.apis.kubernetes.get_service_endpoint(cr.metadata.namespace, service),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get service endpoint",
            retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

        ip_endpoint = util.retry(
            lambda: self.apis.kubernetes.get_service_endpoint(cr.metadata.namespace, service, True),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get service endpoint",
            retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

        if controller_endpoint == ip_endpoint:
            endpoint_str = controller_endpoint
        else:
            endpoint_str = controller_endpoint + ", " + ip_endpoint

        display("Data controller endpoint is available at {}".format(endpoint_str))

        # Use ip endpoint for basic auth during deployment
        #
        controller_endpoint = ip_endpoint

        # Get the initial throw away controller client based on basic auth for
        # the initial bootstrapping. Once controller has been stood up we ignore
        #
        cfg = Configuration()
        cfg.username = os.environ[AZDATA_USERNAME]
        cfg.password = os.environ[AZDATA_PASSWORD]
        tmp_controller_client = ControllerClient(controller_endpoint)
        tmp_controller_client.set_authorization_header(
            "Basic",
            cfg.get_basic_auth_token(strip_prefix=True)
        )

        i = 0
        while not tmp_controller_client.is_ready():
            # Log to console once every 5 minutes if controller is not ready
            #
            if i != 0 and i % 60 == 0:
                display("Waiting for data controller to be ready after %d "
                        "minutes." % ((i * RETRY_INTERVAL) / 60))

            if i != 0 and i % 12 == 0:
                self.notify_data_controller_status(tmp_controller_client)

            time.sleep(RETRY_INTERVAL)
            i = i + 1

        # Create the webhook if validation is enabled
        #
        settings = cr.spec.settings
        if ("controller" in settings and "isValidationEnabled" in settings["controller"]):
            if (settings["controller"]["isValidationEnabled"]):
                self._deploy_webhook(cr)

        # Log status once ready
        #
        self.notify_data_controller_status(tmp_controller_client)

    def monitor_endpoint_list(client, endpoint_name=None):
        """
        List endpoints for the Monitor CR.
        :param client:
        :param endpoint_name: Name of the endpoint.
        :return:
        """
        try:
            util.check_and_set_kubectl_context()

            namespace = client.profile.active_context.namespace

            response = client.apis.kubernetes.get_namespaced_custom_object(
                MONITOR_RESOURCE, namespace, group=ARC_GROUP, version=ARC_API_VERSION, plural=MONITOR_PLURAL
            )
            cr = CustomResource.decode(MonitorCustomResource, response)
            if cr is None:
                raise CliError("Monitor custom resource not found.")

            endpoints = []

            if cr.status:
                descrip_str = "description"
                endpoint_str = "endpoint"
                name_str = "name"
                protocol_str = "protocol"

                # Logs
                logs_endpoint = {
                    descrip_str: "Log Search Dashboard",
                    endpoint_str: cr.status.log_search_dashboard,
                    name_str: "logsui",
                    protocol_str: "https"
                }

                # Metrics
                metrics_endpoint = {
                    descrip_str: "Metrics Dashboard",
                    endpoint_str: cr.status.metrics_dashboard,
                    name_str: "metricsui",
                    protocol_str: "https"
                }

                if endpoint_name is None:
                    endpoints.append(logs_endpoint)
                    endpoints.append(metrics_endpoint)
                    return endpoints
                elif endpoint_name.lower().startswith("metricsui"):
                    return metrics_endpoint
                else:
                    return logs_endpoint

        except KubernetesError as e:
            raise CliError(e.message)
        except Exception as e:
            raise CliError(e)

    def _deploy_webhook(self, dc_cr: DataControllerCustomResource):
        """
        Creates the webhook for the datacontroller
        :param dc_cr: the DataController to deploy the webhook for
        :return:
        """
        namespace = dc_cr.metadata.namespace

        # Retrieve cluster configmap, pull cert, and encode in b64
        #
        cluster_config = util.retry(lambda: self.apis.kubernetes.get_config_map(namespace, "cluster-configmap"),
                                    retry_count=CONNECTION_RETRY_ATTEMPTS,
                                    retry_delay=RETRY_INTERVAL,
                                    retry_method="get config map",
                                    retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))
        raw_cert = cluster_config.data['cluster-ca-certificate.crt']
        b64_encoding = base64.b64encode(raw_cert.encode('utf-8'))
        b64_string = str(b64_encoding, 'utf-8')

        # Grab the token secret and decode
        #
        token_secret = util.retry(lambda: self.apis.kubernetes.get_secret(namespace, "webhook-token"),
                                  retry_count=CONNECTION_RETRY_ATTEMPTS,
                                  retry_delay=RETRY_INTERVAL,
                                  retry_method="get secret",
                                  retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))
        token = str(base64.b64decode(token_secret.data['token']), "utf-8")

        # Read the base spec, patch it, and deploy
        #
        with open(ARC_WEBHOOK_SPEC_TEMPLATE) as f:
            # Read and patch base webhook spec
            #
            spec_obj = yaml.safe_load(f)
            spec_obj['webhooks'][0]['clientConfig']['caBundle'] = b64_string
            spec_obj['metadata']['name'] = "{}-{}".format(ARC_WEBHOOK_PREFIX, namespace)
            spec_obj['webhooks'][0]['clientConfig']['service']['namespace'] = namespace
            spec_obj['webhooks'][0]['clientConfig']['service']['path'] = "/api/v2/arc/admissions/{}".format(token)
            spec_obj['webhooks'][0]['namespaceSelector']['matchExpressions'][0]['key'] = ARC_NAMESPACE_LABEL
            spec_obj['webhooks'][0]['namespaceSelector']['matchExpressions'][0]['values'] = [namespace]

            # Deploy Webhook
            #
            util.retry(lambda: self.apis.kubernetes.create_mutating_webhook_configuration(spec_obj),
                       retry_count=CONNECTION_RETRY_ATTEMPTS,
                       retry_delay=RETRY_INTERVAL,
                       retry_method="get secret",
                       retry_on_exceptions=(NewConnectionError, MaxRetryError, K8sApiException))

    def create_cluster_role_for_monitoring(self, dc_cr: DataControllerCustomResource, namespace):
        """
        Create a cluster role for monitoring
        :param dc_cr:
        :param namespace:
        :return:
        """
        # Create cluster role with read permission on the pod/node resources
        #
        if dc_cr.spec.security is None \
                or getattr(dc_cr.spec.security, "allowPodMetricsCollection", None) is None \
                or dc_cr.spec.security.allowPodMetricsCollection:

            service_account_name = "sa-arc-metricsdc-reader"
            cluster_role_name = namespace + ":cr-arc-metricsdc-reader"
            cluster_role_binding_name = namespace + ":crb-arc-metricsdc-reader"
            try:
                body = yaml.safe_load(util.get_config_from_template(
                    os.path.join(SCRIPT_PATH, "./templates", "clusterrole-metricsdc-reader.yaml"), cluster_role_name))
                kubernetes_util.update_cluster_role(cluster_role_name, body)

                body = k8sClient.V1ClusterRoleBinding(
                    metadata=k8sClient.V1ObjectMeta(
                        name=cluster_role_binding_name),
                    subjects=[k8sClient.V1Subject(
                        kind="ServiceAccount",
                        name=service_account_name,
                        namespace=namespace)],
                    role_ref=k8sClient.V1RoleRef(
                        kind="ClusterRole",
                        name=cluster_role_name,
                        api_group="rbac.authorization.k8s.io"))
                kubernetes_util.update_cluster_role_binding(cluster_role_binding_name, body)

            except K8sApiException as e:
                # Telegraf requires the cluster wide role for the pod collection. The azdata might not have sufficient permissions to create
                # the ClusterRole and ClusterRoleBinding for telegraf. If so, only print the warning message and keep on deployment. The pod
                # metrics will not be collected, but can be resumed automatically if the cluster role gets created at anytime.
                #
                logger.warning(e.body)
                logger.warning(
                    "Azdata does not have sufficient permissions to create '%s' ClusterRole and '%s' ClusterRoleBinding. " +
                    "If these resources already exist, please ignore this warning. Otherwise please ask your cluster administrator "
                    "to manually create them to enable the pod metrics monitoring. More details: https://aka.ms/sql-bdc-rbac",
                    cluster_role_name, cluster_role_binding_name)
                pass

    def create_bootstrapper(self, cr):
        """
        Check if the bootstrapper exists in the given namespace.
        If the bootstrapper does not exist, deploy it.
        :param cr: custom resource spec
        :return:
        """

        try:
            model = dict()
            model["namespace"] = cr.metadata.namespace
            ns = cr.metadata.namespace
            docker = cr.spec.docker

            if not self.apis.kubernetes.replica_set_exists(ns, "bootstrapper"):
                if os.environ.get("BOOTSTRAPPER_IMAGE"):
                    model["bootstrapper"] = os.environ["BOOTSTRAPPER_IMAGE"]
                else:
                    model["bootstrapper"] = "{0}/{1}/arc-bootstrapper:{2}" \
                        .format(docker.registry, docker.repository, docker.imageTag)
                model["imagePullPolicy"] = docker.imagePullPolicy
                model["imagePullSecret"] = cr.spec.credentials.dockerRegistry
                config = get_config_from_template(
                    os.path.join(TEMPLATE_DIR, "rs-bootstrapper.yaml.tmpl"),
                    model)
                rs = yaml.safe_load(config)
                self.apis.kubernetes.create_replica_set(ns, rs)

            if not self.apis.kubernetes.namespaced_role_exists(ns, "role-bootstrapper"):
                config = get_config_from_template(
                    os.path.join(TEMPLATE_DIR, "role-bootstrapper.yaml.tmpl"),
                    model)
                role = yaml.safe_load(config)
                self.apis.kubernetes.create_namespaced_role(ns, role)

            if not self.apis.kubernetes.namespaced_role_binding_exists(ns, "rb-bootstrapper"):
                config = get_config_from_template(
                    os.path.join(TEMPLATE_DIR, "rb-bootstrapper.yaml.tmpl"),
                    model)
                rb = yaml.safe_load(config)
                self.apis.kubernetes.create_namespaced_role_binding(ns, rb)

            if not self.apis.kubernetes.service_account_exists(ns, "sa-mssql-controller"):
                config = get_config_from_template(
                    os.path.join(TEMPLATE_DIR, "sa-bootstrapper.yaml.tmpl"),
                    model)
                sa = yaml.safe_load(config)
                self.apis.kubernetes.create_namespaced_service_account(ns, sa)

            if not self.apis.kubernetes.secret_exists(ns, "controller-login-secret"):
                model[AZDATA_USERNAME] = base64.b64encode(
                    bytes(os.environ[AZDATA_USERNAME], "utf-8")).decode("utf-8")
                model[AZDATA_PASSWORD] = base64.b64encode(
                    bytes(os.environ[AZDATA_PASSWORD], "utf-8")).decode("utf-8")
                config = get_config_from_template(
                    os.path.join(TEMPLATE_DIR, "controller-login-secret.yaml.tmpl"),
                    model)
                secret = yaml.safe_load(config)
                self.apis.kubernetes.create_secret(ns, secret)

            connectivity_mode = cr.spec.settings["azure"][data_controller_properties.CONNECTION_MODE].lower()
            if connectivity_mode == DIRECT and not self.apis.kubernetes.secret_exists(ns,
                                                                                      "upload-service-principal-secret"):
                model['SPN_CLIENT_ID'] = base64.b64encode(
                    bytes(os.environ['SPN_CLIENT_ID'], "utf-8")).decode("utf-8")
                model['SPN_CLIENT_SECRET'] = base64.b64encode(
                    bytes(os.environ['SPN_CLIENT_SECRET'], "utf-8")).decode("utf-8")
                model['SPN_TENANT_ID'] = base64.b64encode(
                    bytes(os.environ['SPN_TENANT_ID'], "utf-8")).decode("utf-8")
                model['SPN_AUTHORITY'] = base64.b64encode(
                    bytes(os.environ['SPN_AUTHORITY'], "utf-8")).decode("utf-8")
                config = get_config_from_template(
                    os.path.join(TEMPLATE_DIR, "secret-upload-service-principal.yaml.tmpl"),
                    model)
                secret = yaml.safe_load(config)
                self.apis.kubernetes.create_secret(ns, secret)

            # If domain service account is provided through environment and active directory mode is
            # enabled in spec, create a secret for domain service account.
            #
            if DOMAIN_SERVICE_ACCOUNT_USERNAME in os.environ and \
                    DOMAIN_SERVICE_ACCOUNT_PASSWORD in os.environ and \
                    getattr(cr.spec, "security", None) is not None and \
                    getattr(cr.spec.security, "activeDirectory", None) is not None and \
                    not self.apis.kubernetes.secret_exists(ns, "domain-service-account-secret"):
                model[DOMAIN_SERVICE_ACCOUNT_USERNAME] = base64.b64encode(
                    bytes(os.environ[DOMAIN_SERVICE_ACCOUNT_USERNAME], "utf-8")).decode("utf-8")
                model[DOMAIN_SERVICE_ACCOUNT_PASSWORD] = base64.b64encode(
                    bytes(os.environ[DOMAIN_SERVICE_ACCOUNT_PASSWORD], "utf-8")).decode("utf-8")
                config = get_config_from_template(
                    os.path.join(TEMPLATE_DIR, "domain-service-account-secret.yaml.tmpl"),
                    model)
                secret = yaml.safe_load(config)
                self.apis.kubernetes.create_secret(ns, secret)

        except K8sApiException as e:
            raise KubernetesError(e)

    def dc_delete(self, namespace, name):
        """
        Delete a data controller.
        :param namespace: Namespace in which the data controller is deployed.
        :param name: Name of the data controller.
        :return:
        """
        if not util.retry(kubernetes_util.namespace_exists, namespace,
                          retry_count=CONNECTION_RETRY_ATTEMPTS, retry_delay=RETRY_INTERVAL,
                          retry_method="check if namespace exists",
                          retry_on_exceptions=(NewConnectionError, MaxRetryError)):
            display("Namespace '%s' doesn't exist" % namespace)
            return

        # Try to delete the cluster
        #
        i = 1
        resources_are_deleted = False
        http_status = None
        cluster_is_empty = False
        while not cluster_is_empty:

            time.sleep(RETRY_INTERVAL)

            if not resources_are_deleted:
                #  Try to delete the remaining resources in the cluster
                #
                (resources_are_deleted, http_status) = util.retry(kubernetes_util.delete_cluster_resources, namespace,
                                                                  retry_count=CONNECTION_RETRY_ATTEMPTS,
                                                                  retry_delay=RETRY_INTERVAL,
                                                                  retry_method="delete cluster resources",
                                                                  retry_on_exceptions=(
                                                                      NewConnectionError, MaxRetryError))
                #  Try to delete the bootstrapper
                #
                util.retry(kubernetes_util.delete_cluster_resources,
                           namespace,
                           "app=bootstrapper",
                           retry_count=CONNECTION_RETRY_ATTEMPTS,
                           retry_delay=RETRY_INTERVAL,
                           retry_method="delete cluster resources",
                           retry_on_exceptions=(
                               NewConnectionError, MaxRetryError))

                if (http_status == HTTPStatus.FORBIDDEN):
                    break

            # Check if the cluster is empty
            #
            cluster_is_empty = util.retry(kubernetes_util.namespace_is_empty, namespace,
                                          retry_count=CONNECTION_RETRY_ATTEMPTS,
                                          retry_delay=RETRY_INTERVAL, retry_method="namespace is empty",
                                          retry_on_exceptions=(NewConnectionError, MaxRetryError))

            if i * RETRY_INTERVAL > DELETE_CLUSTER_TIMEOUT_SECONDS:
                logger.warn("Data controller is not empty after %d minutes." % (DELETE_CLUSTER_TIMEOUT_SECONDS / 60))
                break

            i = i + 1
            time.sleep(RETRY_INTERVAL)

        if not cluster_is_empty:
            raise Exception("Failed to delete data controller.")

    def get_data_controller(self, cluster_name):
        """
        Get data control
        :param cluster_name: cluster name
        :return:
        """
        self.cluster_name = cluster_name

        data_controller_list = util.retry(
            lambda: self.apis.kubernetes.list_namespaced_custom_object(
                namespace=cluster_name,
                group=ARC_GROUP,
                version=ARC_API_VERSION,
                plural=DATA_CONTROLLER_PLURAL),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL, retry_method="get namespaced custom object",
            retry_on_exceptions=(NewConnectionError, MaxRetryError))

        data_controller_cr = None

        # Kubernetes will not block the creation of more than one datacontroller in a namespace. To prevent multiple datacontrollers
        # from being deployed in the same namespace, we update the state for any datacontrollers deployed after the first to
        # state "duplicateerror". To avoid using the incorrect datacontroller custom resource, search for the instance
        # that is not in an error state.
        #
        for data_controller in data_controller_list["items"]:
            if data_controller["status"]["state"] != "" and data_controller["status"][
                "state"].lower() != "duplicateerror":
                data_controller_cr = data_controller
                break

        dc_settings = data_controller_cr["spec"]["settings"]
        return {
            'instanceName': dc_settings["controller"][data_controller_properties.DISPLAY_NAME],
            'instanceNamespace': self.cluster_name,
            'kind': azure_constants.RESOURCE_KIND_DATA_CONTROLLER,
            'subscriptionId': dc_settings["azure"][data_controller_properties.SUBSCRIPTION],
            'resourceGroupName': dc_settings["azure"][data_controller_properties.RESOURCE_GROUP],
            'location': dc_settings["azure"][data_controller_properties.LOCATION],
            'connectionMode': dc_settings["azure"][data_controller_properties.CONNECTION_MODE],
            'infrastructure': data_controller_cr["spec"]["infrastructure"],
            'publicKey': "",
            'k8sRaw': data_controller_cr,
            'infrastructure': _.get(data_controller_cr, 'spec.infrastructure')
        }

    def list_all_custom_resource_instances(self, cluster_name):
        """
        list all custom resource instances
        :param cluster_name:
        :return:
        """
        result = []
        crd_files = [POSTGRES_CRD, SQLMI_CRD]

        for crd_file in crd_files:
            # Create the control plane CRD if it doesn't already exist
            with open(crd_file, "r") as stream:
                temp = yaml.safe_load(stream)
                crd = CustomResourceDefinition(temp)

                try:
                    response = self.apis.kubernetes.list_namespaced_custom_object(cluster_name, crd=crd)
                except K8sApiException as e:
                    if e.status == http_status_codes.not_found:
                        # CRD has not been applied yet, because no custom resource of this kind has been created yet
                        continue
                    else:
                        raise e

                for item in response['items']:
                    spec = item['spec']
                    status = item['status'] if 'status' in item else None

                    if status and 'state' in status and status['state'].lower() == 'ready':
                        result.append({
                            'kind': item['kind'],
                            'instanceName': item['metadata']['name'],
                            'instanceNamespace': item['metadata']['namespace'],
                            'creationTimestamp': item['metadata']['creationTimestamp'],
                            'externalEndpoint': status['externalEndpoint'] if 'externalEndpoint' in status else '-',
                            'vcores': str(spec['limits']['vcores']) if 'limits' in spec and 'vcores' in spec[
                                'limits'] else '-',
                            'k8sRaw': item
                        })

        return result

    def list_deleted_resource_instances(self):
        """
        List resources instances deleted within the last 45 days.
        :return:
        """
        # Custom must export and upload usage at least monthly. Thus 45 days is sufficient to
        # catch all deletion since last export.
        start_date = datetime.now() - timedelta(days=45)

        instances = util.retry(self.apis.controller.list_deleted_resources, start_date,
                               retry_count=CONNECTION_RETRY_ATTEMPTS,
                               retry_delay=RETRY_INTERVAL, retry_method="list deleted resources",
                               retry_on_exceptions=(NewConnectionError, MaxRetryError))

        return map(
            lambda x: {
                'kind': x.kind,
                'instanceName': x.name,
                'instanceNamespace': x.namespace,
                'uid': x.uid
            },
            instances)

    def create_dc_azure_resource(self, data_controller):
        """
        Create a shadow resource for the data controller.
        :param data_controller: The data controller.
        """
        util.retry(lambda: self.azure_resource_client.create_azure_data_controller(
            uid=data_controller['k8sRaw']['metadata']['uid'],
            resource_name=data_controller['instanceName'],
            subscription_id=data_controller['subscriptionId'],
            resource_group_name=data_controller['resourceGroupName'],
            location=data_controller['location'],
            public_key=data_controller['publicKey'],
            extended_properties=
            {
                'k8sRaw': _.get(data_controller, 'k8sRaw'),
                'infrastructure': _.get(data_controller, 'infrastructure')
            }),
                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                   retry_delay=RETRY_INTERVAL,
                   retry_method="create Azure data controller",
                   retry_on_exceptions=(ConnectionError, NewConnectionError, MaxRetryError))

    def create_azure_resource(self, resource, data_controller):
        """
        Create a shadow resource for custom resource.
        :param resource: The custom resource.
        :param data_controller: The data controller.
        """
        util.retry(lambda: self.azure_resource_client.create_azure_resource(
            instance_type=azure_constants.RESOURCE_TYPE_FOR_KIND[resource['kind']],
            data_controller_name=data_controller['instanceName'],
            resource_name=resource['instanceName'],
            subscription_id=data_controller['subscriptionId'],
            resource_group_name=data_controller['resourceGroupName'],
            location=data_controller['location'],
            extended_properties={'k8sRaw': _.get(resource, 'k8sRaw')}),
                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                   retry_delay=RETRY_INTERVAL,
                   retry_method="create Azure resource",
                   retry_on_exceptions=(ConnectionError, NewConnectionError, MaxRetryError))

    def delete_azure_resource(self, resource, data_controller):
        """
        Delete the shadow resource for custom resource.
        :param resource: The custom resource.
        :param data_controller: The data controller.
        """
        resource_name = resource['instanceName']
        instance_type = azure_constants.RESOURCE_TYPE_FOR_KIND[resource['kind']]
        subscription_id = data_controller['subscriptionId']
        resource_group_name = data_controller['resourceGroupName']

        util.retry(self.azure_resource_client.delete_azure_resource,
                   resource_name,
                   instance_type,
                   subscription_id,
                   resource_group_name,
                   retry_count=CONNECTION_RETRY_ATTEMPTS,
                   retry_delay=RETRY_INTERVAL, retry_method="delete Azure resource",
                   retry_on_exceptions=(ConnectionError, NewConnectionError, MaxRetryError))

    def get_usages(self, max_sequence_id_last_upload):
        request_body = {"rowCountLimit": 10000, "maxSequenceIdLastUpload": max_sequence_id_last_upload}
        return self.apis.controller.usages_post(body=request_body)

    def calculate_usage(self, namespace, exclude_curr_period):
        request_body = {"namespace": namespace, "excludeCurrentPeriod": exclude_curr_period}
        return self.apis.controller.usage_calculate_post(body=request_body)

    def upload_usages_dps(self, data_controller, usage, timestamp, correlation_vector):
        import zlib
        import base64
        import json

        uncompressed_usage = json.loads(
            str(zlib.decompress(base64.b64decode(usage['usages']), -zlib.MAX_WBITS), 'utf-8'))

        return self.azure_resource_client.upload_usages_dps(
            cluster_id=data_controller['k8sRaw']['metadata']['uid'],
            correlation_vector=correlation_vector,
            name=data_controller['instanceName'],
            subscription_id=data_controller['subscriptionId'],
            resource_group_name=data_controller['resourceGroupName'],
            location=data_controller['location'],
            connection_mode=data_controller['connectionMode'],
            infrastructure=data_controller['infrastructure'],
            timestamp=timestamp,
            usages=uncompressed_usage,
            signature=usage['signature'],
        )

    @staticmethod
    def notify_data_controller_status(controller):
        """
        Notifies status of deployment
        :param controller:
        :return:
        """
        try:
            resources = controller.get_control_status()["resources"]

            ready = 0

            for k in range(len(resources)):
                if resources[k]["state"] == "ready":
                    ready += 1

            display("{0} out of {1} resources are ready.".format(ready, len(resources)))

        except ControllerError as e:
            logger.info("Data controller service is not ready yet.")

        except Exception as e:
            logger.error(e)
