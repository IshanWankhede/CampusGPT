"""Audit logging service for security and administrative events (WP11).

Provides append-only persistence of security events with strict metadata allowlisting,
IP address hashing, and correlation ID attachment.
"""

import logging
from typing import Any
import uuid

from fastapi import Request
from sqlalchemy.orm import Session

from app.auth.rate_limiter import get_client_ip, hash_ip
from app.core.logging import get_current_request_id
from app.database.session import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

# Strict allowlist of permissible metadata keys to prevent secret leaks
ALLOWED_METADATA_KEYS = {
    "email",
    "role",
    "requested_role",
    "status",
    "college",
    "reason",
    "error",
    "token_jti",
    "family_id",
    "provider",
    "applicant_email",
    "reviewer_email",
    "scope",
    "target_user_id",
}


def sanitize_audit_metadata(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """Filters metadata against the strict allowlist, discarding sensitive or unknown keys."""
    if not raw:
        return None
    sanitized = {}
    for key, val in raw.items():
        if key in ALLOWED_METADATA_KEYS and val is not None:
            # Ensure value is converted to a serializable type
            sanitized[key] = str(val) if isinstance(val, uuid.UUID) else val
    return sanitized if sanitized else None


def record_audit_event(
    action: str,
    outcome: str,
    actor_id: uuid.UUID | None = None,
    target_type: str | None = None,
    target_id: uuid.UUID | None = None,
    request: Request | None = None,
    ip_hash: str | None = None,
    metadata: dict[str, Any] | None = None,
    db: Session | None = None,
) -> AuditLog | None:
    """Records an immutable security audit event into the audit_logs table.

    Guarantees persistence even on failures by committing the transaction.
    """
    if request and not ip_hash:
        try:
            client_ip = get_client_ip(request)
            ip_hash = hash_ip(client_ip)
        except Exception as exc:
            logger.warning("Failed to resolve client IP for audit log: %s", exc)

    correlation_id = get_current_request_id()
    clean_metadata = sanitize_audit_metadata(metadata)

    audit_entry = AuditLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        outcome=outcome,
        ip_hash=ip_hash,
        request_id=correlation_id,
        metadata_=clean_metadata,
    )

    should_close = False
    session = db
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        session.add(audit_entry)
        session.commit()
        session.refresh(audit_entry)
        return audit_entry
    except Exception as exc:
        session.rollback()
        logger.error("Failed to persist audit log entry: %s", exc)
        return None
    finally:
        if should_close:
            session.close()

