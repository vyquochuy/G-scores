# Pipeline Nạp và Đối Soát Dữ Liệu (Data Ingestion & Auditing)

Tài liệu này mô tả chi tiết pipeline xử lý dữ liệu từ tập tin CSV gốc `diem_thi_thpt_2024.csv` vào cơ sở dữ liệu PostgreSQL, các quy tắc chuẩn hóa dữ liệu, cơ chế batch processing và quy trình đối soát dữ liệu tự động.

---

## 1. Đặc Tính Tập Dữ Liệu Gốc

- **Đường dẫn tập tin:** `src/webdev-intern-assignment-3/dataset/diem_thi_thpt_2024.csv`
- **Dung lượng:** ~40.17 MB (42,125,478 bytes).
- **Quy mô:** 1,061,605 dòng dữ liệu + 1 dòng tiêu đề.
- **Cấu trúc 11 cột:**
  ```text
  sbd,toan,ngu_van,ngoai_ngu,vat_li,hoa_hoc,sinh_hoc,lich_su,dia_li,gdcd,ma_ngoai_ngu
  ```

### Các quy tắc dữ liệu cần bảo toàn:
1. **Số báo danh (SBD):**
   - Đúng 8 ký tự số.
   - Các tỉnh có mã từ `01` đến `09` (ví dụ Hà Nội `01000001`, TP.HCM `02000001`) bắt đầu bằng số `0`.
   - **Bắt buộc:** Lưu kiểu chuỗi `String(8)`, không được ép kiểu `Integer` để tránh mất số `0` ở đầu.
2. **Điểm số các môn:**
   - Thang điểm từ `0.0` đến `10.0`.
   - Thí sinh không thi môn nào thì cột môn đó mang giá trị chuỗi rỗng `""`.
   - **Bắt buộc:** Chuỗi rỗng phải được chuyển thành SQL `NULL` (`None` trong Python), tuyệt đối không gán mặc định thành `0.0` vì `0.0` là điểm thi thật (điểm liệt).
3. **Mã ngoại ngữ:**
   - Gồm các mã: `N1`, `N2`, `N3`, `N4`, `N5`, `N6`, `N7` hoặc rỗng (`NULL`).

---

## 2. Pipeline Nạp Dữ Liệu (`scripts/import_scores.py`)

Quy trình nạp dữ liệu được thiết kế streaming và phân đoạn batch nhằm kiểm soát dung lượng bộ nhớ RAM và tối ưu tốc độ chèn dữ liệu.

### 2.1. Đọc dữ liệu theo luồng (Streaming Generator)

Thay vì đọc toàn bộ 1 triệu dòng vào bộ nhớ (dễ gây Out-Of-Memory khi chạy trên môi trường container giới hạn RAM), script sử dụng generator đọc từng dòng thông qua thư viện chuẩn `csv.DictReader`:

```python
def read_csv_chunks(
    file_path: Path,
    batch_size: int = BATCH_SIZE,
) -> Generator[list[dict[str, Any]], None, None]:
    batch: list[dict[str, Any]] = []
    with file_path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append(clean_row(row))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
```

### 2.2. Kích thước Batch và Giới hạn Tham số PostgreSQL

- **Kích thước batch:** `BATCH_SIZE = 4,000` dòng/lần chèn.
- **Lý do chọn 4,000 dòng:**
  - Bảng `students` có 11 cột tham số đầu vào.
  - Số lượng tham số cho mỗi câu lệnh SQL chèn dữ liệu: `4,000 * 11 = 44,000` tham số.
  - Giao thức PostgreSQL giới hạn tối đa `65,535` tham số cho một câu lệnh Prepared Statement. Do đó, kích thước 4,000 đảm bảo an toàn tuyệt đối, tránh lỗi `too many parameters for query`.

### 2.3. Chèn Dữ Liệu bằng SQLAlchemy Core Table Insert

Thay vì sử dụng ORM Session entity-tracking (`session.add_all([Student(...)])` tiêu tốn tài nguyên quản lý vòng đời đối tượng cho 1 triệu đối tượng), script sử dụng Core Table Insert:

```python
stmt = insert(Student.__table__).values(chunk)
await session.execute(stmt)
await session.commit()
```
Phương thức này đưa trực tiếp mảng dữ liệu đã chuẩn hóa xuống database engine với chi phí tối thiểu.

### 2.4. Tính Idempotent (An Toàn Khi Chạy Lại)

- **Mặc định:** Script kiểm tra `SELECT count(*) FROM students`. Nếu đã có dữ liệu (>= 1,061,605 dòng), script thông báo và dừng lại an toàn mà không nhân đôi dữ liệu.
- **Tùy chọn `--reset`:** Cho phép làm sạch bảng bằng `TRUNCATE TABLE students RESTART IDENTITY CASCADE` trước khi nạp lại:
  ```bash
  python scripts/import_scores.py --reset
  ```

---

## 3. Pipeline Tổng Hợp Số Liệu Thống Kê (`scripts/aggregate_statistics.py`)

Sau khi dữ liệu gốc đã được nạp vào bảng `students`, script `aggregate_statistics.py` được thực thi để tính toán trước các bảng thống kê.

### 3.1. Các bước thực hiện:
1. **Chỉ số toàn cục:** Đếm tổng số bản ghi từ bảng `students` và lưu vào bảng `system_metrics` với `metric_key = 'total_students'`.
2. **Phổ điểm 9 môn:** Duyệt qua danh mục 9 môn thi trong `SubjectRegistry`. Với mỗi môn, tính toán số lượng thí sinh theo 4 khoảng điểm (`>= 8.0`, `6.0 - 7.9`, `4.0 - 5.9`, `< 4.0`) và số lượng bài thi hợp lệ (`valid_count`).
3. **Upsert Idempotent:** Sử dụng câu lệnh PostgreSQL `pg_insert().on_conflict_do_update()`:
   ```python
   stmt = (
       pg_insert(ScoreStatistic)
       .values(...)
       .on_conflict_do_update(
           index_elements=[ScoreStatistic.subject_code],
           set_={...}
       )
   )
   ```
   Đảm bảo script có thể chạy lại bất kỳ lúc nào mà không gặp lỗi trùng lặp khóa chính.

### 3.2. Cơ chế Đối soát Tự Động (`--verify`)

Khi truyền cờ `--verify`, script sẽ thực hiện truy vấn trực tiếp trên bảng `students` và so sánh từng chỉ số với bảng thống kê:

```bash
python scripts/aggregate_statistics.py --verify
```

Kết quả đối soát trên tập dữ liệu THPT 2024:
- `total_students`: Khớp chính xác `1,061,605` bản ghi.
- Môn Toán (`toan`): Hợp lệ `1,045,613` | `>=8.0`: `198,392` | `6.0-7.9`: `505,836` | `4.0-5.9`: `258,654` | `<4.0`: `82,731`.
- Môn Ngữ văn (`ngu_van`): Hợp lệ `1,050,101` bài thi.
- Môn Ngoại ngữ (`ngoai_ngu`): Hợp lệ `912,705` bài thi.
- Môn Vật lí (`vat_li`): Hợp lệ `345,615` bài thi.
- Môn Hóa học (`hoa_hoc`): Hợp lệ `346,518` bài thi.
- Môn Sinh học (`sinh_hoc`): Hợp lệ `342,378` bài thi.
- Môn Lịch sử (`lich_su`): Hợp lệ `706,214` bài thi.
- Môn Địa lí (`dia_li`): Hợp lệ `704,682` bài thi.
- Môn GDCD (`gdcd`): Hợp lệ `583,609` bài thi.
