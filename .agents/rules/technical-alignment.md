---
trigger: model_decision
description: Luôn đọc và tuân thủ tuyệt đối các quy tắc kiến trúc, công nghệ trong file ALIGNMENT.md và nghiệp vụ trong CONTEXT.md tại thư mục gốc trước khi viết bất kỳ dòng code nào.
---


---

# 📄 TEAM ALIGNMENT DOCUMENT (TAD)

**Project:** Global Security & Risk Intelligence Platform
**Dataset:** Global Terrorism Database (GTD - 181k rows, 135 columns)
**Purpose of this Document:** Định hướng kỹ thuật, thống nhất Tech Stack, quy tắc giao tiếp hệ thống và làm Context Prompt cho các AI Assistants của team.

---

## 🤖 LỜI MỞ ĐẦU DÀNH CHO AI ASSISTANT CỦA THÀNH VIÊN

*(Các bạn copy đoạn này gửi cho AI của mình để nó hiểu context)*

> **To the AI Assistant:** > Bạn đang đóng vai trò là một Senior Developer/Data Scientist hỗ trợ tôi thực hiện dự án "Global Security & Risk Intelligence Platform".
> Dưới đây là bộ quy tắc kỹ thuật (Technical Alignment) mà toàn team đã thống nhất. Khi tôi yêu cầu bạn viết code, thiết kế schema, hoặc debug, bạn **BẮT BUỘC** phải tuân thủ các quy tắc về Tech Stack, Naming Convention, và Cloud Architecture được liệt kê trong tài liệu này. Không tự ý sử dụng thư viện ngoài nếu chưa được thống nhất. Hãy đọc kỹ phần nhiệm vụ liên quan đến tôi để hỗ trợ tôi tốt nhất.

---

## 🛠️ 1. TECH STACK THỐNG NHẤT (STANDARDIZED TECH STACK)

Toàn bộ dự án sẽ sử dụng các công nghệ sau để đảm bảo tính đồng bộ từ Data đến Web:

* **Data Engineering & ML:** Python 3.10+, `pandas`, `scikit-learn`, `mlxtend` (cho FP-Growth), `xgboost`.
* **Database:** PostgreSQL (Lý do: Hỗ trợ tốt cho Star Schema và các truy vấn phân tích).
* **Backend:** Python FastAPI (Lý do: Tốc độ cao, dễ dàng load model Machine Learning `.pkl` hoặc `.onnx` và tự động sinh Swagger UI/Docs).
* **Frontend:** React.js (hoặc Vue.js), sử dụng `Chart.js` hoặc `D3.js` để vẽ biểu đồ, `TailwindCSS` cho UI.
* **Cloud Infrastructure (AWS):** VPC, 01 EC2 t2.micro (Bastion Host), 01 EC2 t3.medium (Backend + DB), S3 (Host Frontend tĩnh).

---

## 📐 2. QUY TẮC KIẾN TRÚC & GIAO TIẾP HỆ THỐNG (ARCHITECTURE RULES)

### 2.1. Quy tắc Hạ tầng Cloud & Bảo mật (Strict Security)

* **VPC & Subnet:** Frontend nằm ở Public Subnet. Backend và Database nằm ở Private Subnet.
* **Database Port (5432):** TUYỆT ĐỐI KHÔNG mở port 5432 ra Internet.
* **Bastion Host (Jump Box):** Mọi thành viên muốn SSH vào server Backend/DB bắt buộc phải SSH qua Bastion Host.
* **Logging:** Backend phải có middleware ghi log toàn bộ request (Time, IP, Endpoint, Status Code) vào file `/var/log/app/server.log` trên EC2.

### 2.2. Quy tắc Data Warehouse & Iceberg Cube

* **Star Schema Naming Convention:** * Bảng Fact bắt buộc có tiền tố `fact_` (VD: `fact_attacks`).
* Bảng Dimension bắt buộc có tiền tố `dim_` (VD: `dim_time`, `dim_geography`).


* **Iceberg Cube Constraint:** Chỉ tính toán trước (pre-compute) các tổ hợp Aggregate (tổng số vụ, tổng thương vong) có **`min_sup > 100`**. Không lưu các tổ hợp hiếm vào DB để tránh "Curse of Dimensionality" (Bùng nổ dữ liệu).

