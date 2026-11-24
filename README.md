# IT Recruitment Data Analysis in Vietnam
# Phân tích Dữ liệu Tuyển dụng IT Việt Nam

Dự án phân tích dữ liệu tuyển dụng ngành Công nghệ Thông tin tại Việt Nam từ 4 nền tảng tuyển dụng lớn: **ITViec**, **TopCV**, **VietnamWorks** và **LinkedIn**. Dự án tập trung vào việc thu thập, xử lý, tích hợp, xây dựng Data Warehouse (Mô hình Star Schema) và trực quan hóa dữ liệu đa nền tảng (Web Dashboard Streamlit + Power BI) nhằm khảo sát thị trường lao động IT, nhu cầu kỹ năng công nghệ, phân bố mức lương, cơ cấu cấp bậc và xu hướng tuyển dụng.

---

## 🎯 Mục tiêu Dự án

- Thu thập và tích hợp dữ liệu tuyển dụng IT từ 4 nguồn: ITViec, TopCV, VietnamWorks và LinkedIn.
- Xây dựng quy trình ETL tự động để làm sạch, chuẩn hóa, khử trùng lặp và xử lý dữ liệu.
- Xây dựng Data Warehouse theo mô hình Star Schema trên SQLite phục vụ phân tích.
- Phân tích phân bố tin tuyển dụng theo thành phố, vai trò nghề nghiệp và cấp bậc.
- Khảo sát các kỹ năng công nghệ được yêu cầu nhiều nhất và ma trận nhiệt (Heatmap) kỹ năng x vai trò IT.
- Phân tích phân bố mức lương bằng biểu đồ hộp (Boxplot), tình trạng công khai lương và các mức phân vị.
- Khám phá xu hướng tuyển dụng theo mốc thời gian rõ ràng (Tháng/Năm).
- Xây dựng Web Dashboard tương tác bằng **Python (Streamlit + Plotly)** và Power BI phục vụ báo cáo và khám phá dữ liệu.

---

## 📁 Cấu trúc Thư mục Dự án

```text
IT_Recruitment_Analysis/
├── data/
│   ├── raw/                         # Dữ liệu gốc
│   │   ├── ITViec_data.csv
│   │   ├── TopCV_jobs.csv
│   │   ├── job_descriptions.csv
│   │   └── vietjobs_sample.csv
│   ├── interim/                     # Dữ liệu trung gian
│   ├── processed/                    # Dữ liệu sạch
│   │   └── it_jobs_cleaned.csv
│   └── warehouse/                    # Data Warehouse
│       ├── it_recruitment_dwh.db
│       ├── dim_date.csv
│       ├── dim_city.csv
│       ├── dim_role.csv
│       ├── dim_level.csv
│       ├── dim_company.csv
│       ├── dim_skill.csv
│       ├── fact_job_postings.csv
│       └── fact_job_skills.csv
│
├── src/                               # Mã nguồn ETL
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── notebooks/                          # Jupyter Notebooks
│   ├── 01_data_profiling.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_data_integration.ipynb
│   └── 04_exploratory_analysis.ipynb
│
├── results/                            # Kết quả phân tích
│   ├── charts/                         # Các biểu đồ phân tích
│   └── tables/                         # Các bảng thống kê
│
├── dashboard/                          # Power BI Dashboard
│   ├── IT_Recruitment_Dashboard.pbix
│   ├── screenshots/                    # Ảnh chụp Dashboard thực tế
│   │   ├── overview.png
│   │   ├── skills_analysis.png
│   │   ├── salary_analysis.png
│   │   └── recruitment_trends.png
│   └── README.md
│
├── reports/                            # Báo cáo và tài liệu dữ liệu
│   ├── data_quality/
│   │   └── cleaning_overview.png
│   ├── cleaning_log.xlsx
│   └── data_dictionary.xlsx
│
├── run_etl_pipeline.py                # Script chạy ETL
├── requirements.txt
└── README.md
```

---

## 🚀 Chạy ETL Pipeline

### Chạy toàn bộ Pipeline

```bash
python run_etl_pipeline.py
```

Pipeline thực hiện 3 giai đoạn:

1. **EXTRACT** – Trích xuất dữ liệu từ các nguồn trong `data/raw/`.
2. **TRANSFORM** – Làm sạch, chuẩn hóa, xử lý dữ liệu trùng lặp và trích xuất đặc trưng.
3. **LOAD** – Nạp dữ liệu vào Data Warehouse theo mô hình Star Schema.

### Chạy từng bước riêng

```bash
python run_etl_pipeline.py --step extract
python run_etl_pipeline.py --step transform
python run_etl_pipeline.py --step load
```

> **Lưu ý:** Các lệnh trên cần được thực thi theo đúng thứ tự và điều kiện đầu vào của từng bước ETL.

---

## 📊 Phân tích Dữ liệu Khám phá (EDA)

