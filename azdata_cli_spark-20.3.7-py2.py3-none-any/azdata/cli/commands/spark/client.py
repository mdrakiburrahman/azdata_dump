# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
from requests_kerberos import HTTPKerberosAuth, REQUIRED, OPTIONAL
from azdata.cli.core.clients.cli_client import CliClient
from azdata.cli.core.exceptions import CliError, http_status_codes
from azdata.cli.commands.spark.exceptions import *
from azdata.cli.core.enums import (SecurityStrategy, ContextType)


def beget(_):
    """Client factory"""
    return SparkClientMixin(check_auth=True, check_eula=True)


class SparkClientMixin(CliClient):
    def __init__(self, check_auth=False, check_eula=False):
        """
        :param check_auth: Set to `True` to have this command enforce authentication
                           before running.
        :param check_auth: Set to `True` to have this command enforce eula
                           acceptance before running.
        """
        super(SparkClientMixin, self).__init__(
            check_auth=check_auth, check_eula=check_eula
        )

    def get_livy_endpoint(self):
        """
        Call the controller to get the webhdfs endpoint URL
        """
        try:
            endpoint = self.apis.controller.get_endpoints('livy')['endpoint']

            # The endpoint must end with '/' in order for the APIs to succeed
            if not endpoint[len(endpoint) - 1] == '/':
                endpoint = endpoint + '/'
        except Exception as e:
            raise CliError(e)

        return endpoint

    def login(self, livy_url, username=None, password=None):
        self.livy_url_prefix = livy_url

        if self.profile.active_context.security_strategy == SecurityStrategy.basic:
            self.livy_auth = HTTPBasicAuth(username, password)
        elif self.profile.active_context.security_strategy == SecurityStrategy.ad:
            self.livy_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL, sanitize_mutual_error_response=False, force_preemptive = True)
        else:
            raise CliError("Invalid security strategy.  Use azdata login to choose supported strategy.")

        self.request_extra_opts = { 'verify':False, 'auth':self.livy_auth}
        return

    def add_request_extra_opts(self, request_extra_opts):
        self.request_extra_opts = { **self.request_extra_opts, **request_extra_opts}
        return

    def _decode_list(self, value):
        """
        Some Spark parameters need to be lists of values.  For example list of files, archives, or py_files.
        This function checks to see if the content is a json array and if so decodes it.  Otherwise use
        the value as a single array entry.

        Example:
            ["c:\\windows\\assembly", "c:\\windows\assembly\\cache"]
        """
        if value.strip().startswith('['):
            result = json.loads(value)
        else:
            result = [ value ]

        return result

    def _decode_dictionary(self, value):
        """
        Some Spark parameters need to be dictionary of name value pairs.  For example configuration dictionary.
        This function checks to see if the content is a json dictionary and if so decodes it.

        Example:
            { "name": "value", "another_name": "another_value" }
        """
        if value.strip().startswith('{'):
            result = json.loads(value)
        else:
            raise ValueError("Value must be JSON encoded dictionary [{0}].".format(value))

        return result

    def create_session(self,
                       session_kind = None,
                       jars=None,
                       py_files=None,
                       files=None,
                       driver_memory=None,
                       driver_cores = None,
                       executor_memory = None,
                       executor_cores = None,
                       executor_count = None,
                       archives = None,
                       queue = None,
                       name = None,
                       configuration = None,
                       timeout_seconds = None):
        request_body = {}
        if not session_kind == None: request_body["kind"] = session_kind
        if not jars == None: request_body["jars"] = self._decode_list(jars)
        if not py_files == None: request_body["pyFiles"] = self._decode_list(py_files)
        if not files == None: request_body["files"] = self._decode_list(files)
        if not driver_memory == None: request_body["driverMemory"] = driver_memory
        if not driver_cores == None: request_body["driverCores"] = int(driver_cores)
        if not executor_memory == None: request_body["executorMemory"] = executor_memory
        if not executor_cores == None: request_body["executorCores"] = int(executor_cores)
        if not executor_count == None: request_body["numExecutors"] = int(executor_count)
        if not archives == None: request_body["archives"] = self._decode_list(archives)
        if not queue == None: request_body["queue"] = queue
        if not name == None: request_body["name"] = name
        if not configuration == None: request_body["conf"] = self._decode_dictionary(configuration)
        if not timeout_seconds == None: request_body["heartbeatTimeoutInSecond"] = timeout_seconds

        response = self._submit_request(requests.post, True, "/sessions/",
                                        body_data=request_body,
                                        extra_headers={'content-type': 'application/json'})
        if not response.status_code == http_status_codes.created:
            self._raise_exception(response)
        return response.json()

    def list_sessions(self):
        response = self._submit_request(requests.get, True, "/sessions/")
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def session_info(self, session_id):
        response = self._submit_request(requests.get, True, "/sessions/{0}/".format(session_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def session_log(self, session_id):
        response = self._submit_request(requests.get, True, "/sessions/{0}/log".format(session_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def session_state(self, session_id):
        response = self._submit_request(requests.get, True, "/sessions/{0}/state".format(session_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def delete_session(self, session_id):
        response = self._submit_request(requests.delete, True, "/sessions/{0}/".format(session_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def create_statement(self, session_id, code): # TODO Add Kind optional parameter, add option to run to completion
        response = self._submit_request(requests.post, True, "/sessions/{0}/statements".format(session_id), body_data={"code": "{0}".format(code)},
                                        extra_headers={'content-type': 'application/json'})
        if not response.status_code == http_status_codes.created:
            self._raise_exception(response)
        return response.json()

    def list_statements(self, session_id):
        response = self._submit_request(requests.get, True, "/sessions/{0}/statements".format(session_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def statement_info(self, session_id, statement_id):
        response = self._submit_request(requests.get, True, "/sessions/{0}/statements/{1}".format(session_id, statement_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def cancel_statement(self, session_id, statement_id):
        response = self._submit_request(requests.delete, True, "/sessions/{0}/statements/{1}/cancel".format(session_id, statement_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def create_batch(self,
                     file_to_execute,
                     class_name=None,
                     arguments=None,
                     jars=None,
                     py_files=None,
                     files=None,
                     driver_memory=None,
                     driver_cores = None,
                     executor_memory = None,
                     executor_cores = None,
                     executor_count = None,
                     archives = None,
                     queue = None,
                     name = None,
                     configuration = None):
        request_body = {}
        request_body["file"] = file_to_execute
        if not class_name == None: request_body["className"] = class_name
        if not arguments == None: request_body["args"] = self._decode_list(arguments)
        if not jars == None: request_body["jars"] = self._decode_list(jars)
        if not py_files == None: request_body["pyFiles"] = self._decode_list(py_files)
        if not files == None: request_body["files"] = self._decode_list(files)
        if not driver_memory == None: request_body["driverMemory"] = driver_memory
        if not driver_cores == None: request_body["driverCores"] = int(driver_cores)
        if not executor_memory == None: request_body["executorMemory"] = executor_memory
        if not executor_cores == None: request_body["executorCores"] = int(executor_cores)
        if not executor_count == None: request_body["numExecutors"] = int(executor_count)
        if not archives == None: request_body["archives"] = self._decode_list(archives)
        if not queue == None: request_body["queue"] = queue
        if not name == None: request_body["name"] = name
        if not configuration == None: request_body["conf"] = self._decode_dictionary(configuration)

        response = self._submit_request(requests.post, True, "/batches/",
                                        body_data=request_body,
                                        extra_headers={'content-type': 'application/json'})
        if not response.status_code == http_status_codes.created:
            self._raise_exception(response)
        return response.json()

    def list_batches(self):
        response = self._submit_request(requests.get, True, "/batches/")
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def batch_info(self, batch_id):
        response = self._submit_request(requests.get, True, "/batches/{0}/".format(batch_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def batch_log(self, batch_id):
        response = self._submit_request(requests.get, True, "/batches/{0}/log".format(batch_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def batch_state(self, batch_id):
        response = self._submit_request(requests.get, True, "/batches/{0}/state".format(batch_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def delete_batch(self, batch_id):
        response = self._submit_request(requests.delete, True, "/batches/{0}/".format(batch_id))
        if not response.status_code == http_status_codes.ok:
            self._raise_exception(response)
        return response.json()

    def _create_uri(self, url_suffix):
        result = urllib.parse.urljoin(self.livy_url_prefix + r"/", r"./" + url_suffix)
        return result

    def _submit_request(self, request_function, allow_redirect, url_suffix, body_data=None, extra_headers={}):
        extra_opts = self.request_extra_opts
        if not body_data==None:
            extra_opts['data'] = json.dumps(body_data)
        uri = self._create_uri(url_suffix)
        response = request_function(uri, allow_redirects=allow_redirect, headers=extra_headers, **extra_opts)
        return response

    def _raise_exception(self, response):
        if response.status_code == http_status_codes.bad_request:
            raise LivyBadRequest(response.status_code, response.content)
        elif response.status_code == http_status_codes.unauthorized:
            raise LivyUnauthorized(response.status_code, response.content)
        elif response.status_code == http_status_codes.not_found:
            raise LivyNotFound(response.status_code, response.content)
        elif response.status_code == http_status_codes.method_not_allowed:
            raise LivyMethodNotAllowed(response.status_code, response.content)
        else:
            raise LivyException(response.status_code, response.content)


