# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from .api import DefaultApi
from .models.postgres_backup_response_model import PostgresqlBackupResponse
from azdata.cli.core.exceptions import (
    ApiError,
    CliError,
    ControllerError,
    http_status_codes
)
import json

__all__ = ['DuskyControllerService']

# ---------------------------------------------------------------------------- #
# Dusky router: /dusky/*
# ---------------------------------------------------------------------------- #

class DuskyControllerService(object):
    
    def postgres_server_backup_create(self, resource_kind, namespace, server_group_id, backup_name, incremental):
        """
        Creates Arc Postgres backup.
        :return:
        """
        try:
            api = DefaultApi(api_client=self.api_client)
            response = api.postgres_server_backup_create(
                version="1",
                resource_type=resource_kind,
                ns=namespace,
                server_group_id=server_group_id,
                name=backup_name or '',
                incremental=incremental or False)
            return self._format_response('create the backup', response)
        except ApiError as e:
            raise ControllerError(e, status=e.status)

    def postgres_server_backup_restore(self, resource_kind, namespace, server_group_id, backup_id, source_server_group_id, time):
        """
        Restores Arc Postgres backup.
        :return:
        """
        try:
            api = DefaultApi(api_client=self.api_client)
            response = api.postgres_server_backup_restore(
                version="1",
                resource_type=resource_kind,
                ns=namespace, 
                server_group_id=server_group_id, 
                backup_id=backup_id or '',
                source_server_group_id=source_server_group_id or '', 
                time=time or '')
            return self._format_response('restore the backup', response)
        except ApiError as e:
            raise ControllerError(e, status=e.status)

    def postgres_server_backup_restore_status(self, resource_kind, namespace, server_group_id):
        """
        Restores Arc Postgres backup.
        :return:
        """
        try:
            api = DefaultApi(api_client=self.api_client)
            response = api.postgres_server_backup_restore_status(
                version="1",
                resource_type=resource_kind,
                ns=namespace,
                server_group_id=server_group_id)
            return self._format_response('get the restore status', response)
        except ApiError as e:
            raise ControllerError(e, status=e.status)
    
    def postgres_server_backup_show(self, resource_kind, namespace, server_group_id, backup_id):
        """
        Gets Arc Postgres backup.
        :return:
        """
        try:
            api = DefaultApi(api_client=self.api_client)
            response = api.postgres_server_backup_show(
                version="1",
                resource_type=resource_kind,
                ns=namespace,
                server_group_id=server_group_id,
                backup_id=backup_id)
            return self._format_response('get the backup', response)
        except ApiError as e:
            raise ControllerError(e, status=e.status)
    
    def postgres_server_backup_list(self, resource_kind, namespace, server_group_id):
        """
        Lists Arc Postgres backups.
        :return:
        """
        try:
            api = DefaultApi(api_client=self.api_client)
            backups = api.list_dusky_backups(
                version="1",
                resource_type=resource_kind,
                ns=namespace,
                server_group_id=server_group_id)
            return [self._format_response('list backups', response) for response in backups.get('backups', [])]
        except ApiError as e:
            raise ControllerError(e, status=e.status)

    def postgres_server_backup_delete(self, resource_kind, namespace, server_group_id, backup_id):
        """
        Delete Arc Postgres backup for the given backup id.
        :return: The deleted backup, or None if the backup wasn't found.
        """
        try:
            api = DefaultApi(api_client=self.api_client)
            body, code, _ = api.delete_dusky_backup_with_http_info(
                version="1",
                resource_type=resource_kind,
                ns=namespace,
                server_group_id=server_group_id,
                backup_id=backup_id)

            if code == http_status_codes.no_content:
                return None
            else:
                return self._format_response('delete the backup', body)
        except ApiError as e:
            raise ControllerError(e, status=e.status)

    def _format_response(self, msg, resp):
        response = PostgresqlBackupResponse(resp)

        if not response.status.result:
            if response.status.message is not None:
                raise CliError('Failed to {}. {}'.format(msg, response.status.message))
            else:
                raise CliError('Failed to {}.\n{}'.format(msg, json.dumps(response.status.details, indent=2)))

        return response