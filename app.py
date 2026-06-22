"""
Dashboard Phân Tích Dữ Liệu Khám Chữa Bệnh (Y tế Việt Nam)
----------------------------------------------------------
Ứng dụng Streamlit cho phép upload CSV/Excel dữ liệu khám chữa bệnh & viện phí,
phân tích thống kê, vẽ biểu đồ Plotly và lưu trữ vào SQLite.

Chạy:  streamlit run app.py
"""

import os
import sqlite3
import unicodedata
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------- #
# Cấu hình chung
# --------------------------------------------------------------------------- #
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "health_dashboard.db")
SAMPLE_PATH = os.path.join(APP_DIR, "sample_health_data.csv")
TABLE_NAME = "medical_records"

st.set_page_config(
    page_title="Dashboard Phân Tích Dữ Liệu Khám Chữa Bệnh",
    page_icon="🏥",
    layout="wide",
)

# --------------------------------------------------------------------------- #
# Vai trò các cột (role) — ánh xạ tên cột thực tế (VN/EN) sang vai trò logic.
# Nhờ vậy app vừa hiểu dữ liệu y tế tiếng Việt, vừa xử lý được file khác.
# --------------------------------------------------------------------------- #
COLUMN_ROLES = {
    "id":      ["Mã khám", "Mã BN", "Order ID", "ID", "Mã"],
    "date":    ["Ngày khám", "Ngày", "Date"],
    "item":    ["Dịch vụ", "Chẩn đoán", "Dịch vụ y tế", "Product", "Service"],
    "group":   ["Khoa", "Chuyên khoa", "Category", "Department"],
    "region":  ["Tỉnh/Thành", "Tỉnh", "Tỉnh thành", "Khu vực", "Region", "Province"],
    "qty":     ["Số lượng", "SL", "Quantity"],
    "price":   ["Đơn giá", "Giá", "Unit Price"],
    "revenue": ["Viện phí", "Chi phí", "Thành tiền", "Tổng tiền", "Revenue"],
    "entity":  ["Bệnh nhân", "Patient", "Khách hàng", "Customer"],
}

# Nhãn hiển thị thân thiện cho từng vai trò (dùng trong tiêu đề biểu đồ...)
ROLE_LABELS = {
    "item": "dịch vụ", "group": "khoa", "region": "tỉnh/thành",
    "entity": "bệnh nhân", "revenue": "viện phí",
}

# Bảng màu pastel cho gradient bảng (theme sáng)
HUES = {
    "green": (46, 125, 50), "blue": (21, 101, 192), "teal": (0, 131, 143),
    "pink": (194, 24, 91), "amber": (245, 124, 0), "purple": (106, 27, 154),
}


# --------------------------------------------------------------------------- #
# Tiện ích chuẩn hoá tên cột
# --------------------------------------------------------------------------- #
def strip_accents(text):
    """Bỏ dấu tiếng Việt (đ/Đ -> d/D)."""
    text = str(text).replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _norm(text):
    """Chuẩn hoá để so khớp: bỏ dấu, lower, strip."""
    return strip_accents(text).strip().lower()


def sanitize_name(text):
    """Đổi tên cột thành dạng an toàn cho SQL (chỉ chữ/số/_)."""
    base = strip_accents(text).strip()
    out = "".join(ch if ch.isalnum() else "_" for ch in base)
    out = "_".join(filter(None, out.split("_")))  # gộp dấu _ liên tiếp
    if not out:
        out = "col"
    if out[0].isdigit():
        out = "c_" + out
    return out


def resolve_columns(df):
    """Trả về dict {role: tên cột thực tế hoặc None}."""
    lookup = {_norm(c): c for c in df.columns}
    roles = {}
    for role, aliases in COLUMN_ROLES.items():
        found = None
        for alias in aliases:
            if _norm(alias) in lookup:
                found = lookup[_norm(alias)]
                break
        roles[role] = found
    return roles


def build_sql_map(df):
    """Map {tên cột gốc: tên cột an toàn cho SQL}, đảm bảo không trùng."""
    seen, mapping = set(), {}
    for col in df.columns:
        name = sanitize_name(col)
        base, i = name, 2
        while name in seen:
            name = f"{base}_{i}"
            i += 1
        seen.add(name)
        mapping[col] = name
    return mapping


