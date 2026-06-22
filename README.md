# 🏥 Health Dashboard — Dashboard Phân Tích Dữ Liệu Khám Chữa Bệnh

Ứng dụng web chạy **local** bằng **Streamlit** giúp phân tích dữ liệu
**khám chữa bệnh & viện phí** tại một phòng khám/bệnh viện đa khoa ở Việt Nam:
upload file CSV/Excel → hiển thị bảng (tô màu) → thống kê → vẽ biểu đồ tương
tác → lưu trữ vào SQLite và chạy truy vấn SQL.

> Giao diện **theme sáng**, bảng dữ liệu được **tô màu gradient pastel** giúp
> đọc số liệu trực quan hơn. Bạn không cần biết lập trình vẫn dùng được.

---

## 📑 Mục lục

1. [Tính năng chính](#-tính-năng-chính)
2. [Công nghệ sử dụng](#️-công-nghệ-sử-dụng)
3. [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
4. [📊 Dữ liệu — TẤT TẦN TẬT (đọc kỹ để viết báo cáo)](#-dữ-liệu--tất-tần-tật)
5. [Hướng dẫn chạy](#-hướng-dẫn-chạy)
6. [Hướng dẫn sử dụng trong app](#-hướng-dẫn-sử-dụng-trong-app)
7. [Gợi ý phân tích cho báo cáo](#-gợi-ý-phân-tích-cho-báo-cáo)
8. [Dùng dữ liệu riêng & khắc phục sự cố](#-lưu-ý-khi-dùng-dữ-liệu-riêng)

---

## ✨ Tính năng chính

- **Upload file** CSV / Excel (`.csv`, `.xlsx`, `.xls`) hoặc dùng **dữ liệu mẫu** y tế có sẵn.
- **Làm sạch dữ liệu** tự động: chuẩn hoá tên cột, ép kiểu số, chuyển `Ngày khám`
  sang kiểu ngày tháng, tự tính `Viện phí = Số lượng × Đơn giá` khi thiếu.
- **Thẻ tổng quan**: tổng viện phí, tổng lượt khám, tổng lượt dịch vụ, số bệnh nhân.
- **Tab Thống kê**: kiểu dữ liệu, giá trị thiếu, dòng trùng, mô tả thống kê,
  Top 10 theo dịch vụ / khoa / tỉnh thành.
- **Tab Biểu đồ** (Plotly): bar, pie (donut), line theo thời gian, histogram và
  **biểu đồ tùy chỉnh** (Bar / Line / Scatter / Pie / Histogram).
- **Tab SQLite**: lưu vào `health_dashboard.db`, xem bảng, chạy SQL query (có sẵn query mẫu).
- **Export**: tải CSV đã xử lý và tải file SQLite `.db`.
- **Bảng tô màu** gradient pastel + định dạng tiền VND (`₫`), theme sáng.
- **Không crash**: file sai định dạng/rỗng/thiếu cột hoặc SQL sai cú pháp đều
  hiện thông báo thân thiện.

## 🛠️ Công nghệ sử dụng

Python · Streamlit · Pandas · Plotly · SQLite (sqlite3) · OpenPyXL

## 📂 Cấu trúc thư mục

```
retail-sales-dashboard/
├── app.py                   # Code chính của ứng dụng
├── sample_health_data.csv   # Dữ liệu mẫu y tế (210 dòng)
├── generate_sample.py       # Script sinh lại dữ liệu mẫu (tùy chọn)
├── health_dashboard.db      # SQLite tự tạo khi chạy app (không có sẵn trong repo)
├── .streamlit/
│   └── config.toml          # Cấu hình theme sáng (màu y tế)
├── requirements.txt         # Danh sách thư viện cần cài
└── README.md
```

---

## 📊 Dữ liệu — TẤT TẦN TẬT

### 1. Bối cảnh & ý nghĩa

Bộ dữ liệu mô phỏng hoạt động **khám chữa bệnh tại một bệnh viện/phòng khám đa
khoa ở Việt Nam**. **Mỗi dòng = một lượt sử dụng dịch vụ y tế** của một bệnh
nhân, kèm chi phí (viện phí) tương ứng. Đây là dạng dữ liệu giao dịch
(transaction-level), phù hợp để phân tích doanh thu dịch vụ, cơ cấu khám chữa
bệnh theo khoa, theo địa lý và theo thời gian.

File mẫu: **`sample_health_data.csv`** — **210 dòng**, **9 cột**, mã hoá
`UTF-8` (có BOM), dữ liệu trải dài năm **2024**.

### 2. Từ điển dữ liệu (Data Dictionary)

| # | Tên cột | Kiểu dữ liệu | Vai trò (role) | Ý nghĩa | Ví dụ |
|---|---------|--------------|----------------|---------|-------|
| 1 | `Mã khám` | Chuỗi (text) | `id` | Mã định danh duy nhất của mỗi lượt khám | `KB00001` |
| 2 | `Ngày khám` | Ngày (datetime) | `date` | Ngày bệnh nhân sử dụng dịch vụ | `2024-04-24` |
| 3 | `Bệnh nhân` | Chuỗi (text) | `entity` | Mã bệnh nhân (ẩn danh) | `BN0018` |
| 4 | `Khoa` | Chuỗi (text) | `group` | Khoa/chuyên khoa cung cấp dịch vụ | `Khoa Tim mạch` |
| 5 | `Dịch vụ` | Chuỗi (text) | `item` | Tên dịch vụ y tế cụ thể | `Khám tim mạch` |
| 6 | `Tỉnh/Thành` | Chuỗi (text) | `region` | Tỉnh/thành nơi bệnh nhân cư trú | `Lâm Đồng` |
| 7 | `Số lượng` | Số nguyên (int) | `qty` | Số đơn vị dịch vụ trong lượt khám | `1` |
| 8 | `Đơn giá` | Số nguyên (VND) | `price` | Giá một đơn vị dịch vụ (đồng) | `244000` |
| 9 | `Viện phí` | Số nguyên (VND) | `revenue` | Thành tiền = `Số lượng × Đơn giá` | `244000` |

> **Công thức:** `Viện phí = Số lượng × Đơn giá`. Nếu file của bạn thiếu cột
> `Viện phí` nhưng có `Số lượng` và `Đơn giá`, ứng dụng sẽ **tự tính** cột này.

### 3. Danh mục giá trị (domain values) trong dữ liệu mẫu

**11 Khoa** và các dịch vụ tiêu biểu (đơn giá cơ sở, VND):

| Khoa | Dịch vụ (đơn giá cơ sở) |
|------|--------------------------|
| Khoa Nội | Khám nội tổng quát (150.000), Điện tim ECG (120.000), Tư vấn nội tiết - đái tháo đường (200.000) |
| Khoa Ngoại | Khám ngoại (150.000), Tiểu phẫu (800.000), Thay băng - cắt chỉ (100.000) |
| Khoa Sản - Phụ khoa | Khám thai định kỳ (200.000), Siêu âm thai 4D (350.000), Khám phụ khoa (250.000) |
| Khoa Nhi | Khám nhi (150.000), Tiêm chủng vắc-xin (300.000), Khí dung (120.000) |
| Khoa Răng - Hàm - Mặt | Khám răng (100.000), Nhổ răng (500.000), Trám răng (400.000), Cạo vôi răng (300.000) |
| Khoa Tai - Mũi - Họng | Nội soi TMH (350.000), Khám TMH (150.000) |
| Khoa Mắt | Khám mắt (150.000), Đo thị lực (80.000) |
| Khoa Da liễu | Khám da liễu (200.000), Điều trị laser (600.000) |
| Khoa Xét nghiệm | Xét nghiệm máu (250.000), Nước tiểu (120.000), Sinh hóa (400.000) |
| Chẩn đoán hình ảnh | X-quang (200.000), Siêu âm ổ bụng (250.000), CT-Scanner (1.500.000), MRI (2.500.000) |
| Khoa Tim mạch | Khám tim mạch (250.000), Siêu âm tim (400.000), Holter điện tim 24h (700.000) |

**12 Tỉnh/Thành:** Hà Nội, TP. Hồ Chí Minh, Đà Nẵng, Hải Phòng, Cần Thơ,
Nghệ An, Thanh Hóa, Bình Dương, Đồng Nai, Khánh Hòa, Quảng Ninh, Lâm Đồng.

**Bệnh nhân:** 70 mã bệnh nhân ẩn danh (`BN0001`–`BN0070`).
**Số lượng:** chủ yếu là 1 (≈80%), thỉnh thoảng 2–3.
**Đơn giá:** dao động ±5% quanh đơn giá cơ sở, làm tròn tới nghìn đồng.

### 4. Quy tắc làm sạch dữ liệu (do `clean_data()` thực hiện)

1. **Chuẩn hoá tên cột:** loại bỏ khoảng trắng thừa ở đầu/cuối.
2. **Ngày tháng:** cột `Ngày khám` được ép về kiểu `datetime` (`errors="coerce"`
   → giá trị không hợp lệ thành `NaT`).
3. **Cột số:** `Số lượng`, `Đơn giá`, `Viện phí` ép về kiểu số; ký tự không hợp
   lệ trở thành `NaN` thay vì gây lỗi.
4. **Tự sinh viện phí:** thiếu `Viện phí` mà có `Số lượng` + `Đơn giá` →
   tạo cột mới `Viện phí = Số lượng × Đơn giá`.

### 5. Cơ chế nhận diện cột linh hoạt (role mapping)

App không phụ thuộc cứng vào tên cột — nó ánh xạ **tên cột thực tế** sang
**vai trò (role)** qua danh sách bí danh (tiếng Việt & tiếng Anh), nên vừa hiểu
dữ liệu y tế tiếng Việt, vừa xử lý được file khác:

| Vai trò | Bí danh được chấp nhận |
|---------|------------------------|
| `id` | Mã khám, Mã BN, Order ID, ID, Mã |
| `date` | Ngày khám, Ngày, Date |
| `item` | Dịch vụ, Chẩn đoán, Dịch vụ y tế, Product, Service |
| `group` | Khoa, Chuyên khoa, Category, Department |
| `region` | Tỉnh/Thành, Tỉnh, Khu vực, Region, Province |
| `qty` | Số lượng, SL, Quantity |
| `price` | Đơn giá, Giá, Unit Price |
| `revenue` | Viện phí, Chi phí, Thành tiền, Tổng tiền, Revenue |
| `entity` | Bệnh nhân, Patient, Khách hàng, Customer |

So khớp **không phân biệt hoa/thường và không phân biệt dấu**.

### 6. Cấu trúc cơ sở dữ liệu SQLite (`health_dashboard.db`)

Khi nạp dữ liệu, app tạo 2 bảng:

**Bảng `medical_records`** — toàn bộ dữ liệu đã xử lý. Vì tên cột tiếng Việt có
dấu/khoảng trắng khó dùng trong SQL, app **bỏ dấu & thay khoảng trắng bằng `_`**:

| Cột gốc | Cột trong SQL |
|---------|---------------|
| Mã khám | `Ma_kham` |
| Ngày khám | `Ngay_kham` |
| Bệnh nhân | `Benh_nhan` |
| Khoa | `Khoa` |
| Dịch vụ | `Dich_vu` |
| Tỉnh/Thành | `Tinh_Thanh` |
| Số lượng | `So_luong` |
| Đơn giá | `Don_gia` |
| Viện phí | `Vien_phi` |

> Bảng ánh xạ này cũng hiển thị ngay trong tab **SQLite** (mục “Tên cột trong SQL”).

**Bảng `upload_logs`** — nhật ký các lần nạp dữ liệu:

| Cột | Kiểu | Ý nghĩa |
|-----|------|---------|
| `id` | INTEGER PK | Khoá tự tăng |
| `filename` | TEXT | Tên file đã nạp |
| `upload_time` | TEXT | Thời điểm nạp (`YYYY-MM-DD HH:MM:SS`) |
| `row_count` | INTEGER | Số dòng |
| `column_count` | INTEGER | Số cột |

> Mỗi lần nạp dữ liệu mới, `medical_records` bị **ghi đè**; `upload_logs`
> **cộng dồn** lịch sử.

---

## 🚀 Hướng dẫn chạy

> Yêu cầu: máy đã có sẵn **Python 3.9+** và mã nguồn dự án (clone hoặc tải ZIP
> từ <https://github.com/kongwoang/retail-sales-dashboard>). Mở terminal/PowerShell
> và `cd` vào thư mục dự án trước khi chạy.

### Bước 1 — Cài thư viện

```bash
pip install -r requirements.txt
```
Lần đầu có thể mất 1–3 phút để tải Streamlit, Pandas, Plotly, OpenPyXL.

> Trên macOS/Linux nếu `pip` không chạy, thử `pip3`.

### Bước 2 — Chạy ứng dụng

```bash
streamlit run app.py
```
Trình duyệt sẽ tự mở. Nếu không, hãy mở thủ công: 👉 <http://localhost:8501>

Để **dừng** app: quay lại terminal và bấm `Ctrl + C`.

---

## 🧭 Hướng dẫn sử dụng trong app

1. **Nạp dữ liệu** (sidebar bên trái): bấm **“Load dữ liệu mẫu”** để dùng ngay
   dữ liệu y tế giả lập, **hoặc** bấm **Browse files** để upload file của bạn.
2. **Tab 📋 Dữ liệu** — thông tin nguồn, số dòng/cột và bảng dữ liệu tô màu.
3. **Tab 📊 Thống kê** — kiểu dữ liệu, giá trị thiếu, dòng trùng, mô tả thống kê
   và bảng Top 10 viện phí theo dịch vụ/khoa/tỉnh thành.
4. **Tab 📈 Biểu đồ** — biểu đồ mặc định + công cụ **“Tạo biểu đồ tùy chỉnh”**.
5. **Tab 🗄️ SQLite** — xem bảng, chọn query mẫu hoặc tự gõ SQL, tải CSV / `.db`.
6. **Tab 📖 Hướng dẫn** — tóm tắt các bước ngay trong app.

---

## 💡 Gợi ý phân tích cho báo cáo

Một số câu hỏi/insight bạn có thể trình bày trong báo cáo, kèm cách lấy số liệu:

- **Tổng quan:** Tổng viện phí, tổng lượt khám, tổng lượt dịch vụ, số bệnh nhân
  duy nhất → đọc trực tiếp ở 4 thẻ metric đầu trang.
- **Khoa nào tạo doanh thu cao nhất?** → tab Thống kê “Top 10 khoa”, hoặc SQL:
  ```sql
  SELECT Khoa, SUM(Vien_phi) AS tong_vien_phi
  FROM medical_records GROUP BY Khoa ORDER BY tong_vien_phi DESC;
  ```
- **Dịch vụ chủ lực:** “Top 10 dịch vụ theo viện phí” + biểu đồ bar.
- **Phân bố địa lý:** viện phí theo tỉnh/thành (biểu đồ bar + SQL group by `Tinh_Thanh`).
- **Xu hướng thời gian:** biểu đồ line “Viện phí theo thời gian” → nhận diện
  cao điểm/thấp điểm theo ngày/tháng.
- **Cơ cấu theo khoa:** biểu đồ tròn (donut) “Tỷ trọng viện phí theo khoa”.
- **Phân phối viện phí/đơn giá:** dùng Histogram để xem mức chi phí phổ biến,
  phát hiện các dịch vụ giá cao (CT, MRI) tạo “đuôi dài”.
- **Chất lượng dữ liệu:** số dòng trùng, số giá trị thiếu (tab Thống kê) — nên
  nêu trong phần “Tiền xử lý dữ liệu” của báo cáo.

---

## 📝 Lưu ý khi dùng dữ liệu riêng

- Gợi ý các cột: `Mã khám`, `Ngày khám`, `Bệnh nhân`, `Khoa`, `Dịch vụ`,
  `Tỉnh/Thành`, `Số lượng`, `Đơn giá`, `Viện phí` (xem bảng bí danh ở mục 5 — có
  thể đặt tên khác mà app vẫn nhận diện).
- App vẫn hoạt động với file khác miễn là có **cột số** và **cột chữ**; chức
  năng nào thiếu cột tương ứng sẽ hiện thông báo thay vì lỗi.
- Thiếu `Viện phí` nhưng có `Số lượng` + `Đơn giá` → app **tự tính** `Viện phí`.

## ❓ Khắc phục sự cố thường gặp

| Triệu chứng | Cách xử lý |
|-------------|-----------|
| `pip` không nhận diện được | Thử `pip3` (macOS/Linux), hoặc `python -m pip install -r requirements.txt`. |
| `streamlit: command not found` | Chưa cài thư viện. Chạy lại Bước 1, hoặc `python -m streamlit run app.py`. |
| Cổng 8501 đang bận | Chạy `streamlit run app.py --server.port 8600`. |
| Đọc Excel báo lỗi | Đảm bảo đã cài `openpyxl` (đã có trong `requirements.txt`). |
| File CSV tiếng Việt bị lỗi font | Lưu file ở mã hoá **UTF-8**. |

## 🔁 Tạo lại dữ liệu mẫu (tùy chọn)

```bash
python generate_sample.py
```
Lệnh này ghi đè `sample_health_data.csv` với 210 dòng dữ liệu y tế giả lập mới.
