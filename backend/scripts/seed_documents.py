#!/usr/bin/env python3
"""Seed script to generate sample financial documents via the API.

Usage:
    python seed_documents.py                  # creates 20 documents (default)
    python seed_documents.py --count 50       # creates 50 documents
    python seed_documents.py --url http://... # custom API URL
"""

import argparse
import json
import sys
import os

import httpx
from faker import Faker

fake = Faker("es_CO")

# --- Configuration ---
# When running inside Docker the env vars come from the container environment.
DEFAULT_API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

_raw_keys: dict = json.loads(os.getenv("VALID_API_KEYS", "{}"))
DEFAULT_API_KEY = (_raw_keys.get("post") or [""])[0]
DEFAULT_COUNT = 20

DOCUMENT_TYPES = ["invoice", "receipt", "voucher", "credit_note", "debit_note"]

AMOUNT_RANGES = {
    "invoice": (100_000, 50_000_000),
    "receipt": (1_000, 5_000_000),
    "voucher": (5_000, 10_000_000),
    "credit_note": (10_000, 20_000_000),
    "debit_note": (10_000, 20_000_000),
}


def random_amount(doc_type: str) -> float:
    min_val, max_val = AMOUNT_RANGES[doc_type]
    return round(fake.pyfloat(min_value=min_val, max_value=max_val, right_digits=2), 2)


def random_metadata(doc_type: str, index: int) -> dict:
    ref_prefix = doc_type[:3].upper()
    year = fake.year()

    base = {
        "client": fake.company(),
        "client_email": fake.company_email(),
        "client_phone": fake.phone_number(),
        "reference": f"{ref_prefix}-{year}-{index:04d}",
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
        prev = fake.random_int(min=1, max=max(1, index - 1))
        base["original_invoice"] = f"INV-{year}-{prev:04d}"
        base["reason"] = fake.sentence(nb_words=5)

    return base


def create_document(client: httpx.Client, doc_type: str, index: int, created_by: str) -> dict:
    payload = {
        "type": doc_type,
        "amount": random_amount(doc_type),
        "metadata": random_metadata(doc_type, index),
        "created_by": created_by,
    }

    response = client.post("/documents", json=payload)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed financial documents via API")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT, help="Number of documents to create")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="API base URL")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="API key")
    args = parser.parse_args()

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": args.api_key,
    }

    print(f"Connecting to: {args.url}")
    print(f"Creating {args.count} documents...\n")

    created = 0
    failed = 0
    results = []

    with httpx.Client(base_url=args.url, headers=headers, timeout=10) as http:
        # Health check
        try:
            health = http.get("/../../health")
            health.raise_for_status()
            print("API is healthy, starting seed...\n")
        except Exception as e:
            print(f"Cannot connect to API: {e}")
            sys.exit(1)

        for i in range(1, args.count + 1):
            doc_type = fake.random_element(DOCUMENT_TYPES)
            user = fake.email()

            try:
                doc = create_document(http, doc_type, i, user)
                created += 1
                results.append(doc)
                print(f"[{i:>3}/{args.count}] Created #{doc['id']} | {doc['type']} | {doc['amount']}")
            except httpx.HTTPStatusError as e:
                failed += 1
                print(f"[{i:>3}/{args.count}] FAILED: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                failed += 1
                print(f"[{i:>3}/{args.count}] ERROR: {e}")

    print(f"\n{'=' * 50}")
    print(f"Done. Created: {created} | Failed: {failed}")

    if results:
        print(f"\nSample document IDs: {[d['id'] for d in results[:5]]}")
        print("\nFirst document created:")
        print(json.dumps(results[0], indent=2, default=str))


if __name__ == "__main__":
    main()
