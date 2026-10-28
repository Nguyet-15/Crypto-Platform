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

## Kết quả kiểm chứng Giai đoạn 1

Backend: 10 test đạt, 1 PostgreSQL integration test bỏ qua; frontend: 6 test đạt.
Lint hai phía, TypeScript, Next.js production build và offline migration SQL đạt.
Đã smoke test HTTP thật giữa API client và FastAPI, cùng trang frontend production.
Tại lần kiểm chứng Giai đoạn 1, chưa chạy PostgreSQL thật hoặc online migration vì máy chưa có Docker/PostgreSQL.
Starlette TestClient có một deprecation warning với httpx, không làm test thất bại.
Client timeout mặc định 10 giây; DB connect timeout 3 giây cho mỗi địa chỉ host.

## Lộ trình phát triển đầy đủ

Các mục bên dưới là kế hoạch, không phải tính năng đã triển khai. Giai đoạn 1 đã có mã nguồn
Foundation; phần PostgreSQL thật vẫn cần nghiệm thu. Giai đoạn 2–9 chưa triển khai.
Giữ Modular Monolith và các thư mục hiện có trong mọi giai đoạn. Chỉ thêm thư viện khi có
nhu cầu thực tế, có giải thích và kiểm thử; không mặc định thêm microservices hoặc hàng đợi.

| Giai đoạn | Kết quả chính | Điều kiện bắt đầu |
|---|---|---|
| 1. Foundation | Cấu hình, API client, logging, lỗi, PostgreSQL và migrations | Đã có bộ khung |
| 2. Market Data | Thu thập, kiểm tra và lưu OHLCV thật | PostgreSQL thật vượt qua nghiệm thu |
| 3. Chart và Dashboard | Tra cứu và hiển thị candles thật | API dữ liệu lịch sử ổn định |
| 4. Market Structure và Candlestick | Detector xác định, có thời điểm xác nhận | Dữ liệu và quy tắc đã chuẩn hóa |
| 5. SMC, ICT và Chart Patterns | Phân tích có giải thích, phiên bản quy tắc | Detector nền đã kiểm thử |
| 6. Backtesting | Mô phỏng lịch sử có chi phí và kiểm soát lookahead | Tín hiệu có contract và thời điểm khả dụng |
| 7. Predictions | Mô hình baseline được đánh giá ngoài mẫu | Dataset và pipeline đánh giá tái lập |
| 8. Paper Trading và Monitoring | Theo dõi mô phỏng trên dữ liệu mới | Chiến lược đã qua backtest |
| 9. Triển khai và vận hành | Staging, bảo vệ truy cập, backup và giám sát | Luồng nghiên cứu được nghiệm thu |

### Giai đoạn 1 — Hoàn tất nghiệm thu Foundation

**Mục tiêu:** xác nhận toàn bộ nền tảng chạy được với PostgreSQL thật trước khi tạo bảng nghiệp vụ.

- Chuẩn bị Docker Desktop hoặc PostgreSQL riêng và cấu hình `.env` đúng môi trường.
- Chạy `alembic upgrade head`, kiểm tra `alembic current` và integration test với `RUN_DB_TESTS=1`.
- Kiểm tra frontend, FastAPI và database hoạt động cùng nhau; dừng/khởi động DB để kiểm tra phục hồi.
- Xác nhận dữ liệu PostgreSQL còn tồn tại sau khi restart container, không xóa volume.
- Ghi lại phiên bản môi trường, kết quả test và các giới hạn còn lại trong báo cáo giai đoạn.

**Vị trí thực hiện:** cấu hình gốc, `backend/alembic`, `backend/tests/integration` và CI hiện có.

**Nghiệm thu:** migration online thành công; readiness trả 200 khi DB hoạt động và 503 khi DB
không khả dụng; health vẫn trả 200; frontend hiển thị đúng trạng thái; integration test thật đạt.
Các lệnh cần chạy đã có ở phần **Kiểm tra** phía trên.

### Giai đoạn 2 — Market Data và lưu trữ PostgreSQL

**Mục tiêu:** xây nguồn dữ liệu OHLCV thật, có thể truy vết và thu thập lại an toàn.

- Chọn một provider đầu tiên sau khi kiểm tra tài liệu chính thức, phạm vi dữ liệu và giới hạn truy cập;
  xác định rõ spot/futures, symbol, timeframe và khoảng lịch sử được hỗ trợ.
