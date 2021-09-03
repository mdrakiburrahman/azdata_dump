from azdata.cli.core.models.kube_quantity import KubeQuantity

# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

RESOURCE_KIND = "postgresql"
"""
Kubernetes resource kind for postgres.
"""

API_GROUP = "arcdata.microsoft.com"
"""
Defines the API group.
"""

API_VERSION = "v1beta1"
"""
Defines the API version.
"""

COMMAND_UNIMPLEMENTED = "This command is currently unimplemented."
"""
Unimplemented response.
"""

SUPPORTED_ENGINE_VERSIONS = [11, 12]
"""
Supported engine versions.
"""

DEFAULT_ENGINE_VERSION = 12
"""
Default engine versions.
"""

# ------------------------------------------------------------------------------
# Postgres resource constants
# ------------------------------------------------------------------------------
POSTGRES_MIN_MEMORY_SIZE = KubeQuantity("256Mi")
POSTGRES_MIN_CORES_SIZE = KubeQuantity("1")
