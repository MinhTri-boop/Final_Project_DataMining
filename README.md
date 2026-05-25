# 🌐 Global Security & Risk Intelligence Platform

Chào mừng toàn đội đến với Repository chính thức của dự án **Global Security & Risk Intelligence Platform**. 

Tài liệu này đóng vai trò như bản đồ chỉ dẫn (Onboarding Guide) giúp mọi thành viên – từ Data Engineer, Data Scientist đến Backend và Frontend Developer – nắm bắt được tầm nhìn sản phẩm, kiến trúc kỹ thuật và cách thức phối hợp để xây dựng một sản phẩm chất lượng cao nhất.

---

## 🎯 1. Tầm Nhìn Sản Phẩm (Product Vision)

Dự án này không chỉ là một bài tập phân tích dữ liệu, mà là một **"Sản phẩm tư vấn rủi ro an ninh"** cấp doanh nghiệp. Nền tảng tận dụng nguồn dữ liệu khổng lồ từ Global Terrorism Database (GTD) với hơn 180,000 hồ sơ để giải quyết 2 bài toán lớn cho khách hàng (Tập đoàn đa quốc gia, công ty bảo hiểm, cơ quan chính phủ):

1. **Historical Insights (BI Dashboard):** Cung cấp cái nhìn trực quan, tức thời về các khu vực rủi ro, xu hướng và phương thức tấn công trong quá khứ nhờ hệ thống Data Warehouse (Iceberg Cube) siêu tốc.
2. **Predictive Intelligence (Risk Simulator):** Giả lập và dự báo tỷ lệ rủi ro cho các kịch bản đầu tư/xây dựng trong tương lai thông qua các mô hình Machine Learning (FP-Growth, XGBoost).

*Mọi dòng code chúng ta viết ra đều phải hướng tới trải nghiệm người dùng cuối (End-User): Nhanh chóng, Chính xác và Dễ hiểu.*

---

## 🏗️ 2. Cấu Trúc Thư Mục (Project Structure)

Để đảm bảo tính độc lập nhưng vẫn liên kết chặt chẽ giữa các khối nghiệp vụ, mã nguồn dự án được tổ chức theo cấu trúc sau:

```text
📦 Data_Mining_Final
 ┣ 📂 data/             # Nơi chứa dataset GTD (đã được cấu hình .gitignore)
 ┃ ┣ 📂 raw/            # Dữ liệu gốc chưa qua xử lý
 ┃ ┗ 📂 processed/      # Dữ liệu đã làm sạch, sẵn sàng cho Data Warehouse
 ┣ 📂 etl/              # Dành cho Data Engineer (ETL Scripts, Airflow DAGs, etc.)
 ┣ 📂 ml/               # Dành cho Data Scientist (Jupyter notebooks, Training scripts)
 ┃ ┗ 📂 models/         # Lưu trữ các mô hình ML (.pkl, .onnx) đã được train
 ┣ 📂 backend/          # Nơi chứa API Server (FastAPI)
 ┃ ┣ 📂 app/            # Source code chính của Backend
 ┃ ┗ 📂 models/         # Bản sao của mô hình ML để Backend load và Inference
 ┣ 📂 frontend/         # Ứng dụng Web Client (React/Vue + TailwindCSS)
 ┣ 📜 .env.example      # Template file cấu hình môi trường cho toàn dự án
 ┣ 📜 .gitignore        # Cấu hình bỏ qua các file không cần thiết khi push lên Git
 ┣ 📜 ALIGNMENT.md      # Quy tắc kỹ thuật, Convention và Cloud Architecture của team
 ┣ 📜 CONTEXT.md        # Tài liệu phân tích nghiệp vụ, luồng hoạt động
 ┗ 📜 README.md         # Document tổng quan bạn đang đọc
```

---

## 🛠️ 3. Tech Stack Tiêu Chuẩn

Chúng ta thống nhất sử dụng bộ công nghệ dưới đây xuyên suốt quá trình phát triển để đảm bảo tính đồng bộ:

*   **Data & ML:** Python (pandas, scikit-learn, mlxtend, xgboost).
*   **Database:** PostgreSQL (Star Schema, tối ưu hoá với Iceberg Cube).
*   **Backend:** FastAPI (Python) - Tốc độ cao, dễ dàng tích hợp Model ML.
*   **Frontend:** React.js / Vue.js, TailwindCSS, Chart.js / D3.js.
*   **Infrastructure:** AWS (VPC, EC2 Bastion, Private DB/Backend, S3).

---

## 🚀 4. Hướng Dẫn Bắt Đầu (Getting Started)

Mọi thành viên mới khi clone dự án cần thực hiện các bước sau:

1. **Đọc kỹ tài liệu gốc:** 
   * Đọc `CONTEXT.md` để hiểu luồng nghiệp vụ người dùng.
   * Đọc `ALIGNMENT.md` để nắm rõ quy tắc viết code, database schema và chuẩn API.
2. **Thiết lập môi trường:**
   * Copy file `.env.example` thành `.env` (hoặc `.env.local` tuỳ môi trường) và điền các thông số local của bạn. *Tuyệt đối không push file `.env` chứa mật khẩu lên Git.*
3. **Tuân thủ Git Workflow:**
   * Luôn tạo nhánh mới từ `main` với cú pháp: `feature/<tên-tính-năng>_`<tên-bạn> (Ví dụ: `feature/api-predict_John`).
   * Commit message cần rõ ràng (VD: `feat: Thêm API dự đoán` hoặc `fix: Sửa lỗi load model`).

Cảm ơn sự đóng góp của bạn. Chúc cả team có một dự án thành công và mang lại những giá trị thực tế cao nhất! 🚀