Phân tích dữ liệu được thực hiện bằng Python trong Notebook `04_exploratory_analysis.ipynb`. Các biểu đồ và bảng thống kê được xây dựng nhằm khám phá đặc điểm của thị trường tuyển dụng IT.

### 1. Phân bố Tin tuyển dụng

- Số lượng tin tuyển dụng theo thành phố.
- Số lượng tin tuyển dụng theo vai trò nghề nghiệp.

### 2. Phân tích Nhu cầu Kỹ năng

- Top 15 kỹ năng được yêu cầu nhiều nhất.
- Phân bố kỹ năng theo từng vai trò nghề nghiệp.
- Tỷ lệ tin tuyển dụng yêu cầu từng kỹ năng.

### 3. Phân tích Xu hướng Tuyển dụng

- Xu hướng số lượng tin tuyển dụng theo thời gian.
- Tổng số tin tuyển dụng theo từng giai đoạn.
- Quan sát sự thay đổi nhu cầu tuyển dụng trên dữ liệu thu thập được.

### 4. Phân tích Mức lương

- Mức lương theo vai trò nghề nghiệp.
- Mức lương theo cấp bậc.
- Tỷ lệ tin tuyển dụng công khai và không công khai mức lương.

> Các phân tích về mức lương chỉ sử dụng những tin tuyển dụng có thông tin lương hợp lệ. Kết quả mang tính tham khảo trên tập dữ liệu thu thập được, không đại diện tuyệt đối cho toàn bộ thị trường lao động IT Việt Nam.

---

## 🖥️ Web Dashboard Trực Quan (Streamlit + Plotly)

Bên cạnh Power BI, dự án cung cấp Web Dashboard hoàn chỉnh bằng Python sử dụng **Streamlit** và **Plotly**, hỗ trợ tương tác đa chiều không phụ thuộc vào phần mềm cài đặt:

```bash
# Khởi chạy Web Dashboard
streamlit run dashboard/app.py
```

### Các Tab tính năng chính:
1. **📊 1. Tổng Quan Thị Trường:** 4 KPI cards (4.761 tin tuyển dụng, 2.030 công ty, lương trung vị, tỷ lệ công khai), Donut chart cơ cấu nguồn, phân bố địa lý và cơ cấu vai trò IT.
2. **🎯 2. Nhu Cầu Kỹ Năng:** Top 15 kỹ năng công nghệ, cơ cấu nhóm kỹ năng và **Ma trận nhiệt (Heatmap) Kỹ năng x Vai trò IT**.
3. **📈 3. Xu Hướng Biến Động:** Biểu đồ đường (Line chart) cỡ lớn với **mốc thời gian Tháng/Năm rõ nét**, phân tích biến động theo nguồn và theo nhóm kỹ năng.
4. **💰 4. Phân Tích Mức Lương:** **Biểu đồ hộp (Boxplot)** phân bố lương theo Cấp bậc (Intern -> Lead/Manager) và Vai trò IT, bảng thống kê các mức phân vị (Min, Q1, Median, Q3, Max).

---

## 📈 Power BI Dashboard

Dashboard được xây dựng bằng Power BI Desktop nhằm trực quan hóa kết quả phân tích và hỗ trợ người xem khám phá dữ liệu tuyển dụng.

### Các trang Dashboard

| Trang Dashboard | Nội dung phân tích |
|---|---|
| Tổng quan | Tổng số tin tuyển dụng, lương trung vị, số công ty tuyển dụng, số tin theo thành phố và vai trò |
| Phân tích kỹ năng | Top 15 kỹ năng, kỹ năng theo vai trò và tỷ lệ tin tuyển dụng yêu cầu kỹ năng |
| Phân tích lương | Mức lương theo vai trò, cấp bậc và tình trạng công khai lương |
| Xu hướng tuyển dụng | Biến động số lượng tin tuyển dụng theo thời gian |

### Giao diện Dashboard thực tế

Các hình ảnh dưới đây là ảnh chụp trực tiếp Dashboard Power BI đã xây dựng trong dự án.

#### Dashboard Tổng quan

![Dashboard Tổng quan](dashboard/screenshots/overview.png)

#### Dashboard Phân tích kỹ năng

![Dashboard Phân tích kỹ năng](dashboard/screenshots/skills_analysis.png)

#### Dashboard Phân tích lương

![Dashboard Phân tích lương](dashboard/screenshots/salary_analysis.png)

#### Dashboard Xu hướng tuyển dụng

![Dashboard Xu hướng tuyển dụng](dashboard/screenshots/recruitment_trends.png)

### Mở Dashboard

Mở tệp Power BI tại:

```text
dashboard/IT_Recruitment_Dashboard.pbix
```

---

## 🏗️ Data Warehouse – Star Schema

Data Warehouse được xây dựng trên SQLite và các bảng dữ liệu CSV, phục vụ truy vấn và phân tích dữ liệu tuyển dụng.

### Các bảng Dimension