- Định nghĩa contract candle: provider, market, symbol, timeframe, open/close time theo UTC,
  OHLCV, trạng thái đóng nến, thời gian thu thập và phiên bản định dạng dữ liệu.
- Dùng Decimal/PostgreSQL NUMERIC cho giá và khối lượng; thêm unique constraint theo nguồn,
  thị trường, symbol, timeframe, open time và index phục vụ truy vấn theo thời gian.
- Tạo model và migration; tách provider adapter, repository và application service.
- Thực hiện historical ingestion có pagination, giới hạn tốc độ, timeout, retry có giới hạn,
  checkpoint và khả năng chạy lại mà không tạo dữ liệu trùng.
- Kiểm tra thứ tự thời gian, OHLC hợp lệ, volume không âm, nến trùng, khoảng trống và nến chưa đóng.
  Không tự tạo nến bù rồi coi đó là dữ liệu provider.
- Cung cấp API đọc symbols/timeframes được hỗ trợ và candles theo khoảng thời gian, có giới hạn
  số bản ghi, pagination, thông tin nguồn và trạng thái thiếu dữ liệu.
- Bắt đầu bằng script thu thập thủ công trong `backend/scripts`; chỉ thêm scheduler khi cần.

**Vị trí thực hiện:** `backend/app/modules/market_data`, `backend/app/infrastructure/providers`,
`backend/app/infrastructure/repositories`, `backend/alembic` và `backend/tests`.
Các endpoint và tên bảng cụ thể sẽ được chốt khi triển khai, chưa tồn tại ở Foundation.

**Kiểm thử:** unit test parsing/validation/pagination/retry; integration test lưu và đọc PostgreSQL,
unique constraint, transaction rollback và ingestion chạy lại. Provider test dùng fixture ghi rõ nguồn;
kiểm tra mạng thật là opt-in, không khiến unit test phụ thuộc vào mạng.

**Nghiệm thu:** thu thập một tập dữ liệu lịch sử thật có phạm vi được công bố, đối chiếu mẫu với provider;
chạy lại không tăng số nến trùng; API trả đúng thứ tự/phân trang; gaps và nến chưa đóng được ghi rõ.

### Giai đoạn 3 — Chart và Dashboard dữ liệu thật

**Mục tiêu:** người dùng có thể chọn thị trường và kiểm tra dữ liệu thực tế trên giao diện.

- Thêm bộ chọn provider/market, symbol, timeframe và khoảng thời gian theo khả năng backend hỗ trợ.
- Xây biểu đồ candlestick và volume trong `frontend/src/components/charts`; chỉ chọn thư viện chart
  sau khi đánh giá nhu cầu, giấy phép và khả năng tích hợp với Next.js.
- Mở rộng API client và types theo contract backend; hỗ trợ tải lịch sử theo trang và hủy request cũ
  khi người dùng đổi symbol/timeframe để tránh hiển thị nhầm dữ liệu.
- Hiển thị loading, empty, error, dữ liệu cũ, khoảng trống, nến chưa đóng, nguồn và thời điểm cập nhật.
- Cho phép chọn timezone hiển thị hoặc ghi rõ UTC; backend vẫn lưu UTC.
- Ưu tiên luồng đọc lịch sử trước; chỉ thêm polling hoặc streaming khi có yêu cầu dữ liệu cập nhật.

**Vị trí thực hiện:** `frontend/src/components/charts`, `frontend/src/features/analysis`,
`frontend/src/hooks`, `frontend/src/services`, `frontend/src/types` và API market_data.

**Kiểm thử:** contract API client, đổi bộ lọc nhanh, thứ tự nến, giới hạn tải, timezone,
trạng thái không có dữ liệu/lỗi provider và kiểm tra giao diện trên màn hình nhỏ.

**Nghiệm thu:** đối chiếu chart với dữ liệu API cho cùng bộ lọc; không có giá mặc định hoặc dữ liệu
demo khi API lỗi; tải lại trang và đổi thị trường không giữ nhầm candles cũ.

### Giai đoạn 4 — Market Structure và Candlestick

**Mục tiêu:** triển khai các phép phân tích xác định trước khi bổ sung mô hình AI.

- Chốt định nghĩa swing high/low, HH/HL/LH/LL, BOS và CHoCH trong `docs/strategy-definitions.md`:
  lookback, xử lý giá bằng nhau, đóng nến hay wick, điều kiện xác nhận và vô hiệu hóa.
