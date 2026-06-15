"""
Dashboard Phân Tích Doanh Số Bán Lẻ
-----------------------------------
Ứng dụng Streamlit cho phép upload CSV/Excel, phân tích dữ liệu bán hàng,
vẽ biểu đồ Plotly và lưu trữ vào SQLite.

Chạy:  streamlit run app.py
"""

import io
import os
import sqlite3
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------- #
# Cấu hình chung
# --------------------------------------------------------------------------- #
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "sales_dashboard.db")
SAMPLE_PATH = os.path.join(APP_DIR, "sample_sales_data.csv")
TABLE_NAME = "sales_data"

st.set_page_config(
    page_title="Dashboard Phân Tích Doanh Số Bán Lẻ",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------------------------------- #
# Hàm xử lý dữ liệu
# --------------------------------------------------------------------------- #
def load_data(uploaded_file):
    """Đọc dữ liệu từ file upload (CSV/Excel). Trả về (DataFrame, error_msg)."""
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            return None, "Định dạng file không được hỗ trợ. Chỉ chấp nhận .csv, .xlsx, .xls."
    except pd.errors.EmptyDataError:
        return None, "File rỗng, không có dữ liệu để đọc."
    except Exception as exc:  # noqa: BLE001 - hiển thị lỗi thân thiện
        return None, f"Không thể đọc file: {exc}"

    if df is None or df.empty:
        return None, "File không chứa dữ liệu (0 dòng)."
    return df, None


def create_sample_data():
    """Đọc dữ liệu mẫu từ sample_sales_data.csv. Trả về (DataFrame, error_msg)."""
    if not os.path.exists(SAMPLE_PATH):
        return None, f"Không tìm thấy file dữ liệu mẫu: {SAMPLE_PATH}"
    try:
        df = pd.read_csv(SAMPLE_PATH)
    except Exception as exc:  # noqa: BLE001
        return None, f"Lỗi đọc dữ liệu mẫu: {exc}"
    if df.empty:
        return None, "File dữ liệu mẫu rỗng."
    return df, None


def clean_data(df):
    """Làm sạch & chuẩn hoá dữ liệu:
    - Chuẩn hoá tên cột (bỏ khoảng trắng thừa).
    - Chuyển cột Date sang datetime nếu có.
    - Ép các cột số (Quantity, Unit Price, Revenue) về kiểu số.
    - Tự tạo Revenue = Quantity * Unit Price nếu thiếu.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Chuyển cột Date sang datetime nếu có
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Ép các cột số phổ biến về numeric (loại bỏ ký tự không hợp lệ)
    for col in ("Quantity", "Unit Price", "Revenue"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Tự tạo Revenue nếu thiếu nhưng có Quantity và Unit Price
    if "Revenue" not in df.columns and {"Quantity", "Unit Price"} <= set(df.columns):
        df["Revenue"] = df["Quantity"] * df["Unit Price"]

    return df


def calculate_metrics(df):
    """Tính các chỉ số tổng quan. Thiếu cột nào trả 'N/A' cho chỉ số đó."""
    metrics = {
        "total_revenue": "N/A",
        "total_orders": "N/A",
        "total_quantity": "N/A",
        "unique_customers": "N/A",
    }
    if "Revenue" in df.columns:
        metrics["total_revenue"] = float(df["Revenue"].sum())
    if "Order ID" in df.columns:
        metrics["total_orders"] = int(df["Order ID"].nunique())
    else:
        metrics["total_orders"] = int(len(df))  # fallback: số dòng
    if "Quantity" in df.columns:
        metrics["total_quantity"] = int(df["Quantity"].sum())
    if "Customer" in df.columns:
        metrics["unique_customers"] = int(df["Customer"].nunique())
    return metrics


def save_to_sqlite(df, filename):
    """Lưu DataFrame vào SQLite + ghi log upload. Trả về (ok, error_msg)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Lưu toàn bộ dữ liệu (ghi đè bảng cũ)
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

        # Tạo bảng log nếu chưa có
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS upload_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                upload_time TEXT,
                row_count INTEGER,
                column_count INTEGER
            )
            """
        )
        conn.execute(
            "INSERT INTO upload_logs (filename, upload_time, row_count, column_count) "
            "VALUES (?, ?, ?, ?)",
            (filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             len(df), len(df.columns)),
        )
        conn.commit()
        conn.close()
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def run_sql_query(query):
    """Chạy SQL query trên SQLite. Trả về (DataFrame, error_msg)."""
    if not os.path.exists(DB_PATH):
        return None, "Chưa có database. Hãy upload hoặc load dữ liệu mẫu trước."
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Lỗi SQL: {exc}"


def list_tables():
    """Liệt kê các bảng trong database."""
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:  # noqa: BLE001
        return []


def get_numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_columns(df):
    return df.select_dtypes(exclude="number").columns.tolist()


# --------------------------------------------------------------------------- #
# Các hàm render giao diện
# --------------------------------------------------------------------------- #
def render_overview(df):
    """Hiển thị các thẻ metric tổng quan ở đầu trang."""
    metrics = calculate_metrics(df)
    c1, c2, c3, c4 = st.columns(4)

    rev = metrics["total_revenue"]
    c1.metric("💰 Tổng doanh thu",
              f"{rev:,.0f}" if rev != "N/A" else "N/A")
    c2.metric("🧾 Tổng số đơn hàng", metrics["total_orders"])
    qty = metrics["total_quantity"]
    c3.metric("📦 Sản phẩm đã bán",
              f"{qty:,}" if qty != "N/A" else "N/A")
    c4.metric("👥 Khách hàng duy nhất", metrics["unique_customers"])


def render_data_tab(df, filename):
    """Tab Dữ liệu: thông tin file + bảng dữ liệu."""
    st.subheader("📁 Thông tin dữ liệu")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tên nguồn", filename)
    c2.metric("Số dòng", f"{len(df):,}")
    c3.metric("Số cột", len(df.columns))

    st.write("**Danh sách cột:**", ", ".join(map(str, df.columns)))
    st.subheader("📋 Bảng dữ liệu")
    st.dataframe(df, use_container_width=True)


def render_statistics_tab(df):
    """Tab Thống kê: thông tin tổng hợp, missing, describe, top N."""
    st.subheader("🔎 Thông tin tổng quan")
    c1, c2, c3 = st.columns(3)
    c1.metric("Số dòng", f"{len(df):,}")
    c2.metric("Số cột", len(df.columns))
    c3.metric("Số dòng trùng lặp", int(df.duplicated().sum()))

    # Kiểu dữ liệu & giá trị thiếu
    st.subheader("🧬 Kiểu dữ liệu & giá trị thiếu")
    info = pd.DataFrame({
        "Cột": df.columns,
        "Kiểu dữ liệu": [str(t) for t in df.dtypes],
        "Giá trị thiếu": df.isna().sum().values,
    })
    st.dataframe(info, use_container_width=True, hide_index=True)

    # Thống kê mô tả
    st.subheader("📈 Thống kê mô tả (cột số)")
    numeric_cols = get_numeric_columns(df)
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe().T, use_container_width=True)

        st.subheader("➕ Tổng / Trung bình / Min / Max")
        agg = pd.DataFrame({
            "Tổng": df[numeric_cols].sum(),
            "Trung bình": df[numeric_cols].mean(),
            "Min": df[numeric_cols].min(),
            "Max": df[numeric_cols].max(),
        })
        st.dataframe(agg, use_container_width=True)
    else:
        st.info("Không có cột dạng số để thống kê mô tả.")

    # Top 10 theo doanh thu
    st.subheader("🏆 Top 10 theo doanh thu")
    if "Revenue" not in df.columns:
        st.info("Không có cột 'Revenue' nên không thể xếp hạng theo doanh thu.")
        return

    for col, label in (("Product", "sản phẩm"),
                       ("Category", "danh mục"),
                       ("Region", "khu vực")):
        if col in df.columns:
            top = (df.groupby(col)["Revenue"].sum()
                   .sort_values(ascending=False).head(10).reset_index())
            st.markdown(f"**Top 10 {label} theo doanh thu**")
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.caption(f"Bỏ qua top {label}: thiếu cột '{col}'.")


def render_charts_tab(df):
    """Tab Biểu đồ: biểu đồ mặc định + biểu đồ tùy chỉnh."""
    numeric_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    has_revenue = "Revenue" in df.columns

    st.subheader("📊 Biểu đồ mặc định")

    # 1) Bar: Top 10 sản phẩm theo doanh thu
    if has_revenue and "Product" in df.columns:
        top_prod = (df.groupby("Product")["Revenue"].sum()
                    .sort_values(ascending=False).head(10).reset_index())
        fig = px.bar(top_prod, x="Product", y="Revenue",
                     title="Top 10 sản phẩm theo doanh thu", color="Revenue")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột 'Product' và 'Revenue' để vẽ Top 10 sản phẩm.")

    # 2) Pie: tỷ trọng doanh thu theo danh mục
    if has_revenue and "Category" in df.columns:
        cat_rev = df.groupby("Category")["Revenue"].sum().reset_index()
        fig = px.pie(cat_rev, names="Category", values="Revenue",
                     title="Tỷ trọng doanh thu theo danh mục")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột 'Category' và 'Revenue' để vẽ biểu đồ tròn danh mục.")

    # 3) Bar: doanh thu theo khu vực
    if has_revenue and "Region" in df.columns:
        reg_rev = (df.groupby("Region")["Revenue"].sum()
                   .sort_values(ascending=False).reset_index())
        fig = px.bar(reg_rev, x="Region", y="Revenue",
                     title="Doanh thu theo khu vực", color="Region")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột 'Region' và 'Revenue' để vẽ doanh thu theo khu vực.")

    # 4) Line: doanh thu theo thời gian
    if has_revenue and "Date" in df.columns and df["Date"].notna().any():
        ts = (df.dropna(subset=["Date"])
              .groupby(pd.Grouper(key="Date", freq="D"))["Revenue"]
              .sum().reset_index())
        fig = px.line(ts, x="Date", y="Revenue", title="Doanh thu theo thời gian")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột 'Date' hợp lệ và 'Revenue' để vẽ biểu đồ theo thời gian.")

    # 5) Histogram cho cột số do người dùng chọn
    st.subheader("📉 Histogram")
    if numeric_cols:
        col = st.selectbox("Chọn cột số:", numeric_cols, key="hist_col")
        fig = px.histogram(df, x=col, title=f"Phân phối của '{col}'")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Không có cột dạng số để vẽ histogram.")

    # --------------------- Biểu đồ tùy chỉnh --------------------- #
    st.divider()
    st.subheader("🎨 Tạo biểu đồ tùy chỉnh")
    chart_type = st.selectbox("Loại biểu đồ:",
                              ["Bar", "Line", "Scatter", "Pie", "Histogram"])
    all_cols = df.columns.tolist()

    try:
        if chart_type == "Histogram":
            x = st.selectbox("Cột X (số):", numeric_cols or all_cols, key="cx_hist")
            fig = px.histogram(df, x=x, title=f"Histogram - {x}")
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie":
            names = st.selectbox("Cột nhãn (chữ):", cat_cols or all_cols, key="cx_pie")
            values = st.selectbox("Cột giá trị (số):", numeric_cols or all_cols, key="cy_pie")
            if not numeric_cols:
                st.warning("Pie cần ít nhất một cột số làm giá trị.")
            else:
                agg = df.groupby(names)[values].sum().reset_index()
                fig = px.pie(agg, names=names, values=values,
                             title=f"{values} theo {names}")
                st.plotly_chart(fig, use_container_width=True)
        else:
            cx, cy = st.columns(2)
            x = cx.selectbox("Cột X:", all_cols, key="cx")
            y = cy.selectbox("Cột Y:", all_cols, key="cy")
            if chart_type == "Bar":
                fig = px.bar(df, x=x, y=y, title=f"{y} theo {x}")
            elif chart_type == "Line":
                fig = px.line(df.sort_values(x), x=x, y=y, title=f"{y} theo {x}")
            else:  # Scatter
                fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Không thể vẽ biểu đồ với lựa chọn này: {exc}")


def render_sqlite_tab(df):
    """Tab SQLite: hiển thị bảng, preview, query và export."""
    st.success(f"✅ Dữ liệu đã được lưu vào `{os.path.basename(DB_PATH)}` "
               f"(bảng `{TABLE_NAME}`).")

    tables = list_tables()
    st.write("**Các bảng trong database:**",
             ", ".join(tables) if tables else "(chưa có)")

    # Preview 10 dòng đầu từ sales_data
    st.subheader("👀 Preview bảng sales_data (10 dòng đầu)")
    preview, err = run_sql_query(f"SELECT * FROM {TABLE_NAME} LIMIT 10")
    if err:
        st.error(err)
    else:
        st.dataframe(preview, use_container_width=True)

    # Query mẫu
    st.subheader("⚡ Chạy SQL Query")
    sample_queries = {
        "-- Chọn query mẫu --": "",
        "10 dòng đầu": f"SELECT * FROM {TABLE_NAME} LIMIT 10;",
        "Đếm tổng số dòng": f"SELECT COUNT(*) AS total_rows FROM {TABLE_NAME};",
        "Doanh thu theo danh mục":
            f"SELECT Category, SUM(Revenue) AS total_revenue FROM {TABLE_NAME} "
            f"GROUP BY Category ORDER BY total_revenue DESC;",
        "Doanh thu theo khu vực":
            f"SELECT Region, SUM(Revenue) AS total_revenue FROM {TABLE_NAME} "
            f"GROUP BY Region ORDER BY total_revenue DESC;",
    }
    choice = st.selectbox("Query mẫu:", list(sample_queries.keys()))
    default_query = sample_queries[choice] or f"SELECT * FROM {TABLE_NAME} LIMIT 10;"

    query = st.text_area("Nhập SQL query:", value=default_query, height=120)
    if st.button("▶️ Run Query"):
        result, err = run_sql_query(query)
        if err:
            st.error(err)
        else:
            st.success(f"Trả về {len(result)} dòng.")
            st.dataframe(result, use_container_width=True)

    # Export
    st.divider()
    st.subheader("⬇️ Export dữ liệu")
    c1, c2 = st.columns(2)

    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    c1.download_button("📄 Tải CSV đã xử lý", data=csv_bytes,
                       file_name="processed_sales_data.csv", mime="text/csv")

    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            c2.download_button("🗄️ Tải file SQLite (.db)", data=f.read(),
                               file_name="sales_dashboard.db",
                               mime="application/octet-stream")


def render_guide_tab():
    """Tab Hướng dẫn sử dụng."""
    st.subheader("📖 Hướng dẫn sử dụng")
    st.markdown(
        """
