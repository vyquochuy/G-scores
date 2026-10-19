# G-Scores: He Thong Tra Cuu va Phan Tich Pho Diem Thi Tot Nghiep THPT 2024

G-Scores la ung dung web chuyen dung tra cuu diem thi, truc quan hoa pho diem va thong ke thu hang thi sinh trong ky thi Tot nghiep THPT Quoc gia 2024 tai Viet Nam. He thong duoc thiet ke de xu ly hieu nang cao tren tap du lieu hon 1 trieu ban ghi (1,061,605 dong), toi uu hoa truy van co so du lieu va ap dung kien truc huong doi tuong (OOP) chat che.

---

## 1. Cong Nghe Su Dung

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 Asyncio, asyncpg, Alembic, Pytest, Ruff.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS (phong cach TailAdmin).
- **Co so du lieu:** PostgreSQL 16.
- **Dong goi & Van hanh:** Docker, Docker Compose, Nginx.

---

## 2. Yeu Cau He Thong

- Python 3.12 tro len.
- Node.js 18.x hoac 20.x tro len kem npm.
- PostgreSQL 16 tro len (neu chay local khong dung Docker).
- Docker va Docker Compose (neu su dung container).

---

## 3. Khoi Chay Nhanh Bang Docker Compose (Khuyen Nghi)

He thong ho tro khoi chay toan bo gom PostgreSQL, FastAPI Backend va React Frontend (Nginx reverse proxy) chi bang mot cau lenh.

### Buoc 1: Sao chep file cau hinh moi truong
```bash
cp .env.example .env
```

### Buoc 2: Khoi dung cac container
```bash
docker compose up -d --build
```

Sau khi cac service khoi dong thanh cong:
- **Frontend Web UI:** Truy cap tai `http://localhost:5173` hoac `http://localhost:3000`.
- **Backend API:** Truy cap tai `http://localhost:8000`.
- **API Documentation (Swagger UI):** Truy cap tai `http://localhost:8000/docs`.

### Buoc 3: Chay Migration va Nap Du Lieu vao Database trong Docker
```bash
# Thuc thi migration tao bang students
docker compose exec backend alembic upgrade head

# Nap du lieu tu tap tin CSV (khoang 120 giay cho 1,061,605 ban ghi)
docker compose exec backend python scripts/import_scores.py
```

---

## 4. Huong Dan Cai Dat va Chay Local

### 4.1. Cau hinh Co So Du Lieu PostgreSQL
Tao co so du lieu moi tren PostgreSQL:
```sql
CREATE DATABASE gscores;
```

### 4.2. Cai dat va Khoi chay Backend
1. Di chuyen vao thu muc backend:
   ```bash
   cd backend
   ```

2. Tao va kich hoat moi truong ao Python:
   ```bash
   # Tren Windows PowerShell:
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Tren Linux/macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Cai dat cac goi phu thuoc:
   ```bash
   pip install -r requirements.txt
   ```

4. Cau hinh file `.env`:
   Tao file `.env` tai thu muc `backend/` (tham khao `.env.example`) va thiet lap chuoi ket noi:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@localhost:5432/gscores
   ```

5. Chay migration tao schema:
   ```bash
   alembic upgrade head
   ```

6. Nap du lieu tu tap tin CSV vao co so du lieu:
   ```bash
   python scripts/import_scores.py
   ```
   *Luu y:* Script co co che kiem tra idempotent, tu dong bo qua neu da nap du. Truyen them co `--reset` neu muon xoa du lieu cu de nap lai tu dau:
   ```bash
   python scripts/import_scores.py --reset
   ```

7. Khoi dong Backend server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

### 4.3. Cai dat va Khoi chay Frontend
1. Mo mot terminal moi va di chuyen vao thu muc frontend:
   ```bash
   cd frontend
   ```

2. Cai dat dependencies:
   ```bash
   npm install
   ```

3. Khoi dong Development Server:
   ```bash
   npm run dev
   ```
   Ung dung giao dien se san sang tai `http://localhost:5173`.

---

## 5. Kiem Thu Tu Dong (Automated Testing)

Toan bo test suite duoc viet bang `pytest` va `pytest-asyncio`, bao gom Unit Tests, Integration Tests va API Tests.

Chay kiem thu tai thu muc `backend/`:
```bash
cd backend
pytest -v
```

Kiem tra chuan ma nguon bang Ruff:
```bash
ruff check .
```

---

## 6. Danh Sach API Endpoints Chinh

Tat ca cac endpoint deu su dung tien to `/api/v1` va phan hoi theo dinh dang chuan:

| Phuong thuc | Endpoint | Chuc nang |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Kiem tra trang thai hoat dong he thong va ket noi CSDL |
| `GET` | `/api/v1/subjects` | Lay danh muc 9 mon thi tot nghiep THPT 2024 |
| `GET` | `/api/v1/scores/{registration_number}` | Tra cuu diem thi theo so bao danh (8 chu so) |
| `GET` | `/api/v1/reports/score-distribution` | Thong ke pho diem 4 khoang theo ma mon hoc (`?subjectCode=toan`) |
| `GET` | `/api/v1/students/top-a` | Danh sach 10 thi sinh co tong diem Khoi A cao nhat |
| `GET` | `/api/v1/students/total` | Tong so thi sinh trong he thong |

---

## 7. Quyet Dinh Kien Truc Cot Loi (ADR)

1. **Mo hinh Bang phang (Wide Table):**
   - Bang `students` chua day du 9 cot diem mon thi va ma ngoai ngu.
   - Ly do: Giam thieu so luong ban ghi tu 7 trieu dong xuong con 1,061,605 dong, toi uu toc do import va loai bo hoan toan cac phep JOIN nang ne khi tinh toan xep hang Khoi A.
2. **Kien truc Huong doi tuong (OOP Domain Model):**
   - Dong goi mon hoc (`Subject`), quy tac phan khoang diem (`ScoreBand`), to hop khoi thi (`ExamGroup`, `GroupA`) va bo quan ly danh muc mon thi (`SubjectRegistry`).
   - Phan tach ro rang giua tang luu tru CSDL va nghiep vu xu ly huong doi tuong.
3. **Pipeline Ingestion Streaming & Batching:**
   - Su dung `csv.DictReader` phan chia batch dong (toi da 4,000 dong/batch tuong ung 44,000 tham so, dam bao an toan duoi nguong 65,535 tham so cua giao thuc PostgreSQL).
   - Thuc thi bang SQLAlchemy Core Table Bulk Insert, dat toc do trung binh tren 9,000 dong/giay, tong thoi gian nap toan bo hon 1 trieu ban ghi chi khoang 120 giay va giu muc tieu thu bo nho RAM duoi 100MB.
4. **SQL Conditional Aggregation:**
   - Thong ke 4 khoang pho diem truc tiep tai database engine thong qua cau lenh `func.count(case(...))`, thoi gian truy van duoi 100ms tren 1 trieu ban ghi ma khong keo du lieu ve bo nho RAM ung dung.

---

## 8. Trien Khai Truc Tuyen (Deployment)

- **Backend API:** Duoc thiet ke san sang trien khai tren Render / Railway / Fly.io su dung Docker hoac Python Native Environment.
- **Frontend SPA:** San sang trien khai tren Vercel / Netlify / Cloudflare Pages voi file build tinh (`npm run build`).
- **Co so du lieu:** Ho tro ket noi PostgreSQL Cloud (Supabase, Neon, AWS RDS, Render PostgreSQL).
- **Link Ung dung Truc tuyen (Live Demo):** *(Cap nhat URL sau khi trien khai production)*
