# Roadmap

Kế hoạch chi tiết, công việc, kiểm thử và tiêu chí nghiệm thu của từng giai đoạn được
duy trì tại [Lộ trình phát triển đầy đủ trong README](../README.md#lộ-trình-phát-triển-đầy-đủ).
README là nguồn kế hoạch chính để tránh hai tài liệu mô tả khác nhau.

| Giai đoạn | Phạm vi | Trạng thái |
|---|---|---|
| 1 | Foundation, API client, logging/errors, Alembic, PostgreSQL | Đã có mã nguồn; còn nghiệm thu PostgreSQL thật |
| 2 | Provider, OHLCV thật, ingestion, validation và lưu trữ | Chưa triển khai |
| 3 | Chart và dashboard dữ liệu thật | Chưa triển khai |
| 4 | Market structure và candlestick detectors | Chưa triển khai |
| 5 | SMC, ICT, chart patterns và giải thích kết quả | Chưa triển khai |
| 6 | Backtesting có chi phí và kiểm soát lookahead | Chưa triển khai |
| 7 | Predictions, baseline và đánh giá ngoài mẫu | Chưa triển khai |
| 8 | Paper trading, lịch chạy và monitoring | Chưa triển khai |
| 9 | Staging, bảo vệ truy cập, CI, backup/restore và vận hành | Chưa triển khai |

Giữ nguyên Modular Monolith và các thư mục hiện có. Yêu cầu bảo vệ truy cập phải hoàn tất
trước khi công khai hệ thống, kể cả khi triển khai sớm hơn thứ tự trên.
Không có giao dịch bằng tiền thật trong phạm vi roadmap này.
