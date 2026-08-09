"""One-off script to create (or promote) an admin user.

Usage:
    python -m scripts.set_admin <username> <password>
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal  # noqa: E402
from app.models import User  # noqa: E402
from app.security import get_password_hash  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an admin user")
    parser.add_argument("username")
    parser.add_argument("password")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == args.username).first()
        if user:
            user.is_admin = 1
            print(f"Promoted existing user '{args.username}' to admin.")
        else:
            user = User(
                username=args.username,
                password_hash=get_password_hash(args.password),
                is_admin=1,
            )
            db.add(user)
            print(f"Created new admin user '{args.username}'.")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
