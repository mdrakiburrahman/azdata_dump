# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from knack.help_files import helps
from azdata.cli.commands.spark import _

# pylint: disable=line-too-long
helps['bdc spark'] = """
    type: group
    short-summary: {short}
""".format(short=_('The Spark commands allow the user to interact with the Spark system by creating and managing sessions, statements, and batches.'))

helps['bdc spark batch'] = """
    type: group
    short-summary: {short}
""".format(short=_('Manages batch operations within the Spark system.'))

# pylint: disable=line-too-long
helps['bdc spark session'] = """
    type: group
    short-summary: {short}
""".format(short=_('Manages activate session operations within the Spark system.'))

helps['bdc spark statement'] = """
    type: group
    short-summary: {short}
""".format(short=_('Manages Spark statements.'))

# pylint: disable=line-too-long
helps['bdc spark session create'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark session create --session-kind pyspark
""".format(
    short=_('Create a new Spark session.'),
    long=_('This creates a new interactive Spark session. The caller must specify the type of Spark session. This session lives beyond the lifetime of a azdata  execution and must be deleted with \'spark session delete\''),
    ex1=_('Create a session.'))

# pylint: disable=line-too-long
helps['bdc spark session list'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata spark session list
""".format(
    short=_('List all the active sessions in Spark.'),
    ex1=_('List all the active sessions.'))

# pylint: disable=line-too-long
helps['bdc spark session info'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark session info --session-id 0
""".format(
    short=_('Get information about an active Spark session.'),
    long=_('This gets the session information for an active Spark session with the given ID.  The session id is returned from \'spark session create\'.'),
    ex1=_('Get session info for session with ID of 0.'))

# pylint: disable=line-too-long
helps['bdc spark session log'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark session log --session-id 0
""".format(
    short=_('Get execution logs for an active Spark session.'),
    long=_('This gets the session log entries for an active Spark session with the given ID.  The session id is returned from \'spark session create\'.'),
    ex1=_('Get session log for session with ID of 0.'))

# pylint: disable=line-too-long
helps['bdc spark session state'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark session state --session-id 0
""".format(
    short=_('Get execution state for an active Spark session.'),
    long=_('This gets the session state for an active Spark session with the given ID.  The session id is returned from \'spark session create\'.'),
    ex1=_('Get session state for session with ID of 0.'))

# pylint: disable=line-too-long
helps['bdc spark session delete'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark session delete --session-id 0
""".format(
    short=_('Delete a Spark session.'),
    long=_('This deletes an interactive Spark session. The session id is returned from \'spark session create\'.'),
    ex1=_('Delete a session.'))

# pylint: disable=line-too-long
helps['bdc spark statement list'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata spark statement list --session-id 0
""".format(
    short=_('List all the statements in the given Spark session.'),
    ex1=_('List all the session statements.'))

# pylint: disable=line-too-long
helps['bdc spark statement create'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark statement create --session-id 0 --code "2+2"
""".format(
    short=_('Create a new Spark statement in the given session.'),
    long=_('This creates and executes a new statement in the given session.  If the execute is quick the result contains the output from the execution.  Otherwise the result can be retrieved using \'spark session info\' after the statement is complete.'),
    ex1=_('Run a statement.'))

# pylint: disable=line-too-long
helps['bdc spark statement info'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark statement info --session-id 0 --statement-id 0
""".format(
    short=_('Get information about the requested statement in the given Spark session.'),
    long=_('This gets the execution status and execution results if the statement has completed. The statement id is returned from \'spark statement create\'.'),
    ex1=_('Get statement info for session with ID of 0 and statement ID of 0.'))

# pylint: disable=line-too-long
helps['bdc spark statement cancel'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark statement cancel --session-id 0 --statement-id 0
""".format(
    short=_('Cancel a statement within the given Spark session.'),
    long=_('This cancels a statement within the given Spark session. The statement id is returned from \'spark statement create\'.'),
    ex1=_('Cancel a statement.'))

# pylint: disable=line-too-long
helps['bdc spark batch create'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark batch create --code "2+2"
""".format(
    short=_('Create a new Spark batch.'),
    long=_('This creates a new batch Spark job that executes the provided code.'),
    ex1=_('Create a new Spark batch.'))

# pylint: disable=line-too-long
helps['bdc spark batch list'] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            azdata spark batch list
""".format(
    short=_('List all the batches in Spark.'),
    ex1=_('List all the active batches.'))

# pylint: disable=line-too-long
helps['bdc spark batch info'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark batch info --batch-id 0
""".format(
    short=_('Get information about an active Spark batch.'),
    long=_('This gets the information for an Spark batch with the given ID.  The batch id is returned from \'spark batch create\'.'),
    ex1=_('Get batch info for batch with ID of 0.'))

# pylint: disable=line-too-long
helps['bdc spark batch log'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark batch log --batch-id 0
""".format(
    short=_('Get execution logs for a Spark batch.'),
    long=_('This gets the batch log entries for a Spark batch with the given ID.  The batch id is returned from \'spark batch create\'.'),
    ex1=_('Get batch log for batch with ID of 0.'))

# pylint: disable=line-too-long
helps['bdc spark batch state'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark batch state --batch-id 0
""".format(
    short=_('Get execution state for a Spark batch.'),
    long=_('This gets the batch state for a Spark batch with the given ID.  The batch id is returned from \'spark batch create\'.'),
    ex1=_('Get batch state for batch with ID of 0.'))

# pylint: disable=line-too-long
helps['bdc spark batch delete'] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            azdata spark batch delete --batch-id 0
""".format(
    short=_('Delete a Spark batch.'),
    long=_('This deletes a Spark batch. The batch id is returned from \'spark batch create\'.'),
    ex1=_('Delete a batch.'))
