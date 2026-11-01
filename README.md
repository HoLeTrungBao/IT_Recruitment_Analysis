# IT Recruitment Data Analysis in Vietnam (Phân tích Dữ liệu Tuyển dụng IT Việt Nam)

Dự án phân tích dữ liệu tuyển dụng ngành Công nghệ Thông tin tại Việt Nam từ nhiều nền tảng tuyển dụng lớn (ITViec, TopCV, LinkedIn...), phục vụ khảo sát xu hướng công nghệ, phân bố mức lương, cơ cấu cấp bậc và nhu cầu thị trường lao động CNTT.

---

## 📁 Cấu trúc Thư mục Dự án

```
IT_Recruitment_Analysis/
├── data/
│   ├── raw/                      # Dữ liệu gốc thu thập từ các nền tảng
│   │   ├── ITViec_data.csv
│   │   ├── TopCV_jobs.csv
│   │   └── job_descriptions.csv
│   ├── processed/                # Bộ dữ liệu sạch hợp nhất hoàn chỉnh
│   │   └── it_jobs_cleaned.csv   # 4.207 bản ghi sạch với 14 trường chuẩn
│   └── warehouse/                # Data Warehouse (Star Schema)
│       ├── it_recruitment_dwh.db # SQLite database
│       ├── dim_date.csv          # Bảng chiều: Thời gian
│       ├── dim_city.csv          # Bảng chiều: Thành phố
│       ├── dim_role.csv          # Bảng chiều: Vai trò nghề nghiệp
│       ├── dim_level.csv         # Bảng chiều: Cấp bậc
│       ├── dim_company.csv       # Bảng chiều: Công ty
│       ├── dim_skill.csv         # Bảng chiều: Kỹ năng (3.104 kỹ năng)
│       ├── fact_job_postings.csv # Bảng Fact: Tin tuyển dụng (4.207 bản ghi)
│       └── fact_job_skills.csv   # Bảng Fact: Kỹ năng-Tin tuyển dụng (25.791 bản ghi)
├── src/                          # Mã nguồn ETL pipeline
│   ├── extract.py                # Module E - Trích xuất dữ liệu thô
│   ├── transform.py              # Module T - Biến đổi & Làm sạch
│   └── load.py                   # Module L - Nạp vào Data Warehouse
├── notebooks/                    # Jupyter Notebooks thực thi từng giai đoạn
│   └── 02_data_cleaning.ipynb    # Tiền xử lý, làm sạch & trích xuất đặc trưng
├── reports/                      # Báo cáo và từ điển dữ liệu
│   ├── data_quality/
│   │   └── cleaning_overview.png
│   ├── cleaning_log.xlsx
│   └── data_dictionary.xlsx
├── run_etl_pipeline.py           # Script chạy toàn bộ ETL pipeline (1 lệnh)
├── requirements.txt
└── README.md
```

---

## 🚀 Chạy ETL Pipeline

### Chạy toàn bộ pipeline (1 lệnh duy nhất)

```bash
python run_etl_pipeline.py
```

Pipeline sẽ tự động thực hiện 3 bước:
1. **EXTRACT** – Đọc dữ liệu thô từ `data/raw/`
2. **TRANSFORM** – Làm sạch, chuẩn hóa, khử trùng lặp, trích xuất đặc trưng
3. **LOAD** – Xây dựng Star Schema và nạp vào Data Warehouse (`data/warehouse/`)

### Chạy từng bước riêng (demo)

```bash
python run_etl_pipeline.py --step extract      # Chỉ trích xuất
python run_etl_pipeline.py --step transform    # Trích xuất + Biến đổi
python run_etl_pipeline.py --step load         # Toàn bộ ETL
```

> **Lưu ý:** Pipeline được thiết kế **lũy đẳng** (idempotent) – chạy bao nhiêu lần tùy thích, dữ liệu KHÔNG BAO GIỜ bị trùng lặp.

---

## 📊 Kết nối Power BI

1. Mở **Power BI Desktop**
2. Chọn **Get Data → Text/CSV** (hoặc **Folder**)
3. Trỏ vào thư mục `data/warehouse/`
4. Import các tệp CSV (hoặc kết nối SQLite `.db`)
5. Thiết lập relationships giữa các bảng Fact-Dim theo khóa ngoại
6. Khi dữ liệu thay đổi: chạy lại `python run_etl_pipeline.py` → bấm **Refresh** trong Power BI

### Sơ đồ Star Schema

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

## 🛠️ Cài đặt và Môi trường

1. **Khởi tạo môi trường ảo:**
   ```bash
   python -m venv .venv
   ```

2. **Kích hoạt môi trường ảo:**
   * Trên Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   * Trên Linux / macOS:
     ```bash
     source .venv/bin/activate
     ```

3. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Chạy pipeline:**
   ```bash
   python run_etl_pipeline.py
   ```

---

## 📈 Tóm tắt Kết quả

* **Dữ liệu thô ban đầu:** 4.876 bản ghi từ 3 tập dữ liệu (ITViec, TopCV, job_descriptions).
* **Khử trùng lặp:** Loại bỏ 585 bản ghi trùng lặp logic liên nguồn.
* **Dữ liệu sạch hoàn chỉnh:** **4.207 bản ghi** IT chuẩn hóa.
* **Data Warehouse Star Schema:**
  - 6 bảng Dimension (Date, City, Role, Level, Company, Skill)
  - 2 bảng Fact (Job Postings, Job Skills)
  - 3.104 kỹ năng riêng biệt được bóc tách
  - 25.791 liên kết kỹ năng-tin tuyển dụng
