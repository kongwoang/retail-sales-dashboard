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

# 🚀 HƯỚNG DẪN CHẠY TỪ ĐẦU (chưa cài gì cả)

## Bước 0 — Cài đặt Python

Ứng dụng cần **Python 3.9 trở lên** (khuyến nghị 3.11 hoặc 3.12).

### Windows
1. Vào <https://www.python.org/downloads/> → tải bản Python mới nhất.
2. Chạy file cài đặt. **QUAN TRỌNG:** tích vào ô **“Add Python to PATH”** ở
   màn hình đầu tiên, rồi bấm **Install Now**.
3. Mở **PowerShell** (gõ `powershell` ở ô tìm kiếm Windows) và kiểm tra:
   ```powershell
   python --version
   ```
   Nếu hiện ra ví dụ `Python 3.12.x` là đã cài thành công.

### macOS
```bash
brew install python      # nếu đã có Homebrew
python3 --version
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
python3 --version
```

> Nếu lệnh `python` không chạy, thử `python3`. Trên Windows dùng `python`,
> trên macOS/Linux thường là `python3`.

## Bước 1 — Cài Git (nếu chưa có) và tải mã nguồn

### Cách A — Dùng Git (khuyến nghị)
1. Cài Git tại <https://git-scm.com/downloads> (Windows tích chọn mặc định là được).
2. Clone repo về máy:
   ```bash
   git clone https://github.com/kongwoang/retail-sales-dashboard.git
   cd retail-sales-dashboard
   ```

### Cách B — Tải ZIP (không cần Git)
1. Vào <https://github.com/kongwoang/retail-sales-dashboard>.
2. Bấm nút xanh **Code → Download ZIP**, giải nén ra một thư mục.
3. Mở terminal/PowerShell và `cd` vào thư mục vừa giải nén.

## Bước 2 — Tạo môi trường ảo (virtual environment)

Giúp cách ly thư viện, không ảnh hưởng Python hệ thống.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> Nếu báo lỗi *“running scripts is disabled”*, chạy lệnh sau một lần rồi
> activate lại:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Khi thành công, đầu dòng lệnh sẽ có chữ `(venv)`.

## Bước 3 — Cài thư viện

```bash
pip install -r requirements.txt
```
Lần đầu có thể mất 1–3 phút để tải Streamlit, Pandas, Plotly, OpenPyXL.

## Bước 4 — Chạy ứng dụng

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
| `python` / `pip` không nhận diện được | Cài lại Python và nhớ tích **Add Python to PATH**; thử `python3`/`pip3`. |
| `streamlit: command not found` | Chưa activate venv hoặc chưa cài. Chạy lại Bước 2 & 3. |
| PowerShell chặn `Activate.ps1` | Chạy `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` rồi thử lại. |
| Cổng 8501 đang bận | Chạy `streamlit run app.py --server.port 8600`. |
| Đọc Excel báo lỗi | Đảm bảo đã cài `openpyxl` (đã nằm trong `requirements.txt`). |

## 🔁 Tạo lại dữ liệu mẫu (tùy chọn)

```bash
python generate_sample.py
```
Lệnh này ghi đè `sample_sales_data.csv` với 150 dòng dữ liệu giả lập mới.
