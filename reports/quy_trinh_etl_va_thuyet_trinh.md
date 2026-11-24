# BÁO CÁO QUY TRÌNH ETL VÀ TÀI LIỆU THUYẾT TRÌNH BẢO VỆ DỰ ÁN

Tài liệu này được biên soạn nhằm giải quyết toàn bộ các nhận xét và phản biện của Thầy/Cô hướng dẫn sau đợt báo cáo giữa kỳ, bao gồm:
1. **Bổ sung đầy đủ nguồn dữ liệu VietnamWorks** vào kho dữ liệu.
2. **Giải thích quy trình ETL (Extract - Transform - Load)** một cách trực quan, bình dân, dễ hiểu cho mọi người nghe.
3. **Làm rõ nguồn gốc dữ liệu LinkedIn** (được thu thập từ tập mô tả công việc IT chuẩn hóa).
4. **Giải quyết vấn đề mốc thời gian**: Hiển thị mốc thời gian lớn, rõ ràng theo định dạng Tháng/Năm.
5. **Đa dạng hóa biểu đồ trực quan**: Bổ sung Biểu đồ nhiệt (Heatmap), Biểu đồ hộp (Boxplot), Biểu đồ đường (Line Chart) to rõ thay vì chỉ dùng Bar Chart.
6. **Xây dựng Dashboard bằng Python**: Triển khai hoàn chỉnh ứng dụng Web Dashboard bằng **Streamlit & Plotly**.
7. **Quy tắc chạy Demo**: **Tuyệt đối không show code**, chỉ thao tác tương tác trực tiếp trên giao diện Dashboard.

---

## PHẦN 1: GIẢI THÍCH QUY TRÌNH ETL CHO MỌI NGƯỜI ĐỀU HIỂU

### 1.1. Ẩn dụ bình dân: "Từ Nông Sản Thô Đến Kệ Siêu Thị"
Để người nghe không chuyên về kỹ thuật cũng nắm được bản chất, ta có thể hình dung quy trình ETL giống như quy trình đưa nông sản vào siêu thị:

* **E - Extract (Thu gom nguyên liệu thô):** Giống như đi thu hoạch nông sản từ nhiều nông trại khác nhau (ITViec, TopCV, VietnamWorks, LinkedIn). Mỗi nơi thu hoạch theo một rổ khác nhau, có chỗ ghi tiếng Anh, có chỗ ghi tiếng Việt, có củ to củ nhỏ lộn xộn.
* **T - Transform (Sơ chế, làm sạch và đóng gói chuẩn hóa):** Đưa toàn bộ vào nhà máy sơ chế:
  - Rửa sạch đất cát, loại bỏ những củ hỏng, củ bị trùng lặp (Khử trùng lặp).
  - Quy đổi đơn vị: Chỗ ghi "20 - 30 triệu", chỗ ghi "1000 - 1500 USD", chỗ ghi "Thương lượng" -> tất cả được chuẩn hóa về cùng một đơn vị "Triệu VNĐ/tháng".
  - Chuẩn hóa tên gọi: "React", "ReactJS", "React.js" -> gom về một tên chuẩn duy nhất "ReactJS".
  - Phân loại cấp bậc: Gán nhãn rõ ràng: Intern, Fresher, Junior, Middle, Senior, Lead/Manager.
* **L - Load (Xếp lên kệ siêu thị có ngăn nắp - Data Warehouse):** Nông sản sau khi sơ chế chuẩn hóa được chuyển vào siêu thị, xếp gọn gàng theo mô hình Ngôi sao (Star Schema):
  - Kệ trung tâm (Fact): Chứa các số liệu cân đo đong đếm (Mức lương, số tin tuyển dụng).
  - Các kệ danh mục xung quanh (Dimensions): Phân loại theo Ngày tháng (Date), Thành phố (City), Vị trí IT (Role), Cấp bậc (Level), Công ty (Company), Kỹ năng (Skill).

---

