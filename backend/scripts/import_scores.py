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

MAX_PG_PARAMS = 65535
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


def inspect_csv_file(file_path: Path) -> tuple[int, int]:
    """Doc tep CSV de tu dong xac dinh:

    1. total_rows: Tong so dong du lieu thuc te trong tep CSV (khong tinh header va dong trong).
    2. batch_size: Kich thuoc batch toi uu tinh toan dong dua tren so luong cot
       va gioi han tham so (65,535) cua giao thuc PostgreSQL.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Tep CSV khong ton tai: {file_path}")

    # 1. Doc header de xac dinh so cot tu CSV
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return 0, 1000
        num_csv_cols = len(header)

    # 2. Dem tong so dong du lieu thuc te bang cach doc byte stream toc do cao
    with open(file_path, mode="rb") as fb:
        fb.readline()  # Bo qua dong header
        total_rows = sum(1 for line in fb if line.strip())

    # 3. Tinh toan batch size toi uu dong
    # Moi ban ghi chen vao gom cac cot tu CSV cong them cot created_at do backend sinh ra
    cols_per_record = num_csv_cols + 1
    # Gioi han tham so cua giao thuc PostgreSQL la 65,535
    max_safe_batch = MAX_PG_PARAMS // cols_per_record
    # Ap dung he so an toan 0.75 va lam tron xuong boi so cua 1,000 de luong mang toi uu nhat
    optimal_batch = (int(max_safe_batch * 0.75) // 1000) * 1000
    if optimal_batch < 100:
        optimal_batch = max(1, int(max_safe_batch * 0.75))

    batch_size = min(optimal_batch, total_rows) if total_rows > 0 else optimal_batch
    return total_rows, batch_size



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
    chunk_size: int | None = None,
) -> Generator[list[dict[str, Any]], None, None]:
    """Doc luong file CSV va tao ra tung lo ban ghi hop le."""
    if chunk_size is None or chunk_size <= 0:
        _, chunk_size = inspect_csv_file(file_path)

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
    batch_size: int | None = None,
    reset: bool = False,
) -> int:
    """Thuc thi nap toan bo du lieu CSV vao co so du lieu PostgreSQL."""
    if not file_path.exists():
        print(f"Loi: Tep du lieu khong ton tai tai duong dan: {file_path}", flush=True)
        sys.exit(1)

    # Tu dong xac dinh tong so dong va batch size toi uu dong tu tep CSV
    total_dataset_rows, optimal_batch = inspect_csv_file(file_path)
    effective_batch_size = (
        batch_size if batch_size is not None and batch_size > 0 else optimal_batch
    )

    print(f"Bat dau quy trinh import du lieu tu: {file_path}", flush=True)
    print(f"Tong so dong du lieu trong tep CSV: {total_dataset_rows:,} dong", flush=True)
    print(f"Kich thuoc moi batch duoc xac dinh: {effective_batch_size:,} ban ghi", flush=True)
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
        for chunk_idx, chunk in enumerate(
            read_csv_chunks(file_path, chunk_size=effective_batch_size), start=1
        ):
            await session.execute(insert(table), chunk)
            await session.commit()
            total_imported += len(chunk)

            elapsed = time.time() - start_time
            speed = total_imported / elapsed if elapsed > 0 else 0
            percent = (
                (total_imported / total_dataset_rows) * 100
                if total_dataset_rows > 0
                else 100.0
            )
            print(
                f"-> Tien do: {total_imported:,} / {total_dataset_rows:,} dong "
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
        default=None,
        help="Kich thuoc batch cho moi lan insert (mac dinh tu dong tinh toan theo tep CSV)",
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

