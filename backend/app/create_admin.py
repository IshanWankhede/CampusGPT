"""CLI script to bootstrap the initial Admin user for CampusGPT.

Usage:
    Interactive mode:
        python -m app.create_admin

    Argument mode:
        python -m app.create_admin --email admin@campusgpt.dev --name "Admin User" --password "yourpassword"
"""

import argparse
import getpass
import sys

from app.auth import repository, service
from app.database.session import SessionLocal
from app.models.user import AuthProvider, CollegeName, User, UserRole


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the initial Admin user for CampusGPT.")
    parser.add_argument("--email", type=str, help="Admin email address")
    parser.add_argument("--name", type=str, help="Admin full name")
    parser.add_argument("--password", type=str, help="Admin password")
    parser.add_argument(
        "--college",
        type=str,
        choices=[c.value for c in CollegeName],
        default=None,
        help="Optional college assignment (COEP, PICT, VIT)",
    )

    args = parser.parse_args()

    email = args.email
    full_name = args.name
    password = args.password
    college_str = args.college

    # Interactive prompts if arguments are missing
    if not email:
        try:
            email = input("Enter Admin Email: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            sys.exit(1)

    if not email:
        print("Error: Email cannot be empty.", file=sys.stderr)
        sys.exit(1)

    if not full_name:
        try:
            full_name = input("Enter Admin Full Name: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            sys.exit(1)

    if not full_name:
        print("Error: Full name cannot be empty.", file=sys.stderr)
        sys.exit(1)

    if not password:
        try:
            password = getpass.getpass("Enter Admin Password: ").strip()
            confirm_password = getpass.getpass("Confirm Admin Password: ").strip()
            if password != confirm_password:
                print("Error: Passwords do not match.", file=sys.stderr)
                sys.exit(1)
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            sys.exit(1)

    if not password:
        print("Error: Password cannot be empty.", file=sys.stderr)
        sys.exit(1)

    college = None
    if college_str:
        try:
            college = CollegeName(college_str)
        except ValueError:
            print(f"Error: Invalid college '{college_str}'. Valid choices: COEP, PICT, VIT.", file=sys.stderr)
            sys.exit(1)

    db = SessionLocal()
    try:
        existing_user = repository.get_user_by_email(db, email.lower())
        if existing_user:
            print(f"Error: A user with email '{email}' already exists.", file=sys.stderr)
            sys.exit(1)

        hashed_password = service.hash_password(password)

        admin_user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.ADMIN,
            college=college,
            auth_provider=AuthProvider.LOCAL,
            is_active=True,
            is_email_verified=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"Successfully created Admin user: {admin_user.email}")
    except Exception as exc:
        db.rollback()
        print(f"Error creating Admin user: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
