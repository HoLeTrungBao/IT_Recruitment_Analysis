"""
Ứng dụng Dashboard Phân Tích Tuyển Dụng Công Nghệ Thông Tin Việt Nam
Sử dụng: Streamlit, Plotly, SQLite
"""

import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Cấu hình trang giao diện
st.set_page_config(
    page_title="Thị Trường Tuyển Dụng IT Việt Nam",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tùy biến giao diện CSS (tiếng Việt, hiện đại, màu sắc trực quan)
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        text-align: center;
    }
    .metric-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #1E40AF;
    }
    .metric-note {
        font-size: 0.8rem;
        color: #10B981;
        margin-top: 4px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Kết nối cơ sở dữ liệu và tải dữ liệu có bộ nhớ đệm (Cache)
DB_PATH = "data/warehouse/it_recruitment_dwh.db"

@st.cache_data(ttl=600)
def load_all_data():
    """Tải toàn bộ dữ liệu từ kho dữ liệu SQLite."""
    conn = sqlite3.connect(DB_PATH)

    # 1. Bảng dữ liệu việc làm tổng hợp
    query_jobs = """
    SELECT 
        f.job_id,
        f.source,
        f.salary_min,
        f.salary_max,
        f.salary_avg,
        f.is_salary_negotiable,
        c.city_name,
        c.region,
        r.role_name,
        r.role_category,
        l.level_name,
        l.standard_level,
        cp.company_name,
        d.full_date,
        d.month,
        d.year,
        d.month_year
    FROM fact_job_postings f
    LEFT JOIN dim_city c ON f.city_id = c.city_id
    LEFT JOIN dim_role r ON f.role_id = r.role_id
    LEFT JOIN dim_level l ON f.level_id = l.level_id
    LEFT JOIN dim_company cp ON f.company_id = cp.company_id
    LEFT JOIN dim_date d ON f.date_id = d.date_id
    """
    df_jobs = pd.read_sql_query(query_jobs, conn)

    # 2. Bảng kỹ năng gắn với từng việc làm
    query_skills = """
    SELECT 
        fs.job_id,
        s.skill_name,
        s.skill_category
    FROM fact_job_skills fs
    JOIN dim_skill s ON fs.skill_id = s.skill_id
    """
    df_skills = pd.read_sql_query(query_skills, conn)
    conn.close()

    # Chuẩn hóa cột ngày tháng
    df_jobs["full_date"] = pd.to_datetime(df_jobs["full_date"], errors="coerce")
    return df_jobs, df_skills

# Nạp dữ liệu
try:
    df_jobs_raw, df_skills_raw = load_all_data()
except Exception as e:
    st.error(f"Lỗi kết nối cơ sở dữ liệu SQLite: {e}")
    st.stop()

# ============================
# THANH BỘ LỌC (SIDEBAR)
# ============================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3281/3281329.png", width=64)
st.sidebar.title("BỘ LỌC DỮ LIỆU")
st.sidebar.markdown("---")

# 1. Bộ lọc Nguồn dữ liệu
all_sources = sorted(df_jobs_raw["source"].dropna().unique().tolist())
selected_sources = st.sidebar.multiselect(
    "Nguồn dữ liệu tuyển dụng:",
    options=all_sources,
    default=all_sources,
    help="Chọn một hoặc nhiều nguồn (ITViec, TopCV, VietnamWorks, LinkedIn)"
)

# 2. Bộ lọc Địa điểm / Khu vực
all_cities = sorted(df_jobs_raw["city_name"].dropna().unique().tolist())
selected_cities = st.sidebar.multiselect(
    "Địa điểm làm việc:",
    options=all_cities,
    default=all_cities,
)

# 3. Bộ lọc Cấp bậc (Level)
all_levels = [
    lvl for lvl in ["Intern", "Fresher", "Junior", "Middle", "Senior", "Lead / Manager", "Chưa xác định"]
    if lvl in df_jobs_raw["level_name"].unique()
]
selected_levels = st.sidebar.multiselect(
    "Cấp bậc kinh nghiệm:",
    options=all_levels,
    default=all_levels,
)

# 4. Bộ lọc Vai trò IT
all_roles = sorted(df_jobs_raw["role_name"].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect(
    "Vai trò chuyên môn IT:",
    options=all_roles,
    default=all_roles,
)

# Áp dụng bộ lọc vào DataFrame việc làm
filtered_jobs = df_jobs_raw[
    (df_jobs_raw["source"].isin(selected_sources)) &
    (df_jobs_raw["city_name"].isin(selected_cities)) &
    (df_jobs_raw["level_name"].isin(selected_levels)) &
    (df_jobs_raw["role_name"].isin(selected_roles))
]

# Lọc DataFrame kỹ năng theo các job_id hợp lệ
valid_job_ids = set(filtered_jobs["job_id"])
filtered_skills = df_skills_raw[df_skills_raw["job_id"].isin(valid_job_ids)]

# Thông tin trạng thái kho dữ liệu ở Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Trạng thái Kho Dữ Liệu")
st.sidebar.info(
    f"""
    - **Tổng số việc làm (gốc):** {len(df_jobs_raw):,} tin
    - **Đang hiển thị:** {len(filtered_jobs):,} tin
    - **Số doanh nghiệp:** {filtered_jobs['company_name'].nunique():,} công ty
    - **Nguồn tích hợp:** 4 nguồn chuẩn hóa
    """
)

# ============================
# TIÊU ĐỀ CHÍNH
# ============================
st.markdown('<div class="main-header">HỆ THỐNG PHÂN TÍCH DỮ LIỆU TUYỂN DỤNG IT VIỆT NAM</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Phân tích đa chiều về thị trường việc làm, kỹ năng công nghệ, mức lương và xu hướng biến động từ 4 nguồn dữ liệu lớn: ITViec, TopCV, VietnamWorks và LinkedIn.</div>',
    unsafe_allow_html=True,
)

# Hiển thị các Tab nội dung
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. Tổng Quan Thị Trường",
    "🎯 2. Nhu Cầu Kỹ Năng",
    "📈 3. Xu Hướng Biến Động",
    "💰 4. Phân Tích Mức Lương"
])

