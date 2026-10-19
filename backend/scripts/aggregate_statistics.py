"""Script tong hop so lieu thong ke ban dau vao bang system_metrics va score_statistics.

Ho tro chay idempotent (nhieu lan an toan) va co co --verify de doi soat tu dong 100% voi bang goc.
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Them thu muc backend vao sys.path de chay doc lap
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

from sqlalchemy import func, select

from app.core.database import async_session_factory
from app.domain.models.registry import subject_registry
from app.models.student import Student
from app.repositories.score_repo import ScoreRepository
from app.repositories.statistic_repo import StatisticRepository


async def aggregate_all(verify: bool = False) -> bool:
    start_time = time.time()
    print("=== BAT DAU TONG HOP SO LIEU THONG KE (PHASE 6) ===")

    async with async_session_factory() as session:
        # 1. Tinh toan va luu tong so thi sinh
        total_stmt = select(func.count()).select_from(Student)
        total_result = await session.execute(total_stmt)
        total_students = int(total_result.scalar_one_or_none() or 0)
        print(f"[1/2] Tong so thi sinh tinh tu bang students: {total_students:,}")

        await StatisticRepository.set_system_metric(
            session=session,
            metric_key="total_students",
            metric_value=total_students,
        )
        await session.commit()
        print("  -> Da cap nhat metric 'total_students' vao bang system_metrics.")

        # 2. Tinh toan va luu pho diem cho tung mon hoc
        print("[2/2] Dang tong hop pho diem cho 9 mon hoc...")
        all_subjects = subject_registry.list_all()
        for idx, sub in enumerate(all_subjects, 1):
            t_sub = time.time()
            counts = await ScoreRepository.get_distribution_by_column(session, sub.csv_column)
            await StatisticRepository.upsert_score_statistic(
                session=session,
                subject_code=sub.code,
                ge_8=counts["GE_8"],
                ge_6_lt_8=counts["GE_6_LT_8"],
                ge_4_lt_6=counts["GE_4_LT_6"],
                lt_4=counts["LT_4"],
                valid_count=counts["valid_count"],
            )
            await session.commit()
            print(
                f"  [{idx}/9] {sub.name} ({sub.code}): "
                f"valid={counts['valid_count']:,}, >=8={counts['GE_8']:,}, "
                f"6-8={counts['GE_6_LT_8']:,}, 4-6={counts['GE_4_LT_6']:,}, "
                f"<4={counts['LT_4']:,} ({time.time() - t_sub:.2f}s)"
            )

    elapsed = time.time() - start_time
    print(f"=== TONG HOP DU LIEU HOAN TAT TRONG {elapsed:.2f}s ===")

    if verify:
        return await verify_statistics()
    return True


async def verify_statistics() -> bool:
    print("\n=== BAT DAU DOI SOAT DU LIEU 100% VOI BANG GOC (--verify) ===")
    all_matched = True

    async with async_session_factory() as session:
        # 1. Kiem tra total_students
        db_total_stmt = select(func.count()).select_from(Student)
        db_total = int((await session.execute(db_total_stmt)).scalar_one_or_none() or 0)
        cached_total = await StatisticRepository.get_system_metric(session, "total_students")

        matched = (db_total == cached_total)
        if not matched:
            all_matched = False
        print(f"[*] total_students: Goc={db_total:,} | Bang thong ke={cached_total} | Khop: {matched}")

        # 2. Kiem tra 9 mon hoc
        for sub in subject_registry.list_all():
            raw_counts = await ScoreRepository.get_distribution_by_column(session, sub.csv_column)
            stat_record = await StatisticRepository.get_score_statistic(session, sub.code)

            if not stat_record:
                print(f"[x] Khong tim thay ban ghi cho mon {sub.code} trong score_statistics!")
                all_matched = False
                continue

            sub_matched = (
                stat_record.valid_count == raw_counts["valid_count"]
                and stat_record.ge_8 == raw_counts["GE_8"]
                and stat_record.ge_6_lt_8 == raw_counts["GE_6_LT_8"]
                and stat_record.ge_4_lt_6 == raw_counts["GE_4_LT_6"]
                and stat_record.lt_4 == raw_counts["LT_4"]
            )
            if not sub_matched:
                all_matched = False
                print(f"[!] Sai lech tai mon {sub.name} ({sub.code}):")
                print(f"    Goc:      {raw_counts}")
                print(
                    f"    Thong ke: valid={stat_record.valid_count}, ge_8={stat_record.ge_8}, "
                    f"ge_6_lt_8={stat_record.ge_6_lt_8}, ge_4_lt_6={stat_record.ge_4_lt_6}, "
                    f"lt_4={stat_record.lt_4}"
                )
            else:
                print(f"[v] Mon {sub.name} ({sub.code}): Khop 100% (valid={stat_record.valid_count:,})")

    if all_matched:
        print("\n>>> KET QUA DOI SOAT: CHINH XAC 100% SO VOI BANG GOC. GATE 6 CRITERION 2 PASSED!")
    else:
        print("\n>>> KET QUA DOI SOAT: PHAT HIEN SAI LECH!")
    return all_matched


def main() -> None:
    parser = argparse.ArgumentParser(description="Tong hop du lieu thong ke he thong G-Scores.")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Thuc hien doi soat tu dong 100% voi bang goc sau khi tong hop.",
    )
    args = parser.parse_args()

    success = asyncio.run(aggregate_all(verify=args.verify))
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
