# Hướng Dẫn Triển Khai Thực Tế (Deployment Guide)

Tài liệu này hướng dẫn chi tiết quy trình triển khai hệ thống G-Scores dưới hai hình thức:

1. **Triển khai Serverless trên nền tảng Vercel** (Cấu hình đang chạy thực tế trên production).
2. **Khởi chạy môi trường cục bộ (Local Development)** không thông qua Docker.

---

## 1. Triển Khai Fullstack Monorepo Lên Vercel

Dự án sử dụng file cấu hình [`vercel.json`](../vercel.json) tại thư mục gốc để quản lý đồng thời hai dịch vụ trong cùng một repository:

### 1.1. Cơ chế Định Tuyến (Routing & Rewrites)

- **Tầng Backend:** Định vị tại thư mục `backend/`, chạy dưới dạng FastAPI Serverless Function. Toàn bộ các HTTP request có tiền tố `/api` hoặc `/api/(.*)` được Vercel tự động chuyển tiếp tới service `backend`. File `api/index.py` đóng vai trò entrypoint nạp `app` từ package `app.main`.
- **Tầng Frontend:** Định vị tại thư mục `frontend/`, đóng gói tĩnh bằng Vite. Các route không bắt đầu bằng `/api` được chuyển tiếp về `/index.html` để phục vụ cơ chế định tuyến Single Page Application (SPA).
- **Lợi ích kiến trúc:** Cả frontend và backend dùng chung domain (`https://g-scores-amber.vercel.app`), loại bỏ hoàn toàn các cấu hình phức tạp về CORS preflight (`OPTIONS` request) và giảm round-trip time.

### 1.2. Cấu Hình Biến Môi Trường (Environment Variables trên Vercel)

| Tên biến                | Giá trị mẫu                                                                               | Mục đích                                                        |
| :---------------------- | :---------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| `DATABASE_URL`          | `postgresql://postgres.[ref]:[pwd]@aws-0-[region].pooler.supabase.com:5432/postgres`      | Kết nối PostgreSQL qua Supabase Transaction Pooler (PgBouncer)  |
| `REDIS_URL`             | `rediss://default:[token]@[endpoint].upstash.io:6379`                                     | Kết nối Redis Cloud / Upstash phục vụ Cache Layer               |
| `REDIS_TIMEOUT_SECONDS` | `0.5`                                                                                     | Giới hạn timeout 500ms cho kết nối Redis (Graceful Degradation) |
| `BACKEND_CORS_ORIGINS`  | `["https://g-scores-amber.vercel.app", "http://localhost:5173", "http://localhost:3000"]` | Cấu hình danh sách domain được phép gọi API                     |
| `VITE_API_BASE_URL`     | `/api/v1`                                                                                 | Đường dẫn API tương đối dùng cho Frontend                       |

> **Lưu ý về Transaction Pooling với asyncpg:**
> Trong môi trường Serverless, các container function được khởi tạo và hủy liên tục. Việc kết nối trực tiếp cổng `5432` không qua pooler dễ gây cạn kiệt connection pool của PostgreSQL. Khuyến nghị sử dụng connection pooler của Supabase (`aws-0-[region].pooler.supabase.com` qua cổng `5432` hoặc `6543`). Driver `asyncpg` tự động vô hiệu hóa statement cache để tương thích với chế độ Transaction Pooling của PgBouncer.

---
