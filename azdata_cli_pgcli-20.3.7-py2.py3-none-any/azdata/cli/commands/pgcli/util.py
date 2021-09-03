# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azdata.cli.core.text import Text
from knack.prompting import NoTTYException
from azdata.cli.core.prompt import prompt, prompt_pass

import os

__all__ = ["prompt_postgres_username", "prompt_postgres_username"]


def prompt_postgres_username():
    from azdata.cli.core.constants import AZDATA_USERNAME

    env = os.environ.get
    username = env("PGUSER") or env(AZDATA_USERNAME)

    if not username:
        try:
            msg = (
                "\nA username is needed. It can be set for the session by "
                'setting the environment\nvariable "{}" or "PGUSER".'.format(
                    AZDATA_USERNAME
                )
            )
            Text.warning(msg)

            username = prompt("Username: ")
        except NoTTYException:
            raise NoTTYException(
                'Missing [--username, -u], "AZDATA_USERNAME" or "PGUSER" '
                "environment variable\nin non-interactive environment.".format(
                    AZDATA_USERNAME
                )
            )

    return username


def prompt_postgres_password():
    from azdata.cli.core.constants import AZDATA_PASSWORD

    env = os.environ.get
    password = env("PGPASSWORD") or env(AZDATA_PASSWORD)

    if not password:
        try:
            msg = (
                "\nA password is needed. It can be set for the session by "
                'setting the environment\nvariable "{}" or '
                '"PGPASSWORD".'.format(AZDATA_PASSWORD)
            )
            Text.warning(msg)

            password = prompt_pass("Password: ")
        except NoTTYException:
            raise NoTTYException(
                'Missing "{}" or "PGPASSWORD" environment '
                "variable in non-interactive environment.".format(
                    AZDATA_PASSWORD
                )
            )

    return password
