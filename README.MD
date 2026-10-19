# G-Scores: Hệ Thống Tra Cứu và Phân Tích Phổ Điểm Thi Tốt Nghiệp THPT 2024

G-Scores là ứng dụng web chuyên dụng phục vụ tra cứu điểm thi, trực quan hóa phổ điểm và thống kê thứ hạng thí sinh trong kỳ thi Tốt nghiệp THPT Quốc gia 2024 tại Việt Nam.

---

## 1. Giao Diện Người Dùng và Các Chức Năng Chính

Hệ thống cung cấp giao diện quản trị theo phong cách TailAdmin, hỗ trợ hiển thị đầy đủ trên cả máy tính và thiết bị di động, bao gồm 4 phân hệ chính:

### 1.1. Phân hệ Tổng quan Hệ thống

Hiển thị tổng quan các chỉ số vĩ mô của kỳ thi (1,061,605 thí sinh, 9 môn thi tốt nghiệp, điểm thủ khoa Khối A 29.60), giám sát trạng thái kết nối cơ sở dữ liệu thời gian thực và cung cấp các liên kết truy cập nhanh đến các tính năng.

![Tổng quan hệ thống](.github/images/01-tong-quan.png)

### 1.2. Phân hệ Tra cứu Điểm thi Cá nhân

Cho phép tra cứu điểm thi chính xác bằng số báo danh gồm 8 chữ số. Hệ thống tự động phân loại mức điểm từng môn và tính tổng điểm tổ hợp Khối A nếu thí sinh dự thi đủ 3 môn Toán, Vật lí, Hóa học.

![Tra cứu điểm thi](.github/images/02-tra-cuu.png)

### 1.3. Phân hệ Thống kê Phân bố Phổ điểm

Trực quan hóa số lượng và tỷ lệ phần trăm thí sinh theo 4 khoảng điểm chuẩn quy định (`>= 8.0`, `6.0 - 7.9`, `4.0 - 5.9`, `< 4.0`) bằng biểu đồ trực quan, hỗ trợ chuyển đổi động giữa tất cả các môn thi.

![Thống kê phổ điểm](.github/images/03-thong-ke.png)

### 1.4. Phân hệ Bảng xếp hạng Top 10 Khối A

Danh sách 10 thí sinh có tổng điểm 3 môn Toán, Vật lí, Hóa học cao nhất cả nước.

![Top 10 Khối A](.github/images/04-top-10.png)

---

## 2. Công Nghệ Sử Dụng

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 Asyncio, asyncpg, Alembic, Redis (asyncio), Pytest, Ruff.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS (định hướng TailAdmin).
- **Cơ sở dữ liệu & Caching:** PostgreSQL 16, Redis 7 Alpine.
- **Đóng gói và vận hành:** Docker, Docker Compose, Nginx.


---

## 3. Yêu Cầu Môi Trường

- Python từ phiên bản 3.12 trở lên.
- Node.js từ phiên bản 18.x hoặc 20.x trở lên kèm npm.
- PostgreSQL từ phiên bản 16 trở lên (nếu chạy môi trường cục bộ không qua Docker).
- Docker và Docker Compose (nếu chạy môi trường container hóa).

---

## 4. Hướng Dẫn Khởi Chạy Nhanh Bằng Docker Compose (Khuyến Nghị)

Hệ thống được thiết kế để khởi động đồng bộ toàn bộ gồm PostgreSQL, FastAPI Backend và React Frontend (phục vụ qua Nginx) chỉ bằng một câu lệnh duy nhất.

### Bước 1: Sao chép file cấu hình môi trường

```bash
cp .env.example .env
```

### Bước 2: Khởi dựng các container

```bash
docker compose up -d --build
```

Sau khi các dịch vụ khởi động thành công:

- **Giao diện Frontend:** Truy cập tại `http://localhost:5173` hoặc `http://localhost:3000`.
- **Backend API:** Truy cập tại `http://localhost:8000`.
- **Tài liệu API (Swagger UI):** Truy cập tại `http://localhost:8000/docs`.

### Bước 3: Chạy Migration và Nạp Dữ Liệu vào Cơ sở dữ liệu Docker

