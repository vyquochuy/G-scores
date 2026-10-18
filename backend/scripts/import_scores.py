import argparse
import asyncio
import csv
import sys
import time
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.student import Student

DEFAULT_BATCH_SIZE = 4000
TOTAL_DATASET_ROWS = 1061605
SCORE_COLUMNS = (
    "toan",
    "ngu_van",
    "ngoai_ngu",
    "vat_li",
    "hoa_hoc",
    "sinh_hoc",
    "lich_su",
    "dia_li",
    "gdcd",
)


def parse_float(val: str | None) -> float | None:
    """Chuyen doi chuoi diem sang float, tra ve None neu chuoi rong."""
    if val is None:
        return None
    cleaned = val.strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def read_csv_chunks(
    file_path: Path,
    chunk_size: int = DEFAULT_BATCH_SIZE,
) -> Generator[list[dict[str, Any]], None, None]:
    """Doc luong file CSV va tao ra tung lo ban ghi hop le."""
    now_naive = datetime.now(UTC).replace(tzinfo=None)
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        chunk: list[dict[str, Any]] = []

        for row in reader:
            sbd = row.get("sbd", "").strip()
            if not sbd:
                continue

            record: dict[str, Any] = {
                "sbd": sbd,
                "ma_ngoai_ngu": row.get("ma_ngoai_ngu", "").strip() or None,
                "created_at": now_naive,
            }
            for col in SCORE_COLUMNS:
                record[col] = parse_float(row.get(col))

            chunk.append(record)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

        if chunk:
            yield chunk


async def import_dataset(
    file_path: Path,
    batch_size: int = DEFAULT_BATCH_SIZE,
    reset: bool = False,
) -> int:
    """Thuc thi nap toan bo du lieu CSV vao co so du lieu PostgreSQL."""
    if not file_path.exists():
        print(f"Loi: Tep du lieu khong ton tai tai duong dan: {file_path}", flush=True)
        sys.exit(1)

    print(f"Bat dau quy trinh import du lieu tu: {file_path}", flush=True)
    print(f"Kich thuoc moi batch: {batch_size:,} ban ghi", flush=True)
    start_time = time.time()
    total_imported = 0

    async with async_session_factory() as session:
        session: AsyncSession

        existing_count = await session.scalar(select(func.count(Student.id)))
        if existing_count and existing_count > 0:
            if not reset:
                print(
                    f"Du lieu da ton tai trong CSDL ({existing_count:,} ban ghi). "
                    "Bo qua import de dam bao tinh idempotent. "
                    "Su dung co --reset neu muon xoa du lieu cu va nap lai tu dau.",
                    flush=True,
                )
                return existing_count
            print(f"Co --reset duoc kich hoat. Tien hanh xoa {existing_count:,} ban ghi cu...", flush=True)
            await session.execute(text("TRUNCATE TABLE students RESTART IDENTITY"))
            await session.commit()
            print("Da xoa sach du lieu cu trong bang students.", flush=True)

        table = Student.__table__
        for chunk_idx, chunk in enumerate(read_csv_chunks(file_path, chunk_size=batch_size), start=1):
            await session.execute(insert(table), chunk)
            await session.commit()
            total_imported += len(chunk)

            elapsed = time.time() - start_time
            speed = total_imported / elapsed if elapsed > 0 else 0
            percent = (total_imported / TOTAL_DATASET_ROWS) * 100
            print(
                f"-> Tien do: {total_imported:,} / {TOTAL_DATASET_ROWS:,} dong "
                f"({percent:.1f}%) - Toc do: {speed:,.0f} dong/s (Batch #{chunk_idx})",
                flush=True,
            )

        final_count = await session.scalar(select(func.count(Student.id)))
        total_time = time.time() - start_time

    print("--------------------------------------------------", flush=True)
    print(f"Hoan tat import! Tong so ban ghi trong CSDL: {final_count:,}", flush=True)
    print(f"Tong thoi gian thuc thi: {total_time:.2f} giay.", flush=True)
    return final_count or 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline nap du lieu diem thi THPT 2024")
    parser.add_argument(
        "--csv-path",
        type=str,
        default=str(
            Path(__file__).resolve().parent.parent.parent
            / "webdev-intern-assignment-3"
            / "dataset"
            / "diem_thi_thpt_2024.csv"
        ),
        help="Duong dan toi tep diem_thi_thpt_2024.csv",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Kich thuoc batch cho moi lan insert",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Xoa toan bo du lieu cu truoc khi nap lai",
    )

    args = parser.parse_args()
    csv_file = Path(args.csv_path)

    asyncio.run(import_dataset(csv_file, batch_size=args.batch_size, reset=args.reset))


if __name__ == "__main__":
    main()
