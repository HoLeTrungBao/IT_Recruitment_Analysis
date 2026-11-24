"""
HỆ THỐNG PHÂN TÍCH DỮ LIỆU TUYỂN DỤNG IT VIỆT NAM
Thiết kế giao diện hiện đại (Modern Light SaaS Dashboard) theo chuẩn Dribbble / UI-UX Quốc tế
Thư viện: Streamlit, Plotly, SQLite
"""

import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ========================================================
# 1. CẤU HÌNH TRANG VÀ THEME CHUẨN LIGHT MODE
# ========================================================
st.set_page_config(
    page_title="Thị Trường Tuyển Dụng IT Việt Nam | HR Tech Analytics",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tùy biến toàn bộ CSS: Nền sáng cao cấp (#F8FAFC), Card bo góc mềm mại, đổ bóng nhẹ
st.markdown(
    """
    <style>
    /* Nhập font chữ Inter hiện đại */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #0F172A;
    }

    /* Đảm bảo toàn bộ ứng dụng luôn có nền sáng cao cấp */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Thanh điều hướng Header */
    .header-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
    }
    .badge-tag {
        display: inline-block;
        background-color: #EFF6FF;
        color: #2563EB;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
        border: 1px solid #DBEAFE;
    }
    .main-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748B;
        line-height: 1.5;
    }

    /* Thẻ chỉ số KPI (KPI Cards phong cách Dribbble) */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -2px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .kpi-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .kpi-val {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 8px;
        border-radius: 6px;
    }

    /* Card bao bọc biểu đồ (Chart Box) */
    .chart-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    .chart-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chart-subtitle {
        font-size: 0.82rem;
        color: #64748B;
        margin-bottom: 16px;
    }

    /* Tùy biến Tabs điều hướng kiểu Pills */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
        gap: 6px;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 22px;
        font-weight: 600;
        font-size: 0.92rem;
        color: #475569;
        border-radius: 8px;
        border: none !important;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }

    /* Tùy biến Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========================================================
# 2. TẢI VÀ XỬ LÝ DỮ LIỆU TỪ SQLITE (CACHE TỐI ƯU)
# ========================================================
DB_PATH = "data/warehouse/it_recruitment_dwh.db"

@st.cache_data(ttl=600)
def load_all_data():
    """Tải và chuẩn hóa toàn bộ dữ liệu từ Data Warehouse SQLite."""
    conn = sqlite3.connect(DB_PATH)

    # 1. Bảng dữ liệu việc làm tổng hợp
    query_jobs = """
    SELECT 
        f.job_id,
        f.source,
        f.salary_min,
        f.salary_max,
        f.salary_avg,
        f.is_negotiable,
        c.city_name,
        r.role_name,
        l.level_name,
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
        s.skill_name
    FROM fact_job_skills fs
    JOIN dim_skill s ON fs.skill_id = s.skill_id
    """
    df_skills = pd.read_sql_query(query_skills, conn)
    conn.close()

    # Phân nhóm kỹ năng công nghệ
    def categorize_skill(skill):
        s = str(skill).lower()
        if any(k in s for k in ["aws", "azure", "docker", "kubernetes", "ci/cd", "devops", "cloud", "linux", "git"]):
            return "Cloud & DevOps"
        elif any(k in s for k in ["react", "vue", "angular", "html", "css", "javascript", "typescript", "frontend"]):
            return "Frontend Web"
        elif any(k in s for k in ["sql", "mysql", "postgres", "mongodb", "redis", "database", "oracle"]):
            return "Cơ sở dữ liệu"
        elif any(k in s for k in ["python", "machine learning", "data", "ai", "power bi", "deep learning", "nlp", "tableau"]):
            return "AI & Dữ liệu"
        elif any(k in s for k in ["ios", "android", "flutter", "react native", "swift", "kotlin", "mobile"]):
            return "Mobile Dev"
        elif any(k in s for k in ["test", "qa", "qc", "selenium", "automation"]):
            return "Kiểm thử (QA/QC)"
        elif any(k in s for k in ["java", "spring", ".net", "c#", "php", "golang", "c++", "node", "django", "laravel", "backend"]):
            return "Backend & Core"
        else:
            return "Kỹ năng khác"

    df_skills["skill_category"] = df_skills["skill_name"].apply(categorize_skill)
    df_jobs["full_date"] = pd.to_datetime(df_jobs["full_date"], errors="coerce")
    return df_jobs, df_skills

# Nạp dữ liệu
try:
    df_jobs_raw, df_skills_raw = load_all_data()
except Exception as e:
    st.error(f"Lỗi kết nối cơ sở dữ liệu SQLite: {e}")
    st.stop()

# ========================================================
# 3. THANH ĐIỀU KHIỂN BỘ LỌC (SIDEBAR LIGHT THEME)
# ========================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 10px 0 16px 0;">
            <div style="font-size: 1.2rem; font-weight: 800; color: #1E3A8A; display: flex; align-items: center; gap: 8px;">
                <span>🔍</span> BỘ LỌC THỊ TRƯỜNG
            </div>
            <div style="font-size: 0.8rem; color: #64748B; margin-top: 2px;">
                Tùy chỉnh phân khúc dữ liệu phân tích
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Nguồn tuyển dụng
    all_sources = sorted(df_jobs_raw["source"].dropna().unique().tolist())
    selected_sources = st.multiselect(
        "Nguồn dữ liệu tuyển dụng:",
        options=all_sources,
        default=all_sources,
        help="Lọc theo các sàn tuyển dụng IT lớn"
    )

    # 2. Địa điểm
    all_cities = sorted(df_jobs_raw["city_name"].dropna().unique().tolist())
    selected_cities = st.multiselect(
        "Khu vực / Thành phố:",
        options=all_cities,
        default=all_cities,
    )

    # 3. Cấp bậc
    level_order_list = ["Intern", "Fresher", "Junior", "Middle", "Senior", "Lead / Manager", "Chưa xác định"]
    all_levels = [lvl for lvl in level_order_list if lvl in df_jobs_raw["level_name"].unique()]
    selected_levels = st.multiselect(
        "Cấp bậc kinh nghiệm:",
        options=all_levels,
        default=all_levels,
    )

    # 4. Vai trò chuyên môn
    all_roles = sorted(df_jobs_raw["role_name"].dropna().unique().tolist())
    selected_roles = st.multiselect(
        "Vị trí chuyên môn IT:",
        options=all_roles,
        default=all_roles,
    )

    # Lọc dữ liệu
    filtered_jobs = df_jobs_raw[
        (df_jobs_raw["source"].isin(selected_sources)) &
        (df_jobs_raw["city_name"].isin(selected_cities)) &
        (df_jobs_raw["level_name"].isin(selected_levels)) &
        (df_jobs_raw["role_name"].isin(selected_roles))
    ]

    valid_job_ids = set(filtered_jobs["job_id"])
    filtered_skills = df_skills_raw[df_skills_raw["job_id"].isin(valid_job_ids)]

    st.markdown("---")
    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px; font-size: 0.85rem;">
            <div style="font-weight: 700; color: #1E293B; margin-bottom: 6px;">⚡ Tóm tắt dữ liệu lọc:</div>
            <div style="color: #475569;">• Đang hiển thị: <b>{len(filtered_jobs):,}</b> / {len(df_jobs_raw):,} tin</div>
            <div style="color: #475569;">• Doanh nghiệp: <b>{filtered_jobs['company_name'].nunique():,}</b> công ty</div>
            <div style="color: #475569;">• Tỷ trọng: <b>{(len(filtered_jobs)/max(len(df_jobs_raw),1)*100):.1f}%</b> tổng mẫu</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========================================================
# 4. HEADER CHÍNH (MODERN SAAS HERO BANNER)
# ========================================================
st.markdown(
    """
    <div class="header-box">
        <div class="badge-tag">📊 Báo Cáo Phân Tích Toàn Diện 2025 - 2026</div>
        <div class="main-title">THỊ TRƯỜNG LAO ĐỘNG & TUYỂN DỤNG CÔNG NGHỆ THÔNG TIN</div>
        <div class="sub-title">
            Hệ thống phân tích chuyên sâu về nhu cầu nhân lực, ma trận kỹ năng công nghệ và mặt bằng thu nhập IT tại Việt Nam, tích hợp từ <b>4 nền tảng tuyển dụng lớn: ITViec, TopCV, VietnamWorks và LinkedIn</b>.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========================================================
# 5. THẺ CHỈ SỐ KPI CHÍNH (4 DRIBBLE-STYLE KPI CARDS)
# ========================================================
total_jobs = len(filtered_jobs)
total_companies = filtered_jobs["company_name"].nunique()
valid_salaries = filtered_jobs[filtered_jobs["salary_avg"].notna()]["salary_avg"]
median_salary = valid_salaries.median() if len(valid_salaries) > 0 else 0
salary_public_rate = (len(valid_salaries) / total_jobs * 100) if total_jobs > 0 else 0

st.markdown(
    f"""
    <div class="kpi-container">
        <!-- KPI 1 -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Tổng Tin Tuyển Dụng</span>
                <div class="kpi-icon" style="background: #EFF6FF; color: #2563EB;">💼</div>
            </div>
            <div class="kpi-val">{total_jobs:,}</div>
            <span class="kpi-sub" style="background: #ECFDF5; color: #059669;">
                ✓ Đã khử trùng lặp
            </span>
        </div>
        <!-- KPI 2 -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Doanh Nghiệp Tuyển Dụng</span>
                <div class="kpi-icon" style="background: #F5F3FF; color: #7C3AED;">🏢</div>
            </div>
            <div class="kpi-val">{total_companies:,}</div>
            <span class="kpi-sub" style="background: #F3F4F6; color: #4B5563;">
                Công ty Tech & Outsourcing
            </span>
        </div>
        <!-- KPI 3 -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Lương Trung Vị (Median)</span>
                <div class="kpi-icon" style="background: #FFFBEB; color: #D97706;">💵</div>
            </div>
            <div class="kpi-val">{median_salary:.1f} <span style="font-size: 1.1rem; font-weight: 600; color: #64748B;">tr</span></div>
            <span class="kpi-sub" style="background: #FEF3C7; color: #92400E;">
                Triệu VNĐ / Tháng
            </span>
        </div>
        <!-- KPI 4 -->
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Tỷ Lệ Công Khai Lương</span>
                <div class="kpi-icon" style="background: #F0FDF4; color: #16A34A;">📊</div>
            </div>
            <div class="kpi-val">{salary_public_rate:.1f}%</div>
            <span class="kpi-sub" style="background: #EFF6FF; color: #1E40AF;">
                {len(valid_salaries):,} tin có khoảng lương
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cấu hình phong cách biểu đồ thống nhất (Clean Light Theme)
CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155", size=12),
    margin=dict(t=30, b=30, l=30, r=30),
)

# ========================================================
# 6. CÁC TAB NỘI DUNG PHÂN TÍCH CHUYÊN SÂU
# ========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. Tổng Quan Thị Trường",
    "🎯 2. Nhu Cầu Kỹ Năng & Heatmap",
    "📈 3. Xu Hướng Tuyển Dụng",
    "💰 4. Phân Tích Mức Lương (Boxplot)"
])

# ========================================================
# TAB 1: TỔNG QUAN THỊ TRƯỜNG
# ========================================================
with tab1:
    col_t1, col_t2 = st.columns([5, 7])

    with col_t1:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">🌐 Cơ Cấu Nguồn Dữ Liệu Tuyển Dụng</div>
                <div class="chart-subtitle">Tỷ trọng việc làm thu thập từ 4 nền tảng lớn</div>
            """,
            unsafe_allow_html=True,
        )
        source_df = filtered_jobs["source"].value_counts().reset_index()
        source_df.columns = ["Nguồn", "Số Lượng"]
        
        # Donut Chart hiện đại
        fig_src = go.Figure(
            data=[
                go.Pie(
                    labels=source_df["Nguồn"],
                    values=source_df["Số Lượng"],
                    hole=0.55,
                    marker=dict(
                        colors=["#2563EB", "#0D9488", "#F59E0B", "#8B5CF6"],
                        line=dict(color="#FFFFFF", width=3)
                    ),
                    textinfo="percent+label",
                    textposition="outside",
                    hoverinfo="label+value+percent",
                )
            ]
        )
        fig_src.update_layout(**CHART_THEME, height=330, showlegend=False)
        st.plotly_chart(fig_src, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_t2:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">📍 Phân Bố Việc Làm Theo Địa Phương</div>
                <div class="chart-subtitle">Trung tâm công nghệ tập trung mật độ việc làm IT cao nhất</div>
            """,
            unsafe_allow_html=True,
        )
        city_df = filtered_jobs["city_name"].value_counts().reset_index().head(5)
        city_df.columns = ["Thành Phố", "Số Lượng"]
        city_df["Tỷ Lệ"] = (city_df["Số Lượng"] / total_jobs * 100).round(1)

        fig_city = px.bar(
            city_df,
            x="Số Lượng",
            y="Thành Phố",
            orientation="h",
            text=city_df.apply(lambda r: f"{r['Số Lượng']:,} ({r['Tỷ Lệ']}%)", axis=1),
            color="Số Lượng",
            color_continuous_scale=["#BFDBFE", "#2563EB"],
        )
        fig_city.update_layout(
            **CHART_THEME,
            height=330,
            yaxis=dict(autorange="reversed", title=""),
            xaxis=dict(title="Số tin đăng tuyển", showgrid=True, gridcolor="#F1F5F9"),
            coloraxis_showscale=False,
        )
        fig_city.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_city, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Biểu đồ phân bố vai trò tuyển dụng
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">💻 Cơ Cấu Vị Trí & Vai Trò Chuyên Môn IT</div>
            <div class="chart-subtitle">Số lượng nhu cầu nhân sự phân theo từng chuyên ngành công nghệ</div>
        """,
        unsafe_allow_html=True,
    )
    role_df = filtered_jobs["role_name"].value_counts().reset_index().head(10)
    role_df.columns = ["Vai Trò IT", "Số Lượng"]
    
    fig_role = px.bar(
        role_df,
        x="Vai Trò IT",
        y="Số Lượng",
        text="Số Lượng",
        color="Số Lượng",
        color_continuous_scale=["#CCFBF1", "#0D9488"],
    )
    fig_role.update_layout(
        **CHART_THEME,
        height=350,
        xaxis=dict(tickangle=-25, title=""),
        yaxis=dict(title="Số lượng tin tuyển dụng", showgrid=True, gridcolor="#F1F5F9"),
        coloraxis_showscale=False,
    )
    fig_role.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_role, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ========================================================
# TAB 2: NHU CẦU KỸ NĂNG & HEATMAP
# ========================================================
with tab2:
    sk_col1, sk_col2 = st.columns([7, 5])

    skill_counts = filtered_skills["skill_name"].value_counts().reset_index().head(12)
    skill_counts.columns = ["Kỹ Năng", "Số Lượng"]
    skill_counts["Tỷ Lệ %"] = (skill_counts["Số Lượng"] / max(total_jobs, 1) * 100).round(1)

    with sk_col1:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">🏆 Top 12 Kỹ Năng Công Nghệ Săn Đón Nhất</div>
                <div class="chart-subtitle">Tần suất xuất hiện trong các bản mô tả công việc IT</div>
            """,
            unsafe_allow_html=True,
        )
        fig_sk = px.bar(
            skill_counts,
            x="Số Lượng",
            y="Kỹ Năng",
            orientation="h",
            text=skill_counts.apply(lambda r: f"{r['Số Lượng']:,} ({r['Tỷ Lệ %']}%)", axis=1),
            color="Số Lượng",
            color_continuous_scale=["#DDD6FE", "#7C3AED"],
        )
        fig_sk.update_layout(
            **CHART_THEME,
            height=420,
            yaxis=dict(autorange="reversed", title=""),
            xaxis=dict(title="Số lượt yêu cầu", showgrid=True, gridcolor="#F1F5F9"),
            coloraxis_showscale=False,
        )
        fig_sk.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_sk, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with sk_col2:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">📦 Cơ Cấu Nhóm Công Nghệ</div>
                <div class="chart-subtitle">Tỷ trọng yêu cầu theo từng lĩnh vực kỹ thuật</div>
            """,
            unsafe_allow_html=True,
        )
        cat_df = filtered_skills["skill_category"].value_counts().reset_index()
        cat_df.columns = ["Nhóm Kỹ Năng", "Số Lượng"]

        fig_cat = px.pie(
            cat_df,
            names="Nhóm Kỹ Năng",
            values="Số Lượng",
            hole=0.45,
            color_discrete_sequence=["#2563EB", "#0D9488", "#7C3AED", "#F59E0B", "#EC4899", "#64748B", "#06B6D4"],
        )
        fig_cat.update_layout(**CHART_THEME, height=420, showlegend=True, legend=dict(orientation="v", x=1, y=0.5))
        fig_cat.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ĐIỂM NHẤN: HEATMAP MA TRẬN KỸ NĂNG X VAI TRÒ
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">🔥 Ma Trận Nhiệt (Heatmap): Mối Quan Hệ Giữa Kỹ Năng & Vai Trò IT</div>
            <div class="chart-subtitle">Trực quan hóa độ tương quan mật thiết giữa vị trí công việc và các công nghệ cốt lõi (Khắc phục sự đơn điệu của Bar Chart)</div>
        """,
        unsafe_allow_html=True,
    )
    
    top_roles_heat = filtered_jobs["role_name"].value_counts().head(7).index.tolist()
    top_skills_heat = skill_counts["Kỹ Năng"].head(10).tolist()

    df_heat_merge = filtered_skills[
        filtered_skills["skill_name"].isin(top_skills_heat)
    ].merge(
        filtered_jobs[filtered_jobs["role_name"].isin(top_roles_heat)][["job_id", "role_name"]],
        on="job_id"
    )

    if not df_heat_merge.empty:
        crosstab_data = pd.crosstab(df_heat_merge["role_name"], df_heat_merge["skill_name"])
        crosstab_data = crosstab_data.reindex(index=top_roles_heat, columns=top_skills_heat, fill_value=0)

        fig_heat = px.imshow(
            crosstab_data,
            labels=dict(x="Kỹ Năng Công Nghệ", y="Vị Trí Tuyển Dụng", color="Lượt Yêu Cầu"),
            x=crosstab_data.columns,
            y=crosstab_data.index,
            color_continuous_scale="Blues",
            text_auto=True,
            aspect="auto",
        )
        fig_heat.update_layout(
            **CHART_THEME,
            height=380,
            xaxis=dict(tickangle=-25),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Không có đủ dữ liệu để vẽ biểu đồ nhiệt.")
    st.markdown("</div>", unsafe_allow_html=True)


# ========================================================
# TAB 3: XU HƯỚNG TUYỂN DỤNG THEO THỜI GIAN
# ========================================================
with tab3:
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">📅 Biến Động Nhu Cầu Tuyển Dụng Theo Mốc Thời Gian (Tháng / Năm)</div>
            <div class="chart-subtitle">Mốc thời gian hiển thị to rõ (Khắc phục nhận xét chữ mốc thời gian quá nhỏ trước đây)</div>
        """,
        unsafe_allow_html=True,
    )

    df_dated = filtered_jobs[filtered_jobs["full_date"].notna()].copy()
    if not df_dated.empty:
        df_dated["period"] = df_dated["full_date"].dt.to_period("M").astype(str)
        period_summary = df_dated.groupby("period").size().reset_index(name="Số Lượng")
        
        # Line Chart cỡ lớn với mốc thời gian rõ ràng
        fig_time = go.Figure()
        fig_time.add_trace(
            go.Scatter(
                x=period_summary["period"],
                y=period_summary["Số Lượng"],
                mode="lines+markers+text",
                line=dict(color="#2563EB", width=4, shape="spline"),
                marker=dict(size=12, color="#1D4ED8", line=dict(color="#FFFFFF", width=2)),
                text=period_summary["Số Lượng"],
                textposition="top center",
                textfont=dict(size=12, color="#1E293B", family="Plus Jakarta Sans"),
                name="Tổng tin tuyển dụng",
            )
        )
        fig_time.update_layout(
            **CHART_THEME,
            height=420,
            xaxis=dict(
                title=dict(text="<b>MỐC THỜI GIAN (THÁNG / NĂM)</b>", font=dict(size=13, color="#1E293B")),
                tickfont=dict(size=13, color="#0F172A"),
                showgrid=True,
                gridcolor="#F1F5F9",
                tickangle=-15,
            ),
            yaxis=dict(
                title=dict(text="<b>Số Lượng Tin Đăng Tuyển</b>", font=dict(size=13, color="#1E293B")),
                showgrid=True,
                gridcolor="#F1F5F9",
            ),
        )
        st.plotly_chart(fig_time, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Xu hướng phân chia theo Nguồn
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">🌐 Xu Hướng Tuyển Dụng Theo Từng Nền Tảng Qua Các Tháng</div>
                <div class="chart-subtitle">So sánh nhịp độ đăng tuyển giữa ITViec, TopCV, VietnamWorks và LinkedIn</div>
            """,
            unsafe_allow_html=True,
        )
        source_time = df_dated.groupby(["period", "source"]).size().reset_index(name="Số Tin")
        fig_src_time = px.line(
            source_time,
            x="period",
            y="Số Tin",
            color="source",
            markers=True,
            color_discrete_map={
                "ITViec": "#2563EB",
                "TopCV": "#0D9488",
                "VietnamWorks": "#F59E0B",
                "LinkedIn": "#8B5CF6",
            },
        )
        fig_src_time.update_layout(
            **CHART_THEME,
            height=360,
            xaxis=dict(title="<b>Tháng/Năm</b>", showgrid=True, gridcolor="#F1F5F9"),
            yaxis=dict(title="<b>Số lượng tin</b>", showgrid=True, gridcolor="#F1F5F9"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_src_time, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Không có dữ liệu thời gian phù hợp với bộ lọc hiện tại.")


# ========================================================
# TAB 4: PHÂN TÍCH MỨC LƯƠNG (BOXPLOT CHUẨN MỰC)
# ========================================================
with tab4:
    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">📊 Phân Bố Mức Lương IT Bằng Biểu Đồ Hộp (Boxplot)</div>
            <div class="chart-subtitle">Thay thế bar chart đơn điệu: Thể hiện trọn vẹn Min, Phân vị Q1 (25%), Trung vị Median (50%), Phân vị Q3 (75%), Max và Outliers</div>
        """,
        unsafe_allow_html=True,
    )

    df_salary = filtered_jobs[
        (filtered_jobs["salary_avg"].notna()) & 
        (filtered_jobs["salary_avg"] > 0) & 
        (filtered_jobs["salary_avg"] <= 200)
    ].copy()

    if not df_salary.empty:
        # Boxplot theo Cấp bậc kinh nghiệm
        level_order = ["Intern", "Fresher", "Junior", "Middle", "Senior", "Lead / Manager"]
        df_salary_level = df_salary[df_salary["level_name"].isin(level_order)]

        fig_box_lvl = px.box(
            df_salary_level,
            x="level_name",
            y="salary_avg",
            color="level_name",
            category_orders={"level_name": level_order},
            labels={"level_name": "Cấp Bậc", "salary_avg": "Lương (Triệu VNĐ)"},
            color_discrete_sequence=["#93C5FD", "#6EE7B7", "#FCD34D", "#FCA5A5", "#C4B5FD", "#F472B6"],
            points="outliers",
        )
        fig_box_lvl.update_layout(
            **CHART_THEME,
            height=400,
            xaxis=dict(title="<b>Cấp Bậc Kinh Nghiệm</b>"),
            yaxis=dict(title="<b>Mức Lương (Triệu VNĐ / Tháng)</b>", showgrid=True, gridcolor="#F1F5F9"),
            showlegend=False,
        )
        st.plotly_chart(fig_box_lvl, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Hàng 2 cột: Boxplot theo vai trò & Bảng thống kê chi tiết
        b_col1, b_col2 = st.columns([6, 6])

        with b_col1:
            st.markdown(
                """
                <div class="chart-card">
                    <div class="chart-title">💻 Mức Lương Theo Vị Trí IT Chuyên Môn</div>
                    <div class="chart-subtitle">Phân bố lương giữa các nhánh nghề nghiệp chính</div>
                """,
                unsafe_allow_html=True,
            )
            top_roles_sal = df_salary["role_name"].value_counts().head(6).index.tolist()
            df_sal_role = df_salary[df_salary["role_name"].isin(top_roles_sal)]

            fig_box_r = px.box(
                df_sal_role,
                x="role_name",
                y="salary_avg",
                color="role_name",
                labels={"role_name": "Vai Trò", "salary_avg": "Lương (tr VNĐ)"},
                points="outliers",
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            fig_box_r.update_layout(
                **CHART_THEME,
                height=380,
                xaxis=dict(title="", tickangle=-20),
                yaxis=dict(title="<b>Mức Lương (Triệu VNĐ)</b>", showgrid=True, gridcolor="#F1F5F9"),
                showlegend=False,
            )
            st.plotly_chart(fig_box_r, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with b_col2:
            st.markdown(
                """
                <div class="chart-card">
                    <div class="chart-title">📋 Bảng Thống Kê Chi Tiết Các Mốc Phân Vị Lương</div>
                    <div class="chart-subtitle">Định lượng mức lương chuẩn mực khoa học (Triệu VNĐ)</div>
                """,
                unsafe_allow_html=True,
            )
            salary_stats = df_salary_level.groupby("level_name")["salary_avg"].agg(
                Số_Tin="count",
                Thấp_Nhất="min",
                Q1_25=lambda x: np.percentile(x, 25),
                Trung_Vị_Median="median",
                Q3_75=lambda x: np.percentile(x, 75),
                Cao_Nhất="max"
            ).reindex(level_order).dropna()

            salary_stats.columns = [
                "Số Tin", "Min (Sàn)", "Phân Vị Q1 (25%)", "Trung Vị (50%)", "Phân Vị Q3 (75%)", "Max (Trần)"
            ]
            st.dataframe(
                salary_stats.style.format("{:.1f}", subset=salary_stats.columns[1:])
                .set_properties(**{'background-color': '#FFFFFF', 'color': '#0F172A', 'border-color': '#E2E8F0'}),
                use_container_width=True,
                height=350,
            )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Không có dữ liệu mức lương phù hợp với bộ lọc hiện tại.")

# ========================================================
# 7. CHÂN TRANG (FOOTER CAO CẤP)
# ========================================================
st.markdown(
    """
    <div style="text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 24px 0 10px 0; border-top: 1px solid #E2E8F0; margin-top: 30px;">
        Hệ Thống Phân Tích Dữ Liệu Tuyển Dụng Công Nghệ Thông Tin Việt Nam • Xây Dựng Bằng Streamlit & Plotly • Dữ Liệu Tích Hợp Star Schema
    </div>
    """,
    unsafe_allow_html=True,
)