### 1.2. Sơ đồ Luồng Dữ Liệu Chi Tiết

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       1. BƯỚC EXTRACT (TRÍCH XUẤT)                          │
├───────────────┬────────────────┬──────────────────────┬─────────────────────┤
│    ITViec     │     TopCV      │    VietnamWorks      │      LinkedIn       │
│  (1.159 thô)  │   (616 thô)    │      (591 thô)       │    (3.101 thô)      │
└───────┬───────┴────────┬───────┴──────────┬───────────┴──────────┬──────────┘
        │                │                  │                      │
        ▼                ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      2. BƯỚC TRANSFORM (CHUẨN HÓA)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Lọc dữ liệu: Chỉ giữ các vị trí Công nghệ thông tin (is_tech = 'tech')   │
│  • Khử trùng lặp: Nhận diện theo Cặp (Tên công ty + Tiêu đề công việc)      │
│  • Chuẩn hóa Lương: Chuyển đổi USD -> VNĐ, Năm -> Tháng, tính Min/Max/Avg   │
│  • Chuẩn hóa Kỹ năng: Tách mảng, xóa ngoặc/nháy, map vào từ điển chuẩn      │
│  • Chuẩn hóa Thời gian: Đưa về định dạng chuẩn YYYY-MM-DD và MM/YYYY        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         3. BƯỚC LOAD (NẠP VÀO KHO)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│     Kho Dữ Liệu SQLite (it_recruitment_dwh.db) + Bộ tệp CSV Warehouse       │
│                                                                             │
│  • fact_job_postings (4.761 tin IT)   • dim_date (163 mốc thời gian)        │
│  • fact_job_skills  (26.835 liên kết) • dim_city (4 khu vực địa lý)         │
│  • dim_role         (16 vai trò IT)   • dim_level (7 cấp bậc kinh nghiệm)   │
│  • dim_company      (2.030 công ty)   • dim_skill (86 kỹ năng chuẩn hóa)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHẦN 2: LÀM RÕ CÁC NGUỒN DỮ LIỆU THU THẬP

Khi Hội đồng hỏi: *"Nhóm đã thu thập dữ liệu từ những nguồn nào? Tại sao lúc đầu không nhắc LinkedIn mà lại thấy có dữ liệu LinkedIn?"*, bạn trả lời như sau:

1. **Tổng hợp 4 nguồn dữ liệu tuyển dụng uy tín:**
   - **ITViec:** Chuyên trang tuyển dụng việc làm IT chất lượng cao tại Việt Nam (thu thập thông qua crawler tự động của nhóm).
   - **TopCV:** Nền tảng việc làm phổ biến hàng đầu với số lượng tin dồi dào trên cả nước.
   - **VietnamWorks:** Sàn việc làm thâm niên, có lượng lớn các tập đoàn và doanh nghiệp đa quốc gia tuyển dụng nhân sự IT.
   - **LinkedIn:** Mạng xã hội tuyển dụng nghề nghiệp lớn nhất thế giới.
2. **Làm rõ nguồn dữ liệu LinkedIn:**
   - Dữ liệu LinkedIn được nhóm tích hợp từ bộ tập dữ liệu (dataset) mô tả công việc IT thực tế trên LinkedIn do cộng đồng tuyển dụng chia sẻ. 
   - Nhóm quyết định đưa dữ liệu LinkedIn vào vì:
     * Nền tảng LinkedIn phản ánh rõ nhu cầu kỹ năng của các công ty nước ngoài / Outsourcing quốc tế tuyển lập trình viên Việt Nam.
     * Cung cấp một góc nhìn đa chiều, đối sánh giữa thị trường tuyển dụng nội địa (ITViec, TopCV, VietnamWorks) và tiêu chuẩn kỹ năng quốc tế (LinkedIn).

---

## PHẦN 3: KỊCH BẢN THUYẾT TRÌNH DEMO (TUYỆT ĐỐI KHÔNG SHOW CODE)

