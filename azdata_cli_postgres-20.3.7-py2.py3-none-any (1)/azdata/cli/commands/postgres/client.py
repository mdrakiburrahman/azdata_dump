# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.clients.cli_client import CliClient
from azdata.cli.core.enums import ContextType

__all__ = ['beget']


def beget(_):
    """Client factory"""
    return PostgresClientMixin(check_auth=True, check_eula=True)


def beget_no_check_auth(_):
    """Client factory - no check on authentication"""
    return PostgresClientMixin(False)


class PostgresClientMixin(CliClient):
    def __init__(self, check_auth=False, check_eula=False):
        """
        :param check_auth: Set to `True` to have this command enforce authentication
                           before running.
        :param check_auth: Set to `True` to have this command enforce eula
                           acceptance before running.
        """
        super(PostgresClientMixin, self).__init__(
            check_auth=check_auth, check_eula=check_eula
        )
