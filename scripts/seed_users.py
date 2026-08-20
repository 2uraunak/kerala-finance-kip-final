"""
Seed mock users for demonstration.
Creates Admin, Analyst, and Viewer accounts.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kip:kip_secret@localhost:5432/kipdb").replace(
    "postgresql+asyncpg://", "postgresql://"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MOCK_USERS = [
    {
        "id": str(uuid.uuid4()),
        "username": "admin_kerala",
        "email": "admin@finance.kerala.gov.in",
        "password": "Admin@123",
        "role": "admin",
        "department": "Finance Department, Kerala — Administration",
    },
    {
        "id": str(uuid.uuid4()),
        "username": "analyst_finance",
        "email": "analyst@finance.kerala.gov.in",
        "password": "Analyst@123",
        "role": "analyst",
        "department": "Finance Department, Kerala — Budget Division",
    },
    {
        "id": str(uuid.uuid4()),
        "username": "viewer_gst",
        "email": "viewer@finance.kerala.gov.in",
        "password": "Viewer@123",
        "role": "viewer",
        "department": "Finance Department, Kerala — GST Cell",
    },
]


def seed_users():
    with SessionLocal() as session:
        for user in MOCK_USERS:
            existing = session.execute(
                text("SELECT id FROM users WHERE username=:username"),
                {"username": user["username"]}
            ).fetchone()
            if not existing:
                session.execute(text("""
                    INSERT INTO users (id, username, email, hashed_password, role, department, is_active, created_at)
                    VALUES (:id, :username, :email, :hashed_password, :role, :department, true, now())
                """), {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "hashed_password": pwd_context.hash(user["password"]),
                    "role": user["role"],
                    "department": user["department"],
                })
                print(f"✅ Created user: {user['username']} ({user['role']}) — Password: {user['password']}")
            else:
                print(f"⏭️  User already exists: {user['username']}")
        session.commit()
    print("\n✅ User seeding complete!")
    print("\nDemo Credentials:")
    for u in MOCK_USERS:
        print(f"  {u['role'].upper():10} | username: {u['username']:20} | password: {u['password']}")


if __name__ == "__main__":
    seed_users()