# --------------------------------------------------------------------------- #
# Hàm tô màu bảng (gradient pastel, không cần matplotlib)
# --------------------------------------------------------------------------- #
def _grad(series, hue="green"):
    """Trả về list CSS background-color theo độ lớn giá trị (pastel, theme sáng)."""
    base = HUES.get(hue, HUES["green"])
    nums = pd.to_numeric(series, errors="coerce")
    lo, hi = nums.min(), nums.max()
    span = (hi - lo) if pd.notna(hi) and pd.notna(lo) and hi != lo else 1
    out = []
    for v in nums:
        if pd.isna(v):
            out.append("")
            continue
        t = max(0.0, min(1.0, (v - lo) / span)) * 0.6  # giữ tông nhạt, dễ đọc
        r = int(255 + (base[0] - 255) * t)
        g = int(255 + (base[1] - 255) * t)
        b = int(255 + (base[2] - 255) * t)
        out.append(f"background-color: rgb({r},{g},{b}); color: #1a1a1a;")
    return out


def style_frame(df, money_cols=(), int_cols=(), grad=None):
    """Style bảng: format tiền VND, format số nguyên, gradient màu theo cột."""
    grad = grad or {}
    sty = df.style
    fmt = {}
    for c in money_cols:
        if c in df.columns:
            fmt[c] = "{:,.0f} ₫"
    for c in int_cols:
        if c in df.columns:
            fmt[c] = "{:,.0f}"
    if fmt:
        sty = sty.format(fmt, na_rep="—")
    for col, hue in grad.items():
        if col in df.columns:
            sty = sty.apply(lambda s, h=hue: _grad(s, h), subset=[col])
    return sty


def style_numeric(df, hue="teal"):
    """Style cho bảng toàn số (describe, agg): format gọn + gradient mỗi cột."""
    sty = df.style.format(precision=1, thousands=",", na_rep="—")
    for col in df.select_dtypes(include="number").columns:
        sty = sty.apply(lambda s, h=hue: _grad(s, h), subset=[col])
    return sty


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
    """Đọc dữ liệu mẫu y tế từ sample_health_data.csv. Trả về (DataFrame, error_msg)."""
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
    - Chuyển cột ngày sang datetime nếu có.
    - Ép các cột số (số lượng, đơn giá, viện phí) về kiểu số.
    - Tự tạo cột viện phí = số lượng * đơn giá nếu thiếu.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    roles = resolve_columns(df)

    if roles["date"]:
        df[roles["date"]] = pd.to_datetime(df[roles["date"]], errors="coerce")

    for role in ("qty", "price", "revenue"):
        if roles[role]:
            df[roles[role]] = pd.to_numeric(df[roles[role]], errors="coerce")

    # Tự tạo cột thành tiền/viện phí nếu thiếu nhưng có số lượng & đơn giá
    if not roles["revenue"] and roles["qty"] and roles["price"]:
        is_vn = _norm(roles["price"]) == "don gia" or _norm(roles["qty"]) == "so luong"
        new_name = "Viện phí" if is_vn else "Revenue"
        df[new_name] = df[roles["qty"]] * df[roles["price"]]

    return df


def calculate_metrics(df, roles):
    """Tính các chỉ số tổng quan. Thiếu cột nào trả 'N/A' cho chỉ số đó."""
    metrics = {"revenue": "N/A", "visits": "N/A", "services": "N/A", "patients": "N/A"}

    if roles["revenue"]:
        metrics["revenue"] = float(df[roles["revenue"]].sum())
    metrics["visits"] = int(df[roles["id"]].nunique()) if roles["id"] else int(len(df))
    if roles["qty"]:
        metrics["services"] = int(df[roles["qty"]].sum())
    if roles["entity"]:
        metrics["patients"] = int(df[roles["entity"]].nunique())
    return metrics


