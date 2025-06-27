"""Constants for NeoSmart Blue Blinds integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "neosmartblue"

# Device configuration
DEFAULT_NAME = "NeoSmart Blue Blind"
MANUFACTURER = "NeoSmart"

# NeoSmart Blue specific constants
NEOSMART_MANUFACTURER_ID = 2407
STATUS_PAYLOAD_LENGTH = 5

# Scan intervals
SCAN_INTERVAL = 30  # seconds