### 2.3. Quy tắc Machine Learning

* **Pattern Mining:** Dùng FP-Growth thay vì Apriori để tối ưu tốc độ. Chỉ chọn các luật có **Lift > 1.5** làm ràng buộc (Must-Link).
* **Classification Metrics:** TUYỆT ĐỐI KHÔNG dùng `Accuracy` làm thước đo duy nhất. Bắt buộc báo cáo `Precision`, `Recall`, `F1-Score` và `ROC-AUC` (vì dữ liệu GTD có tính mất cân bằng class).
* **Model Export:** Model sau khi train xong phải được dump ra file `.pkl` (thông qua `joblib` hoặc `pickle`) và đặt trong thư mục `/models` của Backend.

### 2.4. Quy tắc Backend API

* **RESTful Standard:** API endpoint phải dùng danh từ số nhiều (VD: `GET /api/v1/attacks`, `POST /api/v1/predictions`).
* **Response Format:** Mọi API trả về cho Frontend phải tuân thủ đúng 1 format JSON duy nhất:
```json
{
  "status": "success" | "error",
  "data": { ... },
  "message": "Chi tiết (nếu có)"
}

```



---

## 💻 3. WORKFLOW & CODING CONVENTION

### 3.1. Git & Version Control

* Dùng mô hình **GitHub Flow** đơn giản.
* Nhánh chính là `main` (mã nguồn chạy trên Production/AWS).
* Khi code tính năng mới, tạo nhánh từ `main`: `feature/<tên-tính-năng>_`<tên-bạn> (VD: `feature/iceberg-cube_John`).
* Commit message rõ ràng (VD: `feat: Add API for prediction`, `fix: Resolve null value in weapon column`).

### 3.2. Quản lý Môi trường (Environment Variables)

* **KHÔNG** push các thông tin nhạy cảm (DB Password, AWS Keys) lên GitHub.
* Mọi file code gọi biến môi trường phải dùng `.env` (Frontend dùng `.env.local`, Backend dùng `.env`).
* Phải tạo một file `.env.example` chứa key rỗng để các thành viên biết cần cấu hình những gì.

---

## 🎯 4. CAM KẾT KỸ THUẬT CỦA CÁC VAI TRÒ (ROLE COMMITMENTS)

* **Data Engineer (A):** Cam kết xử lý sạch missing data. File script ETL phải chạy độc lập được từ đầu đến cuối. Bảng Iceberg Cube phải sẵn sàng trong DB trước khi BE viết API.
* **Data Scientist (B):** Cam kết model giao cho BE phải kèm theo đoạn code mẫu `inference.py` hướng dẫn cách load model và parse JSON input từ FE thành ma trận data để dự đoán.
* **Backend (C):** Cam kết API cho Frontend query dữ liệu Iceberg Cube phải phản hồi dưới **300ms**. Đảm bảo Server không crash khi load file model nặng.
* **Frontend (D):** Cam kết xử lý tốt các trạng thái `Loading`, `Success`, `Error` trên UI khi gọi API. Validate form đầu vào trước khi bắn request dự đoán rủi ro xuống Backend.

---

### 💡 Hướng dẫn sử dụng file này cho nhóm của bạn:

1. Tạo một repo GitHub cho project.
2. Lưu nội dung này thành file `ALIGNMENT.md` ngay thư mục gốc của dự án.
3. Bất cứ khi nào một bạn trong nhóm cần nhờ AI viết code (ví dụ bạn Backend nhờ AI viết API FastAPI), bạn đó chỉ cần copy paste file `ALIGNMENT.md` này kèm câu lệnh:

> *"Dựa trên quy tắc trong file TAD này, hãy viết cho tôi một API dự đoán rủi ro tấn công. Trả về đúng format JSON đã quy định."* Nhờ vậy, code do AI của bạn Frontend, Backend hay Data Engineer sinh ra sẽ tự động khớp nối hoàn hảo với nhau như những bánh răng trong một cỗ máy! Bạn thấy văn bản này đã đủ "cứng cáp" để trị đạo các anh em kỹ thuật chưa?