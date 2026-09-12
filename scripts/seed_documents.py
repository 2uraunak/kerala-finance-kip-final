"""
Seed script — inserts realistic Kerala Finance Government Orders into the database.
Includes a superseded GO + its amendment for the core Round 2 demo scenario.
Run inside the Docker network: docker exec -it kip-api-gateway python /scripts/seed_documents.py
Or directly: python scripts/seed_documents.py (with DATABASE_URL set)
"""
import os
import json
import uuid
from datetime import datetime

SAMPLE_DOCUMENTS = [
    # ─────────────────────────────────────────────────────────────────
    # DEMO SCENARIO DOCUMENT 1: THE OUTDATED / SUPERSEDED GO
    # This is the "trap" — if the system returns this as authoritative, it's wrong.
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "title": "GO(Ms)No.45/2023/Fin — Dearness Allowance Revision for State Government Employees",
        "doc_number": "GO(Ms)No.45/2023/Fin",
        "doc_type": "government_order",
        "status": "superseded",
        "department": "Finance Department, Kerala",
        "subject": "DA/Pay",
        "authority": "Finance Department, Government of Kerala",
        "year": 2023,
        "issue_date": "2023-03-01",
        "is_scanned": False,
        "is_restricted": False,
        "classification_confidence": 0.97,
        "auto_classified": True,
        "tags": ["dearness allowance", "DA", "pay revision", "state employees", "2023", "superseded"],
        "raw_text": """GOVERNMENT OF KERALA
Finance Department

G.O.(Ms) No.45/2023/Fin                                     Dated: Thiruvananthapuram, 01.03.2023

Sub: Revision of Dearness Allowance to State Government Employees – Sanctioned.

Read:
1. G.O.(Ms) No.128/2022/Fin, dated 01.09.2022.
2. Government of India, Ministry of Finance O.M. dated 25.01.2023.

ORDER

In continuation of the orders issued in the Government Order read as first paper above, and in 
accordance with the central Government revision, the Government of Kerala hereby orders 
revision of Dearness Allowance payable to State Government Employees with effect from 01.01.2023 
as follows:

RATES OF DEARNESS ALLOWANCE (Effective 01.01.2023):
- Pay Level 1 to 5:     DA @ 42% of Basic Pay
- Pay Level 6 to 10:    DA @ 42% of Basic Pay  
- Pay Level 11 to 14:   DA @ 42% of Basic Pay

The Dearness Allowance will be treated as Dearness Pay for all purposes.

The arrears on account of revision of DA from 01.01.2023 to 28.02.2023 will be credited to 
the General Provident Fund account of the employees concerned.

NOTE: This order has been SUPERSEDED by GO(Ms)No.112/2023/Fin dated 01.09.2023 which revises 
DA rates to 46% with effect from 01.07.2023. DO NOT CITE THIS ORDER AS CURRENT POLICY.

By order of the Governor,
(Dr. V. P. Joy, IAS)
Additional Chief Secretary (Finance)
Government of Kerala""",
        "summary": "[SUPERSEDED by GO 112/2023] DA revised to 42% of basic pay w.e.f. 01.01.2023 for all Kerala state government employees. Arrears credited to GPF.",
    },

    # ─────────────────────────────────────────────────────────────────
    # DEMO SCENARIO DOCUMENT 2: THE ACTIVE / AUTHORITATIVE GO
    # This is what the system SHOULD return. Supersedes GO 45/2023.
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "title": "GO(Ms)No.112/2023/Fin — Revision of Dearness Allowance to State Government Employees w.e.f. 01.07.2023",
        "doc_number": "GO(Ms)No.112/2023/Fin",
        "doc_type": "government_order",
        "status": "active",
        "department": "Finance Department, Kerala",
        "subject": "DA/Pay",
        "authority": "Finance Department, Government of Kerala",
        "year": 2023,
        "issue_date": "2023-09-01",
        "is_scanned": False,
        "is_restricted": False,
        "classification_confidence": 0.98,
        "auto_classified": True,
        "tags": ["dearness allowance", "DA", "pay revision", "state employees", "2023", "active", "amendment"],
        "raw_text": """GOVERNMENT OF KERALA
Finance Department

G.O.(Ms) No.112/2023/Fin                                    Dated: Thiruvananthapuram, 01.09.2023

Sub: Revision of Dearness Allowance to State Government Employees with effect from 
     01.07.2023 — Sanctioned.

Read:
1. G.O.(Ms) No.45/2023/Fin, dated 01.03.2023. [SUPERSEDED BY THIS ORDER]
2. Government of India, Ministry of Finance O.M. No. 1/3/2023-E-II(B) dated 25.07.2023.

ORDER

In supersession of the Government Order read as first paper above, Government are pleased to 
order revision of Dearness Allowance payable to State Government Employees with effect from 
01.07.2023 as follows:

REVISED RATES OF DEARNESS ALLOWANCE (AUTHORITATIVE — Effective 01.07.2023):
- All Pay Levels (1 to 14):   DA @ 46% of Basic Pay

This represents an increase of 4 percentage points over the rate of 42% sanctioned vide 
G.O.(Ms) No.45/2023/Fin dated 01.03.2023, which stands SUPERSEDED.

ARREAR PAYMENTS:
The arrears from 01.07.2023 to 31.08.2023 shall be paid in cash along with the salary 
for September 2023.

FINANCIAL IMPLICATIONS:
Estimated additional annual outgo: ₹ 1,234 Crore
Head of Account: 2071-01-101-97

VERIFICATION:
This order supersedes GO(Ms)No.45/2023/Fin. Any policy note citing the earlier DA rate 
of 42% is incorrect and must be revised to reflect the current rate of 46%.

By order of the Governor,
(Dr. V. P. Joy, IAS)
Additional Chief Secretary (Finance)
Government of Kerala

CERTIFIED: This is the ACTIVE and AUTHORITATIVE version as on date.""",
        "summary": "[ACTIVE — CURRENT ORDER] DA revised to 46% of basic pay w.e.f. 01.07.2023. Supersedes GO(Ms)No.45/2023/Fin (DA was 42%). Arrears paid with September 2023 salary.",
    },

    # ─────────────────────────────────────────────────────────────────
    # DOCUMENT 3: Kerala Budget 2024-25
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "title": "Kerala Budget Speech 2024-25 — Finance Minister's Statement",
        "doc_number": "BUDGET_2024_25",
        "doc_type": "budget_document",
        "status": "active",
        "department": "Finance Department, Kerala",
        "subject": "Budget",
        "authority": "Finance Minister, Government of Kerala",
        "year": 2024,
        "issue_date": "2024-02-02",
        "is_scanned": False,
        "is_restricted": False,
        "classification_confidence": 0.93,
        "auto_classified": True,
        "tags": ["budget", "2024-25", "expenditure", "GST", "revenue"],
        "raw_text": """KERALA BUDGET SPEECH 2024-25
Hon'ble Finance Minister
Government of Kerala
February 2, 2024

FISCAL OVERVIEW:
Total Outlay: ₹ 2,23,979 Crore
Revenue Receipts: ₹ 1,15,234 Crore
Capital Expenditure: ₹ 22,456 Crore
Revenue Deficit: ₹ 18,234 Crore

STATE'S OWN TAX REVENUE (SOTR):
- State's Own Tax Revenue: ₹ 89,234 Crore
- GST Revenue: ₹ 45,123 Crore (50.57% of SOTR)
- State Excise: ₹ 9,234 Crore
- Stamps & Registration: ₹ 8,456 Crore
- Motor Vehicle Tax: ₹ 5,234 Crore

SECTOR-WISE ALLOCATIONS:
Para 12: Education Sector — ₹ 38,421 Crore (17.1% of total outlay)
Para 23: Health Sector — ₹ 18,234 Crore
Para 34: Infrastructure — ₹ 22,456 Crore (including KIIFB projects)
Para 45: Social Security — Pension enhanced from ₹1,600 to ₹1,800 per month.
Para 78: KFON Phase 2 — ₹ 2,345 Crore allocated for Kerala Fibre Optic Network.
Para 112: GST Compliance — Target 95% filing rate by March 2025.

BORROWING PROGRAMME:
Net Borrowings: ₹ 34,567 Crore
Debt-GSDP Ratio: 34.2% (within FRBM limit of 35%)

By order of the Finance Minister,
Government of Kerala""",
        "summary": "Kerala Budget 2024-25: Total outlay ₹2,23,979 Cr. GST revenue ₹45,123 Cr. Social pension raised to ₹1,800/month. Education ₹38,421 Cr, Infrastructure ₹22,456 Cr.",
    },

    # ─────────────────────────────────────────────────────────────────
    # DOCUMENT 4: GST Circular — Works Contract
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "title": "GST Circular No.178/10/2024-GST — Clarification on Works Contract Services for Government",
        "doc_number": "GST_Circular_178_2024",
        "doc_type": "gst_policy",
        "status": "active",
        "department": "CBIC, Ministry of Finance, Government of India",
        "subject": "GST",
        "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
        "year": 2024,
        "issue_date": "2024-03-15",
        "is_scanned": False,
        "is_restricted": False,
        "classification_confidence": 0.96,
        "auto_classified": True,
        "tags": ["GST", "works contract", "government", "circular", "12%", "18%", "CBIC"],
        "raw_text": """CIRCULAR No. 178/10/2024-GST

F.No. CBIC-20001/7/2024-GST
Government of India, Ministry of Finance
Department of Revenue
Central Board of Indirect Taxes and Customs

Dated: 15th March, 2024

Subject: Clarification regarding applicability of GST on works contract services provided to 
Government entities — reg.

1. References have been received from various trade and industry seeking clarification on the 
   applicability of GST on works contract services provided to Government entities.

2. The matter has been examined. It is hereby clarified:

   2.1 Works contract services to Central/State Government, Union Territories, Local authorities 
       involving CONSTRUCTION OF ROADS, BRIDGES, RAILWAYS, WATERWAYS: GST @ 12%
       
   2.2 Other works contract services to Government: GST @ 18%
   
   2.3 Pure services (excluding works contract) to Government covered under 
       Notification 12/2017-CT(R): Nil GST

3. HSN Codes:
   - Construction services: HSN 9954
   - Other services to Government: HSN 9997

4. This circular supersedes all previous clarifications on this subject.

By order and in the name of the President of India,
(Joint Secretary to Government of India)
CBIC""",
        "summary": "GST clarification on works contracts: roads/bridges/railways to govt = 12%; other works contracts = 18%; pure services under Notification 12/2017-CT(R) = Nil GST.",
    },

    # ─────────────────────────────────────────────────────────────────
    # DOCUMENT 5: Travelling Allowance GO
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "title": "GO(Ms)No.89/2022/Fin — Revision of Travelling Allowance Rules for State Employees",
        "doc_number": "GO(Ms)No.89/2022/Fin",
        "doc_type": "government_order",
        "status": "active",
        "department": "Finance Department, Kerala",
        "subject": "TA/Travelling Allowance",
        "authority": "Finance Department, Government of Kerala",
        "year": 2022,
        "issue_date": "2022-07-01",
        "is_scanned": False,
        "is_restricted": False,
        "classification_confidence": 0.95,
        "auto_classified": True,
        "tags": ["travelling allowance", "TA", "pay rules", "state employees", "2022"],
        "raw_text": """GOVERNMENT OF KERALA
Finance Department

G.O.(Ms) No.89/2022/Fin                                     Dated: Thiruvananthapuram, 01.07.2022

Sub: Revision of Travelling Allowance to State Government Employees — Sanctioned.

ORDER

Government are pleased to revise the Travelling Allowance admissible to State Government 
employees as follows with effect from 01.07.2022:

REVISED TA RATES:
Grade A Officers (Pay ₹75,000 and above):
  - Air Travel: Economy class permitted for journeys above 500 km
  - Rail Travel: AC-1st Class
  - Daily Allowance: ₹750 per day

Grade B Officers (Pay ₹50,000 to ₹74,999):
  - Air Travel: Not permitted (train/road preferred)  
  - Rail Travel: AC-2nd Class
  - Daily Allowance: ₹600 per day

Grade C Officers (Pay below ₹50,000):
  - Rail Travel: Sleeper Class / AC-3rd Class
  - Daily Allowance: ₹450 per day

LOCAL CONVEYANCE:
Auto/Taxi: Actual cost limited to ₹200 per day for local official travel.
Personal vehicle: ₹8 per km (two-wheeler), ₹14 per km (car).

HOTEL ACCOMMODATION LIMITS:
Grade A: ₹3,000 per day (metro), ₹2,000 per day (other cities)
Grade B: ₹2,000 per day (metro), ₹1,500 per day (other cities)
Grade C: ₹1,500 per day (metro), ₹1,000 per day (other cities)

By order of the Governor,
(K. N. Balagopal)
Finance Minister, Government of Kerala""",
        "summary": "TA revision w.e.f. 01.07.2022: Grade A officers (₹75k+) get AC-1st class rail, ₹750 DA; Grade B ₹600 DA; Grade C ₹450 DA. Local travel ₹8/km (two-wheeler).",
    },

    # ─────────────────────────────────────────────────────────────────
    # DOCUMENT 6: Austerity Measures OM
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "title": "Office Memorandum — Austerity Measures for Financial Year 2024-25",
        "doc_number": "OM_Finance_2024_Austerity",
        "doc_type": "office_memorandum",
        "status": "active",
        "department": "Finance Department, Kerala",
        "subject": "Austerity/Expenditure Control",
        "authority": "Principal Secretary (Finance), Government of Kerala",
        "year": 2024,
        "issue_date": "2024-04-01",
        "is_scanned": False,
        "is_restricted": False,
        "classification_confidence": 0.91,
        "auto_classified": True,
        "tags": ["austerity", "expenditure control", "2024-25", "budget discipline"],
        "raw_text": """GOVERNMENT OF KERALA
Finance Department

No. 14/57/2024/Fin                                           Date: 01.04.2024

OFFICE MEMORANDUM

Sub: Austerity measures to be followed during 2024-25.

In continuation of the Government's policy of fiscal prudence and expenditure management, 
the following austerity measures shall be strictly observed during 2024-25:

1. RESTRICTIONS ON EXPENDITURE:
   (a) No new posts shall be created without prior Finance Department concurrence.
   (b) All foreign tours must be pre-approved by the Chief Minister's Office.
   (c) Expenditure on vehicles shall not exceed 80% of the previous year's actual.
   (d) Purchase of new furniture/equipment above ₹5,000 requires Finance sanction.
   (e) Advertisement expenditure to be restricted to 75% of last year's budget.

2. PRIORITY SECTORS (exempt from austerity restrictions):
   (a) Healthcare and medical expenditure
   (b) Infrastructure projects under KIIFB
   (c) Social welfare payments to Direct Benefit Transfer beneficiaries
   (d) Disaster Management and relief operations

3. REPORTING REQUIREMENTS:
   All departments shall submit monthly expenditure statements by the 5th of each month 
   to the Finance Department for monitoring.

4. CONSEQUENCES OF NON-COMPLIANCE:
   Non-compliance will be viewed seriously. The concerned Drawing and Disbursing Officer 
   will be held personally responsible for unauthorized expenditure.

5. These instructions supersede all previous austerity circulars issued for 2023-24.

Principal Secretary (Finance)
Government of Kerala""",
        "summary": "Austerity measures for FY 2024-25: no new posts without Finance concurrence, foreign tours need CM approval, vehicle spend ≤80% of previous year. Healthcare and infrastructure exempt.",
    },

    # ─────────────────────────────────────────────────────────────────
    # DOCUMENT 7: RESTRICTED — Internal Audit Report
    # Demonstrates document-level access control in the demo
    # ─────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "title": "CONFIDENTIAL — Finance Department Internal Audit Report Q3 2024",
        "doc_number": "AUDIT_Q3_2024_RESTRICTED",
        "doc_type": "other",
        "status": "active",
        "department": "Finance Department, Kerala",
        "subject": "Internal Audit",
        "authority": "Finance Department, Government of Kerala",
        "year": 2024,
        "issue_date": "2024-10-01",
        "is_scanned": False,
        "is_restricted": True,
        "classification_confidence": 0.88,
        "auto_classified": True,
        "tags": ["audit", "restricted", "internal", "confidential"],
        "raw_text": """RESTRICTED — FOR AUTHORIZED PERSONNEL ONLY

FINANCE DEPARTMENT INTERNAL AUDIT REPORT
Q3 2024 (July – September 2024)

[This document contains sensitive financial audit findings and is restricted
to authorized Finance Department personnel — Admin access only.]

AUDIT FINDINGS SUMMARY:
1. Overall compliance rate: 87.3%
2. Pending reconciliations: ₹ 234 Crore
3. High-risk transactions identified: 12
4. Departments with below-50% compliance: 3

RISK CATEGORIES:
HIGH RISK: 12 transactions flagged for further investigation
MEDIUM RISK: 34 transactions requiring follow-up
LOW RISK: 89 transactions with minor discrepancies

NOTE: This document is accessible only to Admin-level users in the KIP system.
Analysts and Viewers will receive a 403 Access Denied response.""",
        "summary": "[RESTRICTED — Admin Only] Internal audit Q3 2024. Compliance 87.3%, pending reconciliations ₹234 Cr, 12 high-risk transactions identified.",
    },
]


