#!/usr/bin/env python3
"""Seed script — inserts sample financial documents directly via SQLAlchemy.

Runs inside the backend container (has full DB access without HTTP auth):
    docker compose exec backend python scripts/seed_documents.py
    docker compose exec backend python scripts/seed_documents.py --count 50
"""

import argparse
import sys

from faker import Faker

sys.path.insert(0, "/app")

fake = Faker("es_CO")

DOCUMENT_TYPES = ["invoice", "receipt", "voucher", "credit_note", "debit_note"]
AMOUNT_RANGES = {
    "invoice": (100_000, 50_000_000),
    "receipt": (1_000, 5_000_000),
    "voucher": (5_000, 10_000_000),
    "credit_note": (10_000, 20_000_000),
    "debit_note": (10_000, 20_000_000),
}


def random_amount(doc_type: str) -> float:
    lo, hi = AMOUNT_RANGES[doc_type]
    return round(fake.pyfloat(min_value=lo, max_value=hi, right_digits=2), 2)


def random_metadata(doc_type: str, index: int) -> dict:
    prefix = doc_type[:3].upper()
    year = fake.year()
    base = {
        "client": fake.company(),
        "email": fake.company_email(),
        "phone": fake.phone_number(),
        "reference": f"{prefix}-{year}-{index:04d}",
        "city": fake.city(),
        "notes": fake.sentence(nb_words=6),
    }
    if doc_type == "invoice":
        base["tax"] = f"{fake.random_element([5, 19])}%"
        base["currency"] = "COP"
        base["payment_terms"] = fake.random_element(["30 días", "60 días", "Contado"])
    elif doc_type == "receipt":
        base["payment_method"] = fake.random_element(["Efectivo", "Tarjeta", "Transferencia", "PSE"])
    elif doc_type == "voucher":
        base["approved_by"] = fake.name()
        base["cost_center"] = str(fake.numerify("CC-####"))
    elif doc_type in ("credit_note", "debit_note"):
        base["original_invoice"] = f"INV-{year}-{max(1, index-1):04d}"
        base["reason"] = fake.sentence(nb_words=5)
    return base


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed financial documents directly via SQLAlchemy")
    parser.add_argument("--count", type=int, default=20, help="Number of documents to create (default: 20)")
    args = parser.parse_args()

    from app.domain.entities.document import Document
    from app.infrastructure.database import get_db
    from app.infrastructure.repositories.document_repository import DocumentRepository
    from app.infrastructure.repositories.audit_repository import AuditRepository

    db = next(get_db())
    repo = DocumentRepository(db)
    audit = AuditRepository(db)
    width = len(str(args.count))
    created = 0

    print(f"Creating {args.count} documents directly in the database...\n")

    for i in range(1, args.count + 1):
        doc_type = fake.random_element(DOCUMENT_TYPES)
        created_by = fake.email()

        doc = Document(
            type=doc_type,
            amount=random_amount(doc_type),
            metadata=random_metadata(doc_type, i),
            created_by=created_by,
        )

        saved = repo.create(doc)
        audit.log_created(
            "documents", str(saved.id), f"type={saved.type}, amount={saved.amount}", user_id="seed-script"
        )
        created += 1
        print(f"[{i:>{width}}/{args.count}] #{saved.id} | {saved.type:12s} | {saved.amount:>15,.2f} COP | {created_by}")

    print(f"\n{'=' * 50}")
    print(f"Done. Created: {created} documents.")


if __name__ == "__main__":
    main()