# ========================================================
# TAB 1: TỔNG QUAN THỊ TRƯỜNG
# ========================================================
with tab1:
    st.subheader("Tổng Quan Thị Trường Tuyển Dụng IT")

    # 4 Thẻ KPI nổi bật
    total_jobs = len(filtered_jobs)
    total_companies = filtered_jobs["company_name"].nunique()
    
    # Tính lương trung vị và tỷ lệ công khai lương
    valid_salaries = filtered_jobs[filtered_jobs["salary_avg"].notna()]["salary_avg"]
    median_salary = valid_salaries.median() if len(valid_salaries) > 0 else 0
    salary_public_rate = (len(valid_salaries) / total_jobs * 100) if total_jobs > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Tổng Tin Tuyển Dụng</div>
                <div class="metric-value">{total_jobs:,}</div>
                <div class="metric-note">Đã chuẩn hóa & khử trùng</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Doanh Nghiệp Tuyển Dụng</div>
                <div class="metric-value">{total_companies:,}</div>
                <div class="metric-note">Công ty IT & Tech Hubs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Lương Trung Vị (Median)</div>
                <div class="metric-value">{median_salary:.1f} tr</div>
                <div class="metric-note">Triệu VNĐ / Tháng</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Tỷ Lệ Công Khai Lương</div>
                <div class="metric-value">{salary_public_rate:.1f}%</div>
                <div class="metric-note">{len(valid_salaries):,} tin có khoảng lương rõ</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2 Biểu đồ hàng 1: Cơ cấu nguồn dữ liệu & Phân bố địa lý
    r1_col1, r1_col2 = st.columns(2)

    with r1_col1:
        st.markdown("##### 📌 Cơ Cấu Nguồn Dữ Liệu Thu Thập")
        source_counts = filtered_jobs["source"].value_counts().reset_index()
        source_counts.columns = ["Nguồn", "Số Lượng"]
        fig_source = px.pie(
            source_counts,
            names="Nguồn",
            values="Số Lượng",
            hole=0.45,
            color_discrete_sequence=["#1E40AF", "#0EA5E9", "#10B981", "#F59E0B"],
        )
        fig_source.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#FFFFFF", width=2)),
        )
        fig_source.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
        st.plotly_chart(fig_source, use_container_width=True)

    with r1_col2:
        st.markdown("##### 📌 Phân Bố Việc Làm Theo Địa Phương")
        city_counts = filtered_jobs["city_name"].value_counts().reset_index().head(6)
        city_counts.columns = ["Thành Phố", "Số Lượng"]
        fig_city = px.bar(
            city_counts,
            x="Số Lượng",
            y="Thành Phố",
            orientation="h",
            color="Số Lượng",
            color_continuous_scale="Blues",
            text="Số Lượng",
        )
        fig_city.update_layout(
            yaxis=dict(autorange="reversed"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_city, use_container_width=True)

    # Biểu đồ hàng 2: Cơ cấu vị trí tuyển dụng IT
    st.markdown("##### 📌 Phân Bố Việc Làm Theo Vai Trò Chuyên Môn IT")
    role_counts = filtered_jobs["role_name"].value_counts().reset_index().head(12)
    role_counts.columns = ["Vai Trò IT", "Số Lượng"]
    fig_role = px.bar(
        role_counts,
        x="Vai Trò IT",
        y="Số Lượng",
        color="Số Lượng",
        color_continuous_scale="Teal",
        text="Số Lượng",
    )
    fig_role.update_layout(
        xaxis_tickangle=-30,
        margin=dict(t=10, b=10, l=10, r=10),
        height=350,
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_role, use_container_width=True)


# ========================================================
# TAB 2: NHU CẦU KỸ NĂNG CÔNG NGHỆ
# ========================================================
with tab2:
    st.subheader("Nhu Cầu Kỹ Năng & Công Nghệ Được Săn Đón")
    st.markdown(
        "Phân tích chuyên sâu về các kỹ năng lập trình, framework và công nghệ được yêu cầu nhiều nhất; kết hợp ma trận liên kết giữa kỹ năng và vai trò công việc."
    )

    skill_counts = filtered_skills["skill_name"].value_counts().reset_index().head(15)
    skill_counts.columns = ["Kỹ Năng", "Số Lượng Yêu Cầu"]
    skill_counts["Tỷ Lệ Tuyển Dụng (%)"] = (
        skill_counts["Số Lượng Yêu Cầu"] / max(total_jobs, 1) * 100
    ).round(1)

    s_col1, s_col2 = st.columns([1, 1])

    with s_col1:
        st.markdown("##### 🏆 Top 15 Kỹ Năng Công Nghệ Hàng Đầu")
        fig_top_skills = px.bar(
            skill_counts,
            x="Số Lượng Yêu Cầu",
            y="Kỹ Năng",
            orientation="h",
            color="Số Lượng Yêu Cầu",
            color_continuous_scale="Viridis",
            text=skill_counts["Tỷ Lệ Tuyển Dụng (%)"].apply(lambda v: f"{v}%"),
        )
        fig_top_skills.update_layout(
            yaxis=dict(autorange="reversed"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=480,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_top_skills, use_container_width=True)

    with s_col2:
        st.markdown("##### 📦 Cơ Cấu Nhóm Kỹ Năng Công Nghệ")
        cat_counts = filtered_skills["skill_category"].value_counts().reset_index()
        cat_counts.columns = ["Nhóm Kỹ Năng", "Số Lượng"]
        fig_cat = px.pie(
            cat_counts,
            names="Nhóm Kỹ Năng",
            values="Số Lượng",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_cat.update_traces(textposition="inside", textinfo="percent+label")
        fig_cat.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=480)
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")
    # ĐIỂM NHẤN: HEATMAP MA TRẬN KỸ NĂNG X VAI TRÒ IT (Tránh dùng quá nhiều Bar Chart)
    st.markdown("### 🔥 Ma Trận Nhiệt (Heatmap): Mối Quan Hệ Giữa Kỹ Năng & Vai Trò IT")
    st.caption("Biểu đồ thể hiện mật độ xuất hiện của từng kỹ năng công nghệ trong từng vị trí tuyển dụng chuyên môn.")

    # Lấy top 8 vai trò và top 12 kỹ năng phổ biến nhất để vẽ heatmap trực quan
    top_roles = filtered_jobs["role_name"].value_counts().head(8).index.tolist()
    top_skills_list = skill_counts["Kỹ Năng"].head(12).tolist()

    # Ghép bảng jobs và skills
    df_js = filtered_skills[
        (filtered_skills["skill_name"].isin(top_skills_list))
    ].merge(
        filtered_jobs[filtered_jobs["role_name"].isin(top_roles)][["job_id", "role_name"]],
        on="job_id"
    )

    if not df_js.empty:
        heatmap_data = pd.crosstab(df_js["role_name"], df_js["skill_name"])
        # Đảm bảo đúng thứ tự
        heatmap_data = heatmap_data.reindex(index=top_roles, columns=top_skills_list, fill_value=0)

        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Kỹ Năng Công Nghệ", y="Vai Trò Tuyển Dụng", color="Số Lượt Xuất Hiện"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale="YlGnBu",
            text_auto=True,
            aspect="auto",
        )
        fig_heat.update_layout(
            xaxis_tickangle=-30,
            height=420,
            margin=dict(t=20, b=30, l=30, r=20),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Không có đủ dữ liệu để vẽ biểu đồ nhiệt theo bộ lọc hiện tại.")


# ========================================================
# TAB 3: XU HƯỚNG BIẾN ĐỘNG THEO THỜI GIAN
# ========================================================
with tab3:
    st.subheader("Xu Hướng Tuyển Dụng Theo Mốc Thời Gian (Tháng / Năm)")
    st.markdown(
        "> **Lưu ý:** Biểu đồ hiển thị nổi bật các mốc thời gian rõ ràng (Tháng/Năm) giúp theo dõi chu kỳ tuyển dụng của các công ty công nghệ."
    )

    # Lọc dữ liệu có mốc thời gian hợp lệ
    df_dated = filtered_jobs[filtered_jobs["full_date"].notna()].copy()

    if not df_dated.empty:
        # Chuẩn hóa về chu kỳ Tháng-Năm (Period)
        df_dated["period"] = df_dated["full_date"].dt.to_period("M").astype(str)
        
        # Sắp xếp theo chu kỳ
        period_counts = df_dated.groupby(["period", "source"]).size().reset_index(name="Số Lượng Tin")
        period_totals = df_dated.groupby("period").size().reset_index(name="Tổng Tin Tuyển Dụng")

        # 1. BIỂU ĐỒ ĐƯỜNG LỚN (LINE CHART): TỔNG NHU CẦU TUYỂN DỤNG THEO THÁNG
        st.markdown("##### 📅 Biểu Đồ Đường: Xu Hướng Nhu Cầu Tuyển Dụng Toàn Thị Trường")
        fig_timeline = px.line(
            period_totals,
            x="period",
            y="Tổng Tin Tuyển Dụng",
            markers=True,
            text="Tổng Tin Tuyển Dụng",
            title="Biến Động Nhu Cầu Tuyển Dụng IT Qua Các Tháng",
        )
        fig_timeline.update_traces(
            line=dict(color="#2563EB", width=3.5),
            marker=dict(size=10, color="#1D4ED8"),
            textposition="top center",
        )
        fig_timeline.update_layout(
            xaxis_title="<b>Mốc Thời Gian (Tháng/Năm)</b>",
            yaxis_title="<b>Số Lượng Tin Đăng Tuyển</b>",
            xaxis=dict(
                tickfont=dict(size=13, color="#1F2937"),
                tickangle=-20,
            ),
            yaxis=dict(tickfont=dict(size=12)),
            height=400,
            margin=dict(t=40, b=40, l=40, r=40),
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

        # 2. XU HƯỚNG PHÂN TÁCH THEO NGUỒN TUYỂN DỤNG
        st.markdown("##### 🌐 Xu Hướng Tuyển Dụng Chi Tiết Theo Nguồn Dữ Liệu")
        fig_source_trend = px.line(
            period_counts,
            x="period",
            y="Số Lượng Tin",
            color="source",
            markers=True,
            labels={"period": "Tháng/Năm", "Số Lượng Tin": "Số Lượng Tin", "source": "Nguồn"},
            color_discrete_map={
                "ITViec": "#1E40AF",
                "TopCV": "#10B981",
                "VietnamWorks": "#F59E0B",
                "LinkedIn": "#0EA5E9",
            },
        )
        fig_source_trend.update_layout(
            xaxis_title="<b>Mốc Thời Gian (Tháng/Năm)</b>",
            yaxis_title="<b>Số Lượng Tin Tuyển</b>",
            height=380,
            margin=dict(t=20, b=40, l=40, r=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_source_trend, use_container_width=True)

        # 3. XU HƯỚNG CÁC NHÓM KỸ NĂNG HOT THEO THỜI GIAN
        st.markdown("##### 🚀 Xu Hướng Quan Tâm Kỹ Năng Công Nghệ Qua Các Tháng")
        df_dated_skills = df_dated[["job_id", "period"]].merge(filtered_skills, on="job_id")
        skill_trend = df_dated_skills.groupby(["period", "skill_category"]).size().reset_index(name="Lượt Yêu Cầu")

        fig_skill_trend = px.area(
            skill_trend,
            x="period",
            y="Lượt Yêu Cầu",
            color="skill_category",
            labels={"period": "Tháng/Năm", "skill_category": "Nhóm Kỹ Năng"},
        )
        fig_skill_trend.update_layout(
            xaxis_title="<b>Mốc Thời Gian (Tháng/Năm)</b>",
            yaxis_title="<b>Tổng Lượt Yêu Cầu Kỹ Năng</b>",
            height=380,
            margin=dict(t=20, b=40, l=40, r=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_skill_trend, use_container_width=True)
    else:
        st.warning("Không có dữ liệu thời gian phù hợp với bộ lọc hiện tại.")


# ========================================================
# TAB 4: PHÂN TÍCH MỨC LƯƠNG IT
# ========================================================
with tab4:
    st.subheader("Phân Bố & Mức Lương IT (Triệu VNĐ / Tháng)")
    st.markdown(
        "> **Sử dụng Boxplot (Biểu đồ hộp):** Hiển thị trực quan toàn bộ phân bố mức lương bao gồm: Mức sàn (Min), Phân vị thứ nhất (Q1 - 25%), Mức lương trung vị (Median - 50%), Phân vị thứ ba (Q3 - 75%), Mức trần (Max) và các giá trị ngoại lai (Outliers)."
    )

    # Lọc các tin có thông tin mức lương hợp lệ và nằm trong khoảng thực tế (< 200 triệu/tháng để tránh outliers dị biệt)
    df_salary = filtered_jobs[
        (filtered_jobs["salary_avg"].notna()) & 
        (filtered_jobs["salary_avg"] > 0) & 
        (filtered_jobs["salary_avg"] <= 200)
    ].copy()

    if not df_salary.empty:
        # Hàng 1: Boxplot mức lương theo cấp bậc kinh nghiệm
        st.markdown("##### 🎓 Phân Bố Mức Lương Theo Cấp Bậc Kinh Nghiệm (Level)")
        level_order = ["Intern", "Fresher", "Junior", "Middle", "Senior", "Lead / Manager"]
        df_salary_level = df_salary[df_salary["level_name"].isin(level_order)]

        fig_box_level = px.box(
            df_salary_level,
            x="level_name",
            y="salary_avg",
            color="level_name",
            category_orders={"level_name": level_order},
            labels={"level_name": "Cấp Bậc", "salary_avg": "Mức Lương (Triệu VNĐ)"},
            points="outliers",
        )
        fig_box_level.update_layout(
            xaxis_title="<b>Cấp Bậc Kinh Nghiệm</b>",
            yaxis_title="<b>Mức Lương Trung Bình (Triệu VNĐ/tháng)</b>",
            showlegend=False,
            height=400,
            margin=dict(t=20, b=20, l=40, r=20),
        )
        st.plotly_chart(fig_box_level, use_container_width=True)

        # Hàng 2: Boxplot mức lương theo Vai trò IT
        st.markdown("##### 💻 Phân Bố Mức Lương Theo Vai Trò Chuyên Môn IT")
        top_roles_salary = df_salary["role_name"].value_counts().head(8).index.tolist()
        df_salary_role = df_salary[df_salary["role_name"].isin(top_roles_salary)]

        fig_box_role = px.box(
            df_salary_role,
            x="role_name",
            y="salary_avg",
            color="role_name",
            labels={"role_name": "Vai Trò IT", "salary_avg": "Mức Lương (Triệu VNĐ)"},
            points="outliers",
        )
        fig_box_role.update_layout(
            xaxis_title="<b>Vai Trò Tuyển Dụng</b>",
            yaxis_title="<b>Mức Lương Trung Bình (Triệu VNĐ/tháng)</b>",
            xaxis_tickangle=-25,
            showlegend=False,
            height=430,
            margin=dict(t=20, b=40, l=40, r=20),
        )
        st.plotly_chart(fig_box_role, use_container_width=True)

        # Bảng số liệu thống kê chi tiết
        st.markdown("##### 📋 Bảng Thống Kê Chi Tiết Mức Lương Theo Cấp Bậc")
        salary_stats = df_salary_level.groupby("level_name")["salary_avg"].agg(
            Số_Tin="count",
            Thấp_Nhất="min",
            Q1_25PhanTram=lambda x: np.percentile(x, 25),
            Trung_Vi_Median="median",
            Q3_75PhanTram=lambda x: np.percentile(x, 75),
            Cao_Nhất="max"
        ).reindex(level_order).dropna()

        salary_stats.columns = [
            "Số Lượng Tin", "Lương Thấp Nhất (tr)", "Phân Vị Q1 25% (tr)", 
            "Lương Trung Vị (tr)", "Phân Vị Q3 75% (tr)", "Lương Cao Nhất (tr)"
        ]
        st.dataframe(salary_stats.style.format("{:.1f}", subset=salary_stats.columns[1:]), use_container_width=True)
    else:
        st.info("Không có dữ liệu mức lương phù hợp với bộ lọc hiện tại.")

# ============================
# CHÂN TRANG (FOOTER)
# ============================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; font-size: 0.85rem;">
        Dự án Phân Tích Tuyển Dụng IT Việt Nam • Xây dựng bởi Nhóm Sinh Viên Nghiên Cứu • Sử dụng Streamlit & Plotly
    </div>
    """,
    unsafe_allow_html=True,
)
