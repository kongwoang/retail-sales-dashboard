"""Script tạo file dữ liệu mẫu sample_sales_data.csv (>= 100 dòng)."""
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

products = {
    "Electronics": [("Laptop Pro 15", 1200), ("Smartphone X", 800), ("Wireless Earbuds", 120),
                    ("4K Monitor", 350), ("Mechanical Keyboard", 90)],
    "Home": [("Vacuum Cleaner", 220), ("Coffee Maker", 75), ("Air Purifier", 180),
             ("LED Lamp", 40), ("Blender", 60)],
    "Fashion": [("Running Shoes", 110), ("Leather Jacket", 250), ("Sunglasses", 85),
                ("Backpack", 70), ("Wrist Watch", 300)],
    "Books": [("Python Guide", 45), ("Data Science 101", 55), ("Novel Mystery", 20),
              ("Cookbook Deluxe", 35), ("History Atlas", 65)],
}
regions = ["North", "South", "East", "West", "Central"]
customers = [f"Customer_{i:03d}" for i in range(1, 41)]

rows = []
start_date = datetime(2024, 1, 1)
for i in range(1, 151):
    category = random.choice(list(products.keys()))
    product, base_price = random.choice(products[category])
    quantity = random.randint(1, 10)
    # Dao động giá +- 10%
    unit_price = round(base_price * random.uniform(0.9, 1.1), 2)
    revenue = round(quantity * unit_price, 2)
    date = start_date + timedelta(days=random.randint(0, 364))
    rows.append({
        "Order ID": f"ORD{i:05d}",
        "Date": date.strftime("%Y-%m-%d"),
        "Product": product,
        "Category": category,
        "Region": random.choice(regions),
        "Quantity": quantity,
        "Unit Price": unit_price,
        "Revenue": revenue,
        "Customer": random.choice(customers),
    })

fields = ["Order ID", "Date", "Product", "Category", "Region",
          "Quantity", "Unit Price", "Revenue", "Customer"]
with open("sample_sales_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Đã tạo sample_sales_data.csv với {len(rows)} dòng.")