def save_to_sqlite(df, filename):
    """Lưu DataFrame vào SQLite (đổi tên cột an toàn) + ghi log. Trả (ok, error_msg)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df_sql = df.rename(columns=build_sql_map(df))
        df_sql.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

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


def money_cols_of(df, roles):
    """Các cột thể hiện tiền (đơn giá, viện phí)."""
    cols = []
    for role in ("price", "revenue"):
        if roles[role] and roles[role] in df.columns:
            cols.append(roles[role])
    return cols


# --------------------------------------------------------------------------- #
# Các hàm render giao diện
# --------------------------------------------------------------------------- #
def render_overview(df, roles):
    """Hiển thị các thẻ metric tổng quan ở đầu trang."""
    metrics = calculate_metrics(df, roles)
    c1, c2, c3, c4 = st.columns(4)

    rev = metrics["revenue"]
    c1.metric("💰 Tổng viện phí", f"{rev:,.0f} ₫" if rev != "N/A" else "N/A")
    c2.metric("🩺 Tổng lượt khám", f"{metrics['visits']:,}"
              if metrics["visits"] != "N/A" else "N/A")
    svc = metrics["services"]
    c3.metric("💊 Tổng lượt dịch vụ", f"{svc:,}" if svc != "N/A" else "N/A")
    c4.metric("🧑‍🤝‍🧑 Số bệnh nhân", f"{metrics['patients']:,}"
              if metrics["patients"] != "N/A" else "N/A")


def render_data_tab(df, roles, filename):
    """Tab Dữ liệu: thông tin file + bảng dữ liệu (tô màu)."""
    st.subheader("📁 Thông tin dữ liệu")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tên nguồn", filename)
    c2.metric("Số dòng", f"{len(df):,}")
    c3.metric("Số cột", len(df.columns))

    st.write("**Danh sách cột:**", ", ".join(map(str, df.columns)))

    st.subheader("📋 Bảng dữ liệu")
    money = money_cols_of(df, roles)
    int_cols = [roles["qty"]] if roles["qty"] else []
    grad = {}
    if roles["revenue"]:
        grad[roles["revenue"]] = "green"
    if roles["price"]:
        grad[roles["price"]] = "blue"
    st.dataframe(style_frame(df, money_cols=money, int_cols=int_cols, grad=grad),
                 use_container_width=True)


def render_statistics_tab(df, roles):
    """Tab Thống kê: thông tin tổng hợp, missing, describe, top N."""
    st.subheader("🔎 Thông tin tổng quan")
    c1, c2, c3 = st.columns(3)
    c1.metric("Số dòng", f"{len(df):,}")
    c2.metric("Số cột", len(df.columns))
    c3.metric("Số dòng trùng lặp", int(df.duplicated().sum()))

    # Kiểu dữ liệu & giá trị thiếu (tô màu cột thiếu)
    st.subheader("🧬 Kiểu dữ liệu & giá trị thiếu")
    info = pd.DataFrame({
        "Cột": df.columns,
        "Kiểu dữ liệu": [str(t) for t in df.dtypes],
        "Giá trị thiếu": df.isna().sum().values,
    })
    st.dataframe(style_frame(info, grad={"Giá trị thiếu": "amber"}),
                 use_container_width=True, hide_index=True)

    # Thống kê mô tả
    st.subheader("📈 Thống kê mô tả (cột số)")
    numeric_cols = get_numeric_columns(df)
    if numeric_cols:
        st.dataframe(style_numeric(df[numeric_cols].describe().T, hue="teal"),
                     use_container_width=True)

        st.subheader("➕ Tổng / Trung bình / Min / Max")
        agg = pd.DataFrame({
            "Tổng": df[numeric_cols].sum(),
            "Trung bình": df[numeric_cols].mean(),
            "Min": df[numeric_cols].min(),
            "Max": df[numeric_cols].max(),
        })
        st.dataframe(style_numeric(agg, hue="purple"), use_container_width=True)
    else:
        st.info("Không có cột dạng số để thống kê mô tả.")

    # Top 10 theo viện phí
    st.subheader("🏆 Top 10 theo viện phí")
    if not roles["revenue"]:
        st.info("Không có cột viện phí nên không thể xếp hạng theo viện phí.")
        return

    rev = roles["revenue"]
    for role, hue in (("item", "green"), ("group", "blue"), ("region", "pink")):
        col = roles[role]
        label = ROLE_LABELS[role]
        if col:
            top = (df.groupby(col)[rev].sum()
                   .sort_values(ascending=False).head(10).reset_index())
            st.markdown(f"**Top 10 {label} theo viện phí**")
            st.dataframe(style_frame(top, money_cols=[rev], grad={rev: hue}),
                         use_container_width=True, hide_index=True)
        else:
            st.caption(f"Bỏ qua top {label}: không tìm thấy cột tương ứng.")


def render_charts_tab(df, roles):
    """Tab Biểu đồ: biểu đồ mặc định + biểu đồ tùy chỉnh."""
    numeric_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    rev = roles["revenue"]

    st.subheader("📊 Biểu đồ mặc định")

    # 1) Bar: Top 10 dịch vụ theo viện phí
    if rev and roles["item"]:
        top = (df.groupby(roles["item"])[rev].sum()
               .sort_values(ascending=False).head(10).reset_index())
        fig = px.bar(top, x=roles["item"], y=rev, color=rev,
                     color_continuous_scale="Tealgrn",
                     title="Top 10 dịch vụ theo viện phí")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột dịch vụ và viện phí để vẽ Top 10 dịch vụ.")

    # 2) Pie: tỷ trọng viện phí theo khoa
    if rev and roles["group"]:
        grp = df.groupby(roles["group"])[rev].sum().reset_index()
        fig = px.pie(grp, names=roles["group"], values=rev, hole=0.35,
                     title="Tỷ trọng viện phí theo khoa")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột khoa và viện phí để vẽ biểu đồ tròn.")

    # 3) Bar: viện phí theo tỉnh/thành
    if rev and roles["region"]:
        reg = (df.groupby(roles["region"])[rev].sum()
               .sort_values(ascending=False).reset_index())
        fig = px.bar(reg, x=roles["region"], y=rev, color=roles["region"],
                     title="Viện phí theo tỉnh/thành")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột tỉnh/thành và viện phí để vẽ biểu đồ theo khu vực.")

    # 4) Line: viện phí theo thời gian
    if rev and roles["date"] and df[roles["date"]].notna().any():
        ts = (df.dropna(subset=[roles["date"]])
              .groupby(pd.Grouper(key=roles["date"], freq="D"))[rev]
              .sum().reset_index())
        fig = px.line(ts, x=roles["date"], y=rev, markers=False,
                      title="Viện phí theo thời gian")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần cột ngày hợp lệ và viện phí để vẽ biểu đồ theo thời gian.")

    # 5) Histogram cho cột số do người dùng chọn
    st.subheader("📉 Histogram")
    if numeric_cols:
        col = st.selectbox("Chọn cột số:", numeric_cols, key="hist_col")
        fig = px.histogram(df, x=col, title=f"Phân phối của '{col}'",
                           color_discrete_sequence=["#0E9F6E"])
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
                st.warning("Biểu đồ tròn cần ít nhất một cột số làm giá trị.")
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
                fig = px.scatter(df, x=x, y=y, title=f"{y} so với {x}")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Không thể vẽ biểu đồ với lựa chọn này: {exc}")


def render_sqlite_tab(df, roles):
    """Tab SQLite: hiển thị bảng, preview, query và export."""
    st.success(f"✅ Dữ liệu đã được lưu vào `{os.path.basename(DB_PATH)}` "
               f"(bảng `{TABLE_NAME}`).")

    tables = list_tables()
    st.write("**Các bảng trong database:**",
             ", ".join(tables) if tables else "(chưa có)")

    # Bảng ánh xạ tên cột gốc <-> tên cột trong SQL
    sql_map = build_sql_map(df)
    with st.expander("ℹ️ Tên cột trong SQL (đã bỏ dấu để query dễ dàng)"):
        st.dataframe(
            pd.DataFrame({"Cột gốc": list(sql_map.keys()),
                          "Cột trong SQL": list(sql_map.values())}),
            use_container_width=True, hide_index=True,
        )

    # Preview 10 dòng đầu
    st.subheader("👀 Preview bảng (10 dòng đầu)")
    preview, err = run_sql_query(f"SELECT * FROM {TABLE_NAME} LIMIT 10")
    if err:
        st.error(err)
    else:
        st.dataframe(preview, use_container_width=True)

    # Query mẫu (sinh động theo cột thực tế)
    st.subheader("⚡ Chạy SQL Query")
    sample_queries = {"-- Chọn query mẫu --": ""}
    sample_queries["10 dòng đầu"] = f"SELECT * FROM {TABLE_NAME} LIMIT 10;"
    sample_queries["Đếm tổng số dòng"] = \
        f"SELECT COUNT(*) AS tong_so_dong FROM {TABLE_NAME};"
    if roles["group"] and roles["revenue"]:
        g, r = sql_map[roles["group"]], sql_map[roles["revenue"]]
        sample_queries["Viện phí theo khoa"] = (
            f"SELECT {g}, SUM({r}) AS tong_vien_phi FROM {TABLE_NAME} "
            f"GROUP BY {g} ORDER BY tong_vien_phi DESC;")
    if roles["region"] and roles["revenue"]:
        rg, r = sql_map[roles["region"]], sql_map[roles["revenue"]]
        sample_queries["Viện phí theo tỉnh/thành"] = (
            f"SELECT {rg}, SUM({r}) AS tong_vien_phi FROM {TABLE_NAME} "
            f"GROUP BY {rg} ORDER BY tong_vien_phi DESC;")

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
                       file_name="processed_health_data.csv", mime="text/csv")

    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            c2.download_button("🗄️ Tải file SQLite (.db)", data=f.read(),
                               file_name="health_dashboard.db",
                               mime="application/octet-stream")


def render_guide_tab():
    """Tab Hướng dẫn sử dụng."""
    st.subheader("📖 Hướng dẫn sử dụng")
    st.markdown(
        """
