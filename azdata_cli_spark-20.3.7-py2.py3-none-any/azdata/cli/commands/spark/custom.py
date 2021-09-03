# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
from knack.prompting import NoTTYException
from azdata.cli.core.prompt import prompt_pass
from azdata.cli.core.enums import SecurityStrategy
from azdata.cli.core.exceptions import CliError

def _get_knox_username():
    # Note for now the knox username is hard coded to 'root'.
    return "root"

def _get_knox_password(client):
    # Note for now if the environment variable isn't set prompt for the password..
    if not os.getenv('AZDATA_PASSWORD'):
        try:
            client.stdout(
                "The Knox password is needed.  It can be set for the session by setting the environment variable "
                "AZDATA_PASSWORD.")
            password = prompt_pass('Enter Knox Password: ')
        except NoTTYException:
            raise NoTTYException('Missing AZDATA_PASSWORD environment variable in non-interactive environment.')
    else:
        password = os.environ['AZDATA_PASSWORD']

    return password

def _login(client):
    endpoint = client.get_livy_endpoint()

    if client.profile.active_context.security_strategy == SecurityStrategy.basic:
        username = _get_knox_username()
        password = _get_knox_password(client)

        client.login(endpoint, username, password)
    elif client.profile.active_context.security_strategy == SecurityStrategy.ad:
        client.login(endpoint)
    else:
        raise CliError("Invalid security strategy.  Use azdata login to choose supported strategy.")

    return

def spark_session_create(client,
                         session_kind=None,
                         jars=None,
                         py_files=None,
                         files=None,
                         driver_memory=None,
                         driver_cores=None,
                         executor_memory=None,
                         executor_cores=None,
                         executor_count=None,
                         archives=None,
                         queue=None,
                         name=None,
                         configuration=None,
                         timeout_seconds=None):
    _login(client)
    result = client.create_session(session_kind=session_kind,
                                   jars=jars,
                                   py_files=py_files,
                                   files=files,
                                   driver_memory=driver_memory,
                                   driver_cores=driver_cores,
                                   executor_memory=executor_memory,
                                   executor_cores=executor_cores,
                                   executor_count=executor_count,
                                   archives=archives,
                                   queue=queue,
                                   name=name,
                                   configuration=configuration,
                                   timeout_seconds=timeout_seconds)
    return result

def spark_session_list(client):
    _login(client)
    result = client.list_sessions()
    return result

def spark_session_info(client, session_id):
    _login(client)
    result = client.session_info(session_id)
    return result

def spark_session_log(client, session_id):
    _login(client)
    result = client.session_log(session_id)
    return result

def spark_session_state(client, session_id):
    _login(client)
    result = client.session_state(session_id)
    return result

def spark_session_delete(client, session_id):
    _login(client)
    result = client.delete_session(session_id)
    return result

def spark_statement_list(client, session_id):
    _login(client)
    result = client.list_statements(session_id)
    return result

def spark_statement_create(client, session_id, code):
    _login(client)
    result = client.create_statement(session_id, code)
    return result

def spark_statement_info(client, session_id, statement_id):
    _login(client)
    result = client.statement_info(session_id, statement_id)
    return result

def spark_statement_cancel(client, session_id, statement_id):
    _login(client)
    result = client.cancel_statement(session_id, statement_id)
    return result

def spark_batch_create(client,
                       file_to_execute,
                       class_name=None,
                       arguments=None,
                       jars=None,
                       py_files=None,
                       files=None,
                       driver_memory=None,
                       driver_cores=None,
                       executor_memory=None,
                       executor_cores=None,
                       executor_count=None,
                       archives=None,
                       queue=None,
                       name=None,
                       configuration=None):
    _login(client)
    result = client.create_batch(file_to_execute=file_to_execute,
                                   class_name=class_name,
                                   arguments=arguments,
                                   jars=jars,
                                   py_files=py_files,
                                   files=files,
                                   driver_memory=driver_memory,
                                   driver_cores=driver_cores,
                                   executor_memory=executor_memory,
                                   executor_cores=executor_cores,
                                   executor_count=executor_count,
                                   archives=archives,
                                   queue=queue,
                                   name=name,
                                   configuration=configuration)
    return result

def spark_batch_list(client):
    _login(client)
    result = client.list_batches()
    return result

def spark_batch_info(client, batch_id):
    _login(client)
    result = client.batch_info(batch_id)
    return result

def spark_batch_log(client, batch_id):
    _login(client)
    result = client.batch_log(batch_id)
    return result

def spark_batch_state(client, batch_id):
    _login(client)
    result = client.batch_state(batch_id)
    return result

def spark_batch_delete(client, batch_id):
    _login(client)
    result = client.delete_batch(batch_id)
    return result
