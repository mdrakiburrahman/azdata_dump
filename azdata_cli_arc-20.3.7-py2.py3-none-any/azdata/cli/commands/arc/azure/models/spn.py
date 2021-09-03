# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


class Spn(object):
    authority = ''
    tenant_id = ''
    client_id = ''
    client_secret = ''

    def __init__(self, **entries):
        self.__dict__.update(entries)
