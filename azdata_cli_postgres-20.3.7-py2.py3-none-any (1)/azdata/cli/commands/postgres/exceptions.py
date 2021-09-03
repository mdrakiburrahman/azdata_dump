# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


from azdata.cli.core.exceptions import CliError


class PostgresError(CliError):
    """All errors related to postgres API calls."""
    pass