> **QUY TẮC SỐNG CÒN:** Không mở file code `.py`, không chiếu các dòng lệnh phức tạp. Chỉ mở Terminal gõ 1 dòng khởi động duy nhất, sau đó chuyển toàn màn hình sang Trình duyệt Web để thao tác.

### Bước 1: Khởi động ứng dụng (Mất 3 giây)
Mở cửa sổ dòng lệnh và gõ:
```bash
streamlit run dashboard/app.py
```
*(Ngay khi trình duyệt mở ra trang `http://localhost:8501`, hãy phóng to toàn màn hình F11).*

### Bước 2: Thuyết trình theo cấu trúc 4 Tab trên Web Dashboard

#### Mở đầu (Giới thiệu chung & Bộ lọc Sidebar)
*"Kính thưa Thầy/Cô và Hội đồng, nhóm chúng em xin phép trình diễn ứng dụng Web Dashboard phân tích dữ liệu tuyển dụng IT Việt Nam được xây dựng hoàn toàn bằng ngôn ngữ Python trên nền tảng Streamlit và Plotly. Ứng dụng kết nối trực tiếp với Kho dữ liệu Data Warehouse tổng hợp hơn 4.700 tin tuyển dụng từ 4 nguồn lớn..."*
- Chỉ vào **Thanh bộ lọc bên trái (Sidebar)**: Demo lọc theo Nguồn (chọn/bỏ chọn VietnamWorks, ITViec), lọc theo Địa điểm (TP.HCM, Hà Nội), Cấp bậc và Vai trò IT để chứng minh dữ liệu phản hồi tức thì.

#### Tab 1: Tổng Quan Thị Trường (📊)
- **4 Thẻ chỉ số cốt lõi (KPI):**
  - Tổng số việc làm: **4.761 tin tuyển dụng IT**.
  - Doanh nghiệp tuyển dụng: **2.030 công ty**.
  - Mức lương trung vị thị trường: **32.5 triệu VNĐ/tháng**.
  - Tỷ lệ tin công khai lương: **25.4%** (cho thấy đa số doanh nghiệp IT vẫn chuộng hình thức "Lương thỏa thuận").
- **Biểu đồ cơ cấu nguồn (Donut Chart):** Cho thấy tỷ trọng đóng góp từ cả 4 nguồn.
- **Biểu đồ phân bố địa lý:** TP.HCM tiếp tục là trung tâm công nghệ lớn nhất cả nước, tiếp theo là Hà Nội và Đà Nẵng.

#### Tab 2: Nhu Cầu Kỹ Năng & Điểm Nhấn Ma Trận Nhiệt Heatmap (🎯)
- **Top 15 Kỹ năng hàng đầu:** Java, Python, ReactJS, SQL, Docker, AWS dẫn đầu danh sách yêu cầu.
- **Biểu đồ Ma trận Nhiệt (Heatmap) Kỹ năng x Vai trò IT:**
  - *"Để khắc phục sự đơn điệu của các biểu đồ cột thông thường, nhóm đã thiết kế biểu đồ nhiệt thể hiện mối quan hệ giữa Vị trí công việc và Kỹ năng công nghệ."*
  - Chỉ vào ô màu đậm: Ví dụ vị trí Backend tập trung cao độ vào Java, Python, Node.js, trong khi DevOps tập trung vào Docker, AWS, Kubernetes.

#### Tab 3: Xu Hướng Biến Động Theo Mốc Thời Gian (📈)
- *"Giải quyết nhận xét về việc mốc thời gian trước đây khó quan sát, nhóm đã thiết kế biểu đồ đường cỡ lớn với các mốc thời gian Tháng/Năm hiển thị trực quan."*
- Quan sát chu kỳ tuyển dụng IT qua các tháng (tăng trưởng mạnh vào các giai đoạn cuối năm và sau Tết).
- Cho thấy sự chuyển dịch nhu cầu kỹ năng: Xu hướng các công nghệ Cloud/DevOps và Data/AI gia tăng liên tục qua các chu kỳ.

