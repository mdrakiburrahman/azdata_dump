# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


from azdata.cli.core.exceptions import CliError


class LivyException(CliError):
    pass

class LivyBadRequest(CliError):
    pass

class LivyUnauthorized(CliError):
    pass

class LivyNotFound(CliError):
    pass

class LivyMethodNotAllowed(CliError):
    pass

