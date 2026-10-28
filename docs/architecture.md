# Architecture

Modular Monolith: một FastAPI deployable và một PostgreSQL, frontend Next.js giao tiếp
qua API `/api/v1`. Không thêm microservices, queue, ORM frontend hoặc thư viện HTTP riêng.

## Luồng phụ thuộc

HTTP router -> application service -> domain rules / ports -> infrastructure adapters.
Domain rules không import FastAPI, SQLAlchemy hoặc exchange SDK. Service nhận dependency
qua constructor hoặc tham số, không tự tạo provider hay đọc env. Router chịu trách nhiệm
HTTP validation và dependency injection. Settings và database session là foundation chung.

Mỗi module có README nêu trách nhiệm và contract; chỉ thêm schemas/domain/service/ports/router/models
khi có chức năng thật. Không thêm file rỗng giả vờ hoàn thiện. API registry chỉ công bố trạng thái.
Cross-module gọi public service/contract, không truy vấn trực tiếp bảng nội bộ module khác.

## Các ranh giới nghiệp vụ (đều chưa triển khai)

| Module | Đầu vào dự kiến | Đầu ra / trách nhiệm |
|---|---|---|
| market_data | Provider lịch sử có nguồn và thời gian thu thập | OHLCV hợp lệ, UTC, closed candles, kiểm tra trùng/lỗ hổng |
| market_structure | Candles hợp lệ | Swing/BOS/CHoCH có thời điểm xác nhận và phiên bản quy tắc |
| smc | Candles và structure đã xác nhận | Liquidity/order block/imbalance theo định nghĩa cụ thể |
| ict | Candles, structure, timezone và session config | Sự kiện nghiên cứu ICT theo quy tắc phiên bản hóa |
| candlestick | Candles và thresholds | Pattern xác định bằng hàm thuần |
| chart_patterns | Chuỗi candles/structure | Candidate, confirmation, invalidation tách biệt |
| predictions | Feature đã version, model artifact | Dự đoán, uncertainty, data cutoff và model version |
| backtesting | Candles lịch sử, tín hiệu có confirmation time | Trades mô phỏng, fees/slippage, metrics và cấu hình tái lập |

Không module nào mặc định phát sinh lệnh giao dịch thật. Các thư mục confluence,
decision_support, indicators, paper_trading và ml hiện giữ nguyên placeholder.

## Dữ liệu và kiểm định

Dữ liệu tương lai phải có source, symbol, timeframe, UTC timestamps và trạng thái đóng nến.
Giá/khối lượng dùng Decimal ở domain/storage; không dùng binary float làm giá lưu trữ chuẩn.
Không forward-fill OHLCV như thể provider đã cung cấp; ghi rõ missing/partial candles.
Detector phải ghi thời điểm phát hiện và xác nhận riêng để tránh lookahead.
Prediction/backtest tách tập dữ liệu theo thời gian; không công bố metric khi chưa chạy evaluation.

SQLAlchemy Base giữ metadata chung. Khi thêm model, import tường minh vào Alembic env,
review migration và kiểm tra upgrade trên PostgreSQL. Không dùng create_all thay migration.
Secrets lấy từ môi trường, không commit .env. CORS chỉ cho phép origins được cấu hình.