#### Tab 4: Phân Tích Mức Lương Bằng Biểu Đồ Hộp Boxplot (💰)
- *"Thay vì chỉ tính mức lương trung bình đơn giản dễ bị bóp méo bởi các giá trị quá cao hoặc quá thấp, nhóm sử dụng Biểu đồ Hộp (Boxplot) để phản ánh trung thực toàn bộ phân bố lương."*
- Giải thích các đường trên hộp:
  - Vạch giữa hộp: **Lương trung vị (Median)** - mức lương thực tế mà 50% lập trình viên nhận được.
  - Cạnh đáy và đỉnh hộp: Mức phân vị 25% (Q1) và 75% (Q3).
  - Hai râu và điểm rời: Mức lương sàn (Min), trần (Max) và các mức lương cao vượt trội (Outliers).
- Phân tích bậc thang lương theo kinh nghiệm: Intern (~5-8 tr) -> Fresher (~10-15 tr) -> Junior (~15-22 tr) -> Middle (~25-35 tr) -> Senior (~40-60 tr) -> Lead/Manager (~60-100+ tr).

---

## PHẦN 4: HƯỚNG DẪN TRẢ LỜI CÁC CÂU HỎI THƯỜNG GẶP CỦA HỘI ĐỒNG

| Câu hỏi của Thầy/Cô | Cách trả lời tự tin, đúng trọng tâm |
| :--- | :--- |
| **Tại sao lại chọn Lương trung vị (Median) thay vì Lương trung bình (Mean)?** | Trong dữ liệu tiền lương, phân bố thường bị **lệch phải** (Right-skewed) do có một số ít chuyên gia hoặc cấp quản lý nhận mức lương rất cao (vài trăm triệu), điều này sẽ kéo giá trị trung bình lên cao giả tạo. Do đó, **Lương trung vị (Median)** là chỉ số chuẩn mực khoa học nhất vì nó phản ánh chính xác điểm phân đôi: 50% người lao động có mức lương thấp hơn và 50% có mức lương cao hơn con số này. |
| **Nhóm xử lý các tin tuyển dụng ghi lương bằng USD như thế nào?** | Trong bước Transform của ETL, nhóm áp dụng tỷ giá quy đổi chuẩn thị trường (1 USD ≈ 25.400 VNĐ). Đối với các tin ghi lương theo năm, hệ thống tự động chia cho 12 tháng để đưa tất cả về cùng một đơn vị đo lường duy nhất là **Triệu VNĐ/tháng**. |
| **Làm sao nhóm đảm bảo không bị trùng lặp tin khi lấy từ 4 nguồn khác nhau?** | Nhóm áp dụng thuật toán khử trùng lặp đa tầng: Đầu tiên chuẩn hóa tên công ty (xóa các ký tự đặc biệt, viết thường) và tiêu đề công việc. Sau đó tạo khóa định danh kết hợp `(tên_công_ty_chuẩn_hóa, tiêu_đề_công_việc_chuẩn_hóa, địa_điểm)`. Nếu một vị trí xuất hiện ở cả TopCV và VietnamWorks trong cùng khoảng thời gian, hệ thống sẽ chỉ giữ lại một bản ghi chuẩn đại diện trong bảng Fact. |
| **Tại sao lại chuyển từ Power BI sang Dashboard Python (Streamlit)?** | Việc xây dựng Dashboard trên nền tảng Python (Streamlit + Plotly) mang lại nhiều ưu điểm vượt trội: (1) Khả năng tùy biến sâu các biểu đồ nâng cao như Heatmap ma trận và Boxplot phức tạp; (2) Dễ dàng đóng gói, triển khai độc lập trên môi trường web nội bộ hoặc đám mây mà không phụ thuộc vào bản quyền phần mềm hay cấu hình đường dẫn tuyệt đối của máy cá nhân; (3) Tích hợp trực tiếp và mượt mà với cơ sở dữ liệu SQLite của kho dữ liệu. |
