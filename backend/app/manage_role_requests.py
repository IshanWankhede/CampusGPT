"""CLI script to manage role requests for CampusGPT.

Usage:
    List role requests:
        python -m app.manage_role_requests list [--status PENDING|APPROVED|REJECTED]

    Approve a role request:
        python -m app.manage_role_requests approve --id <request_uuid> [--note "Approval note"] [--admin admin@campusgpt.dev]

    Reject a role request:
        python -m app.manage_role_requests reject --id <request_uuid> [--note "Rejection reason"] [--admin admin@campusgpt.dev]
"""

import argparse
from datetime import datetime, timezone
import sys
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app.auth import repository
from app.database.session import SessionLocal
from app.models.role_request import RoleRequestStatus
from app.models.user import UserRole


def list_requests(
    status_filter: str | None = None,
    db: Session | None = None,
) -> None:
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        status_enum = RoleRequestStatus(status_filter) if status_filter else None
        requests = repository.get_role_requests(db, status=status_enum)
        if not requests:
            print("No role requests found.")
            return

        print(f"\n{'ID':<38} {'Applicant':<30} {'Requested Role':<15} {'Status':<10} {'Created At'}")
        print("-" * 110)
        for req in requests:
            created_str = req.created_at.strftime("%Y-%m-%d %H:%M:%S") if req.created_at else "N/A"
            print(
                f"{str(req.id):<38} {req.applicant_email:<30} {req.requested_role.value:<15} {req.status.value:<10} {created_str}"
            )
            if req.note:
                print(f"  Note: {req.note}")
        print(f"\nTotal: {len(requests)} request(s).\n")
    finally:
        if close_db:
            db.close()


def review_request(
    request_id_str: str,
    action: str,
    note: str | None = None,
    admin_email: str | None = None,
    db: Session | None = None,
) -> None:
    try:
        request_id = uuid.UUID(request_id_str)
    except ValueError:
        print(f"Error: Invalid UUID '{request_id_str}'", file=sys.stderr)
        sys.exit(1)

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        admin_user = None
        if admin_email:
            admin_user = repository.get_user_by_email(db, admin_email)
            if not admin_user:
                print(f"Error: Admin user with email '{admin_email}' not found.", file=sys.stderr)
                sys.exit(1)
            if admin_user.role != UserRole.ADMIN:
                print(f"Error: User '{admin_email}' is not an administrator.", file=sys.stderr)
                sys.exit(1)

        role_req = repository.get_role_request_by_id(db, request_id)
        if not role_req:
            print(f"Error: Role request '{request_id}' not found.", file=sys.stderr)
            sys.exit(1)

        if role_req.status != RoleRequestStatus.PENDING:
            print(f"Error: Role request is already {role_req.status.value}.", file=sys.stderr)
            sys.exit(1)

        if admin_user and role_req.user_id == admin_user.id:
            print("Error: Admins cannot approve or review their own role requests.", file=sys.stderr)
            sys.exit(1)

        now = datetime.now(timezone.utc)
        admin_id = admin_user.id if admin_user else None

        if action == "approve":
            if role_req.user_id:
                user = repository.get_user_by_id(db, role_req.user_id)
                if user:
                    user.role = role_req.requested_role
            role_req.status = RoleRequestStatus.APPROVED
            role_req.reviewed_by = admin_id
            role_req.reviewed_at = now
            if note:
                role_req.note = note
            db.commit()
            print(f"Successfully approved role request {role_req.id} for {role_req.applicant_email}.")
            print(f"User role updated to: {role_req.requested_role.value}")

        elif action == "reject":
            role_req.status = RoleRequestStatus.REJECTED
            role_req.reviewed_by = admin_id
            role_req.reviewed_at = now
            if note:
                role_req.note = note
            db.commit()
            print(f"Successfully rejected role request {role_req.id} for {role_req.applicant_email}.")
            print("Applicant role remains unchanged.")

    except Exception as exc:
        db.rollback()
        print(f"Error reviewing role request: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        if close_db:
            db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage CampusGPT Role Requests.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list subcommand
    list_parser = subparsers.add_parser("list", help="List role requests")
    list_parser.add_argument(
        "--status",
        choices=[s.value for s in RoleRequestStatus],
        default=None,
        help="Filter requests by status",
    )

    # approve subcommand
    approve_parser = subparsers.add_parser("approve", help="Approve a role request")
    approve_parser.add_argument("--id", required=True, help="Role request UUID")
    approve_parser.add_argument("--note", default=None, help="Optional approval note")
    approve_parser.add_argument("--admin", default=None, help="Reviewing admin email")

    # reject subcommand
    reject_parser = subparsers.add_parser("reject", help="Reject a role request")
    reject_parser.add_argument("--id", required=True, help="Role request UUID")
    reject_parser.add_argument("--note", default=None, help="Optional rejection note")
    reject_parser.add_argument("--admin", default=None, help="Reviewing admin email")

    args = parser.parse_args()

    if args.command == "list":
        list_requests(args.status)
    elif args.command in ("approve", "reject"):
        review_request(args.id, args.command, args.note, args.admin)


if __name__ == "__main__":
    main()