def seed_documents():
    """Insert Kerala Finance documents into the database with full lineage setup."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://kip:kip_secret@localhost:5432/kipdb"
    ).replace("postgresql+asyncpg://", "postgresql://")

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)

    seeded_ids = {}

    with SessionLocal() as session:
        for doc in SAMPLE_DOCUMENTS:
            existing = session.execute(
                text("SELECT id FROM documents WHERE doc_number=:dn"),
                {"dn": doc["doc_number"]},
            ).fetchone()

            if not existing:
                session.execute(
                    text("""
                    INSERT INTO documents (
                        id, title, doc_number, doc_type, status, department,
                        year, issue_date, is_scanned, is_restricted,
                        is_indexed, tags, raw_text, summary,
                        created_at, updated_at, created_by
                    ) VALUES (
                        :id, :title, :doc_number, :doc_type::documenttype, :status::documentstatus,
                        :department, :year, :issue_date, :is_scanned,
                        :is_restricted, true, :tags::json, :raw_text, :summary,
                        now(), now(), 'seed_script'
                    )
                    ON CONFLICT (doc_number) DO NOTHING
                    """),
                    {
                        "id": doc["id"],
                        "title": doc["title"],
                        "doc_number": doc["doc_number"],
                        "doc_type": doc["doc_type"].upper(),
                        "status": doc["status"].upper(),
                        "department": doc.get("department", "Finance Department, Kerala"),
                        "year": doc.get("year"),
                        "issue_date": datetime.strptime(doc["issue_date"], "%Y-%m-%d"),
                        "is_scanned": doc.get("is_scanned", False),
                        "is_restricted": doc.get("is_restricted", False),
                        "tags": json.dumps(doc.get("tags", [])),
                        "raw_text": doc.get("raw_text", ""),
                        "summary": doc.get("summary", ""),
                    },
                )
                print(f"✅ Seeded: {doc['doc_number']} — {doc['title'][:60]}...")
            else:
                print(f"⚠️  Already exists: {doc['doc_number']}")

            seeded_ids[doc["doc_number"]] = doc["id"]

        session.commit()

        # ── CRITICAL: Set up lineage — GO 45/2023 superseded by GO 112/2023 ──
        old_num = "GO(Ms)No.45/2023/Fin"
        new_num = "GO(Ms)No.112/2023/Fin"

        old_row = session.execute(
            text("SELECT id FROM documents WHERE doc_number=:dn"), {"dn": old_num}
        ).fetchone()
        new_row = session.execute(
            text("SELECT id FROM documents WHERE doc_number=:dn"), {"dn": new_num}
        ).fetchone()

        if old_row and new_row:
            old_id = str(old_row[0])
            new_id = str(new_row[0])

            session.execute(
                text("""
                UPDATE documents
                SET status='superseded', superseded_by_id=:new_id, updated_at=now()
                WHERE id=:old_id
                """),
                {"new_id": new_id, "old_id": old_id},
            )
            session.execute(
                text("""
                UPDATE documents
                SET supersedes_id=:old_id, updated_at=now()
                WHERE id=:new_id
                """),
                {"old_id": old_id, "new_id": new_id},
            )
            session.commit()
            print(f"\n🔗 LINEAGE SET: GO 45/2023 [SUPERSEDED] → superseded by → GO 112/2023 [ACTIVE]")
        else:
            print("\n⚠️  WARNING: Could not set lineage — one or both GOs not found!")

    print("\n✅ Document seeding complete!")
    print(f"   Total documents: {len(SAMPLE_DOCUMENTS)}")
    print(f"   Superseded GOs: 1 (GO 45/2023)")
    print(f"   Active GOs: 4")
    print(f"   Restricted docs: 1 (Audit Report — Admin only)")


if __name__ == "__main__":
    seed_documents()
