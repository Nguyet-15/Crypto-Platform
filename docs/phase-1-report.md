# Giai đoạn 1 — Foundation

## Khảo sát trước khi sửa

Đã đọc tất cả file nguồn, cấu hình, workflow, tài liệu và thư mục placeholder ban đầu.
Không có AGENTS.md trong cây dự án. Chưa có thư mục .git trong workspace được cung cấp.

Đã có: Next.js 16/React 19/TypeScript/Tailwind, FastAPI health endpoint, API client cơ bản,
SQLAlchemy engine, PostgreSQL 16 Compose với volume/healthcheck, pytest health, hai workflow CI,
các thư mục module, infrastructure, ml, infra và research.

Còn thiếu: đường dẫn .env ổn định, database readiness, session lifecycle, migrations hoạt động,
logging/error contract, client timeout/validation/cancellation, frontend tests, lockfile và CI
khớp package manager, thiết kế ranh giới module và hướng dẫn kiểm chứng đầy đủ.

## File tạo/chỉnh sửa và chức năng

| File | Thay đổi / chức năng |
|---|---|
| `.env.example` | Bổ sung CORS JSON, log level và database connect timeout |
| `.gitignore` | Bỏ qua cache, metadata Python, output test và TypeScript build info |
| `README.md` | Cài đặt, chạy trong VS Code, migration, test và cách đọc trạng thái |
| `backend/pyproject.toml` | Thêm Alembic cần thiết cho migration; cấu hình Ruff cục bộ |
| `backend/app/core/config.py` | Nạp env bằng đường dẫn tuyệt đối, xác thực timeout/log level, CORS cấu hình được |
| `backend/app/core/logging.py` | Request ID và log request ra stdout |
| `backend/app/core/errors.py` | Error envelope HTTP/validation/internal, che thông tin nội bộ |
| `backend/app/db/session.py` | Pool pre-ping/timeout, dependency đóng session và SELECT 1 |
| `backend/app/db/base.py` | SQLAlchemy metadata nền để thêm model sau này |
| `backend/app/main.py` | Đăng ký middleware, error handlers, router; dispose engine khi shutdown |
| `backend/app/api/v1/health.py` | Giữ liveness và thêm readiness 200/503 có dependency override cho tests |
| `backend/app/api/v1/modules.py` | Endpoint trạng thái module, không tạo kết quả phân tích |
| `backend/app/modules/__init__.py` | Ranh giới package module |
| `backend/app/modules/registry.py` | Danh mục tám module với trạng thái not_implemented |
| `backend/app/modules/{market_data,market_structure,smc,ict,candlestick,chart_patterns,predictions,backtesting}/__init__.py` | Khởi tạo từng package, ghi rõ nghiệp vụ chưa triển khai |
| `backend/app/modules/{market_data,market_structure,smc,ict,candlestick,chart_patterns,predictions,backtesting}/README.md` | Trách nhiệm, public contract, vị trí domain/service/ports/router/model khi mở rộng |
| `backend/alembic.ini` | Đường dẫn migration độc lập thư mục chạy |
| `backend/alembic/env.py` | Online/offline migration lấy cấu hình chung, metadata chung |
| `backend/alembic/script.py.mako` | Template tạo revision |
| `backend/alembic/versions/0001_foundation.py` | Baseline rỗng nghiệp vụ; Alembic quản lý bảng phiên bản |
| `backend/tests/test_health.py` | Giữ test có sẵn, chuẩn hóa định dạng/import |
| `backend/tests/test_foundation.py` | Readiness, lỗi không lộ secret, CORS, env/timeout, module status |
| `backend/tests/integration/test_postgres.py` | SELECT 1 trên PostgreSQL thật, opt-in RUN_DB_TESTS=1 |
| `frontend/src/types/api.ts` | TypeScript contracts health/readiness/module |
| `frontend/src/services/api-client.ts` | Fetch adapter riêng, timeout, abort, validation và ApiError |
| `frontend/src/app/page.tsx` | Trạng thái API/DB riêng, danh sách module từ backend, cleanup request |
| `frontend/package.json` | Script test/typecheck, dùng dependency đã có |
| `frontend/package-lock.json` | Lock dependency npm để npm ci tái lập |
| `frontend/next-env.d.ts` | Next.js t? c?p nh?t type references khi build |
| `frontend/postcss.config.mjs` | ??t t?n c?u h?nh export ?? lint kh?ng c?nh b?o |
| `frontend/tsconfig.json` | Chuẩn hóa định dạng và bỏ qua output test |
| `frontend/tsconfig.test.json` | Biên dịch client test bằng TypeScript có sẵn |
| `frontend/tests/api-client.test.mjs` | Node test runner, mock transport; không thêm framework test |
| `frontend/eslint.config.mjs` | Bỏ qua output test/cache khỏi lint |
| `.github/workflows/backend-ci.yml` | Pytest, lint và offline migration SQL |
| `.github/workflows/frontend-ci.yml` | npm ci theo lockfile, lint, test và production build |
| `docs/architecture.md` | Luồng phụ thuộc, ranh giới tám module và chính sách dữ liệu |
| `docs/roadmap.md` | Các giai đoạn từ Foundation tới paper trading |
| `docs/phase-1-report.md` | Báo cáo này |

