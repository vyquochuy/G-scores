import tempfile
from pathlib import Path

from scripts.import_scores import parse_float, read_csv_chunks


def test_parse_float_valid() -> None:
    assert parse_float("8.5") == 8.5
    assert parse_float("10.0") == 10.0
    assert parse_float("0.0") == 0.0
    assert parse_float(" 7.25 ") == 7.25


def test_parse_float_empty_and_invalid() -> None:
    assert parse_float("") is None
    assert parse_float("   ") is None
    assert parse_float(None) is None
    assert parse_float("invalid_str") is None


def test_read_csv_chunks_preserves_leading_zeros_and_nulls() -> None:
    csv_content = (
        "sbd,toan,ngu_van,ngoai_ngu,vat_li,hoa_hoc,sinh_hoc,lich_su,dia_li,gdcd,ma_ngoai_ngu\n"
        "01000001,8.4,6.75,8.0,6.0,5.25,5.0,,,,N1\n"
        "01000002,8.6,8.5,7.2,,,,7.25,6.0,8.0,N1\n"
        "26020938,9.6,,,10.0,10.0,,,,,\n"
    )

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".csv") as f:
        f.write(csv_content)
        temp_path = Path(f.name)

    try:
        chunks = list(read_csv_chunks(temp_path, chunk_size=2))
        assert len(chunks) == 2
        assert len(chunks[0]) == 2
        assert len(chunks[1]) == 1

        first = chunks[0][0]
        assert first["sbd"] == "01000001"
        assert first["toan"] == 8.4
        assert first["ngu_van"] == 6.75
        assert first["lich_su"] is None
        assert first["dia_li"] is None
        assert first["gdcd"] is None
        assert first["ma_ngoai_ngu"] == "N1"

        third = chunks[1][0]
        assert third["sbd"] == "26020938"
        assert third["toan"] == 9.6
        assert third["ngu_van"] is None
        assert third["vat_li"] == 10.0
        assert third["hoa_hoc"] == 10.0
        assert third["ma_ngoai_ngu"] is None
    finally:
        if temp_path.exists():
            temp_path.unlink()