1. **Bước 1 – Nạp dữ liệu:** Upload file CSV/Excel ở sidebar, hoặc bấm
   **"Load dữ liệu mẫu"** để dùng dữ liệu khám chữa bệnh giả lập.
2. **Bước 2 – Xem bảng dữ liệu:** Vào tab **Dữ liệu** để xem thông tin file
   và toàn bộ bảng (đã tô màu).
3. **Bước 3 – Xem thống kê:** Tab **Thống kê** hiển thị kiểu dữ liệu, giá trị
   thiếu, mô tả thống kê và bảng xếp hạng viện phí theo dịch vụ/khoa/tỉnh thành.
4. **Bước 4 – Xem biểu đồ:** Tab **Biểu đồ** có các biểu đồ mặc định và công
   cụ tạo biểu đồ tùy chỉnh (Bar, Line, Scatter, Pie, Histogram).
5. **Bước 5 – Chạy SQL:** Tab **SQLite** cho phép xem các bảng, chạy SQL query
   tùy ý hoặc dùng query mẫu.
6. **Bước 6 – Download:** Tải dữ liệu đã xử lý dưới dạng CSV hoặc tải file
   SQLite `.db` trong tab **SQLite**.

---
**Gợi ý cấu trúc dữ liệu y tế** (không bắt buộc): `Mã khám`, `Ngày khám`,
`Bệnh nhân`, `Khoa`, `Dịch vụ`, `Tỉnh/Thành`, `Số lượng`, `Đơn giá`, `Viện phí`.

