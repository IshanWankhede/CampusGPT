from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import logging
import random

from fastapi import HTTPException, Request, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_attempt import AuthAttempt

logger = logging.getLogger(__name__)


def hash_identifier(identifier: str | None) -> str | None:
    """Return SHA-256 hash of normalized identifier (email/username), or None."""
    if not identifier:
        return None
    normalized = identifier.lower().strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def hash_ip(ip: str) -> str:
    """Return SHA-256 hash of normalized IP address."""
    normalized = ip.strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _get_trusted_networks() -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    """Parse configured TRUSTED_PROXIES into ipaddress network objects."""
    networks = []
    raw = getattr(settings, "TRUSTED_PROXIES", "127.0.0.1")
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            networks.append(ipaddress.ip_network(part, strict=False))
        except ValueError:
            logger.warning("Invalid trusted proxy network configuration: %s", part)
    return networks


def is_trusted_proxy(ip_str: str) -> bool:
    """Check if the given IP belongs to the configured trusted proxy networks."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in _get_trusted_networks():
            if ip in net:
                return True
    except ValueError:
        pass
    return False


def get_client_ip(request: Request) -> str:
    """Extract and validate client IP.

    If request originates from a trusted proxy (e.g. Nginx), inspects
    X-Forwarded-For or X-Real-IP. If direct / untrusted, strictly uses
    the direct socket IP to neutralize header spoofing.
    """
    socket_host = request.client.host if request.client else "127.0.0.1"

    # Strip port if present in socket_host (e.g., "127.0.0.1:54321")
    if ":" in socket_host and not socket_host.startswith("["):
        # Could be IPv4 with port or bare IPv6
        parts = socket_host.split(":")
        if len(parts) == 2:
            try:
                ipaddress.IPv4Address(parts[0])
                socket_host = parts[0]
            except ValueError:
                pass

    if not is_trusted_proxy(socket_host):
        # Untrusted direct connection: strictly use socket IP
        return socket_host

    # Trusted proxy: inspect forwarded headers
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # Client IP is the leftmost entry in X-Forwarded-For
        client_candidate = xff.split(",")[0].strip()
        try:
            ipaddress.ip_address(client_candidate)
            return client_candidate
        except ValueError:
            pass

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        client_candidate = x_real_ip.strip()
        try:
            ipaddress.ip_address(client_candidate)
            return client_candidate
        except ValueError:
            pass

    return socket_host


def check_rate_limit(
    db: Session,
    request: Request,
    action: str,
    identifier: str | None = None,
) -> None:
    """Check if the action is currently rate limited for the identifier or IP.

    Raises HTTPException(429) with Retry-After header if limits are exceeded.
    """
    if not settings.RATE_LIMIT_ENABLED:
        return

    now = datetime.now(timezone.utc)
    client_ip = get_client_ip(request)
    ip_h = hash_ip(client_ip)
    ident_h = hash_identifier(identifier)

    if action == "login":
        # 1. Identifier limit: 5 failures / 15 min (900s)
        if ident_h:
            window_start = now - timedelta(seconds=900)
            # Find timestamp of last successful login (if any within window)
            last_success = db.execute(
                select(func.max(AuthAttempt.created_at)).where(
                    AuthAttempt.action == "login",
                    AuthAttempt.identifier_hash == ident_h,
                    AuthAttempt.success.is_(True),
                    AuthAttempt.created_at >= window_start,
                )
            ).scalar()

            effective_start = last_success if last_success else window_start

            failures = db.execute(
                select(AuthAttempt.created_at)
                .where(
                    AuthAttempt.action == "login",
                    AuthAttempt.identifier_hash == ident_h,
                    AuthAttempt.success.is_(False),
                    AuthAttempt.created_at >= effective_start,
                )
                .order_by(AuthAttempt.created_at.asc())
            ).scalars().all()

            if len(failures) >= settings.RATE_LIMIT_LOGIN_FAILURES_PER_IDENTIFIER:
                oldest_failure = failures[0]
                retry_after = max(1, int(oldest_failure.timestamp() + 900 - now.timestamp()))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed login attempts. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )

        # 2. IP limit: 20 failures / 15 min (900s)
        window_start_ip = now - timedelta(seconds=900)
        ip_failures = db.execute(
            select(AuthAttempt.created_at)
            .where(
                AuthAttempt.action == "login",
                AuthAttempt.ip_hash == ip_h,
                AuthAttempt.success.is_(False),
                AuthAttempt.created_at >= window_start_ip,
            )
            .order_by(AuthAttempt.created_at.asc())
        ).scalars().all()

        if len(ip_failures) >= settings.RATE_LIMIT_LOGIN_FAILURES_PER_IP:
            oldest_ip_failure = ip_failures[0]
            retry_after = max(1, int(oldest_ip_failure.timestamp() + 900 - now.timestamp()))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts from this network. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    elif action == "otp_send":
        # 1. Identifier limit: 3 requests / 15 min (900s)
        if ident_h:
            window_start = now - timedelta(seconds=900)
            sends = db.execute(
                select(AuthAttempt.created_at)
                .where(
                    AuthAttempt.action == "otp_send",
                    AuthAttempt.identifier_hash == ident_h,
                    AuthAttempt.created_at >= window_start,
                )
                .order_by(AuthAttempt.created_at.asc())
            ).scalars().all()

            if len(sends) >= settings.RATE_LIMIT_OTP_SEND_PER_IDENTIFIER:
                oldest_send = sends[0]
                retry_after = max(1, int(oldest_send.timestamp() + 900 - now.timestamp()))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests, please wait before requesting another code",
                    headers={"Retry-After": str(retry_after)},
                )

        # 2. IP limit: 10 requests / 60 min (3600s)
        window_start_ip = now - timedelta(seconds=3600)
        ip_sends = db.execute(
            select(AuthAttempt.created_at)
            .where(
                AuthAttempt.action == "otp_send",
                AuthAttempt.ip_hash == ip_h,
                AuthAttempt.created_at >= window_start_ip,
            )
            .order_by(AuthAttempt.created_at.asc())
        ).scalars().all()

        if len(ip_sends) >= settings.RATE_LIMIT_OTP_SEND_PER_IP:
            oldest_ip_send = ip_sends[0]
            retry_after = max(1, int(oldest_ip_send.timestamp() + 3600 - now.timestamp()))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many code requests from this network. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    elif action == "otp_verify":
        # Identifier limit: 10 failed guesses / 60 min (3600s) cumulative across all OTP codes
        if ident_h:
            window_start = now - timedelta(seconds=3600)
            failed_guesses = db.execute(
                select(AuthAttempt.created_at)
                .where(
                    AuthAttempt.action == "otp_verify",
                    AuthAttempt.identifier_hash == ident_h,
                    AuthAttempt.success.is_(False),
                    AuthAttempt.created_at >= window_start,
                )
                .order_by(AuthAttempt.created_at.asc())
            ).scalars().all()

            if len(failed_guesses) >= settings.RATE_LIMIT_OTP_VERIFY_PER_IDENTIFIER:
                oldest_guess = failed_guesses[0]
                retry_after = max(1, int(oldest_guess.timestamp() + 3600 - now.timestamp()))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed verification attempts. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )

    elif action == "password_reset":
        # Identifier limit: 5 attempts / 60 min (3600s)
        if ident_h:
            window_start = now - timedelta(seconds=3600)
            resets = db.execute(
                select(AuthAttempt.created_at)
                .where(
                    AuthAttempt.action == "password_reset",
                    AuthAttempt.identifier_hash == ident_h,
                    AuthAttempt.created_at >= window_start,
                )
                .order_by(AuthAttempt.created_at.asc())
            ).scalars().all()

            if len(resets) >= settings.RATE_LIMIT_PASSWORD_RESET_PER_IDENTIFIER:
                oldest_reset = resets[0]
                retry_after = max(1, int(oldest_reset.timestamp() + 3600 - now.timestamp()))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many password reset attempts. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )


def record_attempt(
    db: Session,
    request: Request,
    action: str,
    identifier: str | None = None,
    success: bool = False,
) -> None:
    """Record an authentication attempt in auth_attempts table."""
    if not settings.RATE_LIMIT_ENABLED:
        return

    client_ip = get_client_ip(request)
    attempt = AuthAttempt(
        action=action,
        identifier_hash=hash_identifier(identifier),
        ip_hash=hash_ip(client_ip),
        success=success,
    )
    db.add(attempt)
    db.commit()

    # Probabilistic lazy pruning (1% of requests)
    if random.random() < 0.01:
        try:
            prune_old_attempts(db)
        except Exception:
            logger.warning("Lazy pruning of auth_attempts failed", exc_info=True)


def prune_old_attempts(db: Session, older_than_hours: int = 24) -> int:
    """Prune auth_attempts older than the retention threshold (default 24 hours)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
    stmt = delete(AuthAttempt).where(AuthAttempt.created_at < cutoff)
    result = db.execute(stmt)
    db.commit()
    return result.rowcount or 0