1. **Bước 1 – Nạp dữ liệu:** Upload file CSV/Excel ở sidebar, hoặc bấm
   **"Load dữ liệu mẫu"** để dùng dữ liệu giả lập.
2. **Bước 2 – Xem bảng dữ liệu:** Vào tab **Dữ liệu** để xem thông tin file
   và toàn bộ bảng.
3. **Bước 3 – Xem thống kê:** Tab **Thống kê** hiển thị kiểu dữ liệu, giá trị
   thiếu, mô tả thống kê và bảng xếp hạng theo doanh thu.
4. **Bước 4 – Xem biểu đồ:** Tab **Biểu đồ** có các biểu đồ mặc định và công
   cụ tạo biểu đồ tùy chỉnh (Bar, Line, Scatter, Pie, Histogram).
5. **Bước 5 – Chạy SQL:** Tab **SQLite** cho phép xem các bảng, chạy SQL query
   tùy ý hoặc dùng query mẫu.
6. **Bước 6 – Download:** Tải dữ liệu đã xử lý dưới dạng CSV hoặc tải file
   SQLite `.db` trong tab **SQLite**.

---
**Gợi ý cấu trúc dữ liệu** (không bắt buộc): `Order ID`, `Date`, `Product`,
`Category`, `Region`, `Quantity`, `Unit Price`, `Revenue`, `Customer`.

