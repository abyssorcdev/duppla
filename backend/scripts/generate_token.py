#!/usr/bin/env python3
"""Generate a JWT token for local API testing without Google OAuth.

Usage (inside backend container):
    docker compose exec backend python scripts/generate_token.py
    docker compose exec backend python scripts/generate_token.py --email user@example.com
    docker compose exec backend python scripts/generate_token.py --hours 8
    docker compose exec backend python scripts/generate_token.py --list
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/app")

from jose import jwt

from app.core.config import settings
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.user import UserModel


def list_users() -> None:
    db = SessionLocal()
    try:
        users = db.query(UserModel).all()
        if not users:
            print("No hay usuarios en la base de datos.")
            return
        print(f"{'Email':<35} {'Rol':<10} {'Status':<10}")
        print("-" * 55)
        for u in users:
            print(f"{u.email:<35} {u.role or '-':<10} {u.status:<10}")
    finally:
        db.close()


def generate_token(email: str | None, hours: int) -> None:
    db = SessionLocal()
    try:
        if email:
            user = db.query(UserModel).filter(UserModel.email == email).first()
        else:
            user = (
                db.query(UserModel)
                .filter(UserModel.role == "admin", UserModel.status == "active")
                .first()
            )

        if not user:
            print(f"Error: no se encontró usuario{f' con email {email!r}' if email else ' admin activo'}.\n")
            print("Usa --list para ver los usuarios disponibles.")
            sys.exit(1)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "status": user.status,
            "exp": datetime.now(timezone.utc) + timedelta(hours=hours),
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        print(f"Usuario:  {user.name} <{user.email}>")
        print(f"Rol:      {user.role}")
        print(f"Status:   {user.status}")
        print(f"Expira:   {hours}h\n")
        print(token)
        print(f"\nUso con curl:")
        print(f'  export TOKEN="{token}"')
        print(f'  curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/documents')
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera un JWT para testing local")
    parser.add_argument("--email", default=None, help="Email del usuario (default: primer admin activo)")
    parser.add_argument("--hours", type=int, default=2, help="Horas de validez del token (default: 2)")
    parser.add_argument("--list", action="store_true", help="Listar usuarios disponibles")
    args = parser.parse_args()

    if args.list:
        list_users()
    else:
        generate_token(args.email, args.hours)
