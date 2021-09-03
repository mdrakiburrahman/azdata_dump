# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from datetime import datetime, timezone
import humanfriendly

class PostgresqlBackup(object):
    """
    Internal Backup object.
    """

    def __init__(self, b):
        """
        Initializes a backup with the given json
        :param b: The backup json
        """
        def mapType(t):
            if t == 2: return 'Incr'
            else: return 'Full'

        self._name = b.get('label', '')
        self._size = b.get('size', 0)
        self._type = mapType(b.get('backupType', 0))
    
    @property
    def name(self):
        """
        Gets the name of the backup.
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of the backup.
        """
        self._name = name

    @property
    def type(self):
        """
        Gets the type of the backup.
        """
        return self._type

    @type.setter
    def type(self, value):
        """
        Sets the type of the backup.
        """
        self._type = value

    @property
    def size(self):
        """
        Gets the size of the backup in a human readable format.
        """
        return humanfriendly.format_size(self._size, binary=True)

    @size.setter
    def size(self, size):
        """
        Gets the size of the backup.
        """
        self._size = size

class PostgresqlBackupStatus(object):
    """
    Internal Backup status object.
    """

    def __init__(self, s):
        """
        Initializes a backup status with the given json
        :param s: The status json
        """
        self._result = s.get('result', True)
        self._message = s.get('message', None)
        self._details = s.get('details', None)
    
    @property
    def result(self):
        """
        Gets the status result.
        """
        return self._result

    @result.setter
    def result(self, result):
        """
        Sets the status result.
        """
        self._result = result

    @property
    def message(self):
        """
        Gets the status message.
        """
        return self._message

    @message.setter
    def message(self, message):
        """
        Sets the status message.
        """
        self._message = message

    @property
    def details(self):
        """
        Gets the status details.
        """
        return self._details

    @details.setter
    def details(self, details):
        """
        Sets the status details.
        """
        self._details = details

class PostgresqlBackupResponse(object):
    """
    Internal Backup Response object.
    """
    def __init__(self, resp):
        """
        Initializes a backup response object with the given json.
        :param resp: The backup response.
        """
        self._backup = PostgresqlBackup(resp['backup'] if 'backup' in resp and resp['backup'] is not None else {})
        self._status = PostgresqlBackupStatus(resp.get('status', {}))
        self._ID = resp['receipt'].get('id', '') if 'receipt' in resp and resp['receipt'] is not None else ''
        self._progress = resp.get('progress', None)
        self._timestamp = resp['timestamp'].get('seconds', None) if 'timestamp' in resp and resp['timestamp'] is not None else None

    @property
    def backup(self):
        """
        Gets information for the backup object.
        """
        return self._backup

    @backup.setter
    def backup(self, b):
        """
        Sets information for the backup object.
        """
        self._backup = b

    @property
    def status(self):
        """
        Gets the status for the backup object.
        """
        return self._status

    @status.setter
    def status(self, s):
        """
        Sets the status for the backup object.
        """
        self._status = s

    @property
    def ID(self):
        """
        Gets the ID for the backup object.
        """
        return self._ID.replace('-', '')

    @ID.setter
    def ID(self, ID):
        """
        Sets the ID for the backup object.
        """
        self._ID = ID

    @property
    def progress(self):
        """
        Gets the progress for the backup object.
        """
        return self._map_progress(self._progress)

    @progress.setter
    def progress(self, progress):
        """
        Sets the progress for the backup object.
        """
        self._progress = progress

    @property
    def timestamp(self):
        """
        Gets the timestamp for the backup object in a datetime format.
        """
        return str(datetime.fromtimestamp(self._timestamp, tz=timezone.utc)) if self._timestamp is not None else None

    @timestamp.setter
    def timestamp(self, timestamp):
        """
        Sets the timestamp for the backup object.
        """
        self._timestamp = timestamp

    def _map_progress(self, state):
        """
        Maps the Grpc status code into a human-readable state.
        :return:
        """
        if state == 0:
            return 'Pending'
        if state == 1:
            return 'Active'
        if state == 2:
            return 'Done'
        if state == 3:
            return 'Failed'
        else:
            return 'Unknown'