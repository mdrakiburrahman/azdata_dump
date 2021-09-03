from azdata.cli.core.models.kube_quantity import KubeQuantity

RESOURCE_KIND = "sqlmanagedinstance"
"""
Defines the Kubernetes custom resource kind.
"""

RESOURCE_KIND_PLURAL = "sqlmanagedinstances"
"""
Defines the plural name.
"""

API_GROUP = "sql.arcdata.microsoft.com"
"""
Defines the API group.
"""

API_VERSION = "v1beta1"
"""
Defines the API version.
"""

# -----------------------------------------------------------------------------------------------------------------
# SQL server related constants
# -----------------------------------------------------------------------------------------------------------------
SQLMI_PASSWORD_CHARS = r'[@_!#$%^&*?/\|:]'
SQLMI_PASSWORD_MIN_LENGTH = 8
SQLMI_PASSWORD_REQUIRED_GROUPS = 3
SQLMI_MIN_MEMORY_SIZE = KubeQuantity("2Gi")
SQLMI_MIN_CORES_SIZE = KubeQuantity("1")

# ------------------------------------------------------------------------------
# SQL MI license type constansts
# ------------------------------------------------------------------------------
SQLMI_LICENSE_TYPE_BASE_PRICE = "BasePrice"
SQLMI_LICENSE_TYPE_BASE_PRICE_AZURE = SQLMI_LICENSE_TYPE_BASE_PRICE # the format expected by ARM RP
SQLMI_LICENSE_TYPE_LICENSE_INCLUDED = "LicenseIncluded"
SQLMI_LICENSE_TYPE_LICENSE_INCLUDED_AZURE = SQLMI_LICENSE_TYPE_LICENSE_INCLUDED # the format expected by ARM RP
SQLMI_LICENSE_TYPES = set([SQLMI_LICENSE_TYPE_BASE_PRICE, SQLMI_LICENSE_TYPE_LICENSE_INCLUDED])

# message to display allowed values when creating an instance
SQLMI_LICENSE_TYPE_ALLOWED_VALUES_MSG_CREATE = f"Allowed values are: {SQLMI_LICENSE_TYPE_BASE_PRICE}, {SQLMI_LICENSE_TYPE_LICENSE_INCLUDED}. Default is {SQLMI_LICENSE_TYPE_LICENSE_INCLUDED}. The license type cannot be changed"

# generic message to display allowed values
SQLMI_LICENSE_TYPE_ALLOWED_VALUES_MSG = f"Allowed values are: {SQLMI_LICENSE_TYPE_BASE_PRICE}, {SQLMI_LICENSE_TYPE_LICENSE_INCLUDED}. Default is {SQLMI_LICENSE_TYPE_LICENSE_INCLUDED}."
SQLMI_LICENSE_TYPE_DEFAULT = SQLMI_LICENSE_TYPE_LICENSE_INCLUDED

# ------------------------------------------------------------------------------
# SQL MI tier constansts
# ------------------------------------------------------------------------------
SQLMI_TIER_GENERAL_PURPOSE = "GeneralPurpose"
SQLMI_TIER_GENERAL_PURPOSE_SHORT = "gp"
SQLMI_TIER_GENERAL_PURPOSE_AZURE = SQLMI_TIER_GENERAL_PURPOSE # the format exptected by ARM RP
SQLMI_TIER_GENERAL_PURPOSE_ALL = set([SQLMI_TIER_GENERAL_PURPOSE, SQLMI_TIER_GENERAL_PURPOSE_SHORT])
SQLMI_TIER_BUSINESS_CRITICAL = "BusinessCritical"
SQLMI_TIER_BUSINESS_CRITICAL_AZURE = SQLMI_TIER_BUSINESS_CRITICAL # the format expected by ARM RP
SQLMI_TIER_BUSINESS_CRITICAL_SHORT = "bc"
SQLMI_TIER_BUSINESS_CRITICAL_ALL = set([SQLMI_TIER_BUSINESS_CRITICAL, SQLMI_TIER_BUSINESS_CRITICAL_SHORT])
SQLMI_TIERS = set([SQLMI_TIER_GENERAL_PURPOSE, SQLMI_TIER_BUSINESS_CRITICAL, SQLMI_TIER_GENERAL_PURPOSE_SHORT, SQLMI_TIER_BUSINESS_CRITICAL_SHORT])

# message to display allowed values when creating an instance
SQLMI_TIER_ALLOWED_VALUES_MSG_CREATE = f"Allowed values: {SQLMI_TIER_BUSINESS_CRITICAL} ({SQLMI_TIER_BUSINESS_CRITICAL_SHORT} for short) or {SQLMI_TIER_GENERAL_PURPOSE} ({SQLMI_TIER_GENERAL_PURPOSE_SHORT} for short). Default is {SQLMI_TIER_GENERAL_PURPOSE}. The price tier cannot be changed."

# generic message to display allowed values
SQLMI_TIER_ALLOWED_VALUES_MSG = f"Allowed values: {SQLMI_TIER_BUSINESS_CRITICAL} ({SQLMI_TIER_BUSINESS_CRITICAL_SHORT} for short) or {SQLMI_TIER_GENERAL_PURPOSE} ({SQLMI_TIER_GENERAL_PURPOSE_SHORT} for short). Default is {SQLMI_TIER_GENERAL_PURPOSE}."
SQLMI_TIER_DEFAULT = SQLMI_TIER_GENERAL_PURPOSE

# ------------------------------------------------------------------------------
# SQL MI sku constansts
# ------------------------------------------------------------------------------
SQL_MI_SKU_NAME_VCORE = "vCore"