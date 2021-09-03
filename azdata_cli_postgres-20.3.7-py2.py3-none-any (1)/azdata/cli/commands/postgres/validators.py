# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

def validate_backup_delete(args):
    if args.backup_id is not None and args.backup_name is not None:
        raise ValueError("-id cannot be used with --name.")
    elif args.backup_id is None and args.backup_name is None:
        raise ValueError("Either -id or --name must be provided.")

