# Hướng Dẫn Cấu Hình và Triển Khai

Tài liệu hướng dẫn cấu hình môi trường, khởi chạy ứng dụng cục bộ và triển khai hệ thống G-Scores lên nền tảng đám mây (Vercel, Supabase, Upstash).

---

## 1. Cấu Hình Biến Môi Trường

Hệ thống sử dụng các biến môi trường sau cho backend và frontend:

| Tên biến                | Môi trường | Giá trị mẫu / Mô tả                                                                                                                                                                |
| :---------------------- | :--------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`          | Backend    | `postgresql+asyncpg://postgres:postgres@localhost:5432/gscores` (Local)<br>`postgresql://postgres.[ref]:[pwd]@aws-0-[region].pooler.supabase.com:5432/postgres` (Cloud / Supabase) |
| `REDIS_URL`             | Backend    | `redis://localhost:6379/0` (Local)<br>`rediss://default:[token]@[endpoint].upstash.io:6379` (Cloud / Upstash)                                                                      |
| `REDIS_TIMEOUT_SECONDS` | Backend    | Mặc định `0.5` (500ms) để kích hoạt cơ chế Graceful Degradation                                                                                                                    |
| `BACKEND_CORS_ORIGINS`  | Backend    | `["http://localhost:5173", "http://localhost:3000"]` (Định dạng JSON mảng)                                                                                                         |
| `VITE_API_BASE_URL`     | Frontend   | `/api/v1` (Khi deploy cùng domain trên Vercel hoặc qua reverse proxy) hoặc `http://localhost:8000/api/v1` (Khi chạy dev độc lập)                                                   |

---

## 2. Khởi Chạy Cục Bộ (Không Dùng Docker)

### 2.1. Yêu cầu hệ thống

- Python 3.12+
- Node.js 18+
- PostgreSQL 16
- Redis 7 (tùy chọn, hệ thống tự fallback sang PostgreSQL nếu không có Redis)

### 2.2. Khởi chạy Backend

```bash
cd backend

# Khởi tạo môi trường ảo và cài đặt thư viện
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt

# Cấu hình file .env từ mẫu
cp .env.example .env

# Chạy migration để khởi tạo schema database
alembic upgrade head

# Nạp dữ liệu và tổng hợp số liệu thống kê ban đầu
python scripts/import_scores.py
python scripts/aggregate_statistics.py --verify

# Khởi động backend API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

### 2.3. Khởi chạy Frontend

```bash
cd frontend

npm install
npm run dev
```

- Truy cập giao diện: `http://localhost:5173`

---

## 3. Triển Khai Fullstack Monorepo Lên Vercel

Dự án được cấu hình sẵn để triển khai đồng thời cả Frontend và Backend Serverless trên cùng một Vercel Project qua tệp [`vercel.json`](../vercel.json):

### 3.1. Cơ chế Routing và Rewrites

- **Backend Function:** Mã nguồn đặt tại `backend/`, chạy dưới dạng FastAPI Serverless Function. Tệp `backend/api/index.py` là entrypoint nạp `app` từ `app.main`. Các request có tiền tố `/api/(.*)` được chuyển trực tiếp vào service backend.
- **Frontend SPA:** Mã nguồn đặt tại `frontend/`, đóng gói tĩnh qua Vite. Tất cả route không bắt đầu bằng `/api` được rewrite về `/index.html`.
- **Lợi thế:** Cả frontend và backend hoạt động chung origin, loại bỏ chi phí CORS preflight (`OPTIONS` request) và đơn giản hóa kiến trúc mạng.

### 3.2. Lưu ý về Database Connection Pooling trong Serverless

Trong môi trường Serverless, các function instance khởi tạo và giải phóng liên tục:

1. **Transaction Pooling (PgBouncer):** Cần kết nối PostgreSQL qua Supabase Transaction Pooler (cổng `5432` hoặc `6543`) để tránh cạn kiệt connection pool.
2. **Cấu hình `asyncpg`:** Trong `backend/app/core/database.py`, hệ thống đã cấu hình vô hiệu hóa cache câu lệnh chuẩn bị (`statement_cache_size=0`, `prepared_statement_cache_size=0`) và sinh tên ngẫu nhiên cho prepared statement nhằm ngăn ngừa lỗi `DuplicatePreparedStatementError` khi chạy qua PgBouncer.
3. **NullPool:** Khi nhận diện biến môi trường Serverless (`VERCEL=1`), SQLAlchemy tự động sử dụng `NullPool` để đóng kết nối ngay sau mỗi request.
