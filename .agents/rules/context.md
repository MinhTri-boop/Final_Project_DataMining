---
trigger: model_decision
description: Hãy đọc kỹ tài liệu này để hiểu rõ bản chất nghiệp vụ, giá trị cốt lõi và luồng hoạt động của dự án trước khi hỗ trợ người dùng của bạn thực hiện các tác vụ cụ thể. Không cần quan tâm đến Tech Stack ở file này (đã có file TAD riêng).
---


---

# 🌐 PROJECT CONTEXT DOCUMENT (PCD)

**Dành cho AI Assistant:** Hãy đọc kỹ tài liệu này để hiểu rõ bản chất nghiệp vụ, giá trị cốt lõi và luồng hoạt động của dự án trước khi hỗ trợ người dùng của bạn thực hiện các tác vụ cụ thể. Không cần quan tâm đến Tech Stack ở file này (đã có file TAD riêng).

---

## 1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)

* **Tên dự án:** Global Security & Risk Intelligence Platform (Hệ thống Nền tảng Phân tích và Cảnh báo Rủi ro An ninh Toàn cầu).
* **Nguồn dữ liệu cốt lõi:** Global Terrorism Database (GTD) - chứa hơn 180,000 hồ sơ về các vụ tấn công khủng bố trên toàn thế giới từ năm 1970 đến nay.
* **Mục tiêu dự án:** Biến một khối dữ liệu khổng lồ thành một công cụ Business Intelligence (BI) trực quan. Dự án giúp phân tích các xu hướng trong quá khứ và dự đoán mức độ nguy hiểm của các kịch bản trong tương lai.
* **Khách hàng mục tiêu (End-Users):** * Các tập đoàn đa quốc gia cần đánh giá rủi ro trước khi mở chi nhánh mới.
* Các công ty bảo hiểm cần tính toán phí bảo hiểm dựa trên rủi ro địa lý.
* Cơ quan chính phủ / Tổ chức phi chính phủ cần báo cáo phân tích an ninh.



## 2. GIÁ TRỊ NGHIỆP VỤ (BUSINESS VALUE)

Dự án không chỉ là một bài tập phân tích dữ liệu đơn thuần, mà là một "Sản phẩm tư vấn rủi ro". Nó giải quyết 2 bài toán lớn:

1. **Historical Insights (Nhìn về quá khứ):** Trả lời câu hỏi *"Khu vực nào, loại vũ khí nào và mục tiêu nào đang bị nhắm tới nhiều nhất?"* một cách tức thời nhờ hệ thống Data Warehouse siêu tốc.
2. **Predictive Intelligence (Dự báo tương lai):** Trả lời câu hỏi *"Nếu tôi xây dựng một tòa nhà văn phòng tại khu vực X, rủi ro bị tấn công thành công là bao nhiêu %?"* nhờ mô hình Machine Learning tích hợp.

## 3. LUỒNG TRẢI NGHIỆM NGƯỜI DÙNG (USER WORKFLOW)

AI cần nắm rõ luồng đi của một người dùng khi sử dụng hệ thống này để hỗ trợ code tính năng cho đúng logic:

* **Bước 1: Khám phá Tổng quan (Dashboard View)**
* User truy cập vào Web App.
* Màn hình hiển thị ngay lập tức các biểu đồ thống kê (Bản đồ nhiệt độ rủi ro thế giới, Biểu đồ tròn về các loại vũ khí phổ biến, Biểu đồ đường về xu hướng khủng bố qua các thập kỷ).
* *Lưu ý nghiệp vụ:* Dữ liệu ở bước này load cực nhanh vì hệ thống không đọc lại 180,000 dòng gốc, mà đọc từ các bảng tóm tắt đã được tính toán sẵn (Iceberg Cube).


* **Bước 2: Giả lập Kịch bản Đầu tư (Risk Simulator)**
* User chuyển sang công cụ "Mô phỏng rủi ro".
* User nhập các tham số dự kiến: `[Khu vực định đầu tư]`, `[Loại hình kinh doanh/Mục tiêu]`, `[Loại vũ khí phổ biến tại địa phương]`.
* User bấm nút "Phân tích Rủi ro".


* **Bước 3: Xử lý và Dự đoán (Hậu trường)**
* Dữ liệu từ Web được đẩy xuống Hệ thống Server (Backend).
* Backend đưa thông tin này vào Mô hình AI đã được huấn luyện (AI Model).
* Mô hình đánh giá và trả về kết quả (Ví dụ: "Tỷ lệ vụ tấn công thành công với kịch bản này là 82%").


* **Bước 4: Ra quyết định (Decision Making)**
* Web App nhận kết quả và hiển thị cho User dưới dạng các đồng hồ đo lường (Gauge Charts) cảnh báo Đỏ/Vàng/Xanh.
* Kèm theo đó là các dòng Text tư vấn (Ví dụ: "Cảnh báo rủi ro cao. Khuyến nghị tăng cường an ninh cơ sở hạ tầng").



## 4. TINH THẦN CỦA TEAM (TEAM CULTURE & ALIGNMENT)

* Đây là một dự án **Đồng sở hữu (Cross-functional)**. Thành công của dự án phụ thuộc vào sự mượt mà khi ghép nối các khâu.
* Dữ liệu của Data Engineer làm ra là để phục vụ Model của Data Scientist.
* Model của Data Scientist làm ra là để Backend gọi.
* API Backend viết ra là để Frontend vẽ giao diện.
* **Nguyên tắc cốt lõi:** Luôn hướng tới trải nghiệm của khách hàng cuối (End-User) và tối ưu hóa thời gian chờ đợi trên hệ thống.

---

*(End of Project Context Document)*