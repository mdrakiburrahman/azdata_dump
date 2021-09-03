# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

def validate_copy_logs(args):
    if (args.resource_kind is None) ^ (args.resource_name is None):
        raise ValueError("Either --resource-kind or --resource-name is not specified. They need to be provided or omitted at the same time.")