> Nếu thiếu cột `Revenue` nhưng có `Quantity` và `Unit Price`, app sẽ tự tính
> `Revenue = Quantity × Unit Price`.
        """
    )


# --------------------------------------------------------------------------- #
# Ứng dụng chính
# --------------------------------------------------------------------------- #
def main():
    st.title("📊 Dashboard Phân Tích Doanh Số Bán Lẻ")

    # Khởi tạo session_state
    if "df" not in st.session_state:
        st.session_state.df = None
        st.session_state.filename = None

    # ----------------------------- Sidebar ----------------------------- #
    with st.sidebar:
        st.header("⚙️ Nạp dữ liệu")
        uploaded = st.file_uploader(
            "Upload file dữ liệu",
            type=["csv", "xlsx", "xls"],
            help="Hỗ trợ .csv, .xlsx, .xls",
        )

        if st.button("📥 Load dữ liệu mẫu", use_container_width=True):
            df, err = create_sample_data()
            if err:
                st.error(err)
            else:
                df = clean_data(df)
                ok, db_err = save_to_sqlite(df, "sample_sales_data.csv")
                st.session_state.df = df
                st.session_state.filename = "sample_sales_data.csv"
                if not ok:
                    st.warning(f"Lưu SQLite lỗi: {db_err}")
                st.success("Đã nạp dữ liệu mẫu!")

        # Xử lý file upload
        if uploaded is not None:
            df, err = load_data(uploaded)
            if err:
                st.error(err)
            else:
                df = clean_data(df)
                ok, db_err = save_to_sqlite(df, uploaded.name)
                st.session_state.df = df
                st.session_state.filename = uploaded.name
                if not ok:
                    st.warning(f"Lưu SQLite lỗi: {db_err}")

        # Thông tin nhanh về dữ liệu hiện tại
        if st.session_state.df is not None:
            st.divider()
            st.caption(f"📄 Nguồn: **{st.session_state.filename}**")
            st.caption(f"Dòng: {len(st.session_state.df):,} | "
                       f"Cột: {len(st.session_state.df.columns)}")

    # --------------------------- Khu vực chính --------------------------- #
    df = st.session_state.df

    if df is None:
        st.info("👈 Hãy upload file CSV/Excel hoặc bấm **Load dữ liệu mẫu** "
                "ở sidebar để bắt đầu.")
        render_guide_tab()
        return

    # Thẻ metric tổng quan
    render_overview(df)
    st.divider()

    # Các tab nội dung
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Dữ liệu", "📊 Thống kê", "📈 Biểu đồ", "🗄️ SQLite", "📖 Hướng dẫn"]
    )
    with tab1:
        render_data_tab(df, st.session_state.filename)
    with tab2:
        render_statistics_tab(df)
    with tab3:
        render_charts_tab(df)
    with tab4:
        render_sqlite_tab(df)
    with tab5:
        render_guide_tab()


if __name__ == "__main__":
    main()
