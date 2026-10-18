import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_list_subjects(client: AsyncClient) -> None:
    response = await client.get("/api/v1/subjects")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    subjects = body["data"]
    assert len(subjects) == 9

    codes = [s["code"] for s in subjects]
    assert "toan" in codes
    assert "ngu_van" in codes
    assert "ngoai_ngu" in codes
    assert "vat_li" in codes
    assert "hoa_hoc" in codes


@pytest.mark.asyncio
async def test_get_student_scores_success(client: AsyncClient) -> None:
    response = await client.get("/api/v1/scores/01000001")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    data = body["data"]
    assert data["registrationNumber"] == "01000001"
    assert len(data["scores"]) > 0

    toan_score = next((s for s in data["scores"] if s["subjectCode"] == "toan"), None)
    assert toan_score is not None
    assert toan_score["subjectName"] == "Toán"
    assert toan_score["score"] == 8.4


@pytest.mark.asyncio
async def test_get_student_scores_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/scores/99999999")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "NOT_FOUND"
    assert "Không tìm thấy" in body["error"]["message"]


@pytest.mark.asyncio
async def test_get_student_scores_invalid_format(client: AsyncClient) -> None:
    # SBD chua chu cai
    res1 = await client.get("/api/v1/scores/0100000A")
    assert res1.status_code == 400
    body1 = res1.json()
    assert body1["error"]["code"] == "VALIDATION_ERROR"
    assert "8 chữ số" in body1["error"]["message"]

    # SBD khong du 8 chu so
    res2 = await client.get("/api/v1/scores/12345")
    assert res2.status_code == 400
    body2 = res2.json()
    assert body2["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_get_score_distribution_success(client: AsyncClient) -> None:
    response = await client.get("/api/v1/reports/score-distribution?subjectCode=toan")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    data = body["data"]
    assert data["subjectCode"] == "toan"
    assert data["subjectName"] == "Toán"
    assert data["validScoreCount"] == 1045613
    assert len(data["bands"]) == 4

    keys = [b["key"] for b in data["bands"]]
    assert keys == ["GE_8", "GE_6_LT_8", "GE_4_LT_6", "LT_4"]

    band_ge_8 = next(b for b in data["bands"] if b["key"] == "GE_8")
    assert band_ge_8["count"] == 198392


@pytest.mark.asyncio
async def test_get_score_distribution_invalid_subject(client: AsyncClient) -> None:
    response = await client.get("/api/v1/reports/score-distribution?subjectCode=invalid_sub")
    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "không hợp lệ" in body["error"]["message"]


@pytest.mark.asyncio
async def test_get_top_a_students(client: AsyncClient) -> None:
    response = await client.get("/api/v1/students/top-a")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    students = body["data"]
    assert len(students) == 10

    # Thu khoa
    top1 = students[0]
    assert top1["rank"] == 1
    assert top1["registrationNumber"] == "26020938"
    assert top1["math"] == 9.6
    assert top1["physics"] == 10.0
    assert top1["chemistry"] == 10.0
    assert top1["total"] == 29.60

    # Á khoa 1
    top2 = students[1]
    assert top2["rank"] == 2
    assert top2["registrationNumber"] == "26009943"
    assert top2["math"] == 9.8
    assert top2["physics"] == 9.75
    assert top2["chemistry"] == 10.0
    assert top2["total"] == 29.55

    # Kiem tra thu hang lien tuc tu 1 den 10
    ranks = [s["rank"] for s in students]
    assert ranks == list(range(1, 11))

    # Kiem tra tong diem giam dan
    totals = [s["total"] for s in students]
    for i in range(len(totals) - 1):
        assert totals[i] >= totals[i + 1]
