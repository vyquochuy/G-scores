# G-Scores: Hệ Thống Tra Cứu và Phân Tích Phổ Điểm Thi THPT 2024

- **Trực tuyến:** [https://g-scores-amber.vercel.app](https://g-scores-amber.vercel.app)
- **API Health:** [https://g-scores-amber.vercel.app/api/v1/health](https://g-scores-amber.vercel.app/api/v1/health)

---

## 1. Chức Năng Chính

### 1.1. Tra cứu điểm thi cá nhân

Tra cứu kết quả thi theo số báo danh 8 chữ số. Hệ thống hiển thị điểm từng môn, phân loại mức điểm học lực và tự động tính tổng điểm tổ hợp Khối A (nếu thí sinh dự thi đủ 3 môn).

![Giao diện tra cứu điểm thi](.github/images/02-tra-cuu.png)

### 1.2. Thống kê phân bố phổ điểm

Trực quan hóa số lượng và tỷ lệ thí sinh theo 4 khoảng điểm chuẩn (`>= 8.0`, `6.0 - 7.9`, `4.0 - 5.9`, `< 4.0`). Hỗ trợ chuyển đổi linh hoạt giữa từng môn thi hoặc xem tổng hợp tất cả các môn.

![Biểu đồ thống kê phổ điểm](.github/images/03-thong-ke.png)

### 1.3. Bảng xếp hạng Top 10 Khối A

Danh sách 10 thí sinh có tổng điểm 3 môn Toán, Vật lí, Hóa học cao nhất. Khi có các trường hợp đồng điểm, hệ thống áp dụng tiêu chí phụ sắp xếp theo số báo danh tăng dần (`sbd ASC`).

![Bảng xếp hạng Top 10 Khối A](.github/images/04-top-10.png)

### 1.4. Tổng quan hệ thống

Hiển thị các chỉ số vĩ mô của kỳ thi (1,061,605 thí sinh, 9 môn thi tốt nghiệp, điểm thủ khoa Khối A 29.60) và giám sát trạng thái kết nối backend/database theo thời gian thực.

![Màn hình tổng quan hệ thống](.github/images/01-tong-quan.png)

---

## 2. Công Nghệ Sử Dụng

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Asyncio), asyncpg, Alembic.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS.
- **Database & Cache:** PostgreSQL 16 (Supabase / Local), Redis 7 (Upstash / Local).
- **Testing & Tooling:** Pytest, pytest-asyncio, HTTPX, Ruff.
- **Container & Deployment:** Docker, Docker Compose, Vercel Serverless.

---

## 3. Kiến Trúc và Quyết Định Kỹ Thuật

1. **Thiết kế bảng phẳng (Wide Table):**
   Lưu trữ 9 môn thi trên cùng một hàng trong bảng `students`. Với tập dữ liệu tĩnh có số cột cố định, cấu trúc này giữ bảng ở quy mô 1,061,605 bản ghi (thay vì hơn 7.5 triệu dòng nếu chuẩn hóa dọc), giúp thao tác bulk insert nhanh hơn và loại bỏ các phép `JOIN` khi tính tổng điểm tổ hợp 3 môn.
2. **Tách biệt nghiệp vụ Hướng đối tượng (OOP Domain Model):**
   Đóng gói môn học (`Subject`), phổ điểm (`ScoreBand`), tổ hợp môn (`ExamGroup`, `GroupA`) và registry (`SubjectRegistry`) ở tầng domain độc lập. Nghiệp vụ tính điểm và kiểm tra dữ liệu được tách rời khỏi SQLAlchemy ORM và Pydantic schemas, cho phép viết unit test độc lập không cần database.
3. **Bảng thống kê tính toán trước (Pre-aggregated Tables):**
   Dữ liệu điểm thi THPT là dữ liệu tĩnh. Việc thực hiện `COUNT(*)` toàn bảng hoặc gom nhóm 4 khoảng điểm trên 1 triệu dòng ở mỗi lượt truy cập dashboard gây tốn CPU. Hệ thống sử dụng 2 bảng thống kê: `system_metrics` (chỉ số toàn cục) và `score_statistics` (phổ điểm 9 môn). Repository ưu tiên đọc từ bảng thống kê (1 dòng indexed read), chỉ fallback quét bảng gốc nếu dữ liệu chưa sẵn sàng.
4. **Partial Functional Index cho Top 10 Khối A:**
   Thiết lập index `idx_students_group_a_sum` trên biểu thức `((toan + vat_li + hoa_hoc) DESC, sbd ASC)` với điều kiện lọc `WHERE toan IS NOT NULL AND vat_li IS NOT NULL AND hoa_hoc IS NOT NULL`. Qua kiểm tra `EXPLAIN (ANALYZE, BUFFERS)`, database sử dụng trực tiếp B-Tree Index Scan trên tập thí sinh đủ 3 môn khối A và loại bỏ hoàn toàn nút `Sort` khỏi query plan.
5. **Redis Cache-Aside và Graceful Degradation:**
   Áp dụng cache bất đồng bộ với TTL 24 giờ cho các endpoint tĩnh (`/total`, `/reports/score-distribution`, `/top-a`) kèm key versioning (`v1`). Đặt timeout kết nối 500ms; khi Redis offline hoặc timeout, module tự động bắt lỗi và fallback truy vấn PostgreSQL, đảm bảo tiến trình API không bị treo và không trả lỗi HTTP 500.

> Xem giải trình chi tiết về kiến trúc, trade-offs và cấu trúc module tại [docs/architecture.md](docs/architecture.md).

---

## 4. Hướng Dẫn Khởi Chạy

### 4.1 Docker Compose

Khởi động đồng bộ 4 dịch vụ: PostgreSQL 16, Redis 7, Backend FastAPI và Frontend Nginx bằng Docker Compose:

1. **Chuẩn bị cấu hình môi trường:**

   ```bash
   cp .env.example .env
   ```

2. **Khởi dựng các container:**

   ```bash
   docker compose up -d --build
   ```

3. **Chạy migration và nạp dữ liệu vào database:**

   ```bash
   # Chạy migration tạo bảng và indexes
   docker compose exec backend alembic upgrade head

   # Nạp dữ liệu từ file CSV vào database
   docker compose exec backend python scripts/import_scores.py

   # Tạo dữ liệu bảng thống kê và kiểm tra tính đúng đắn
   docker compose exec backend python scripts/aggregate_statistics.py --verify
   ```

4. **Truy cập dịch vụ:**
   - **Frontend:** `http://localhost:5173` hoặc `http://localhost:3000`
   - **Backend API:** `http://localhost:8000`
   - **Swagger Docs:** `http://localhost:8000/docs`

### 4.2. Hướng Dẫn Chạy Môi Trường Cục Bộ nếu không dùng docker (Local Development)

### 4.2.1. Chuẩn bị Cơ sở dữ liệu và Redis

1. Cài đặt PostgreSQL 16 và tạo cơ sở dữ liệu:
   ```sql
   CREATE DATABASE gscores;
   ```
2. Khởi động máy chủ Redis cục bộ trên cổng mặc định `6379` (nếu không có Redis, hệ thống sẽ tự động fallback truy vấn database trực tiếp nhờ cơ chế graceful degradation).

### 4.2.2. Khởi chạy Backend

1. Di chuyển vào thư mục backend và tạo môi trường ảo Python 3.12:

   ```bash
   cd backend
   python -m venv venv

   # Kích hoạt trên Windows PowerShell:
   .\venv\Scripts\Activate.ps1

   # Kích hoạt trên Linux / macOS:
   source venv/bin/activate
   ```

2. Cài đặt các gói phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
3. Tạo file `backend/.env` từ file mẫu `backend/.env.example`:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@localhost:5432/gscores
   REDIS_URL=redis://localhost:6379/0
   REDIS_TIMEOUT_SECONDS=0.5
   ```
4. Chạy migration tạo cấu trúc bảng:
   ```bash
   alembic upgrade head
   ```
5. Nạp dữ liệu từ tập tin CSV gốc:
   ```bash
   python scripts/import_scores.py
   ```
6. Tổng hợp các chỉ số thống kê và đối soát:
   ```bash
   python scripts/aggregate_statistics.py --verify
   ```
7. Khởi động server API:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

### 4.2.3. Khởi chạy Frontend

1. Mở một terminal mới và di chuyển vào thư mục frontend:
   ```bash
   cd frontend
   npm install
   ```
2. Khởi động Vite development server:
   ```bash
   npm run dev
   ```
3. Truy cập giao diện tại `http://localhost:5173`.

---

## 5. Pipeline nạp xử lý dữ liệu

Pipeline xử lý dữ liệu được thiết kế thành các script độc lập và idempotent:

- **`scripts/import_scores.py`:** Đọc dữ liệu theo luồng bằng `csv.DictReader`, xử lý chuẩn hóa dữ liệu (giữ 8 chữ số SBD có số 0 đầu, chuyển chuỗi rỗng thành `NULL`, ép kiểu float), chia nhỏ thành từng batch 4,000 dòng (44,000 tham số, nằm trong giới hạn 65,535 của PostgreSQL) và chèn qua SQLAlchemy Core bulk insert để bỏ qua chi phí entity-tracking của ORM. Hỗ trợ cờ `--reset` để xóa bảng và nạp lại từ đầu.
- **`scripts/aggregate_statistics.py`:** Tổng hợp `total_students` và phân bố 4 khoảng điểm cho 9 môn học vào bảng `system_metrics` và `score_statistics` bằng upsert (`ON CONFLICT DO UPDATE`). Hỗ trợ cờ `--verify` để tự động đối soát chéo từng môn với bảng `students`.

> Xem chi tiết pipeline xử lý dữ liệu và bảng checklist đối soát tại [docs/data-pipeline.md](docs/data-pipeline.md).

---

## 6. Danh Mục API Endpoints

Tất cả các endpoint sử dụng tiền tố `/api/v1`:

| Method | Endpoint                               | Tham số                                   | Chức năng                                          |
| :----- | :------------------------------------- | :---------------------------------------- | :------------------------------------------------- |
| `GET`  | `/api/v1/health`                       | Không                                     | Kiểm tra trạng thái hoạt động của hệ thống         |
| `GET`  | `/api/v1/subjects`                     | Không                                     | Lấy danh mục 9 môn thi tốt nghiệp THPT             |
| `GET`  | `/api/v1/scores/{registration_number}` | `registration_number`: 8 chữ số           | Tra cứu kết quả thi theo số báo danh               |
| `GET`  | `/api/v1/reports/score-distribution`   | `subjectCode`: chuỗi (`toan`, `all`, ...) | Thống kê số lượng thí sinh theo 4 khoảng điểm      |
| `GET`  | `/api/v1/students/top-a`               | Không                                     | Danh sách 10 thí sinh có tổng điểm Khối A cao nhất |
| `GET`  | `/api/v1/students/total`               | Không                                     | Lấy tổng số lượng thí sinh dự thi toàn quốc        |

### Phản hồi mẫu (`GET /api/v1/scores/01000001`):

```json
{
  "data": {
    "registrationNumber": "01000001",
    "scores": [
      { "subjectCode": "toan", "subjectName": "Toán", "score": 8.4 },
      { "subjectCode": "ngu_van", "subjectName": "Ngữ văn", "score": 6.75 },
      { "subjectCode": "ngoai_ngu", "subjectName": "Ngoại ngữ", "score": 8.0 },
      { "subjectCode": "vat_li", "subjectName": "Vật lí", "score": 6.0 },
      { "subjectCode": "hoa_hoc", "subjectName": "Hóa học", "score": 5.25 },
      { "subjectCode": "sinh_hoc", "subjectName": "Sinh học", "score": 5.0 }
    ]
  }
}
```

---

## 7. Kiểm Thử và Chất Lượng Mã Nguồn

Dự án áp dụng bộ kiểm thử tự động gồm 28 bài test (Unit, Integration và API tests) sử dụng `pytest`:

```bash
cd backend

# Chạy toàn bộ test suite
pytest -v

# Kiểm tra chuẩn mã nguồn bằng Ruff
ruff check .
```

Phạm vi kiểm thử bao gồm: tính đúng đắn của logic tính điểm OOP (`test_domain.py`), logic phân batch và làm sạch dữ liệu import (`test_import_logic.py`), cơ chế đọc/ghi cache và graceful degradation khi Redis timeout/offline (`test_cache.py`), truy vấn cơ sở dữ liệu (`test_queries.py`), tính toàn vẹn dữ liệu bảng thống kê (`test_statistics.py`), và mã trạng thái HTTP/schema phản hồi của toàn bộ API (`test_endpoints.py`).

---

## 8. Triển Khai Thực Tế (Deployment)

Dự án được cấu hình Monorepo Fullstack triển khai trực tiếp trên **Vercel** thông qua file [`vercel.json`](vercel.json):

- **Backend:** Chạy dưới dạng FastAPI Serverless Function tại thư mục `backend/`, tiếp nhận các yêu cầu có tiền tố `/api/(.*)`.
- **Frontend:** Đóng gói tĩnh bằng Vite tại thư mục `frontend/`, tiếp nhận các đường dẫn `/(.*)` và phục vụ SPA routing qua `/index.html`.
- **Cơ sở dữ liệu:** PostgreSQL trên Supabase kết nối qua Transaction Pooler (PgBouncer cổng `5432`/`6543`).

> Xem hướng dẫn cấu hình biến môi trường và chi tiết triển khai tại [docs/deployment.md](docs/deployment.md).

---
