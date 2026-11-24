"""
HỆ THỐNG PHÂN TÍCH DỮ LIỆU TUYỂN DỤNG CÔNG NGHỆ THÔNG TIN VIỆT NAM
Giao diện: Thiết kế sáng sủa, tinh tế, tối ưu trải nghiệm người dùng
Ngôn ngữ: Tiếng Việt 100% (giữ nguyên thuật ngữ kỹ thuật quốc tế)
"""

import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from statsmodels.tsa.api import Holt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ========================================================
# 1. CẤU HÌNH TRANG VÀ GIAO DIỆN SÁNG
# ========================================================
st.set_page_config(
    page_title="Phân Tích Tuyển Dụng IT Việt Nam",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tùy biến CSS: Sạch sẽ, sáng sủa, loại bỏ thanh bên thô ráp
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1E293B;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* Khung giới thiệu đầu trang */
    .hero-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }
    .hero-tag {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 0.03em;
        margin-bottom: 8px;
        border: 1px solid #DBEAFE;
    }
    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 6px;
    }
    .hero-desc {
        font-size: 0.95rem;
        color: #64748B;
        line-height: 1.5;
    }

    /* 4 Thẻ chỉ số tổng quan (KPI) */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kpi-number {
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .kpi-badge {
        font-size: 0.78rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-block;
    }

    /* Hộp chứa biểu đồ */
    .box-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .box-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .box-caption {
        font-size: 0.83rem;
        color: #64748B;
        margin-bottom: 14px;
    }

    /* Tùy chỉnh thanh Tab */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #E2E8F0;
        padding: 4px;
        border-radius: 10px;
        gap: 4px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #475569;
        border-radius: 8px;
        border: none !important;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1D4ED8 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Thanh điều khiển bên trái (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        padding-top: 1rem;
    }
    .sidebar-heading {
        font-size: 1rem;
        font-weight: 700;
        color: #1E293B;
        padding-bottom: 10px;
        margin-bottom: 12px;
        border-bottom: 2px solid #EFF6FF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========================================================
# 2. TẢI DỮ LIỆU TỪ KHO SQLITE
# ========================================================
DB_PATH = "data/warehouse/it_recruitment_dwh.db"

@st.cache_data(ttl=600)
def load_all_data():
    """Tải toàn bộ dữ liệu từ kho dữ liệu SQLite."""
    conn = sqlite3.connect(DB_PATH)

    # 1. Bảng dữ liệu việc làm
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

    # 2. Bảng dữ liệu kỹ năng
    query_skills = """
    SELECT 
        fs.job_id,
        s.skill_name
    FROM fact_job_skills fs
    JOIN dim_skill s ON fs.skill_id = s.skill_id
    """
    df_skills = pd.read_sql_query(query_skills, conn)
    conn.close()

    # Phân loại nhóm công nghệ
    def categorize_skill(skill):
        s = str(skill).lower()
        if any(k in s for k in ["aws", "azure", "docker", "kubernetes", "ci/cd", "devops", "cloud", "linux", "git"]):
            return "Điện toán đám mây & DevOps"
        elif any(k in s for k in ["react", "vue", "angular", "html", "css", "javascript", "typescript", "frontend"]):
            return "Lập trình Web Frontend"
        elif any(k in s for k in ["sql", "mysql", "postgres", "mongodb", "redis", "database", "oracle"]):
            return "Hệ cơ sở dữ liệu"
        elif any(k in s for k in ["python", "machine learning", "data", "ai", "power bi", "deep learning", "nlp", "tableau"]):
            return "Trí tuệ nhân tạo & Dữ liệu"
        elif any(k in s for k in ["ios", "android", "flutter", "react native", "swift", "kotlin", "mobile"]):
            return "Lập trình Di động"
        elif any(k in s for k in ["test", "qa", "qc", "selenium", "automation"]):
            return "Kiểm thử phần mềm (QA/QC)"
        elif any(k in s for k in ["java", "spring", ".net", "c#", "php", "golang", "c++", "node", "django", "laravel", "backend"]):
            return "Lập trình Hệ thống & Backend"
        else:
            return "Kỹ năng khác"

    df_skills["skill_category"] = df_skills["skill_name"].apply(categorize_skill)
    df_jobs["full_date"] = pd.to_datetime(df_jobs["full_date"], errors="coerce")
    return df_jobs, df_skills

# Nạp dữ liệu
try:
    df_jobs_raw, df_skills_raw = load_all_data()
except Exception as e:
    st.error(f"Lỗi khi đọc cơ sở dữ liệu: {e}")
    st.stop()

# ========================================================
# 3. THANH BỘ LỌC BÊN TRÁI (THIẾT KẾ GỌN GÀNG, DỄ DÙNG)
# ========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-heading">🎯 BỘ LỌC TÙY CHỌN</div>', unsafe_allow_html=True)

    # 1. Nguồn tuyển dụng (chọn dạng Selectbox đơn giản hoặc Multiselect)
    all_sources = ["Tất cả nguồn"] + sorted(df_jobs_raw["source"].dropna().unique().tolist())
    source_choice = st.selectbox("Nguồn tin tuyển dụng:", options=all_sources, index=0)

    # 2. Thành phố (chỉ liệt kê các tỉnh/thành phố cụ thể)
    valid_city_list = [c for c in df_jobs_raw["city_name"].dropna().unique() if c not in ["Không xác định", "Khác", "Unknown"]]
    all_cities = ["Tất cả thành phố"] + sorted(valid_city_list)
    city_choice = st.selectbox("Khu vực / Thành phố:", options=all_cities, index=0)

    # 3. Cấp bậc (chỉ lấy các cấp bậc chuẩn hóa)
    level_list = ["Tất cả cấp bậc", "Intern / Fresher", "Junior", "Middle", "Senior", "Lead / Manager"]
    level_choice = st.selectbox("Cấp bậc kinh nghiệm:", options=level_list, index=0)

    # 4. Vai trò
    all_roles = ["Tất cả vị trí"] + sorted(df_jobs_raw["role_name"].dropna().unique().tolist())
    role_choice = st.selectbox("Vị trí chuyên môn:", options=all_roles, index=0)

    # Lọc dữ liệu dựa trên lựa chọn
    filtered_jobs = df_jobs_raw.copy()
    if source_choice != "Tất cả nguồn":
        filtered_jobs = filtered_jobs[filtered_jobs["source"] == source_choice]
    if city_choice != "Tất cả thành phố":
        filtered_jobs = filtered_jobs[filtered_jobs["city_name"] == city_choice]
    if level_choice != "Tất cả cấp bậc":
        filtered_jobs = filtered_jobs[filtered_jobs["level_name"] == level_choice]
    if role_choice != "Tất cả vị trí":
        filtered_jobs = filtered_jobs[filtered_jobs["role_name"] == role_choice]

    valid_job_ids = set(filtered_jobs["job_id"])
    filtered_skills = df_skills_raw[df_skills_raw["job_id"].isin(valid_job_ids)]

    # Hộp thông tin tóm tắt bên dưới bộ lọc
    st.markdown("---")
    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px; font-size: 0.85rem;">
            <div style="font-weight: 700; color: #0F172A; margin-bottom: 6px;">📌 Kết Quả Lọc Hiện Tại:</div>
            <div style="color: #475569;">• Số việc làm: <b>{len(filtered_jobs):,}</b> tin</div>
            <div style="color: #475569;">• Doanh nghiệp: <b>{filtered_jobs['company_name'].nunique():,}</b> công ty</div>
            <div style="color: #475569;">• Tỷ trọng: <b>{(len(filtered_jobs)/len(df_jobs_raw)*100):.1f}%</b> toàn bộ kho</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========================================================
# 4. KHUNG GIỚI THIỆU CHÍNH (HERO BANNER)
# ========================================================
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-tag">ĐỀ TÀI PHÂN TÍCH DỮ LIỆU MÔN HỌC</div>
        <div class="hero-title">KHẢO SÁT DỮ LIỆU TUYỂN DỤNG IT THU THẬP ĐƯỢC</div>
        <div class="hero-desc">
            Báo cáo thống kê dựa trên tập dữ liệu mẫu gồm <b>4.761 tin tuyển dụng IT</b> thu thập từ 4 trang: ITViec, TopCV, VietnamWorks và LinkedIn.
            <br>
            <span style="font-size: 0.85rem; color: #94A3B8;">
                ⚠️ <i>Lưu ý: Dữ liệu chỉ phản ánh các tin tuyển dụng thu thập được trong phạm vi đề tài, mang tính tham khảo và không đại diện cho toàn bộ thị trường IT Việt Nam.</i>
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========================================================
# 5. BỐN THẺ CHỈ SỐ QUAN TRỌNG (KPIs)
# ========================================================
total_jobs = len(filtered_jobs)
total_companies = filtered_jobs["company_name"].nunique()
valid_salaries = filtered_jobs[filtered_jobs["salary_avg"].notna()]["salary_avg"]
median_salary = valid_salaries.median() if len(valid_salaries) > 0 else 0
salary_public_rate = (len(valid_salaries) / max(total_jobs, 1) * 100)

st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="kpi-item">
            <div class="kpi-title">
                <span>TỔNG VIỆC LÀM IT</span>
                <span>💼</span>
            </div>
            <div class="kpi-number">{total_jobs:,}</div>
            <span class="kpi-badge" style="background: #EFF6FF; color: #1D4ED8;">Tin tuyển dụng hợp lệ</span>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">
                <span>DOANH NGHIỆP TUYỂN DỤNG</span>
                <span>🏢</span>
            </div>
            <div class="kpi-number">{total_companies:,}</div>
            <span class="kpi-badge" style="background: #EEF2FF; color: #3730A3;">Công ty công nghệ</span>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">
                <span>LƯƠNG TRUNG VỊ</span>
                <span>💵</span>
            </div>
            <div class="kpi-number">{median_salary:.1f} <span style="font-size: 1rem; font-weight: 600; color: #64748B;">triệu</span></div>
            <span class="kpi-badge" style="background: #FEF3C7; color: #B45309;">Triệu VNĐ / Tháng</span>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">
                <span>CÔNG KHAI MỨC LƯƠNG</span>
                <span>📊</span>
            </div>
            <div class="kpi-number">{salary_public_rate:.1f}%</div>
            <span class="kpi-badge" style="background: #ECFDF5; color: #047857;">{len(valid_salaries):,} tin có số liệu</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cấu hình biểu đồ sáng, sạch sẽ
CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155", size=12),
    margin=dict(t=25, b=25, l=25, r=25),
)

# ========================================================
# 6. CÁC TRANG PHÂN TÍCH (TABS)
# ========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. Tổng Quan Dữ Liệu",
    "🎯 2. Kỹ Năng Theo Vị Trí",
    "📈 3. Xu Hướng & Dự Báo",
    "💰 4. Mức Lương Tham Khảo"
])

