"""
Script tạo file dữ liệu mẫu y tế Việt Nam: sample_health_data.csv (>= 150 dòng).

Mô phỏng dữ liệu KHÁM CHỮA BỆNH & VIỆN PHÍ tại một phòng khám/bệnh viện đa khoa.
Mỗi dòng = một lượt sử dụng dịch vụ y tế của bệnh nhân (kèm viện phí).
"""
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# Khoa -> danh sách (Dịch vụ, đơn giá cơ sở - VND)
departments = {
    "Khoa Nội": [
        ("Khám nội tổng quát", 150_000),
        ("Điện tim (ECG)", 120_000),
        ("Tư vấn nội tiết - đái tháo đường", 200_000),
    ],
    "Khoa Ngoại": [
        ("Khám ngoại", 150_000),
        ("Tiểu phẫu", 800_000),
        ("Thay băng - cắt chỉ", 100_000),
    ],
    "Khoa Sản - Phụ khoa": [
        ("Khám thai định kỳ", 200_000),
        ("Siêu âm thai 4D", 350_000),
        ("Khám phụ khoa", 250_000),
    ],
    "Khoa Nhi": [
        ("Khám nhi", 150_000),
        ("Tiêm chủng vắc-xin", 300_000),
        ("Khí dung", 120_000),
    ],
    "Khoa Răng - Hàm - Mặt": [
        ("Khám răng", 100_000),
        ("Nhổ răng", 500_000),
        ("Trám răng", 400_000),
        ("Cạo vôi răng", 300_000),
    ],
    "Khoa Tai - Mũi - Họng": [
        ("Nội soi tai mũi họng", 350_000),
        ("Khám tai mũi họng", 150_000),
    ],
    "Khoa Mắt": [
        ("Khám mắt", 150_000),
        ("Đo thị lực", 80_000),
    ],
    "Khoa Da liễu": [
        ("Khám da liễu", 200_000),
        ("Điều trị laser", 600_000),
    ],
    "Khoa Xét nghiệm": [
        ("Xét nghiệm máu", 250_000),
        ("Xét nghiệm nước tiểu", 120_000),
        ("Xét nghiệm sinh hóa", 400_000),
    ],
    "Chẩn đoán hình ảnh": [
        ("Chụp X-quang", 200_000),
        ("Siêu âm ổ bụng", 250_000),
        ("Chụp CT-Scanner", 1_500_000),
        ("Chụp cộng hưởng từ (MRI)", 2_500_000),
    ],
    "Khoa Tim mạch": [
        ("Khám tim mạch", 250_000),
        ("Siêu âm tim", 400_000),
        ("Holter điện tim 24h", 700_000),
    ],
}

provinces = [
    "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
    "Nghệ An", "Thanh Hóa", "Bình Dương", "Đồng Nai", "Khánh Hòa",
    "Quảng Ninh", "Lâm Đồng",
]

# Tạo danh sách bệnh nhân giả lập
patients = [f"BN{idx:04d}" for idx in range(1, 71)]

rows = []
start_date = datetime(2024, 1, 1)
for i in range(1, 211):  # 210 lượt khám
    department = random.choice(list(departments.keys()))
    service, base_price = random.choice(departments[department])
    # Số lượng đơn vị dịch vụ (đa số là 1)
    quantity = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
    # Đơn giá dao động +-5%, làm tròn tới nghìn đồng
    unit_price = round(base_price * random.uniform(0.95, 1.05) / 1000) * 1000
    total = quantity * unit_price
    visit_date = start_date + timedelta(days=random.randint(0, 364))
    rows.append({
        "Mã khám": f"KB{i:05d}",
        "Ngày khám": visit_date.strftime("%Y-%m-%d"),
        "Bệnh nhân": random.choice(patients),
        "Khoa": department,
        "Dịch vụ": service,
        "Tỉnh/Thành": random.choice(provinces),
        "Số lượng": quantity,
        "Đơn giá": unit_price,
        "Viện phí": total,
    })

fields = ["Mã khám", "Ngày khám", "Bệnh nhân", "Khoa", "Dịch vụ",
          "Tỉnh/Thành", "Số lượng", "Đơn giá", "Viện phí"]
with open("sample_health_data.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Da tao sample_health_data.csv voi {len(rows)} dong.")