```bash
# Thực thi migration tạo bảng students, bảng thống kê và index tối ưu
docker compose exec backend alembic upgrade head

# Nạp dữ liệu từ tập tin CSV (khoảng 120 giây cho 1,061,605 dòng)
docker compose exec backend python scripts/import_scores.py

# Tổng hợp số liệu ban đầu và đối soát tự động 100% ground truth
docker compose exec backend python scripts/aggregate_statistics.py --verify
```


---

## 5. Hướng Dẫn Cài Đặt và Khởi Chạy Cục Bộ (Local)

### 5.1. Cấu hình Cơ sở dữ liệu PostgreSQL

Khởi tạo cơ sở dữ liệu trên PostgreSQL cục bộ:

```sql
CREATE DATABASE gscores;
```

### 5.2. Cài đặt và Khởi chạy Backend

1. Di chuyển vào thư mục backend:

   ```bash
   cd backend
   ```

2. Tạo và kích hoạt môi trường ảo Python:

   ```bash
   # Trên Windows PowerShell:
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Trên Linux/macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Cài đặt các gói phụ thuộc:

   ```bash
   pip install -r requirements.txt
   ```

4. Cấu hình file `.env`:
   Tạo file `.env` tại thư mục `backend/` (tham khảo `.env.example`) và cấu hình chuỗi kết nối:

   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@localhost:5432/gscores
   ```

5. Chạy migration khởi tạo cấu trúc bảng:

   ```bash
   alembic upgrade head
   ```

6. Nạp dữ liệu từ tập tin CSV vào cơ sở dữ liệu:

   ```bash
   python scripts/import_scores.py
   ```

   _Lưu ý:_ Script được tích hợp cơ chế idempotent, tự động kiểm tra số lượng và bỏ qua an toàn nếu dữ liệu đã tồn tại. Truyền thêm cờ `--reset` nếu muốn xóa dữ liệu cũ để nạp lại từ đầu:

   ```bash
   python scripts/import_scores.py --reset
   ```

7. Tổng hợp dữ liệu thống kê và đối soát 100% với bảng gốc:

   ```bash
   python scripts/aggregate_statistics.py --verify
   ```

8. Khởi động máy chủ Backend:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```


### 5.3. Cài đặt và Khởi chạy Frontend

1. Mở một cửa sổ dòng lệnh mới và di chuyển vào thư mục frontend:

   ```bash
   cd frontend
   ```

2. Cài đặt các thư viện phụ thuộc:

   ```bash
   npm install
   ```

3. Khởi động Development Server:
   ```bash
   npm run dev
   ```
   Ứng dụng sẽ sẵn sàng tại `http://localhost:5173`.

---

## 6. Kiểm Thử Tự Động (Automated Testing)

Toàn bộ test suite được xây dựng bằng `pytest` và `pytest-asyncio`, bao gồm đầy đủ Unit Tests, Integration Tests và API Tests.

Chạy toàn bộ kiểm thử tại thư mục `backend/`:

```bash
cd backend
pytest -v
```

Kiểm tra chuẩn mực mã nguồn bằng Ruff:

```bash
ruff check .
```

---

## 7. Danh Mục API Endpoints

Tất cả các endpoint đều sử dụng tiền tố `/api/v1` và chuẩn hóa cấu trúc dữ liệu JSON:

| Phương thức | Đường dẫn Endpoint                     | Mục đích chức năng                                           |
| :---------- | :------------------------------------- | :----------------------------------------------------------- |
| `GET`       | `/api/v1/health`                       | Kiểm tra trạng thái hoạt động hệ thống và kết nối CSDL       |
| `GET`       | `/api/v1/subjects`                     | Lấy danh mục 9 môn thi tốt nghiệp THPT 2024                  |
| `GET`       | `/api/v1/scores/{registration_number}` | Tra cứu kết quả thi theo số báo danh 8 chữ số                |
| `GET`       | `/api/v1/reports/score-distribution`   | Thống kê phổ điểm 4 khoảng theo mã môn (`?subjectCode=toan`) |
| `GET`       | `/api/v1/students/top-a`               | Lấy danh sách 10 thí sinh có tổng điểm Khối A cao nhất       |
| `GET`       | `/api/v1/students/total`               | Lấy tổng số lượng thí sinh trong toàn hệ thống               |

---

## 8. Các Quyết Định Kiến Trúc Cốt Lõi (Architecture Decision Records)

