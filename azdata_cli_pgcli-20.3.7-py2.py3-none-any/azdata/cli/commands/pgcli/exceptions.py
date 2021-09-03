# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


from azdata.cli.core.exceptions import CliError
from knack.prompting import NoTTYException
from azdata.cli.core.constants import AZDATA_USERNAME, AZDATA_PASSWORD

__all__ = ["PgcliError", "PgcliNoTTYException"]


class PgcliError(CliError):
    """All errors related to pgcli API calls."""


class NoTTYUsernameOrPasswordException(NoTTYException, CliError):
    """
    All errors related to Notty
    """

    def __init__(self):
        reason = (
            "Please specify [--username]|{0} and/or {1} in "
            "non-interactive mode.".format(AZDATA_USERNAME, AZDATA_PASSWORD)
        )
        super(CliError, self).__init__(reason)
