"""Domain enumerations shared across models and schemas."""

from enum import StrEnum


class ProjectStatus(StrEnum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class EquipmentStatus(StrEnum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    DECOMMISSIONED = "decommissioned"


class Criticality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DocumentStatus(StrEnum):
    """Document processing pipeline state machine.

    uploaded → ocr → extracted → graphed → embedded → ready (or failed).
    """

    UPLOADED = "uploaded"
    OCR = "ocr"
    EXTRACTED = "extracted"
    GRAPHED = "graphed"
    EMBEDDED = "embedded"
    READY = "ready"
    FAILED = "failed"