# ========================================================
# TAB 1: TỔNG QUAN THỊ TRƯỜNG
# ========================================================
with tab1:
    col1, col2 = st.columns([5, 7])

    with col1:
        st.markdown(
            """
            <div class="box-card">
                <div class="box-title">🌐 Phân Bố Theo Nguồn Thu Thập</div>
                <div class="box-caption">Số lượng và tỷ lệ tin thu thập từ 4 trang tuyển dụng</div>
            """,
            unsafe_allow_html=True,
        )
        source_df = filtered_jobs["source"].value_counts().reset_index()
        source_df.columns = ["Nguồn", "Số Lượng"]
        
        fig_src = go.Figure(
            data=[
                go.Pie(
                    labels=source_df["Nguồn"],
                    values=source_df["Số Lượng"],
                    hole=0.55,
                    marker=dict(
                        colors=["#2563EB", "#0D9488", "#F59E0B", "#8B5CF6"],
                        line=dict(color="#FFFFFF", width=2)
                    ),
                    textinfo="percent+label",
                    textposition="outside",
                )
            ]
        )
        fig_src.update_layout(**CHART_THEME, height=320, showlegend=False)
        st.plotly_chart(fig_src, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="box-card">
                <div class="box-title">📍 Top Tỉnh / Thành Phố Tập Trung Nhiều Tin Tuyển Dụng</div>
                <div class="box-caption">Các địa phương có số lượng việc làm IT ghi nhận cao nhất trong tập dữ liệu</div>
            """,
            unsafe_allow_html=True,
        )
        # Chỉ lấy các tỉnh thành phố cụ thể, loại bỏ các mục không xác định
        valid_cities_df = filtered_jobs[~filtered_jobs["city_name"].isin(["Không xác định", "Khác", "Unknown"])]
        city_df = valid_cities_df["city_name"].value_counts().reset_index().head(5)
        city_df.columns = ["Thành Phố", "Số Lượng"]
        city_df["Tỷ Lệ"] = (city_df["Số Lượng"] / max(len(valid_cities_df), 1) * 100).round(1)

        fig_city = px.bar(
            city_df,
            x="Số Lượng",
            y="Thành Phố",
            orientation="h",
            text=city_df.apply(lambda r: f"{r['Số Lượng']:,} tin ({r['Tỷ Lệ']}%)", axis=1),
            color="Số Lượng",
            color_continuous_scale=["#BFDBFE", "#1D4ED8"],
        )
        fig_city.update_layout(
            **CHART_THEME,
            height=320,
            yaxis=dict(autorange="reversed", title=""),
            xaxis=dict(title="Số lượng tin tuyển dụng", showgrid=True, gridcolor="#F1F5F9"),
            coloraxis_showscale=False,
        )
        fig_city.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_city, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Biểu đồ phân bố các vai trò IT chính
    st.markdown(
        """
        <div class="box-card">
            <div class="box-title">💻 Phân Bố Tin Tuyển Dụng Theo Vị Trí IT</div>
            <div class="box-caption">Số lượng tin theo các vai trò công việc phổ biến trong tập dữ liệu</div>
        """,
        unsafe_allow_html=True,
    )
    role_df = filtered_jobs["role_name"].value_counts().reset_index().head(8)
    role_df.columns = ["Vị Trí IT", "Số Lượng"]
    
    fig_role = px.bar(
        role_df,
        x="Vị Trí IT",
        y="Số Lượng",
        text=role_df["Số Lượng"].apply(lambda v: f"{v:,} tin"),
        color="Số Lượng",
        color_continuous_scale=["#CCFBF1", "#0D9488"],
    )
    fig_role.update_layout(
        **CHART_THEME,
        height=340,
        xaxis=dict(title=""),
        yaxis=dict(title="Số lượng việc làm", showgrid=True, gridcolor="#F1F5F9"),
        coloraxis_showscale=False,
    )
    fig_role.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_role, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ========================================================
# TAB 2: KỸ NĂNG THEO TỪNG VỊ TRÍ
# ========================================================
with tab2:
    st.markdown(
        """
        <div class="box-card">
            <div class="box-title">🏆 Top Kỹ Năng Xuất Hiện Nhiều Nhất Trong Dữ Liệu</div>
            <div class="box-caption">Các ngôn ngữ, framework được đề cập nhiều nhất trong tập dữ liệu thu thập</div>
        """,
        unsafe_allow_html=True,
    )
    skill_counts = filtered_skills["skill_name"].value_counts().reset_index().head(10)
    skill_counts.columns = ["Kỹ Năng", "Số Lượng"]
    skill_counts["Tỷ Lệ %"] = (skill_counts["Số Lượng"] / max(total_jobs, 1) * 100).round(1)

    fig_sk = px.bar(
        skill_counts,
        x="Số Lượng",
        y="Kỹ Năng",
        orientation="h",
        text=skill_counts.apply(lambda r: f"{r['Số Lượng']:,} lượt ({r['Tỷ Lệ %']}%)", axis=1),
        color="Số Lượng",
        color_continuous_scale=["#BAE6FD", "#1D4ED8"],
    )
    fig_sk.update_layout(
        **CHART_THEME,
        height=380,
        yaxis=dict(autorange="reversed", title=""),
        xaxis=dict(title="Số lượt xuất hiện trong tin tuyển dụng", showgrid=True, gridcolor="#F1F5F9"),
        coloraxis_showscale=False,
    )
    fig_sk.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_sk, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # THỐNG KÊ KỸ NĂNG THEO TỪNG VỊ TRÍ CHUYÊN MÔN
    st.markdown(
        """
        <div class="box-card">
            <div class="box-title">🔍 Thống Kê Kỹ Năng Theo Từng Vị Trí Công Việc</div>
            <div class="box-caption">Xem các công nghệ được yêu cầu nhiều nhất trong từng vị trí theo mẫu dữ liệu</div>
        """,
        unsafe_allow_html=True,
    )

    # Danh sách các vị trí tiêu biểu
    top_available_roles = [
        r for r in ["Backend Developer", "Frontend Developer", "Fullstack Developer", 
                   "DevOps / Cloud Engineer", "Mobile Developer", "Data Engineer / AI", 
                   "QA / QC / Tester"]
        if r in filtered_jobs["role_name"].unique()
    ]
    if not top_available_roles:
        top_available_roles = filtered_jobs["role_name"].value_counts().head(6).index.tolist()

    selected_role_to_view = st.selectbox(
        "👉 Chọn vị trí muốn khảo sát kỹ năng:",
        options=top_available_roles,
        index=0
    )

    # Lấy các job thuộc role này
    role_job_ids = set(filtered_jobs[filtered_jobs["role_name"] == selected_role_to_view]["job_id"])
    role_total_postings = len(role_job_ids)
    role_skills = filtered_skills[filtered_skills["job_id"].isin(role_job_ids)]

    if not role_skills.empty and role_total_postings > 0:
        role_sk_counts = role_skills["skill_name"].value_counts().reset_index().head(8)
        role_sk_counts.columns = ["Kỹ Năng", "Số Tin Yêu Cầu"]
        role_sk_counts["Tỷ Lệ Yêu Cầu (%)"] = (role_sk_counts["Số Tin Yêu Cầu"] / role_total_postings * 100).round(1)

        sk_col_a, sk_col_b = st.columns([7, 5])
        with sk_col_a:
            fig_role_sk = px.bar(
                role_sk_counts,
                x="Số Tin Yêu Cầu",
                y="Kỹ Năng",
                orientation="h",
                text=role_sk_counts["Tỷ Lệ Yêu Cầu (%)"].apply(lambda v: f"{v}% tin"),
                color="Số Tin Yêu Cầu",
                color_continuous_scale=["#BAE6FD", "#0284C7"],
            )
            fig_role_sk.update_layout(
                **CHART_THEME,
                height=340,
                yaxis=dict(autorange="reversed", title=""),
                xaxis=dict(title=f"Số tin tuyển vị trí {selected_role_to_view}", showgrid=True, gridcolor="#F1F5F9"),
                coloraxis_showscale=False,
            )
            fig_role_sk.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_role_sk, use_container_width=True)

        with sk_col_b:
            st.markdown(f"**💡 Thống kê mẫu cho vị trí `{selected_role_to_view}`:**")
            st.markdown(f"- Số tin tuyển trong tập mẫu: **{role_total_postings:,} tin**.")
            top_1_sk = role_sk_counts.iloc[0]["Kỹ Năng"]
            top_1_pct = role_sk_counts.iloc[0]["Tỷ Lệ Yêu Cầu (%)"]
            st.markdown(f"- Kỹ năng xuất hiện nhiều nhất: **{top_1_sk}** (có trong **{top_1_pct}%** tin).")
            st.markdown(f"- Các kỹ năng phổ biến kế tiếp: **{', '.join(role_sk_counts['Kỹ Năng'].head(4).tolist())}**.")
    else:
        st.info("Không có dữ liệu kỹ năng cho vị trí được chọn.")
    st.markdown("</div>", unsafe_allow_html=True)


# ========================================================
# TAB 3: XU HƯỚNG & DỰ BÁO TUYỂN DỤNG
# ========================================================
with tab3:
    st.markdown(
        """
        <div class="box-card">
            <div class="box-title">📈 Xu Hướng & Dự Báo Số Lượng Tuyển Dụng IT</div>
            <div class="box-caption">Kết hợp số liệu ghi nhận thực tế từ tập mẫu và mô hình dự báo chuỗi thời gian (Time Series) cho các tháng tới</div>
        """,
        unsafe_allow_html=True,
    )

    df_dated = filtered_jobs[filtered_jobs["full_date"].notna()].copy()
    if not df_dated.empty and len(df_dated["month_year"].unique()) >= 4:
        # Gom nhóm số lượng theo tháng
        df_monthly_series = (
            df_dated.groupby("month_year")
            .agg(start_date=("full_date", "min"), job_count=("job_id", "count"))
            .reset_index()
            .sort_values("start_date")
            .reset_index(drop=True)
        )

        # Bộ điều khiển số tháng dự báo
        forecast_col1, forecast_col2 = st.columns([8, 4])
        with forecast_col2:
            n_months_ahead = st.slider(
                "🔮 Số tháng tương lai cần dự báo:",
                min_value=2,
                max_value=6,
                value=4,
                step=1,
                help="Chọn số tháng tiếp theo để mô hình thực hiện ước tính xu hướng"
            )

        # Huấn luyện mô hình Holt's Linear Trend
        y_vals = df_monthly_series["job_count"].values
        model_holt = Holt(y_vals, initialization_method="estimated")
        fit_holt = model_holt.fit(smoothing_level=0.5, smoothing_trend=0.3, optimized=True)
        
        # Đánh giá sai số MAE
        fitted = fit_holt.fittedvalues
        mae_score = mean_absolute_error(y_vals, fitted)
        rmse_score = np.sqrt(mean_squared_error(y_vals, fitted))

        # Tính toán dự báo tương lai
        future_pred = fit_holt.forecast(n_months_ahead)
        future_pred = np.maximum(future_pred, 50)

        # Tạo chuỗi nhãn tháng tiếp theo theo đúng thứ tự thời gian tăng dần
        last_dt = df_monthly_series["start_date"].max()
        future_dts = pd.date_range(start=last_dt + pd.DateOffset(months=1), periods=n_months_ahead, freq="MS")
        future_periods = [d.strftime("%m/%Y") for d in future_dts]

        # Toàn bộ dòng thời gian chuẩn từ quá khứ đến tương lai
        full_timeline = list(df_monthly_series["month_year"]) + future_periods

        # Tính khoảng tin cậy
        lower_vals = np.maximum(future_pred - 1.28 * rmse_score, 50)
        upper_vals = future_pred + 1.28 * rmse_score

        # ĐIỂM NHẤN: ĐƯA NHẬN ĐỊNH LÊN VỊ TRÍ NỔI BẬT NHẤT TRÊN ĐẦU
        growth_text = "tăng trưởng nhẹ" if future_pred[-1] >= future_pred[0] else "ổn định"
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #EFF6FF 0%, #ECFDF5 100%); border-left: 5px solid #2563EB; border-radius: 12px; padding: 16px 20px; margin-bottom: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-weight: 800; font-size: 1.05rem; color: #1E3A8A; display: flex; align-items: center; gap: 8px;">
                    <span>💡</span> NHẬN ĐỊNH XU HƯỚNG TƯƠNG LAI:
                </div>
                <div style="font-size: 0.95rem; color: #1E293B; margin-top: 6px; line-height: 1.6;">
                    Dựa trên nhịp độ tuyển dụng 13 tháng qua, mô hình dự đoán nhu cầu tuyển dụng IT trong <b>{n_months_ahead} tháng tới (từ {future_periods[0]} đến {future_periods[-1]})</b> có chiều hướng <b>{growth_text}</b>.
                    Dự kiến số lượng tin tuyển sẽ dao động trong khoảng từ <b>{future_pred[0]:.0f} đến {future_pred[-1]:.0f} tin/tháng</b>, phù hợp với chu kỳ tăng cường nhân sự công nghệ phục vụ dự án cuối năm và đầu năm mới.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Điểm nối giữa điểm cuối thực tế và tương lai
        last_actual_period = df_monthly_series["month_year"].iloc[-1]
        last_actual_val = df_monthly_series["job_count"].iloc[-1]

        plot_forecast_periods = [last_actual_period] + future_periods
        plot_forecast_vals = [last_actual_val] + list(future_pred)
        plot_lower_vals = [last_actual_val] + list(lower_vals)
        plot_upper_vals = [last_actual_val] + list(upper_vals)

        # Vẽ biểu đồ kết hợp Plotly
        fig_forecast = go.Figure()

        # 1. Vẽ đường THỰC TẾ trước (10/2025 -> 10/2026)
        fig_forecast.add_trace(
            go.Scatter(
                x=df_monthly_series["month_year"],
                y=df_monthly_series["job_count"],
                mode="lines+markers+text",
                name="Thực tế ghi nhận",
                line=dict(color="#1D4ED8", width=3.5),
                marker=dict(size=9, color="#1E40AF"),
                text=df_monthly_series["job_count"].apply(lambda v: f"{v:,}"),
                textposition="top center",
                textfont=dict(size=11, color="#1E293B", family="Plus Jakarta Sans"),
            )
        )

        # 2. Dải vùng tin cậy dự báo
        fig_forecast.add_trace(
            go.Scatter(
                x=plot_forecast_periods + plot_forecast_periods[::-1],
                y=plot_upper_vals + plot_lower_vals[::-1],
                fill="toself",
                fillcolor="rgba(245, 158, 11, 0.15)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                name="Khoảng dao động dự báo (80%)",
            )
        )

        # 3. Đường DỰ BÁO nối tiếp từ điểm cuối thực tế sang tương lai
        fig_forecast.add_trace(
            go.Scatter(
                x=plot_forecast_periods,
                y=plot_forecast_vals,
                mode="lines+markers+text",
                name="Đường dự báo tương lai",
                line=dict(color="#D97706", width=3, dash="dash"),
                marker=dict(size=9, color="#B45309", symbol="diamond"),
                text=[f"{v:.0f}" for v in plot_forecast_vals],
                textposition="top center",
                textfont=dict(size=11, color="#B45309", family="Plus Jakarta Sans"),
            )
        )

        fig_forecast.update_layout(
            **CHART_THEME,
            height=430,
            xaxis=dict(
                type="category",
                categoryorder="array",
                categoryarray=full_timeline,
                title=dict(text="<b>Mốc Thời Gian Tuyến Tính (Tháng / Năm)</b>", font=dict(size=13, color="#0F172A")),
                tickfont=dict(size=12, color="#0F172A"),
                showgrid=True,
                gridcolor="#F1F5F9",
                tickangle=-15,
            ),
            yaxis=dict(
                title=dict(text="<b>Số Lượng Tin Tuyển Dụng</b>", font=dict(size=13, color="#0F172A")),
                showgrid=True,
                gridcolor="#F1F5F9",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)"
            ),
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        # Chú thích ngắn gọn, tinh giản, không rườm rà
        st.caption("ℹ️ *Ghi chú: Đường nét đứt màu cam và dải bóng mờ thể hiện ước tính xu hướng tham khảo dựa trên dữ liệu các tháng gần nhất.*")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Không có đủ chuỗi thời gian để thực hiện mô hình dự báo.")


# ========================================================
# TAB 4: MỨC LƯƠNG THAM KHẢO
# ========================================================
with tab4:
    df_salary = filtered_jobs[
        (filtered_jobs["salary_avg"].notna()) & 
        (filtered_jobs["salary_avg"] > 0) & 
        (filtered_jobs["salary_avg"] <= 200)
    ].copy()

    if not df_salary.empty:
        # Thứ tự chuẩn từ thấp đến cao
        level_order = ["Intern / Fresher", "Junior", "Middle", "Senior", "Lead / Manager"]
        df_salary_level = df_salary[df_salary["level_name"].isin(level_order)]

        # Tính toán các chỉ số: Số tin, Thấp nhất, Trung vị, Cao nhất
        level_stats = df_salary_level.groupby("level_name")["salary_avg"].agg(
            Số_Tin="count",
            Thấp_Nhất="min",
            Trung_Vị="median",
            Cao_Nhất="max"
        ).reindex(level_order).dropna().reset_index()

        col_sal_1, col_sal_2 = st.columns([7, 5])

        with col_sal_1:
            st.markdown(
                """
                <div class="box-card">
                    <div class="box-title">📊 Bậc Thang Thu Nhập IT Theo Cấp Bậc (Từ Thấp Đến Cao)</div>
                    <div class="box-caption">So sánh mức lương sàn (thấp nhất) và mức lương trung vị thực tế (triệu VNĐ/tháng)</div>
                """,
                unsafe_allow_html=True,
            )

            # Biểu đồ cột đứng so sánh song song Mức Sàn vs Lương Trung Vị
            fig_sal_bar = go.Figure()

            # 1. Cột Mức sàn (Thấp nhất)
            fig_sal_bar.add_trace(
                go.Bar(
                    name="Mức Sàn (Thấp nhất)",
                    x=level_stats["level_name"],
                    y=level_stats["Thấp_Nhất"],
                    marker=dict(color="#93C5FD"),
                    text=level_stats["Thấp_Nhất"].apply(lambda v: f"{v:.1f} tr"),
                    textposition="outside",
                    textfont=dict(size=11, color="#1E3A8A"),
                )
            )

            # 2. Cột Lương Trung Vị (Phổ biến)
            fig_sal_bar.add_trace(
                go.Bar(
                    name="Lương Trung Vị (Phổ biến)",
                    x=level_stats["level_name"],
                    y=level_stats["Trung_Vị"],
                    marker=dict(color="#1D4ED8"),
                    text=level_stats["Trung_Vị"].apply(lambda v: f"{v:.1f} tr"),
                    textposition="outside",
                    textfont=dict(size=12, color="#0F172A", family="Plus Jakarta Sans"),
                )
            )

            fig_sal_bar.update_layout(
                **CHART_THEME,
                barmode="group",
                height=380,
                xaxis=dict(title="<b>Cấp Bậc Kinh Nghiệm (Từ Thấp Đến Cao)</b>", tickangle=-10),
                yaxis=dict(title="Mức Lương (Triệu VNĐ / Tháng)", showgrid=True, gridcolor="#F1F5F9"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_sal_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_sal_2:
            st.markdown(
                """
                <div class="box-card">
                    <div class="box-title">💻 Lương Trung Vị Theo Từng Vị Trí IT</div>
                    <div class="box-caption">Mức thu nhập phổ biến giữa các nhánh nghề nghiệp chính</div>
                """,
                unsafe_allow_html=True,
            )
            top_roles_salary = df_salary["role_name"].value_counts().head(6).index.tolist()
            df_role_sal = df_salary[df_salary["role_name"].isin(top_roles_salary)]
            role_sal_stats = df_role_sal.groupby("role_name")["salary_avg"].median().reset_index()
            role_sal_stats.columns = ["Vị Trí IT", "Lương Trung Vị"]
            role_sal_stats = role_sal_stats.sort_values("Lương Trung Vị", ascending=True)

            fig_role_sal = px.bar(
                role_sal_stats,
                x="Lương Trung Vị",
                y="Vị Trí IT",
                orientation="h",
                text=role_sal_stats["Lương Trung Vị"].apply(lambda v: f"{v:.1f} tr"),
                color="Lương Trung Vị",
                color_continuous_scale=["#CCFBF1", "#0D9488"],
            )
            fig_role_sal.update_layout(
                **CHART_THEME,
                height=380,
                yaxis=dict(title=""),
                xaxis=dict(title="Triệu VNĐ / Tháng", showgrid=True, gridcolor="#F1F5F9"),
                coloraxis_showscale=False,
            )
            fig_role_sal.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_role_sal, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Bảng số liệu chi tiết
        st.markdown(
            """
            <div class="box-card">
                <div class="box-title">📋 Bảng Thống Kê Chi Tiết Thu Nhập Theo Cấp Bậc (Sắp Xếp Từ Thấp Đến Cao)</div>
                <div class="box-caption">Định lượng mức sàn, mức trung vị phổ biến và mức trần ghi nhận trong mẫu dữ liệu (Đơn vị: Triệu VNĐ / Tháng)</div>
            """,
            unsafe_allow_html=True,
        )
        display_table = level_stats.copy()
        display_table.columns = ["Cấp Bậc (Kinh Nghiệm)", "Số Tin Có Lương", "Mức Sàn Thấp Nhất (tr)", "Lương Trung Vị Phổ Biến (tr)", "Mức Trần Cao Nhất (tr)"]
        st.dataframe(
            display_table.style.format({
                "Số Tin Có Lương": "{:,.0f}",
                "Mức Sàn Thấp Nhất (tr)": "{:.1f}",
                "Lương Trung Vị Phổ Biến (tr)": "{:.1f}",
                "Mức Trần Cao Nhất (tr)": "{:.1f}",
            }).set_properties(**{'background-color': '#FFFFFF', 'color': '#0F172A', 'border-color': '#E2E8F0'}),
            use_container_width=True,
            height=240,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Không có dữ liệu mức lương phù hợp với bộ lọc hiện tại.")

# ========================================================
# 7. CHÂN TRANG
# ========================================================
st.markdown(
    """
    <div style="text-align: center; color: #94A3B8; font-size: 0.82rem; padding: 24px 0 10px 0; border-top: 1px solid #E2E8F0; margin-top: 20px;">
        Đề Tài Khảo Sát Dữ Liệu Tuyển Dụng IT • Sử dụng Streamlit & Plotly • Số liệu mang tính tham khảo trong phạm vi tập dữ liệu môn học
    </div>
    """,
    unsafe_allow_html=True,
)
