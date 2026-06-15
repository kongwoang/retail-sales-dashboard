# 📊 Retail Sales Dashboard — Dashboard Phân Tích Doanh Số Bán Lẻ

Ứng dụng web chạy **local** bằng **Streamlit** giúp phân tích dữ liệu bán hàng:
upload file CSV/Excel → hiển thị bảng → thống kê → vẽ biểu đồ tương tác →
lưu trữ vào SQLite và chạy truy vấn SQL.

> Bạn **không cần biết lập trình** vẫn dùng được. Hướng dẫn bên dưới viết theo
> kiểu "máy tính chưa cài gì cả", làm tuần tự từ trên xuống là chạy được.

---

## ✨ Tính năng chính

- **Upload file** CSV / Excel (`.csv`, `.xlsx`, `.xls`) hoặc dùng **dữ liệu mẫu** có sẵn.
- **Làm sạch dữ liệu** tự động: chuẩn hoá tên cột, ép kiểu số, chuyển `Date`
  sang ngày tháng, tự tính `Revenue = Quantity × Unit Price` khi thiếu.
- **Thẻ tổng quan**: tổng doanh thu, số đơn hàng, số sản phẩm bán ra, số khách hàng.
- **Tab Thống kê**: kiểu dữ liệu, giá trị thiếu, dòng trùng, mô tả thống kê,
  Top 10 theo sản phẩm / danh mục / khu vực.
- **Tab Biểu đồ** (Plotly): bar, pie, line theo thời gian, histogram và
  **biểu đồ tùy chỉnh** (Bar / Line / Scatter / Pie / Histogram).
- **Tab SQLite**: lưu vào `sales_dashboard.db`, xem bảng, chạy SQL query (có sẵn query mẫu).
- **Export**: tải CSV đã xử lý và tải file SQLite `.db`.
- **Không crash**: file sai định dạng/rỗng/thiếu cột hoặc SQL sai cú pháp đều
  hiện thông báo thân thiện.

## 🛠️ Công nghệ sử dụng

Python · Streamlit · Pandas · Plotly · SQLite (sqlite3) · OpenPyXL

## 📂 Cấu trúc thư mục

```
retail-sales-dashboard/
├── app.py                  # Code chính của ứng dụng
├── sample_sales_data.csv   # Dữ liệu mẫu (150 dòng)
├── generate_sample.py      # Script sinh lại dữ liệu mẫu (tùy chọn)
├── sales_dashboard.db      # Tự tạo khi chạy app (không có sẵn trong repo)
├── requirements.txt        # Danh sách thư viện cần cài
└── README.md
```

---

# 🚀 HƯỚNG DẪN CHẠY

> Yêu cầu: máy đã có sẵn **Python 3.9+** và mã nguồn dự án (clone hoặc tải ZIP
> từ <https://github.com/kongwoang/retail-sales-dashboard>). Mở terminal/PowerShell
> và `cd` vào thư mục `retail-sales-dashboard` trước khi chạy các lệnh dưới đây.

## Bước 1 — Cài thư viện

```bash
pip install -r requirements.txt
```
Lần đầu có thể mất 1–3 phút để tải Streamlit, Pandas, Plotly, OpenPyXL.

> Trên macOS/Linux nếu `pip` không chạy, thử `pip3`.

## Bước 2 — Chạy ứng dụng

```bash
streamlit run app.py
```
Trình duyệt sẽ tự mở. Nếu không, hãy mở thủ công:

👉 <http://localhost:8501>

Để **dừng** app: quay lại terminal và bấm `Ctrl + C`.

---

# 🧭 HƯỚNG DẪN SỬ DỤNG TRONG APP

1. **Nạp dữ liệu** (cột bên trái – sidebar):
   - Bấm **“Load dữ liệu mẫu”** để dùng ngay dữ liệu giả lập, **hoặc**
   - Bấm **Browse files** để upload file `.csv` / `.xlsx` / `.xls` của bạn.
2. **Tab 📋 Dữ liệu** — xem tên nguồn, số dòng/cột và toàn bộ bảng dữ liệu.
3. **Tab 📊 Thống kê** — kiểu dữ liệu, giá trị thiếu, dòng trùng, mô tả thống
   kê và bảng Top 10 theo doanh thu.
4. **Tab 📈 Biểu đồ** — xem các biểu đồ mặc định, hoặc dùng phần
   **“Tạo biểu đồ tùy chỉnh”** để tự chọn cột X, Y và loại biểu đồ.
5. **Tab 🗄️ SQLite** — dữ liệu đã được lưu vào `sales_dashboard.db`. Bạn có thể:
   - Xem danh sách bảng và preview;
   - Chọn **query mẫu** hoặc tự gõ SQL rồi bấm **Run Query**;
   - **Tải CSV đã xử lý** hoặc **tải file SQLite `.db`**.
6. **Tab 📖 Hướng dẫn** — tóm tắt các bước ngay trong app.

---

## 📝 Lưu ý khi dùng dữ liệu riêng

- Gợi ý các cột: `Order ID`, `Date`, `Product`, `Category`, `Region`,
  `Quantity`, `Unit Price`, `Revenue`, `Customer`.
- App vẫn hoạt động với file khác miễn là có **cột số** và **cột chữ**; chức
  năng nào thiếu cột tương ứng sẽ hiện thông báo thay vì lỗi.
- Thiếu `Revenue` nhưng có `Quantity` + `Unit Price` → app **tự tính** `Revenue`.
- Mỗi lần nạp dữ liệu mới, bảng `sales_data` sẽ bị **ghi đè**; bảng
  `upload_logs` lưu lại lịch sử các lần nạp.

## ❓ Khắc phục sự cố thường gặp

| Triệu chứng | Cách xử lý |
|-------------|-----------|
| `pip` không nhận diện được | Thử `pip3` (macOS/Linux), hoặc `python -m pip install -r requirements.txt`. |
| `streamlit: command not found` | Chưa cài thư viện. Chạy lại Bước 1, hoặc dùng `python -m streamlit run app.py`. |
| Cổng 8501 đang bận | Chạy `streamlit run app.py --server.port 8600`. |
| Đọc Excel báo lỗi | Đảm bảo đã cài `openpyxl` (đã nằm trong `requirements.txt`). |

## 🔁 Tạo lại dữ liệu mẫu (tùy chọn)

```bash
python generate_sample.py
```
Lệnh này ghi đè `sample_sales_data.csv` với 150 dòng dữ liệu giả lập mới.