- Bắt đầu với một bộ quy tắc nhỏ, sau đó thêm pattern candlestick được định nghĩa cụ thể,
  chẳng hạn Doji hoặc Engulfing; thresholds phải cấu hình được và được ghi trong kết quả.
- Viết domain rules dưới dạng hàm thuần, độc lập HTTP, database và provider.
- Kết quả chứa symbol/timeframe, các nến liên quan, event time, confirmation time,
  phiên bản quy tắc, tham số và lý do phát hiện; không tự gán xác suất thành công.
- Chỉ cung cấp tín hiệu đã xác nhận cho luồng đánh giá; candidate phải có nhãn riêng.
- Thêm API phân tích và overlay tương ứng lên chart, giới hạn độ dài dữ liệu đầu vào.

**Vị trí thực hiện:** `backend/app/modules/market_structure`, `backend/app/modules/candlestick`,
`backend/tests` và `frontend/src/features/analysis`.

**Kiểm thử:** chuỗi tăng/giảm/đi ngang, giá bằng nhau, dữ liệu quá ngắn, gaps và nến chưa đóng.
Thêm kiểm tra từng prefix của chuỗi dữ liệu để bảo đảm detector không dùng nến tương lai.
Fixture tổng hợp chỉ dùng trong test và phải được ghi rõ là dữ liệu kiểm thử.

**Nghiệm thu:** cùng dữ liệu và tham số luôn cho cùng kết quả; mọi nhãn có lý do và thời điểm xác nhận;
không đưa sự kiện lên chart như đã biết trước thời điểm hệ thống có thể xác nhận.

### Giai đoạn 5 — SMC, ICT và Chart Patterns

**Mục tiêu:** mở rộng phân tích theo quy tắc có thể kiểm chứng, tránh nhãn diễn giải mơ hồ.

- Chốt riêng định nghĩa và phiên bản cho liquidity sweep, equal highs/lows, FVG, order block,
  session windows và từng chart pattern được chọn; không coi SMC/ICT là bộ chuẩn thống nhất.
- Triển khai lần lượt từng detector, ghi rõ dữ liệu cần có, điều kiện xác nhận, mitigation,
  invalidation và giới hạn của thuật toán.
- ICT session rules phải khai báo timezone và xử lý daylight saving khi áp dụng.
- Với chart patterns, tách candidate khỏi confirmed pattern và quy định tolerance/minimum lookback.
- Tái sử dụng public contract của market_data/market_structure; không truy vấn trực tiếp bảng nội bộ
  của module khác. Dùng các thư mục `smc`, `ict`, `chart_patterns` hiện có.
- Nếu thêm `confluence` và `decision_support`, công bố cách tổng hợp, trọng số và tín hiệu xung đột;
  điểm tổng hợp không được trình bày như xác suất thắng nếu chưa được hiệu chỉnh và đánh giá.
- Bổ sung overlay, bộ lọc detector và giải thích trên giao diện.

**Kiểm thử:** ví dụ đúng/sai theo tài liệu quy tắc, trường hợp biên, session/DST,
invalidation và kiểm tra không lookahead cho từng detector.

**Nghiệm thu:** mỗi detector có định nghĩa, unit test và ví dụ đối chiếu trên dữ liệu có nguồn;
người dùng phân biệt được candidate/confirmed/invalidated; không công bố hiệu quả giao dịch khi chưa backtest.

### Giai đoạn 6 — Backtesting và đánh giá chiến lược

**Mục tiêu:** đo kết quả mô phỏng lịch sử một cách tái lập trước khi dùng dữ liệu mới.

- Xây engine theo trình tự thời gian trong `backend/app/modules/backtesting`, tách chiến lược
  khỏi execution simulator và nguồn dữ liệu.
- Chốt contract chiến lược: entry/exit, position sizing, stop loss/take profit, giới hạn vị thế
  và cách xử lý tín hiệu trùng/xung đột; tín hiệu chỉ khả dụng từ confirmation time.
- Quy định thời điểm khớp lệnh, phí, spread/slippage; thêm funding nếu mô phỏng sản phẩm cần funding.
  Nếu cùng một nến chạm stop loss và take profit mà không biết thứ tự, phải dùng giả định công khai.
- Lưu cấu hình run, snapshot hoặc định danh phiên bản dataset, phiên bản code/quy tắc,
  seed nếu có ngẫu nhiên, danh sách lệnh mô phỏng và lý do giao dịch.