| Bảng | Nội dung |
|---|---|
| dim_date | Thông tin thời gian |
| dim_city | Thông tin thành phố |
| dim_role | Vai trò nghề nghiệp |
| dim_level | Cấp bậc tuyển dụng |
| dim_company | Thông tin công ty |
| dim_skill | Danh mục kỹ năng |

### Các bảng Fact

| Bảng | Nội dung |
|---|---|
| fact_job_postings | Dữ liệu tin tuyển dụng |
| fact_job_skills | Liên kết giữa tin tuyển dụng và kỹ năng |

### Sơ đồ tổng quan
```
                  ┌──────────────┐
                  │   DIM_DATE   │
                  └──────┬───────┘
                         │
   ┌────────────┐  ┌─────┴──────────┐  ┌──────────────┐
   │  DIM_CITY  ├──┤ FACT_JOB_      ├──┤  DIM_ROLE    │
   └────────────┘  │   POSTINGS     │  └──────────────┘
                   │ (4.207 dòng)   │
   ┌────────────┐  └──┬──────────┬──┘  ┌──────────────┐
   │ DIM_LEVEL  ├─────┘          └─────┤ DIM_COMPANY  │
   └────────────┘                      └──────────────┘

                   ┌─────────────────┐
                   │  FACT_JOB_      │  ┌──────────────┐
                   │    SKILLS       ├──┤  DIM_SKILL   │
                   │ (25.791 dòng)   │  │ (3.104 kn)   │
                   └─────────────────┘  └──────────────┘
```
---

## 📌 Kết quả Hiện tại

### Dữ liệu sau xử lý

| Chỉ tiêu | Kết quả |
|---|---:|
| Dữ liệu thô ban đầu (4 nguồn: ITViec, TopCV, VietnamWorks, LinkedIn) | 5.467 bản ghi |
| Bản ghi trùng lặp & ngoại lai được loại bỏ | 706 bản ghi |
| Dữ liệu sạch sau chuẩn hóa (Fact Job Postings) | **4.761 bản ghi** |
| Doanh nghiệp tuyển dụng (Dim Company) | **2.030 công ty** |
| Khu vực địa lý (Dim City) | 4 khu vực |
| Vai trò nghề nghiệp (Dim Role) | 16 vai trò IT |
| Kỹ năng công nghệ riêng biệt (Dim Skill) | 3.078 kỹ năng |
| Liên kết việc làm – kỹ năng (Fact Job Skills) | **26.835 liên kết** |

### Data Warehouse

- 6 bảng Dimension.
- 2 bảng Fact.
- Mô hình Star Schema.
- Dữ liệu được tổ chức phục vụ phân tích và trực quan hóa trên Power BI.

### Kết quả phân tích

- Xác định các thành phố có nhiều tin tuyển dụng IT.
- Khám phá cơ cấu nhu cầu tuyển dụng theo vai trò nghề nghiệp.
- Xác định các kỹ năng công nghệ được yêu cầu phổ biến.
- Phân tích sự khác biệt về kỹ năng giữa các vai trò.
- Khảo sát phân bố mức lương theo vai trò và cấp bậc.
- Đánh giá tình trạng công khai mức lương trong dữ liệu tuyển dụng.
- Quan sát xu hướng tuyển dụng theo thời gian.

---

## ⚠️ Lưu ý

- Dữ liệu được thu thập từ các nền tảng tuyển dụng cụ thể, không bao phủ toàn bộ thị trường IT Việt Nam.
- Các nguồn có thể khác nhau về cấu trúc, cách đặt tên vai trò và cách thể hiện mức lương.
- Số lượng tin tuyển dụng phản ánh dữ liệu thu thập được, không đồng nghĩa hoàn toàn với số lượng vị trí việc làm thực tế.
- Chỉ một phần tin tuyển dụng công khai mức lương; do đó các thống kê lương có thể không đại diện cho toàn bộ thị trường.
- Các kết quả phân tích xu hướng hiện tại mang tính mô tả dữ liệu lịch sử, chưa phải kết quả dự báo.

---

## 🛠️ Cài đặt và Môi trường

### 1. Clone Repository

```bash
git clone https://github.com/HoLeTrungBao/IT_Recruitment_Analysis.git
cd IT_Recruitment_Analysis
```

### 2. Khởi tạo môi trường ảo

```bash
python -m venv .venv
```

### 3. Kích hoạt môi trường ảo

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 4. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 5. Chạy ETL Pipeline

```bash
python run_etl_pipeline.py
```

### 6. Khởi chạy Web Dashboard (Python Streamlit)

Chạy lệnh sau để mở Dashboard tương tác trực tiếp trên trình duyệt web:

```bash
streamlit run dashboard/app.py
```

Trình duyệt sẽ tự động mở giao diện tại địa chỉ `http://localhost:8501`.

### 7. Mở Power BI Dashboard (Tùy chọn)

Mở Power BI Desktop và sử dụng tệp:

```text
dashboard/IT_Recruitment_Dashboard.pbix
```
