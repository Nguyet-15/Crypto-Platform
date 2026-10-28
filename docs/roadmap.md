# Roadmap

1. Foundation: cấu hình, API client, health/readiness, logging/errors, Alembic baseline và tests.
2. Market data: xác định provider, schema OHLCV, migration, pagination, provenance và integration tests.
3. Chart hiển thị dữ liệu thật, thông báo missing/partial candles và lỗi provider rõ ràng.
4. Market structure và candlestick: chốt quy tắc, confirmation time, fixtures và unit tests.
5. SMC/ICT/chart patterns: định nghĩa phiên bản hóa, invalidation và kiểm tra không lookahead.
6. Backtesting: time split, fees/slippage, kết quả tái lập và benchmark.
7. Predictions: baseline, calibration, uncertainty, model version và out-of-sample evaluation.
8. Paper trading và monitoring; không triển khai giao dịch tiền thật trong phạm vi hiện tại.