1. **Mô hình Bảng phẳng (Wide Table):**
   - Bảng `students` lưu trữ trực tiếp 9 cột điểm môn thi và mã ngoại ngữ của thí sinh.
   - Cơ sở lý luận: Giảm thiểu số lượng bản ghi từ 7 triệu dòng (nếu chuẩn hóa dạng dọc) xuống đúng 1,061,605 dòng. Tối ưu hóa vượt trội tốc độ nạp dữ liệu và loại bỏ hoàn toàn các phép JOIN phức tạp khi tính toán điểm Khối A.
2. **Thiết kế Hướng đối tượng (OOP Domain Modeling):**
   - Đóng gói môn học (`Subject`), phân loại khoảng điểm (`ScoreBand`), tổ hợp xét tuyển (`ExamGroup`, `GroupA`) và bộ quản lý danh mục môn thi (`SubjectRegistry`) thành các lớp đối tượng chuyên trách ở tầng domain.
   - Tách biệt rành mạch giữa mô hình lưu trữ cơ sở dữ liệu và logic nghiệp vụ hướng đối tượng của ứng dụng.
3. **Pipeline Nạp Dữ Liệu Streaming và Phân Đoạn Batch:**
   - Sử dụng `csv.DictReader` kết hợp tính toán kích thước batch động (tối đa 4,000 dòng/batch tương ứng 44,000 tham số, an toàn tuyệt đối dưới ngưỡng giới hạn 65,535 tham số của giao thức PostgreSQL).
   - Sử dụng phương thức SQLAlchemy Core Table Bulk Insert, đạt tốc độ trung bình trên 9,000 dòng/giây, tổng thời gian nạp toàn bộ hơn 1 triệu bản ghi chỉ mất khoảng 120 giây và duy trì lượng RAM dưới 100MB.
4. **Thống Kê Trực Tiếp Tại Database Engine (SQL Conditional Aggregation):**
   - Tổng hợp 4 khoảng phổ điểm và đếm số lượng bài thi hợp lệ trực tiếp thông qua câu lệnh `func.count(case(...))`. Thời gian phản hồi dưới 100ms mà không kéo dữ liệu thô về bộ nhớ của backend.
5. **Tối Ưu Hiệu Năng Bằng Bảng Thống Kê và Functional Index (PostgreSQL P0 Optimization):**
   - Thay vì quét toàn bộ 1,061,605 dòng ở mỗi lượt người dùng truy cập, hệ thống sử dụng bảng `system_metrics` (lưu chỉ số tĩnh toàn cục như `total_students`) và `score_statistics` (lưu phổ điểm 4 khoảng của 9 môn học).
   - Thiết lập Partial Functional Index `idx_students_group_a_sum` trên biểu thức `((toan + vat_li + hoa_hoc) DESC, sbd ASC) WHERE toan IS NOT NULL AND vat_li IS NOT NULL AND hoa_hoc IS NOT NULL`. Xác minh bằng `EXPLAIN (ANALYZE, BUFFERS)` cho thấy PostgreSQL thực thi trực tiếp `Index Scan` và loại bỏ hoàn toàn nút `Sort`, giảm thời gian truy vấn nội bộ CSDL xuống chỉ 2.8ms - 4.4ms.
   - Script `aggregate_statistics.py` được thiết kế idempotent và có cờ `--verify` đối soát tự động 100% ground truth với bảng gốc.
6. **Lớp Cache Redis (Cache-Aside Pattern & Graceful Degradation) và CDN Cache:**
   - Triển khai mô hình Cache-Aside bất đồng bộ với TTL 24 giờ cho các endpoint `/total`, `/reports/score-distribution` và `/top-a` kèm key versioning (`v1`).
   - Tích hợp timeout kết nối 500ms và cơ chế Graceful Degradation: nếu Redis offline hoặc timeout, API tự động chuyển tiếp truy vấn PostgreSQL mà không gây gián đoạn hay phát sinh lỗi HTTP 500. Khi Redis Cache Hit, độ trễ API giảm xuống dưới 2ms (tăng tốc gấp 170-700 lần).
   - Thiết lập header HTTP `Cache-Control: public, max-age=3600, s-maxage=86400, stale-while-revalidate=86400` phục vụ CDN caching cho các tài nguyên tĩnh.

---


## 9. Hướng Dẫn Triển Khai Thực Tế Lên Vercel (Fullstack Deployment Guide)