- Tính equity curve, drawdown, return, số giao dịch, win rate, expectancy, profit factor
  và benchmark; xử lý rõ trường hợp không có giao dịch hoặc mẫu số bằng không.
- Tách dữ liệu theo thời gian, dùng validation/walk-forward khi phù hợp; không tối ưu tham số
  trên tập test rồi báo kết quả đó là ngoài mẫu.
- Thêm API chạy/đọc kết quả và giao diện báo cáo. Chỉ bổ sung background job khi thời gian chạy
  thực tế yêu cầu; không chặn request HTTP bằng tác vụ dài không giới hạn.

**Kiểm thử:** kịch bản tính tay cho khớp lệnh, phí, equity/drawdown, tín hiệu đến muộn,
gaps, vốn không đủ và tình huống thứ tự khớp lệnh không xác định.

**Nghiệm thu:** chạy lại với cùng đầu vào cho cùng kết quả; không khớp trước confirmation time;
báo cáo có giả định, chi phí, giai đoạn đánh giá và cảnh báo giới hạn dữ liệu cụ thể.
Giai đoạn hoàn tất khi engine đúng và tái lập được, không yêu cầu chiến lược phải có lợi nhuận.

### Giai đoạn 7 — Predictions và pipeline AI

**Mục tiêu:** xây baseline có bằng chứng đánh giá trước khi mở rộng mô hình phức tạp.

- Chọn bài toán cụ thể: mục tiêu dự đoán, horizon, thời điểm dự đoán, nhãn và thước đo;
  xác định mẫu dữ liệu đủ dùng thay vì huấn luyện trên tập quá nhỏ rồi công bố độ chính xác.
- Tách feature engineering, labels, datasets, training và evaluation trong các thư mục `backend/ml` hiện có.
  Feature chỉ sử dụng dữ liệu khả dụng tại thời điểm inference.
- Bắt đầu bằng baseline đơn giản và benchmark; fit scaler/feature selection chỉ trên tập train.
- Chia train/validation/test theo thời gian; xử lý overlap của label horizon bằng gap/purging phù hợp;
  giữ test cuối độc lập và kiểm soát leakage trong toàn pipeline.
- Chọn metric phù hợp bài toán, đánh giá calibration nếu xuất xác suất, hiệu quả sau chi phí nếu
  chuyển dự đoán thành chiến lược; so sánh với baseline trên cùng tập đánh giá.
- Lưu model artifact tin cậy, feature schema, phiên bản dataset/model, tham số và báo cáo đánh giá;
  không tải model artifact không rõ nguồn vào tiến trình ứng dụng.
- Tạo inference service trong `backend/app/modules/predictions`; API trả data cutoff, horizon,
  model version và uncertainty khi đã có phương pháp đo hợp lệ.
- Khi thiếu model, dữ liệu cũ hoặc feature không tương thích, trả lỗi/trạng thái rõ ràng;
  không phát sinh score ngẫu nhiên để lấp giao diện.

**Kiểm thử:** tính feature/label, ranh giới thời gian, chống leakage, khả năng tái lập,
model loading, schema mismatch, missing model và inference trên tập đánh giá cố định.

**Nghiệm thu:** có pipeline tái lập và báo cáo ngoài mẫu so với baseline. Nếu mô hình không tốt hơn
baseline, ghi rõ kết quả và giữ trạng thái thử nghiệm; không diễn giải accuracy thành xác suất sinh lời.

### Giai đoạn 8 — Paper Trading và Monitoring

**Mục tiêu:** quan sát chiến lược trên dữ liệu mới bằng tài khoản mô phỏng hoàn toàn.

- Tạo portfolio, số dư, vị thế, lệnh và fills mô phỏng trong `backend/app/modules/paper_trading`;
  không kết nối API đặt lệnh thật và không yêu cầu khóa có quyền giao dịch.
- Dùng cùng contract tín hiệu và mô hình chi phí của backtesting; phân biệt số dư/equity mô phỏng
  với giá thị trường lấy từ provider thật trên mọi màn hình liên quan.
- Lưu trạng thái để restart không mất vị thế hoặc xử lý trùng một sự kiện; quy định cách resume,
  reset tài khoản mô phỏng, xử lý dữ liệu đến muộn và dữ liệu thị trường bị gián đoạn.
