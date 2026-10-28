# Crypto AI Analysis Platform

Giai đoạn 1: Foundation của Modular Monolith gồm Next.js/TypeScript, FastAPI và PostgreSQL.
Chưa có dữ liệu thị trường, detector, dự đoán, backtest hay giao dịch tiền thật.

## Yêu cầu

- Node.js 22+ và npm; Python 3.11+ (khuyến nghị 3.12).
- Docker Desktop với Compose để chạy PostgreSQL 16, hoặc PostgreSQL cài riêng.
- Lệnh bên dưới dùng terminal PowerShell trong VS Code, bắt đầu tại thư mục gốc.

## Chạy PostgreSQL

```powershell
Copy-Item .env.example .env
# Chỉ chạy Copy-Item lần đầu, không ghi đè cấu hình cá nhân đã có.
docker compose up -d db
docker compose ps
docker compose exec db pg_isready -U crypto -d crypto_ai
```

PostgreSQL chỉ bind localhost; volume `postgres_data` giữ dữ liệu qua lần restart.
Thông tin đăng nhập mẫu chỉ dùng local. Nếu đổi user/password/db, phải sửa DATABASE_URL
cho khớp. Biến khởi tạo PostgreSQL chỉ có tác dụng khi volume được tạo lần đầu.
Không dùng `docker compose down -v` nếu cần giữ dữ liệu.

## Chạy backend (terminal 1)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend nạp `.env` gốc rồi `backend/.env` nếu có; biến môi trường hệ điều hành ưu tiên cao nhất.
Không cần tạo backend/.env riêng. CORS_ORIGINS dùng JSON array.
Backend vẫn khởi động khi database offline; readiness trả 503.
Migration nền chỉ tạo bảng phiên bản Alembic, chưa tạo bảng market/candle.
Migration chạy thủ công, không tự chạy khi khởi động server.

## Chạy frontend (terminal 2, từ thư mục gốc)

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Mở http://localhost:3000 và http://localhost:8000/docs.
`NEXT_PUBLIC_API_URL` là địa chỉ trình duyệt truy cập được, không phải hostname Docker.
Sau khi đổi biến NEXT_PUBLIC, restart dev server hoặc build lại bản production.

## Kiểm tra

Từ thư mục gốc:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/health/ready
Invoke-RestMethod http://localhost:8000/api/v1/modules
cd backend
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m alembic upgrade head --sql
$env:RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest tests/integration
Remove-Item Env:RUN_DB_TESTS
.\.venv\Scripts\python.exe -m alembic current
cd ../frontend
npm test
npm run lint
npm run typecheck
npm run build
```

Health phải trả `status: ok`; readiness trả `status: ready, database: ok` khi PostgreSQL hoạt động.
Dừng DB bằng `docker compose stop db` ở gốc: health vẫn 200, readiness 503 và UI hiển thị
chưa sẵn sàng sau khi tải lại trang. Chạy lại `docker compose up -d db` để phục hồi.
Danh sách module luôn ghi `not_implemented` ở giai đoạn này.
Unit test dùng dependency override/mocked fetch, không trình bày fixture như dữ liệu thị trường.
Integration test PostgreSQL thật chỉ chạy khi RUN_DB_TESTS=1.

## Cấu trúc và phạm vi

Giữ nguyên frontend/, backend/, docs/, infra/, research/ và các thư mục module đã có.
Frontend chỉ gọi HTTP qua `src/services/api-client.ts`, với kiểm tra runtime, timeout,
hủy request và ApiError có HTTP status/request ID. Backend dùng SQLAlchemy session dependency,
đóng session tự động; service tương lai phải quản lý commit/rollback rõ ràng.

Log ra stdout gồm request ID, method, path, status, thời gian xử lý; không ghi query string,
request body hay URL database. Lỗi HTTP/validation/internal có dạng `error: {code,message,request_id}`.
Unexpected error log giữ loại lỗi và request ID, không ghi exception chứa secrets.
Liveness và readiness tách biệt; readiness là kiểm tra kết nối, không xác nhận schema đã migrate.

Thiết kế module: [docs/architecture.md](docs/architecture.md).
Báo cáo file và giới hạn kiểm chứng: [docs/phase-1-report.md](docs/phase-1-report.md).
Kế hoạch tiếp theo: [docs/roadmap.md](docs/roadmap.md).

## K?t qu? ki?m ch?ng Giai ?o?n 1

Backend: 10 test ??t, 1 PostgreSQL integration test b? qua; frontend: 6 test ??t.
Lint hai ph?a, TypeScript, Next.js production build v? offline migration SQL ??t.
?? smoke test HTTP th?t gi?a API client v? FastAPI, c?ng trang frontend production.
Ch?a ch?y PostgreSQL th?t ho?c online migration v? m?y hi?n ch?a c? Docker/PostgreSQL.
Starlette TestClient c? m?t deprecation warning v?i httpx, kh?ng l?m test th?t b?i.
Client timeout m?c ??nh 10 gi?y; DB connect timeout 3 gi?y cho m?i ??a ch? host.