Các thư mục ban đầu và `.gitkeep` được giữ nguyên. `docker-compose.yml`, frontend `.env.example`,
next config, CSS, layout và tài liệu định nghĩa chiến lược hiện có vẫn được sử dụng.
Chỉ bổ sung một dependency runtime trực tiếp: Alembic, phục vụ migration PostgreSQL.

## Lệnh và cách kiểm tra

Xem các khối PowerShell đầy đủ trong [README](../README.md).
API `/health` trả 200 độc lập DB; `/health/ready` chỉ 200 khi SELECT 1 thành công;
`/modules` trả tám trạng thái not_implemented. Frontend hiển thị lỗi kết nối thực tế,
không thay lỗi bằng giá thị trường hay tín hiệu giả.

## Phát triển tiếp

Ưu tiên chốt provider và contract OHLCV, thêm model/migration market_data, thu thập dữ liệu
lịch sử có provenance và kiểm tra pagination/gaps/duplicates. Sau đó mới hiển thị chart và
triển khai detector theo định nghĩa có kiểm thử, tránh lookahead. Các chức năng phân tích,
prediction, backtesting, auth và paper trading chưa được triển khai ở Foundation.

## K?t qu? ki?m ch?ng t?i workspace (28/10/2026)

- M?i tr??ng: Python 3.14.3, Node 24.15.0, npm 11.12.1; ch?a c? Docker ho?c psql.
- Backend: **10 passed, 1 skipped**; Ruff ??t; Alembic `upgrade head --sql` sinh SQL h?p l?.
- C? m?t deprecation warning t? Starlette TestClient v?i httpx; test v?n ??t.
  Ch?a th?m httpx2 ch? ?? t?t c?nh b?o ph? thu?c ? Foundation.
- Frontend: **6 tests passed**; ESLint, TypeScript v? production build Next.js ??t.
- npm install t?o package-lock; audit l?c c?i ??t b?o 0 vulnerabilities.
- Smoke HTTP th?t: production frontend tr? 200 v? c? ti?u ?? trang; API client ?? bi?n d?ch
  g?i FastAPI th?t, ki?m ch?ng health 200, modules 200, CORS origin v? readiness 503 c? request ID.
- ?i?u ch?nh timeout client t? 5 l?n 10 gi?y sau smoke test: localhost tr?n m?y n?y th?
  IPv6 v? IPv4, database offline m?t kho?ng 6 gi?y v?i connect_timeout=3 cho m?i ??a ch?.
- **Ch?a ki?m ch?ng PostgreSQL th?t ho?c online migration** v? m?i tr??ng ch?a c? server DB.
  Test readiness th?nh c?ng hi?n d?ng dependency override, kh?ng ???c coi l? b?ng ch?ng DB th?t.
  Ch?y Docker, Alembic upgrade v? RUN_DB_TESTS theo README ?? ho?n t?t ph?n ki?m ch?ng n?y.
- Build/test c?n quy?n t?o worker process; l?n ??u sandbox ch?n EPERM, sau khi ch?y v?i
  quy?n ph? h?p c?c ki?m tra ??u ??t. Kh?ng thay ??i global package hay c?i framework test m?i.

Kh?ng c? d? li?u th? tr??ng gi?, d? ?o?n gi?, detector gi? ho?c giao d?ch th?t ???c th?m v?o.