Hệ thống được thiết kế theo mô hình Monorepo và triển khai đồng bộ toàn diện cả **Frontend** (React + Vite) lẫn **Backend API** (Python FastAPI) trực tiếp trên nền tảng **Vercel** thông qua file cấu hình `src/vercel.json`.

### 9.1. Kiến Trúc Triển Khai Đa Dịch Vụ trên Vercel (Vercel Multi-Service Routing)

File cấu hình [`vercel.json`](vercel.json) phân tách rành mạch hai dịch vụ:

1. **Dịch vụ Backend (FastAPI Serverless):**
   - Thư mục gốc (`root`): `backend`.
   - Framework: `fastapi`.
   - Toàn bộ các yêu cầu HTTP có tiền tố `/api` hoặc `/api/(.*)` được Vercel tự động chuyển tiếp (rewrite) trực tiếp về backend FastAPI xử lý.
2. **Dịch vụ Frontend (Vite React SPA):**
   - Thư mục gốc (`root`): `frontend`.
   - Framework: `vite`.
   - Xử lý điều hướng Single Page Application (SPA routing rewrite): toàn bộ đường dẫn web không thuộc `/api` được chuyển tiếp về `/index.html`.

_Lợi ích kiến trúc:_ Frontend và Backend hoạt động trên cùng một domain (`https://g-scores-amber.vercel.app`), giúp loại bỏ hoàn toàn các vấn đề phức tạp về CORS preflight request, giảm độ trễ mạng (network latency round-trip) và tối ưu hóa hiệu năng tổng thể.

### 9.2. Các Bước Triển Khai trên Vercel Dashboard

1. Kết nối kho lưu trữ GitHub chứa dự án với Vercel.
2. Thiết lập thư mục gốc (Root Directory) tại Vercel Project Settings là `src` (nơi chứa `vercel.json`).
3. Vercel sẽ tự động đọc `vercel.json` để nhận diện cấu trúc hai dịch vụ `backend` và `frontend`.
4. Cấu hình các biến môi trường (Environment Variables) trên Vercel:
   - `DATABASE_URL`: Chuỗi kết nối PostgreSQL Cloud (khuyến nghị sử dụng Supabase Session/Transaction Pooler qua cổng 5432 hoặc 6543 để tương thích với driver `asyncpg` trong môi trường serverless).
   - `REDIS_URL`: Chuỗi kết nối Redis Cloud / Upstash Redis (ví dụ: `rediss://default:token@region.upstash.io:6379`).
   - `REDIS_TIMEOUT_SECONDS`: `0.5` (500ms để đảm bảo cơ chế Graceful Degradation).
   - `BACKEND_CORS_ORIGINS`: `["https://g-scores-amber.vercel.app", "http://localhost:5173", "http://localhost:3000"]`.
   - `VITE_API_BASE_URL`: `/api/v1` (sử dụng đường dẫn tương đối trực tiếp cùng domain).
5. Nhấn **Deploy** để hoàn tất quá trình triển khai tự động.

---

## 10. Liên Kết Ứng Dụng Trực Tuyến (Live Demo)

- **Giao diện Web Ứng dụng (Frontend):** [https://g-scores-amber.vercel.app](https://g-scores-amber.vercel.app)
- **Kiểm tra trạng thái hệ thống (Health Check API):** [https://g-scores-amber.vercel.app/api/v1/health](https://g-scores-amber.vercel.app/api/v1/health)
- **Tra cứu điểm thi mẫu (SBD 01000001):** [https://g-scores-amber.vercel.app/api/v1/scores/01000001](https://g-scores-amber.vercel.app/api/v1/scores/01000001)
- **Bảng xếp hạng Top 10 Khối A:** [https://g-scores-amber.vercel.app/api/v1/students/top-a](https://g-scores-amber.vercel.app/api/v1/students/top-a)
- **Báo cáo phổ điểm môn Toán:** [https://g-scores-amber.vercel.app/api/v1/reports/score-distribution?subjectCode=toan](https://g-scores-amber.vercel.app/api/v1/reports/score-distribution?subjectCode=toan)
- **Tổng số lượng thí sinh toàn quốc:** [https://g-scores-amber.vercel.app/api/v1/students/total](https://g-scores-amber.vercel.app/api/v1/students/total)

