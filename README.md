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
│   │   ├── job_descriptions.csv
│   │   └── vietjobs_sample.csv
│   ├── interim/                  # Dữ liệu trung gian đã làm sạch riêng theo từng nguồn
│   │   ├── ITViec_cleaned.csv
│   │   ├── TopCV_cleaned.csv
│   │   └── job_descriptions_cleaned.csv
│   └── processed/                # Bộ dữ liệu sạch hợp nhất hoàn chỉnh
│       └── it_jobs_cleaned.csv   # 4.207 bản ghi sạch với 13 trường chuẩn
├── notebooks/                    # Jupyter Notebooks thực thi từng giai đoạn
│   ├── 01_data_profiling.ipynb   # Khảo sát & đánh giá chất lượng dữ liệu
│   ├── 02_data_cleaning.ipynb    # Tiền xử lý, làm sạch & trích xuất đặc trưng
│   ├── 03_data_integration.ipynb # Tích hợp và liên kết đa nguồn
│   └── 04_exploratory_analysis.ipynb # Phân tích khám phá dữ liệu (EDA)
├── reports/                      # Báo cáo và từ điển dữ liệu
│   ├── data_quality/             # Biểu đồ và báo cáo chất lượng dữ liệu
│   │   └── cleaning_overview.png
│   ├── cleaning_log.xlsx         # Nhật ký theo dõi chi tiết 10 bước làm sạch
│   └── data_dictionary.xlsx      # Từ điển dữ liệu mô tả 13 trường chuẩn
├── results/                      # Kết quả phân tích đầu ra
│   ├── tables/                   # Bảng thống kê kết quả
│   └── charts/                   # Biểu đồ trực quan hóa chuyên đề
├── requirements.txt              # Danh sách các thư viện phụ thuộc
└── README.md                     # Tài liệu giới thiệu dự án
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

4. **Khởi chạy Jupyter Lab:**
   ```bash
   jupyter lab
   ```

---

## 📊 Tóm tắt Kết quả Tiền xử lý & Làm sạch Dữ liệu

* **Dữ liệu thô ban đầu:** 4.881 bản ghi từ 4 tập dữ liệu.
* **Khử trùng lặp:** Loại bỏ 57 bản ghi trùng lặp tuyệt đối và 585 bản ghi trùng lặp logic liên nguồn.
* **Lọc bỏ dữ liệu ngoài ngành:** Loại bỏ 32 bản ghi phi IT (tin tuyển dụng cơ khí CNC, máy phay, kỹ thuật điện, xử lý nước thải).
* **Dữ liệu sạch hoàn chỉnh:** **4.207 bản ghi** IT chuẩn hóa, sẵn sàng cho phân tích khám phá (EDA) và mô hình hóa.
* **Các đặc trưng chính đã trích xuất:**
  - Mức lương định lượng chuẩn hóa sang đơn vị Triệu VNĐ/tháng (`salary_min`, `salary_max`, `salary_avg`, `is_negotiable`).
  - Phân nhóm 12 danh mục nghề IT chuẩn hóa (`role_category`).
  - Phân loại cấp bậc chuyên môn (`job_level`: Intern/Fresher, Junior, Middle, Senior, Lead).
  - Trích xuất số năm kinh nghiệm tối thiểu (`exp_years_min`, độ phủ 86%).
  - Chuẩn hóa Tỉnh/Thành phố làm việc (`city`).
  - Chuẩn hóa và bù khuyết kỹ năng công nghệ (`skills_list`, độ phủ 92.8%).
