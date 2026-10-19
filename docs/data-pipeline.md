# Pipeline Nạp và Đối Soát Dữ Liệu

Quy trình nhập dữ liệu điểm thi THPT 2024 vào PostgreSQL, tổng hợp phổ điểm và kiểm tra tính toàn vẹn dữ liệu.

## 1. Dữ liệu nguồn

- **Tập tin:** `webdev-intern-assignment-3/dataset/diem_thi_thpt_2024.csv`
- **Quy mô:** 1.061.605 thí sinh, 11 cột dữ liệu.
- **Dung lượng:** Khoảng 40,17 MB.

Các quy tắc chuẩn hóa:

- **Số báo danh:** Lưu dưới dạng chuỗi 8 chữ số để bảo toàn số `0` ở đầu.
- **Điểm thi:** Chuyển chuỗi rỗng thành `NULL`; giữ nguyên điểm `0.0` hợp lệ.
- **Mã ngoại ngữ:** Giữ mã nguồn từ `N1` đến `N7` hoặc `NULL`.

## 2. Nạp dữ liệu

Script: `backend/scripts/import_scores.py`

Pipeline sử dụng `csv.DictReader` kết hợp generator để đọc dữ liệu theo luồng, chuẩn hóa từng bản ghi và chia thành các batch trước khi ghi vào PostgreSQL.

- **Batch insert:** Mặc định 4.000 bản ghi mỗi batch.
- **SQLAlchemy Core:** Sử dụng thao tác insert hàng loạt, tránh chi phí quản lý từng ORM entity.
- **Giới hạn tham số:** Với 12 tham số mỗi bản ghi, một batch 4.000 dòng tương ứng 48.000 tham số, thấp hơn giới hạn 65.535 tham số của giao thức PostgreSQL liên quan. Cần bảo đảm số tham số thực tế của câu lệnh phù hợp với phép tính này.
- **Chạy lại:** Script kiểm tra bảng đích trước khi import để hạn chế chèn trùng dữ liệu. Tùy chọn `--reset` xóa dữ liệu hiện có trước khi nạp lại.

```bash
python scripts/import_scores.py
python scripts/import_scores.py --reset
```

**Lưu ý:** `--reset` là thao tác phá hủy dữ liệu hiện có. Chỉ sử dụng khi chủ động muốn nạp lại từ đầu. Cần kiểm tra trạng thái import nếu tiến trình trước đó bị gián đoạn.

## 3. Tổng hợp thống kê

Script: `backend/scripts/aggregate_statistics.py`

Sau khi import hoàn tất, script cập nhật hai bảng thống kê:

- `system_metrics`: Lưu các chỉ số toàn cục như tổng số thí sinh.
- `score_statistics`: Lưu số lượng bài thi hợp lệ theo bốn khoảng điểm cho từng môn.

Các khoảng điểm được xác định như sau:

| Khoảng điểm     | Điều kiện                  |
| --------------- | -------------------------- |
| Từ 8 điểm       | `score >= 8`               |
| Từ 6 đến dưới 8 | `score >= 6 AND score < 8` |
| Từ 4 đến dưới 6 | `score >= 4 AND score < 6` |
| Dưới 4 điểm     | `score < 4`                |

Script sử dụng PostgreSQL `ON CONFLICT DO UPDATE` để cập nhật các bản ghi thống kê hiện có, cho phép chạy lại quy trình tổng hợp.

## 4. Đối soát dữ liệu

Chạy lệnh sau để kiểm tra tính nhất quán của các bảng thống kê:

```bash
python scripts/aggregate_statistics.py --verify
```

Quy trình đối soát kiểm tra:

- Tổng số thí sinh trong `system_metrics` so với bảng `students`.
- Số lượng bài thi hợp lệ và số thí sinh trong từng khoảng điểm của mỗi môn.
- Kết quả tổng hợp lưu sẵn so với kết quả truy vấn trực tiếp trên dữ liệu gốc.

Theo số liệu được ghi nhận của dự án, tổng số thí sinh là **1.061.605**. Mỗi môn phải thỏa mãn điều kiện tổng số bài thi hợp lệ bằng tổng số thí sinh thuộc bốn khoảng điểm.

Chỉ xác nhận đối soát thành công khi script `--verify` thực sự chạy và không phát hiện sai lệch.

## 5. Quy trình thực thi

Thực hiện theo thứ tự:

1. Chuẩn bị tập tin CSV và cấu hình database.
2. Chạy migration tạo bảng và index.
3. Import dữ liệu thí sinh.
4. Tổng hợp các bảng thống kê.
5. Chạy `--verify` để kiểm tra kết quả.

```bash
alembic upgrade head
python scripts/import_scores.py
python scripts/aggregate_statistics.py --verify
```

Chạy các lệnh trong thư mục `backend/` hoặc sử dụng tiền tố `docker compose exec backend` khi thực thi bên trong container.
