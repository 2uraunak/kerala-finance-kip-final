"""
demo_scenario.py — Reset and verify the Round 2 demo environment.

Run this before the live demo to ensure everything is perfectly set up:
    docker exec -it kip-api-gateway python /scripts/demo_scenario.py

Or locally (with DATABASE_URL set):
    python scripts/demo_scenario.py
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://kip:kip_secret@localhost:5432/kipdb"
).replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

CHECKS = []


def check(label: str, passed: bool, detail: str = ""):
    icon = "✅" if passed else "❌"
    CHECKS.append(passed)
    print(f"  {icon} {label}" + (f" — {detail}" if detail else ""))


def run_demo_checks():
    print("\n" + "=" * 60)
    print("  KIP ROUND 2 — DEMO SCENARIO VERIFICATION")
    print("=" * 60)

    with SessionLocal() as session:

        # ── 1. GO 45/2023 exists and is SUPERSEDED ──
        go45 = session.execute(
            text("SELECT id, status, superseded_by_id FROM documents WHERE doc_number='GO(Ms)No.45/2023/Fin'")
        ).fetchone()
        check("GO(Ms)No.45/2023/Fin exists", go45 is not None)
        if go45:
            check(
                "GO 45/2023 is marked SUPERSEDED",
                go45.status == "superseded",
                f"status={go45.status}"
            )
            check(
                "GO 45/2023 has superseded_by_id set",
                go45.superseded_by_id is not None,
                f"superseded_by={go45.superseded_by_id}"
            )

        # ── 2. GO 112/2023 exists and is ACTIVE ──
        go112 = session.execute(
            text("SELECT id, status, supersedes_id FROM documents WHERE doc_number='GO(Ms)No.112/2023/Fin'")
        ).fetchone()
        check("GO(Ms)No.112/2023/Fin exists", go112 is not None)
        if go112:
            check(
                "GO 112/2023 is ACTIVE",
                go112.status == "active",
                f"status={go112.status}"
            )
            check(
                "GO 112/2023 has supersedes_id pointing to GO 45",
                go112.supersedes_id is not None,
                f"supersedes={go112.supersedes_id}"
            )

        # ── 3. Lineage chain is consistent ──
        if go45 and go112:
            chain_consistent = str(go45.superseded_by_id) == str(go112.id)
            check(
                "Lineage chain is consistent (GO45→GO112)",
                chain_consistent,
                f"GO45.superseded_by_id == GO112.id: {chain_consistent}"
            )

        # ── 4. Restricted document exists ──
        restricted = session.execute(
            text("SELECT id, is_restricted FROM documents WHERE doc_number='AUDIT_Q3_2024_RESTRICTED'")
        ).fetchone()
        check("Restricted audit document exists", restricted is not None)
        if restricted:
            check("Audit document is marked restricted", restricted.is_restricted is True)

        # ── 5. Total document count ──
        total = session.execute(text("SELECT COUNT(*) FROM documents")).scalar()
        check(f"Corpus has at least 6 documents", total >= 6, f"found {total} documents")

        # ── 6. All documents have subject/authority metadata ──
        missing_meta = session.execute(
            text("SELECT COUNT(*) FROM documents WHERE subject IS NULL OR subject=''")
        ).scalar()
        check("All documents have subject metadata", missing_meta == 0, f"{missing_meta} docs missing subject")

        # ── 7. Users exist ──
        user_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        check("Users are seeded", user_count > 0, f"found {user_count} users")

    # ── Summary ──
    print()
    passed = sum(CHECKS)
    total_checks = len(CHECKS)
    print("=" * 60)
    if passed == total_checks:
        print(f"  🎉 ALL {total_checks} CHECKS PASSED — Demo is ready!")
        print()
        print("  DEMO FLOW REMINDER:")
        print("  1. Search 'DA arrear payment rate' → GO 45 appears with 🔴 SUPERSEDED")
        print("  2. Response warns: NOT authoritative → points to GO 112")
        print("  3. Policy agent drafts note citing ONLY GO 112 (46% DA)")
        print("  4. Human checkpoint before finalizing the policy note")
        print("  5. Switch to Viewer role → try to open Audit Report → 403 Access Denied")
    else:
        failed = total_checks - passed
        print(f"  ⚠️  {failed}/{total_checks} CHECKS FAILED — Run seed_documents.py first!")
        print("  Run: python scripts/seed_documents.py")
        sys.exit(1)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_demo_checks()
