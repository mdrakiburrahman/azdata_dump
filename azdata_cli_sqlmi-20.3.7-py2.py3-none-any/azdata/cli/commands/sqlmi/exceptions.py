# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


from azdata.cli.core.exceptions import CliError


class SqlmiError(CliError):
    """All errors related to sqlmi API calls."""
