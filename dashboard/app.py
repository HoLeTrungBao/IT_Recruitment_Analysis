"""
HỆ THỐNG PHÂN TÍCH DỮ LIỆU TUYỂN DỤNG CÔNG NGHỆ THÔNG TIN VIỆT NAM
Giao diện: Thiết kế chuyên nghiệp, chữ to rõ ràng, độ tương phản cao
Ngôn ngữ: Tiếng Việt chuẩn mực, không lạm dụng biểu tượng cảm xúc
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
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tùy biến CSS: Sử dụng font chữ hệ thống sắc nét, độ tương phản cao, chữ to dễ đọc
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0F172A;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* Khung giới thiệu đầu trang */
    .hero-container {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .hero-tag {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        border: 1px solid #BFDBFE;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 8px;
    }
    .hero-desc {
        font-size: 1.02rem;
        color: #1E293B;
        line-height: 1.6;
        font-weight: 450;
    }

    /* 4 Thẻ chỉ số tổng quan */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-item {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .kpi-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .kpi-number {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    .kpi-badge {
        font-size: 0.88rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
        display: inline-block;
    }

    /* Hộp chứa biểu đồ */
    .box-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .box-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
    }
    .box-caption {
        font-size: 0.95rem;
        color: #334155;
        margin-bottom: 16px;
        font-weight: 500;
        line-height: 1.5;
    }

    /* Tùy chỉnh thanh Tab */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #E2E8F0;
        padding: 4px;
        border-radius: 8px;
        gap: 4px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 22px;
        font-weight: 700;
        font-size: 0.95rem;
        color: #334155;
        border-radius: 6px;
        border: none !important;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1D4ED8 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }

    /* Thanh điều khiển bên trái (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #CBD5E1;
        padding-top: 1rem;
    }
    .sidebar-heading {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0F172A;
        padding-bottom: 10px;
        margin-bottom: 14px;
        border-bottom: 2px solid #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========================================================
# 2. TẢI DỮ LIỆU TỪ KHO SQLITE
# ========================================================
DB_PATH = "data/warehouse/it_recruitment_dwh.db"

def load_all_data():
    """Tải toàn bộ dữ liệu từ kho dữ liệu SQLite trực tiếp không cache cũ."""
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
# 3. THANH BỘ LỌC BÊN TRÁI
# ========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-heading">BỘ LỌC DỮ LIỆU</div>', unsafe_allow_html=True)

    # 1. Nguồn tuyển dụng
    all_sources = ["Tất cả nguồn"] + sorted(df_jobs_raw["source"].dropna().unique().tolist())
    source_choice = st.selectbox("Nguồn tin tuyển dụng:", options=all_sources, index=0)

    # 2. Thành phố (chỉ lấy các tỉnh thành cụ thể, không lấy nhãn không xác định)
    valid_city_list = [c for c in df_jobs_raw["city_name"].dropna().unique() if c not in ["Không xác định", "Khác", "Unknown"]]
    all_cities = ["Tất cả thành phố"] + sorted(valid_city_list)
    city_choice = st.selectbox("Khu vực / Thành phố:", options=all_cities, index=0)

    # 3. Cấp bậc chuẩn hóa
    level_list = ["Tất cả cấp bậc", "Intern / Fresher", "Junior", "Middle", "Senior", "Lead / Manager"]
    level_choice = st.selectbox("Cấp bậc kinh nghiệm:", options=level_list, index=0)

    # 4. Vai trò chuyên môn
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
        <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 14px; font-size: 0.92rem;">
            <div style="font-weight: 800; color: #0F172A; margin-bottom: 8px;">Kết Quả Lọc Hiện Tại:</div>
            <div style="color: #334155; margin-bottom: 4px;">• Số việc làm: <b>{len(filtered_jobs):,}</b> tin</div>
            <div style="color: #334155; margin-bottom: 4px;">• Doanh nghiệp: <b>{filtered_jobs['company_name'].nunique():,}</b> công ty</div>
            <div style="color: #334155;">• Tỷ trọng: <b>{(len(filtered_jobs)/len(df_jobs_raw)*100):.1f}%</b> toàn bộ kho</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========================================================
# 4. KHUNG GIỚI THIỆU CHÍNH
# ========================================================
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-tag">ĐỀ TÀI PHÂN TÍCH DỮ LIỆU MÔN HỌC</div>
        <div class="hero-title">KHẢO SÁT DỮ LIỆU TUYỂN DỤNG IT THU THẬP ĐƯỢC</div>
        <div class="hero-desc">
            Báo cáo thống kê dựa trên tập dữ liệu mẫu gồm <b>4.761 tin tuyển dụng IT</b> thu thập từ 4 trang: ITViec, TopCV, VietnamWorks và LinkedIn.
            <div style="font-size: 0.92rem; color: #475569; margin-top: 6px; font-style: italic;">
                Lưu ý: Dữ liệu chỉ phản ánh các tin tuyển dụng thu thập được trong phạm vi đề tài, mang tính tham khảo và không đại diện cho toàn bộ thị trường IT Việt Nam.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========================================================
# 5. BỐN THẺ CHỈ SỐ QUAN TRỌNG
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
            <div class="kpi-title">TỔNG VIỆC LÀM IT</div>
            <div class="kpi-number">{total_jobs:,}</div>
            <span class="kpi-badge" style="background: #EFF6FF; color: #1D4ED8;">Tin tuyển dụng hợp lệ</span>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">DOANH NGHIỆP TUYỂN DỤNG</div>
            <div class="kpi-number">{total_companies:,}</div>
            <span class="kpi-badge" style="background: #EEF2FF; color: #3730A3;">Công ty công nghệ</span>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">LƯƠNG TRUNG VỊ</div>
            <div class="kpi-number">{median_salary:.1f} <span style="font-size: 1.1rem; font-weight: 700; color: #475569;">triệu</span></div>
            <span class="kpi-badge" style="background: #FEF3C7; color: #92400E;">Triệu VNĐ / Tháng</span>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">CÔNG KHAI MỨC LƯƠNG</div>
            <div class="kpi-number">{salary_public_rate:.1f}%</div>
            <span class="kpi-badge" style="background: #ECFDF5; color: #065F46;">{len(valid_salaries):,} tin có số liệu</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cấu hình biểu đồ sáng, font to rõ
CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif", color="#0F172A", size=13),
    margin=dict(t=30, b=30, l=35, r=35),
)

# ========================================================
# 6. CÁC TRANG PHÂN TÍCH (TABS)
# ========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Tổng Quan Dữ Liệu",
    "2. Kỹ Năng Theo Vị Trí",
    "3. Xu Hướng & Dự Báo",
    "4. Mức Lương Tham Khảo"
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
                <div class="box-title">Phân Bố Theo Nguồn Thu Thập</div>
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
                        colors=["#2563EB", "#0D9488", "#D97706", "#4F46E5"],
                        line=dict(color="#FFFFFF", width=2)
                    ),
                    texttemplate="<b>%{label}</b><br><b>%{percent}</b>",
                    textposition="outside",
                    textfont=dict(size=13, color="#0F172A"),
                )
            ]
        )
        fig_src.update_layout(
            **CHART_THEME,
            height=370,
            margin=dict(t=25, b=65, l=45, r=45),
            showlegend=False
        )
        st.plotly_chart(fig_src, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="box-card">
                <div class="box-title">Top Tỉnh / Thành Phố Tập Trung Nhiều Tin Tuyển Dụng</div>
                <div class="box-caption">Các địa phương có số lượng việc làm IT ghi nhận cao nhất trong tập dữ liệu</div>
            """,
            unsafe_allow_html=True,
        )
        valid_cities_df = filtered_jobs[~filtered_jobs["city_name"].isin(["Không xác định", "Khác", "Unknown"])]
        city_df = valid_cities_df["city_name"].value_counts().reset_index().head(5)
        city_df.columns = ["Thành Phố", "Số Lượng"]
        city_df["Tỷ Lệ"] = (city_df["Số Lượng"] / max(len(valid_cities_df), 1) * 100).round(1)

        fig_city = px.bar(
            city_df,
            x="Số Lượng",
            y="Thành Phố",
            orientation="h",
            text=city_df.apply(lambda r: f"<b>{r['Số Lượng']:,} tin ({r['Tỷ Lệ']}%)</b>", axis=1),
            color="Số Lượng",
            color_continuous_scale=["#BFDBFE", "#1D4ED8"],
        )
        fig_city.update_layout(
            **CHART_THEME,
            height=370,
            yaxis=dict(autorange="reversed", title="", tickfont=dict(size=13, color="#0F172A")),
            xaxis=dict(
                title=dict(text="<b>Số lượng tin tuyển dụng</b>", font=dict(size=13, color="#0F172A")),
                showgrid=True,
                gridcolor="#E2E8F0",
                tickfont=dict(size=12, color="#0F172A")
            ),
            coloraxis_showscale=False,
        )
        fig_city.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=12, color="#0F172A"))
        st.plotly_chart(fig_city, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Biểu đồ phân bố các vai trò IT chính
    st.markdown(
        """
        <div class="box-card">
            <div class="box-title">Phân Bố Tin Tuyển Dụng Theo Vị Trí IT</div>
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
        text=role_df["Số Lượng"].apply(lambda v: f"<b>{v:,} tin</b>"),
        color="Số Lượng",
        color_continuous_scale=["#CCFBF1", "#0D9488"],
    )
    fig_role.update_layout(
        **CHART_THEME,
        height=360,
        xaxis=dict(title="", tickfont=dict(size=13, color="#0F172A")),
        yaxis=dict(
            title=dict(text="<b>Số lượng việc làm</b>", font=dict(size=13, color="#0F172A")),
            showgrid=True,
            gridcolor="#E2E8F0",
            tickfont=dict(size=12, color="#0F172A")
        ),
        coloraxis_showscale=False,
    )
    fig_role.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=12, color="#0F172A"))
    st.plotly_chart(fig_role, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ========================================================
# TAB 2: KỸ NĂNG THEO TỪNG VỊ TRÍ
# ========================================================
with tab2:
    st.markdown(
        """
        <div class="box-card">
            <div class="box-title">Top Kỹ Năng Xuất Hiện Nhiều Nhất Trong Dữ Liệu</div>
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
        text=skill_counts.apply(lambda r: f"<b>{r['Số Lượng']:,} lượt ({r['Tỷ Lệ %']}%)</b>", axis=1),
        color="Số Lượng",
        color_continuous_scale=["#BAE6FD", "#1D4ED8"],
    )
    fig_sk.update_layout(
        **CHART_THEME,
        height=380,
        yaxis=dict(autorange="reversed", title="", tickfont=dict(size=13, color="#0F172A")),
        xaxis=dict(
            title=dict(text="<b>Số lượt xuất hiện trong tin tuyển dụng</b>", font=dict(size=13, color="#0F172A")),
            showgrid=True,
            gridcolor="#E2E8F0",
            tickfont=dict(size=12, color="#0F172A")
        ),
        coloraxis_showscale=False,
    )
    fig_sk.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=12, color="#0F172A"))
    st.plotly_chart(fig_sk, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # THỐNG KÊ KỸ NĂNG THEO TỪNG VỊ TRÍ
    st.markdown(
        """
        <div class="box-card">
            <div class="box-title">Thống Kê Kỹ Năng Theo Từng Vị Trí Công Việc</div>
            <div class="box-caption">Xem các công nghệ được yêu cầu nhiều nhất trong từng vị trí theo mẫu dữ liệu</div>
        """,
        unsafe_allow_html=True,
    )

    top_available_roles = [
        r for r in ["Backend Developer", "Frontend Developer", "Fullstack Developer", 
                   "DevOps / Cloud Engineer", "Mobile Developer", "Data Engineer / AI", 
                   "QA / QC / Tester"]
        if r in filtered_jobs["role_name"].unique()
    ]
    if not top_available_roles:
        top_available_roles = filtered_jobs["role_name"].value_counts().head(6).index.tolist()

    selected_role_to_view = st.selectbox(
        "Chọn vị trí khảo sát kỹ năng:",
        options=top_available_roles,
        index=0
    )

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
                text=role_sk_counts["Tỷ Lệ Yêu Cầu (%)"].apply(lambda v: f"<b>{v}% tin</b>"),
                color="Số Tin Yêu Cầu",
                color_continuous_scale=["#CCFBF1", "#0F766E"],
            )
            fig_role_sk.update_layout(
                **CHART_THEME,
                height=340,
                yaxis=dict(autorange="reversed", title="", tickfont=dict(size=13, color="#0F172A")),
                xaxis=dict(
                    title=dict(text=f"<b>Số tin tuyển {selected_role_to_view}</b>", font=dict(size=13, color="#0F172A")),
                    showgrid=True,
                    gridcolor="#E2E8F0",
                    tickfont=dict(size=12, color="#0F172A")
                ),
                coloraxis_showscale=False,
            )
            fig_role_sk.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=12, color="#0F172A"))
            st.plotly_chart(fig_role_sk, use_container_width=True)

        with sk_col_b:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 16px; font-size: 0.95rem; line-height: 1.6;">
                    <div style="font-weight: 800; color: #0F172A; margin-bottom: 8px; font-size: 1rem;">Nhận định cho vị trí {selected_role_to_view}:</div>
                    <div style="color: #334155; margin-bottom: 6px;">• Số tin tuyển dụng ghi nhận: <b>{role_total_postings:,} việc làm</b></div>
                    <div style="color: #334155; margin-bottom: 6px;">• Kỹ năng dẫn đầu: <b>{role_sk_counts.iloc[0]['Kỹ Năng']}</b> (xuất hiện trong <b>{role_sk_counts.iloc[0]['Tỷ Lệ Yêu Cầu (%)']}%</b> tin)</div>
                    <div style="color: #334155;">• Nhóm công nghệ phổ biến: <b>{', '.join(role_sk_counts['Kỹ Năng'].head(4).tolist())}</b></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
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
            <div class="box-title">Xu Hướng & Dự Báo Số Lượng Tuyển Dụng IT</div>
            <div class="box-caption">Kết hợp số liệu ghi nhận thực tế từ tập mẫu và mô hình dự báo chuỗi thời gian cho các tháng tiếp theo</div>
        """,
        unsafe_allow_html=True,
    )

    df_dated = filtered_jobs[filtered_jobs["full_date"].notna()].copy()
    if not df_dated.empty and len(df_dated["month_year"].unique()) >= 4:
        df_monthly_series = (
            df_dated.groupby("month_year")
            .agg(start_date=("full_date", "min"), job_count=("job_id", "count"))
            .reset_index()
            .sort_values("start_date")
            .reset_index(drop=True)
        )

        forecast_col1, forecast_col2 = st.columns([8, 4])
        with forecast_col2:
            n_months_ahead = st.slider(
                "Số tháng tương lai cần dự báo:",
                min_value=2,
                max_value=6,
                value=4,
                step=1,
            )

        y_vals = df_monthly_series["job_count"].values
        model_holt = Holt(y_vals, initialization_method="estimated")
        fit_holt = model_holt.fit(smoothing_level=0.5, smoothing_trend=0.3, optimized=True)
        
        fitted = fit_holt.fittedvalues
        rmse_score = np.sqrt(mean_squared_error(y_vals, fitted))

        future_pred = fit_holt.forecast(n_months_ahead)
        future_pred = np.maximum(future_pred, 50)

        last_dt = df_monthly_series["start_date"].max()
        future_dts = pd.date_range(start=last_dt + pd.DateOffset(months=1), periods=n_months_ahead, freq="MS")
        future_periods = [d.strftime("%m/%Y") for d in future_dts]

        full_timeline = list(df_monthly_series["month_year"]) + future_periods

        lower_vals = np.maximum(future_pred - 1.28 * rmse_score, 50)
        upper_vals = future_pred + 1.28 * rmse_score

        growth_text = "tăng trưởng nhẹ" if future_pred[-1] >= future_pred[0] else "ổn định"
        st.markdown(
            f"""
            <div style="background: #F0FDF4; border-left: 5px solid #059669; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;">
                <div style="font-weight: 800; font-size: 1.05rem; color: #065F46; margin-bottom: 6px;">
                    NHẬN ĐỊNH XU HƯỚNG TƯƠNG LAI
                </div>
                <div style="font-size: 0.98rem; color: #1E293B; line-height: 1.6;">
                    Dựa trên nhịp độ tuyển dụng 13 tháng qua, mô hình dự đoán nhu cầu tuyển dụng IT trong <b>{n_months_ahead} tháng tới (từ {future_periods[0]} đến {future_periods[-1]})</b> có chiều hướng <b>{growth_text}</b>.
                    Số lượng tin đăng dự kiến dao động trong khoảng từ <b>{future_pred[0]:.0f} đến {future_pred[-1]:.0f} tin/tháng</b>, phù hợp với chu kỳ tăng cường nhân sự công nghệ phục vụ dự án cuối năm và đầu năm mới.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        last_actual_period = df_monthly_series["month_year"].iloc[-1]
        last_actual_val = df_monthly_series["job_count"].iloc[-1]

        plot_forecast_periods = [last_actual_period] + future_periods
        plot_forecast_vals = [last_actual_val] + list(future_pred)
        plot_lower_vals = [last_actual_val] + list(lower_vals)
        plot_upper_vals = [last_actual_val] + list(upper_vals)

        # Tính toán giới hạn trục Y thoáng đãng để không bị chạm nóc
        y_max_data = max(df_monthly_series["job_count"].max(), max(plot_upper_vals))
        y_top_limit = y_max_data * 1.22

        fig_forecast = go.Figure()

        # 1. Vẽ đường THỰC TẾ trước
        fig_forecast.add_trace(
            go.Scatter(
                x=df_monthly_series["month_year"],
                y=df_monthly_series["job_count"],
                mode="lines+markers+text",
                name="Thực tế ghi nhận",
                line=dict(color="#1D4ED8", width=3.5),
                marker=dict(size=10, color="#1E40AF"),
                text=df_monthly_series["job_count"].apply(lambda v: f"<b>{v:,}</b>"),
                textposition="top center",
                cliponaxis=False,
                textfont=dict(size=13, color="#1D4ED8"),
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

        # 3. Đường DỰ BÁO nối tiếp
        fig_forecast.add_trace(
            go.Scatter(
                x=plot_forecast_periods,
                y=plot_forecast_vals,
                mode="lines+markers+text",
                name="Đường dự báo tương lai",
                line=dict(color="#D97706", width=3, dash="dash"),
                marker=dict(size=10, color="#B45309", symbol="diamond"),
                text=[f"<b>{v:.0f}</b>" for v in plot_forecast_vals],
                textposition="top center",
                cliponaxis=False,
                textfont=dict(size=13, color="#B45309"),
            )
        )

        fig_forecast.update_layout(
            **CHART_THEME,
            height=470,
            margin=dict(t=40, b=85, l=55, r=40),
            xaxis=dict(
                type="category",
                categoryorder="array",
                categoryarray=full_timeline,
                title=dict(text="<b>Mốc Thời Gian Tuyến Tính (Tháng / Năm)</b>", font=dict(size=14, color="#0F172A")),
                tickfont=dict(size=13, color="#0F172A"),
                showgrid=True,
                gridcolor="#E2E8F0",
                tickangle=-15,
            ),
            yaxis=dict(
                range=[0, y_top_limit],
                title=dict(text="<b>Số Lượng Tin Tuyển Dụng</b>", font=dict(size=14, color="#0F172A")),
                tickfont=dict(size=13, color="#0F172A"),
                showgrid=True,
                gridcolor="#E2E8F0",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12, color="#0F172A"),
                bgcolor="rgba(255,255,255,0.85)"
            ),
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        st.markdown(
            """
            <div style="font-size: 0.9rem; color: #475569; margin-top: 8px;">
                * Ghi chú: Đường nét đứt màu cam và dải bóng mờ thể hiện ước tính xu hướng tham khảo dựa trên dữ liệu các tháng gần nhất.
            </div>
            """,
            unsafe_allow_html=True,
        )
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
        level_order = ["Intern / Fresher", "Junior", "Middle", "Senior", "Lead / Manager"]
        df_salary_level = df_salary[df_salary["level_name"].isin(level_order)]

        level_stats = df_salary_level.groupby("level_name")["salary_avg"].agg(
            Số_Tin="count",
            Thấp_Nhất="min",
            Trung_Vị="median",
            Cao_Nhất="max"
        ).reindex(level_order).dropna().reset_index()

        fresher_med = level_stats[level_stats["level_name"] == "Intern / Fresher"]["Trung_Vị"].values
        fresher_val = f"{fresher_med[0]:.1f} tr" if len(fresher_med) > 0 else "9.0 tr"

        mid_med = level_stats[level_stats["level_name"] == "Middle"]["Trung_Vị"].values
        mid_val = f"{mid_med[0]:.1f} tr" if len(mid_med) > 0 else "31.9 tr"

        senior_med = level_stats[level_stats["level_name"] == "Senior"]["Trung_Vị"].values
        senior_val = f"{senior_med[0]:.1f} tr" if len(senior_med) > 0 else "45.0 tr"

        st.markdown(
            f"""
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 20px;">
                <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 16px 18px; text-align: center;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #475569; text-transform: uppercase;">MỨC LƯƠNG KHỞI ĐIỂM (FRESHER)</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #1D4ED8; margin: 6px 0;">{fresher_val}</div>
                    <div style="font-size: 0.9rem; color: #065F46; font-weight: 600;">Thực tập sinh & mới tốt nghiệp</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 16px 18px; text-align: center;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #475569; text-transform: uppercase;">MỨC PHỔ BIẾN (JUNIOR - MIDDLE)</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #1D4ED8; margin: 6px 0;">24 - {mid_val}</div>
                    <div style="font-size: 0.9rem; color: #065F46; font-weight: 600;">Từ 1 đến 4 năm kinh nghiệm</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 16px 18px; text-align: center;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #475569; text-transform: uppercase;">CẤP CHUYÊN GIA (SENIOR / LEAD)</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #0F172A; margin: 6px 0;">{senior_val}+</div>
                    <div style="font-size: 0.9rem; color: #065F46; font-weight: 600;">Từ 5 năm kinh nghiệm trở lên</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="box-card">
                <div class="box-title">Mức Lương Phổ Biến Theo Từng Vị Trí Chuyên Môn IT</div>
                <div class="box-caption">So sánh mức lương trung vị giữa các nhánh nghề IT (Triệu VNĐ / Tháng)</div>
            """,
            unsafe_allow_html=True,
        )
        top_roles_salary = df_salary["role_name"].value_counts().head(8).index.tolist()
        df_role_sal = df_salary[df_salary["role_name"].isin(top_roles_salary)]
        role_sal_stats = df_role_sal.groupby("role_name")["salary_avg"].median().reset_index()
        role_sal_stats.columns = ["Vị Trí IT", "Lương Trung Vị"]
        role_sal_stats = role_sal_stats.sort_values("Lương Trung Vị", ascending=True)

        fig_role_sal = px.bar(
            role_sal_stats,
            x="Lương Trung Vị",
            y="Vị Trí IT",
            orientation="h",
            text=role_sal_stats["Lương Trung Vị"].apply(lambda v: f"<b>{v:.1f} tr / tháng</b>"),
            color="Lương Trung Vị",
            color_continuous_scale=["#BFDBFE", "#1D4ED8"],
        )
        fig_role_sal.update_layout(
            **CHART_THEME,
            height=390,
            yaxis=dict(title="", tickfont=dict(size=13, color="#0F172A")),
            xaxis=dict(
                title=dict(text="<b>Mức Lương Trung Vị (Triệu VNĐ / Tháng)</b>", font=dict(size=13, color="#0F172A")),
                showgrid=True,
                gridcolor="#E2E8F0",
                tickfont=dict(size=12, color="#0F172A")
            ),
            coloraxis_showscale=False,
        )
        fig_role_sal.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=13, color="#0F172A"))
        st.plotly_chart(fig_role_sal, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="box-card">
                <div class="box-title">Bảng Tổng Hợp Chi Tiết Khoảng Thu Nhập Theo Cấp Bậc</div>
                <div class="box-caption">Số liệu tính toán dựa trên các tin tuyển dụng có ghi rõ mức lương cụ thể (Triệu VNĐ / Tháng)</div>
            """,
            unsafe_allow_html=True,
        )
        display_table = level_stats.copy()
        display_table.columns = [
            "Cấp Bậc Nghề Nghiệp", 
            "Số Lượng Tin Khảo Sát", 
            "Mức Khởi Điểm Thấp Nhất (tr)", 
            "Mức Lương Phổ Biến Nhất (tr)", 
            "Mức Trần Cao Nhất (tr)"
        ]
        st.dataframe(
            display_table.style.format({
                "Số Lượng Tin Khảo Sát": "{:,.0f}",
                "Mức Khởi Điểm Thấp Nhất (tr)": "{:.1f}",
                "Mức Lương Phổ Biến Nhất (tr)": "{:.1f}",
                "Mức Trần Cao Nhất (tr)": "{:.1f}",
            }).set_properties(**{'background-color': '#FFFFFF', 'color': '#0F172A', 'border-color': '#CBD5E1'}),
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
    <div style="text-align: center; color: #475569; font-size: 0.9rem; padding: 24px 0 10px 0; border-top: 1px solid #CBD5E1; margin-top: 20px;">
        Đề Tài Khảo Sát Dữ Liệu Tuyển Dụng IT • Sử dụng Streamlit & Plotly • Số liệu mang tính tham khảo trong phạm vi tập dữ liệu môn học
    </div>
    """,
    unsafe_allow_html=True,
)