- Thêm giới hạn vị thế/mức lỗ và nút dừng mô phỏng; theo dõi latency, data freshness,
  gaps, lỗi ingestion, lỗi inference và sai lệch so với giả định backtest.
- Thêm lịch chạy ingestion/inference khi cần, với khóa chống chạy trùng, retry có giới hạn,
  log và lịch sử job trong cấu trúc ứng dụng hiện tại.
- Làm dashboard so sánh paper results và backtest; chỉ thêm kênh cảnh báo ngoài ứng dụng
  khi có cấu hình và yêu cầu cụ thể.

**Kiểm thử:** vòng đời lệnh/vị thế, accounting, phí, event trùng, restart/resume,
mất nguồn dữ liệu, kích hoạt giới hạn rủi ro và dừng mô phỏng.

**Nghiệm thu:** đối chiếu được số dư/vị thế từ lịch sử sự kiện; chạy qua khoảng quan sát đã thỏa thuận,
không xử lý trùng sau restart; mọi giao dịch và kết quả được gắn nhãn mô phỏng.

### Giai đoạn 9 — Triển khai, bảo vệ truy cập và vận hành

**Mục tiêu:** đưa nền tảng nghiên cứu lên môi trường dùng được và có thể phục hồi.
Các yêu cầu bảo vệ truy cập phải thực hiện trước khi công khai hệ thống, kể cả khi triển khai
sớm hơn thứ tự roadmap này.

- Chuẩn bị cấu hình/container build cần thiết trong `infra/docker` và môi trường staging;
  tách cấu hình development/staging/production, quản lý secrets ngoài repository.
- Chọn cơ chế đăng nhập và phân quyền phù hợp trước khi mở endpoint ingestion, backtest job,
  thay đổi cấu hình hoặc truy cập portfolio; kiểm thử truy cập không được phép.
- Cấu hình HTTPS, CORS đúng domain, giới hạn request/payload và tài nguyên job, timeout,
  database connection pool và quyền database tối thiểu.
- Mở rộng CI cho PostgreSQL integration test, migration và các luồng frontend/backend quan trọng;
  không gọi provider thật bắt buộc trong mọi lần CI.
- Xây quy trình deploy: kiểm tra backup, chạy migration có kiểm soát, smoke test, theo dõi lỗi;
  có kế hoạch rollback ứng dụng và migration tương thích, không giả định downgrade luôn an toàn.
- Thiết lập backup PostgreSQL và kiểm tra restore; xác định mức mất dữ liệu và thời gian phục hồi chấp nhận được.
- Theo dõi health/readiness, lỗi, latency, disk/database growth, ingestion lag và model/data drift nếu có;
  ghi hướng dẫn xử lý sự cố, retention và chi phí vận hành.

**Vị trí thực hiện:** `infra`, `.github/workflows`, cấu hình ứng dụng và tài liệu vận hành trong `docs`.

**Nghiệm thu:** deploy staging từ mã nguồn sạch, test truy cập và smoke test đạt; restore backup
thành công; diễn tập rollback ứng dụng và xử lý DB/provider offline; không có secrets trong Git.
Giao dịch bằng tiền thật vẫn nằm ngoài phạm vi dự án này.

### Quy trình bàn giao sau mỗi giai đoạn

- Báo cáo file tạo/chỉnh sửa và chức năng của từng file, kèm migration và thay đổi contract nếu có.
- Bổ sung lệnh cài đặt/chạy/test trong VS Code đã được thực thi; lệnh mới chưa triển khai
  không được trình bày như đang sử dụng được.
- Ghi kết quả thực tế: test đạt/thất bại/bỏ qua, dữ liệu dùng để kiểm tra, phiên bản môi trường
  và những phần chưa kiểm chứng bằng provider hoặc PostgreSQL thật.
- Cập nhật `.env.example`, tài liệu API, README, roadmap và trạng thái module chỉ khi hành vi
  tương ứng đã được triển khai và kiểm thử; phân biệt rõ trạng thái một phần và hoàn tất.
- Nêu giới hạn, vấn đề còn mở, cách tái hiện và công việc kế tiếp; không tự chuyển sang
  giao dịch tiền thật hoặc trình bày dữ liệu kiểm thử như dữ liệu thị trường.

**Việc nên làm ngay:** hoàn tất PostgreSQL thật của Giai đoạn 1, sau đó triển khai Giai đoạn 2
với một provider, một loại thị trường và một phạm vi symbol/timeframe được chốt rõ để nghiệm thu.
