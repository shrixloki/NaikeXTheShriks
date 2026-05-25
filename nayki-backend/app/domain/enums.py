from enum import StrEnum


class RiskLevel(StrEnum):
    LOWER = "lower"
    MODERATE = "moderate"
    HIGHER = "higher"
    UNKNOWN = "unknown"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CoverageStatus(StrEnum):
    UNAVAILABLE = "unavailable"
    LIMITED = "limited"
    MODERATE = "moderate"
    STRONG = "strong"


class HelpPoiType(StrEnum):
    POLICE = "police"
    HOSPITAL = "hospital"
    PHARMACY = "pharmacy"
    PUBLIC_PLACE = "public_place"
    TRANSIT = "transit"
    OTHER = "other"


class EvidenceSource(StrEnum):
    GOVERNMENT = "government"
    POLICE = "police"
    MUNICIPAL = "municipal"
    OSM = "osm"
    USER_REPORT = "user_report"
    VERIFIED_PARTNER = "verified_partner"
    SYSTEM = "system"


class EvidenceType(StrEnum):
    CRIME = "crime"
    LIGHTING = "lighting"
    INCIDENT = "incident"
    ROAD_TYPE = "road_type"
    ISOLATION = "isolation"
    HELP_DISTANCE = "help_distance"
    CROWD_PROXY = "crowd_proxy"
    SOS_DENSITY = "sos_density"


# Part 2 Enums
class ReportType(StrEnum):
    POOR_LIGHTING = "poor_lighting"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCIDENT = "accident"
    HARASSMENT = "harassment"
    ROAD_BLOCKED = "road_blocked"
    MEDICAL_EMERGENCY = "medical_emergency"
    OTHER = "other"


class ReportStatus(StrEnum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class SosAlertType(StrEnum):
    SOS = "sos"
    CAUTION = "caution"
    ACCIDENT = "accident"
    MEDICAL = "medical"


class SosAlertStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    MARKED_SAFE = "marked_safe"
    EXPIRED = "expired"


class SosRecipientDeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class SosRecipientResponse(StrEnum):
    CONFIRMED = "confirmed"
    FALSE_ALARM = "false_alarm"
    IGNORED = "ignored"
