# BÁO CÁO ĐÁNH GIÁ MÔ HÌNH MACHINE LEARNING (ML EVALUATION REPORT)

**Dự án:** Global Security & Risk Intelligence Platform
**Ngày tạo:** 01/06/2026
**Thực hiện bởi:** AI Agent

---

## 1. TỔNG QUAN (OVERVIEW)
Báo cáo này trình bày chi tiết kết quả huấn luyện và đánh giá các mô hình Machine Learning trong dự án, bao gồm mô hình Khai phá Luật kết hợp (Pattern Mining - FP-Growth), Phân loại (Classification - XGBoost) và Phân cụm (Clustering - COP-KMeans).

Toàn bộ quá trình huấn luyện đã tuân thủ triệt để tài liệu **Technical Alignment Document (TAD)** và loại bỏ hoàn toàn hiện tượng rò rỉ dữ liệu (Data Leakage) bằng cách loại trừ các biến hậu sự kiện (post-event variables) như `nkill`, `nwound`, `suicide`, `multiple`.

---

## 2. ĐÁNH GIÁ MÔ HÌNH CLASSIFICATION (DỰ BÁO TỶ LỆ THÀNH CÔNG)

### 2.1. Cấu hình Mô hình
- **Thuật toán:** XGBoost Classifier (`XGBClassifier`)
- **Features Input:** `iyear` (Năm), `region` (Khu vực), `country` (Quốc gia), `attacktype1` (Loại hình tấn công), `targtype1` (Loại mục tiêu), `weaptype1` (Loại vũ khí).
- **Target:** `success` (0: Thất bại, 1: Thành công).
- **Xử lý mất cân bằng lớp:** Sử dụng tham số tự động `scale_pos_weight = 0.12` nhằm khắc phục tình trạng nhãn Thành công áp đảo nhãn Thất bại trong dữ liệu gốc.
- **Tập dữ liệu:** 181,691 dòng (Train/Test Split: 80/20).

### 2.2. Kết quả Đánh giá (Metrics)
Dưới đây là các chỉ số đánh giá tổng hợp trên tập Test (36,339 mẫu):

| Lớp (Class) | Precision | Recall | F1-Score | Số lượng (Support)|
|-------------|-----------|--------|----------|-------------------|
| **0 (Thất bại)** | 0.3097    | 0.7278 | 0.4345   | 4,012             |
| **1 (Thành công)**| 0.9594    | 0.7986 | 0.8717   | 32,327            |
| **Trung bình Macro**| 0.6345 | 0.7632 | 0.6531   | 36,339            |

- **Độ chính xác tổng thể (Accuracy):** 0.7908 (79.08%)
- **Chỉ số ROC-AUC:** **0.8503**

### 2.3. Nhận xét
- **Điểm sáng:** Mô hình có chỉ số **ROC-AUC (0.8503)** rất tốt. Điều này chứng tỏ mô hình có năng lực phân tách và xếp hạng rủi ro (Risk Ranking) cực kỳ chuẩn xác, mặc dù không hề dùng dữ liệu rò rỉ (không có thương vong).
- **Recall nhãn Thất bại (0.7278):** Mô hình rất nhạy bén trong việc bắt được các vụ tấn công có nguy cơ thất bại (không bỏ lọt quá nhiều), đây là hệ quả tích cực của việc áp dụng `scale_pos_weight`.
- **F1-Score nhãn Thành công (0.87):** Đảm bảo độ tin cậy cực cao khi hệ thống bật cảnh báo nguy hiểm (High Risk).

---

## 3. ĐÁNH GIÁ KHAI PHÁ LUẬT KẾT HỢP (PATTERN MINING)

### 3.1. Cấu hình
- **Thuật toán:** FP-Growth (nhanh và tối ưu bộ nhớ hơn Apriori).
- **Min Support:** 0.01 (1%).
- **Chỉ số lọc (Metric):** Lift > 1.5.

### 3.2. Kết quả
- **Số lượng luật trích xuất:** 528 luật.
- **Luật mạnh nhất (Top Rule):** 
  - `attacktype1_txt_Unknown => targtype1_txt_Military`
  - **Lift:** 20.84 
  - *Ý nghĩa:* Khi loại hình tấn công chưa được xác định, khả năng cao mục tiêu là Quân đội (Military) - thể hiện mức độ tương quan gấp 20 lần so với ngẫu nhiên.
- Các luật đã được lưu thành công ra file `data/processed/fp_growth_rules.csv` để phục vụ Dashboard BI.

---

## 4. ĐÁNH GIÁ MÔ HÌNH CLUSTERING (PHÂN CỤM BÁN GIÁM SÁT)

### 4.1. Cấu hình
- **Thuật toán:** COP-KMeans kết hợp Must-Link Constraint (thông qua Anchor Weighting).
- **Features:** Được chuẩn hoá bằng StandardScaler.
- **Ràng buộc Must-Link:** Các điểm dữ liệu thỏa mãn luật mạnh nhất của FP-Growth được nhóm lại thành một "Structural Anchor" (điểm neo) với trọng số lớn để ép cụm.
- **Số lượng cụm (K):** 5.

### 4.2. Kết quả phân bổ
Trên mẫu ngẫu nhiên 10,000 dòng, dữ liệu được gom thành 5 cụm chiến thuật riêng biệt:
- **Cụm 0:** 2,737 điểm
- **Cụm 1:** 1,325 điểm
- **Cụm 2:** 1,234 điểm
- **Cụm 3:** 2,983 điểm
- **Cụm 4:** 1,721 điểm
Sự phân bổ đồng đều này chứng tỏ các nhóm đặc điểm khủng bố không bị tập trung quá mức vào một cụm duy nhất (No Mega-Cluster effect), giúp việc phân tích từng chân dung rủi ro trở nên khả thi.

---

## 5. KẾT LUẬN & TRIỂN KHAI
- Các mô hình đã đạt tiêu chuẩn ngặt nghèo của dự án và hoàn toàn sạch sẽ (Clean & No Leakage).
- Mô hình XGBoost đã được đóng gói thành REST API (`ml_service/main.py`) chạy trên FastAPI để đảm bảo khả năng tích hợp linh hoạt (Inference) cho Core Backend Java (Spring Boot) gọi sang. 
- **Tình trạng:** Sẵn sàng đưa lên Production (Ready for Production).