> Nếu thiếu cột `Viện phí` nhưng có `Số lượng` và `Đơn giá`, app sẽ tự tính
> `Viện phí = Số lượng × Đơn giá`.
        """
    )


# --------------------------------------------------------------------------- #
# CSS làm đẹp thẻ metric (theme sáng)
# --------------------------------------------------------------------------- #
def inject_css():
    st.markdown(
        """
        <style>
        [data-testid="stMetric"] {
            background: #F0FBF4;
            border: 1px solid #CDEFE0;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 1px 3px rgba(14,159,110,0.08);
        }
        [data-testid="stMetricLabel"] { color: #166534; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Ứng dụng chính
# --------------------------------------------------------------------------- #
def main():
    inject_css()
    st.title("🏥 Dashboard Phân Tích Dữ Liệu Khám Chữa Bệnh")
    st.caption("Phân tích lượt khám & viện phí — dữ liệu y tế Việt Nam")

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
                ok, db_err = save_to_sqlite(df, os.path.basename(SAMPLE_PATH))
                st.session_state.df = df
                st.session_state.filename = os.path.basename(SAMPLE_PATH)
                if not ok:
                    st.warning(f"Lưu SQLite lỗi: {db_err}")
                st.success("Đã nạp dữ liệu mẫu y tế!")

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

    roles = resolve_columns(df)

    # Thẻ metric tổng quan
    render_overview(df, roles)
    st.divider()

    # Các tab nội dung
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Dữ liệu", "📊 Thống kê", "📈 Biểu đồ", "🗄️ SQLite", "📖 Hướng dẫn"]
    )
    with tab1:
        render_data_tab(df, roles, st.session_state.filename)
    with tab2:
        render_statistics_tab(df, roles)
    with tab3:
        render_charts_tab(df, roles)
    with tab4:
        render_sqlite_tab(df, roles)
    with tab5:
        render_guide_tab()


if __name__ == "__main__":
    main()
