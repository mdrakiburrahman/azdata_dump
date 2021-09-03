# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext
    from azdata.cli.commands.spark import _

    with ArgumentsContext(self, 'bdc spark session create') as arg_context:
        arg_context.argument(
            'session_kind',
            options_list=['--session-kind', '-k'],
            help=_('Name of the type of session to create.  One of spark, pyspark, sparkr, or sql.')
        )

        arg_context.argument(
            'jars',
            options_list=['--jar-files', '-j'],
            help=_('List of jar file paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'py_files',
            options_list=['--py-files', '-p'],
            help=_('List of python file paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'files',
            options_list=['--files', '-f'],
            help=_('List of file paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'driver_memory',
            options_list=['--driver-memory'],
            help=_('Amount of memory to allocate to the driver.  Specify units as part of value.  Example 512M or 2G.')
        )

        arg_context.argument(
            'driver_cores',
            options_list=['--driver-cores'],
            help=_('Amount of CPU cores to allocate to the driver.')
        )

        arg_context.argument(
            'executor_memory',
            options_list=['--executor-memory'],
            help=_('Amount of memory to allocate to the executor.  Specify units as part of value.  Example 512M or 2G.')
        )

        arg_context.argument(
            'executor_cores',
            options_list=['--executor-cores'],
            help=_('Amount of CPU cores to allocate to the executor.')
        )

        arg_context.argument(
            'executor_count',
            options_list=['--executor-count'],
            help=_('Number of instances of the executor to run.')
        )

        arg_context.argument(
            'archives',
            options_list=['--archives', '-a'],
            help=_('List of archives paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'queue',
            options_list=['--queue', '-q'],
            help=_('Name of the Spark queue to execute the session in.')
        )

        arg_context.argument(
            'name',
            options_list=['--name', '-n'],
            help=_('Name of the Spark session.')
        )

        arg_context.argument(
            'configuration',
            options_list=['--config', '-c'],
            help=_('List of name value pairs containing Spark configuration values.  Encoded as JSON dictionary.  Example: \'{"name":"value", "name2":"value2"}\'.')
        )

        arg_context.argument(
            'timeout_seconds',
            options_list=['--timeout-seconds', '-t'],
            help=_('Session idle timeout in seconds.')
        )

    with ArgumentsContext(self, 'bdc spark session list') as arg_context:
        pass

    with ArgumentsContext(self, 'bdc spark session info') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

    with ArgumentsContext(self, 'bdc spark session log') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

    with ArgumentsContext(self, 'bdc spark session state') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

    with ArgumentsContext(self, 'bdc spark session delete') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

    with ArgumentsContext(self, 'bdc spark statement list') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

    with ArgumentsContext(self, 'bdc spark statement create') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

        arg_context.argument(
            'code',
            options_list=['--code', '-c'],
            help=_('String containing code to execute as part of the statement.')
        )

    with ArgumentsContext(self, 'bdc spark statement info') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

        arg_context.argument(
            'statement_id',
            options_list=['--statement-id', '-s'],
            help=_('Spark statement ID number within the given session ID.')
        )

    with ArgumentsContext(self, 'bdc spark statement cancel') as arg_context:
        arg_context.argument(
            'session_id',
            options_list=['--session-id', '-i'],
            help=_('Spark session ID number.')
        )

        arg_context.argument(
            'statement_id',
            options_list=['--statement-id', '-s'],
            help=_('Spark statement ID number within the given session ID.')
        )

    with ArgumentsContext(self, 'bdc spark batch create') as arg_context:
        arg_context.argument(
            'file_to_execute',
            options_list=['--file', '-f'],
            required = True,
            help=_('Path to file to execute.')
        )

        arg_context.argument(
            'class_name',
            options_list=['--class-name', '-c'],
            help=_('Name of the class to execute when passing in one or more jar files.')
        )

        arg_context.argument(
            'arguments',
            options_list=['--arguments', '-a'],
            help=_('List of arguments.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'jars',
            options_list=['--jar-files', '-j'],
            help=_('List of jar file paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'py_files',
            options_list=['--py-files', '-p'],
            help=_('List of python file paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'files',
            options_list=['--files'],
            help=_('List of file paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'driver_memory',
            options_list=['--driver-memory'],
            help=_('Amount of memory to allocate to the driver.  Specify units as part of value.  Example 512M or 2G.')
        )

        arg_context.argument(
            'driver_cores',
            options_list=['--driver-cores'],
            help=_('Amount of CPU cores to allocate to the driver.')
        )

        arg_context.argument(
            'executor_memory',
            options_list=['--executor-memory'],
            help=_(
                'Amount of memory to allocate to the executor.  Specify units as part of value.  Example 512M or 2G.')
        )

        arg_context.argument(
            'executor_cores',
            options_list=['--executor-cores'],
            help=_('Amount of CPU cores to allocate to the executor.')
        )

        arg_context.argument(
            'executor_count',
            options_list=['--executor-count'],
            help=_('Number of instances of the executor to run.')
        )

        arg_context.argument(
            'archives',
            options_list=['--archives'],
            help=_('List of archives paths.  To pass in a list JSON encode the values.  Example: \'["entry1", "entry2"]\'.')
        )

        arg_context.argument(
            'queue',
            options_list=['--queue', '-q'],
            help=_('Name of the Spark queue to execute the session in.')
        )

        arg_context.argument(
            'name',
            options_list=['--name', '-n'],
            help=_('Name of the Spark session.')
        )

        arg_context.argument(
            'configuration',
            options_list=['--config'],
            help=_('List of name value pairs containing Spark configuration values.  Encoded as JSON dictionary.  Example: \'{"name":"value", "name2":"value2"}\'.')
        )

    with ArgumentsContext(self, 'bdc spark batch list') as arg_context:
        pass

    with ArgumentsContext(self, 'bdc spark batch info') as arg_context:
        arg_context.argument(
            'batch_id',
            options_list=['--batch-id', '-i'],
            help=_('Spark batch ID number.')
        )

    with ArgumentsContext(self, 'bdc spark batch log') as arg_context:
        arg_context.argument(
            'batch_id',
            options_list=['--batch-id', '-i'],
            help=_('Spark batch ID number.')
        )

    with ArgumentsContext(self, 'bdc spark batch state') as arg_context:
        arg_context.argument(
            'batch_id',
            options_list=['--batch-id', '-i'],
            help=_('Spark batch ID number.')
        )

    with ArgumentsContext(self, 'bdc spark batch delete') as arg_context:
        arg_context.argument(
            'batch_id',
            options_list=['--batch-id', '-i'],
            help=_('Spark batch ID number.')
        )
