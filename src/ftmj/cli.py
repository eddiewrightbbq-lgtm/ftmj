"""Command-line tools for preparing Jackson campaign-finance FtM streams."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from followthemoney import model


REQUIRED_COLUMNS = {
    "report_id",
    "transaction_id",
    "transaction_type",
    "transaction_date",
    "amount",
    "committee_name",
    "donor_name",
    "donor_type",
    "recipient_name",
    "recipient_type",
    "purpose",
    "source_url",
    "source_page",
    "review_status",
}
ALLOWED_TYPES = {"contribution", "expenditure"}
PARTY_SCHEMAS = {"person": "Person", "organization": "Organization"}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _key_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def _stable_id(kind: str, *parts: str) -> str:
    material = "\x1f".join((kind, *(_key_text(part) for part in parts)))
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return f"ftmj:{kind}:{digest}"


def _parse_amount(raw: str, line_number: int) -> str:
    cleaned = raw.strip().replace("$", "").replace(",", "")
    try:
        amount = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"line {line_number}: invalid amount {raw!r}") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"line {line_number}: amount must be a non-negative number")
    return format(amount.quantize(Decimal("0.01")), "f")


def _parse_date(raw: str, line_number: int) -> str:
    value = raw.strip()
    if not value:
        return ""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"line {line_number}: unsupported date {raw!r}") from exc


def _entity(schema_name: str, entity_id: str, properties: dict[str, str]) -> Any:
    entity = model.make_entity(schema_name)
    entity.id = entity_id
    for prop, value in properties.items():
        if value:
            entity.add(prop, value)
    return entity


def _party_id(
    *,
    role: str,
    name: str,
    kind: str,
    report_id: str,
    explicit_key: str,
) -> str:
    # Without a reviewer-supplied cross-report key, keep identity local to this filing.
    identity = explicit_key.strip() or f"report:{report_id}|name:{_key_text(name)}"
    return _stable_id(f"{role}:{kind}", identity)


def import_transactions(input_path: Path, output_path: Path) -> int:
    entities: dict[str, Any] = {}
    errors: list[str] = []

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - columns)
        if missing_columns:
            raise ValueError("missing CSV columns: " + ", ".join(missing_columns))

        for line_number, row in enumerate(reader, start=2):
            try:
                report_id = _clean(row.get("report_id"))
                transaction_id = _clean(row.get("transaction_id")) or f"row-{line_number}"
                tx_type = _clean(row.get("transaction_type")).lower()
                committee_name = _clean(row.get("committee_name"))
                donor_name = _clean(row.get("donor_name"))
                donor_type = _clean(row.get("donor_type")).lower()
                recipient_name = _clean(row.get("recipient_name"))
                recipient_type = _clean(row.get("recipient_type")).lower()
                review_status = _clean(row.get("review_status")).lower()

                if not report_id:
                    raise ValueError("report_id is required")
                if tx_type not in ALLOWED_TYPES:
                    raise ValueError("transaction_type must be contribution or expenditure")
                if not committee_name:
                    raise ValueError("committee_name is required")
                if review_status != "reviewed":
                    raise ValueError("review_status must be reviewed before import")
                if tx_type == "contribution" and (not donor_name or donor_type not in PARTY_SCHEMAS):
                    raise ValueError("contributions require donor_name and donor_type (person or organization)")
                if tx_type == "expenditure" and (not recipient_name or recipient_type not in PARTY_SCHEMAS):
                    raise ValueError("expenditures require recipient_name and recipient_type (person or organization)")

                amount = _parse_amount(_clean(row.get("amount")), line_number)
                tx_date = _parse_date(_clean(row.get("transaction_date")), line_number)
                if not tx_date:
                    raise ValueError("transaction_date is required")

                committee_key = _clean(row.get("committee_key"))
                committee_id = _stable_id(
                    "committee",
                    committee_key or f"report:{report_id}|name:{_key_text(committee_name)}",
                )
                entities.setdefault(
                    committee_id,
                    _entity("Organization", committee_id, {"name": committee_name}),
                )

                if tx_type == "contribution":
                    donor_id = _party_id(
                        role="donor",
                        name=donor_name,
                        kind=donor_type,
                        report_id=report_id,
                        explicit_key=_clean(row.get("donor_key")),
                    )
                    entities.setdefault(
                        donor_id,
                        _entity(PARTY_SCHEMAS[donor_type], donor_id, {"name": donor_name}),
                    )
                    payer_id, beneficiary_id = donor_id, committee_id
                else:
                    recipient_id = _party_id(
                        role="recipient",
                        name=recipient_name,
                        kind=recipient_type,
                        report_id=report_id,
                        explicit_key=_clean(row.get("recipient_key")),
                    )
                    entities.setdefault(
                        recipient_id,
                        _entity(PARTY_SCHEMAS[recipient_type], recipient_id, {"name": recipient_name}),
                    )
                    payer_id, beneficiary_id = committee_id, recipient_id

                payment_id = _stable_id("payment", report_id, transaction_id)
                payment = _entity(
                    "Payment",
                    payment_id,
                    {
                        "payer": payer_id,
                        "beneficiary": beneficiary_id,
                        "date": tx_date,
                        "amount": amount,
                        "purpose": _clean(row.get("purpose")) or tx_type.title(),
                        "recordId": transaction_id,
                        "sourceUrl": _clean(row.get("source_url")),
                        "publisher": "City of Jackson Municipal Clerk",
                        "description": _description(row, report_id, tx_type),
                    },
                )
                if not payment.has("payer") or not payment.has("beneficiary"):
                    raise ValueError("FollowTheMoney rejected a required payer or beneficiary")
                entities[payment_id] = payment
            except (InvalidOperation, ValueError) as exc:
                errors.append(str(exc))

    if errors:
        raise ValueError("\n".join(errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for entity_id in sorted(entities):
            handle.write(json.dumps(entities[entity_id].to_dict(), ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
    return len(entities)


def _description(row: dict[str, str], report_id: str, tx_type: str) -> str:
    details = [
        f"Report {report_id}",
        f"transaction type {tx_type}",
        f"source page {_clean(row.get('source_page')) or 'not recorded'}",
    ]
    source_category = _clean(row.get("source_category"))
    source_line = _clean(row.get("source_line"))
    if source_category:
        details.append(f"source category {source_category}")
    if source_line:
        details.append(f"source line {source_line}")
    return "; ".join(details)


def main() -> None:
    parser = argparse.ArgumentParser(prog="ftmj", description="FTMJ campaign-finance data tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    importer = subparsers.add_parser("import-transactions", help="convert reviewed transaction CSV to FtM NDJSON")
    importer.add_argument("input_csv", type=Path)
    importer.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        count = import_transactions(args.input_csv, args.output)
    except (OSError, ValueError) as exc:
        print(f"FTMJ import stopped: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"Wrote {count} FtM entities to {args.output}")


if __name__ == "__main__":
    main()

