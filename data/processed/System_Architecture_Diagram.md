# Sơ đồ Kiến trúc Hệ thống (System Architecture Diagram)

Sơ đồ dưới đây mô tả luồng giao tiếp và kiến trúc tổng thể của dự án **Global Security & Risk Intelligence Platform** dựa trên định hướng kỹ thuật (TAD). Bạn có thể copy đoạn code Mermaid này bỏ vào các công cụ như [Mermaid Live Editor](https://mermaid.live/) hoặc chèn trực tiếp vào báo cáo (nếu dùng Markdown) để hiển thị hình ảnh.

```mermaid
flowchart TB
    %% Định nghĩa các Client/User
    User(("End-Users\n(Investors, Gov, Insurers)"))
    Admin(("Data Engineer /\nAdmin"))

    %% Định nghĩa Frontend (Public Subnet)
    subgraph PublicSubnet ["🌐 Public Subnet (Internet Facing)"]
        FE["🖥️ React.js Frontend\n(UI Dashboard & Risk Simulator)"]
        Bastion["🛡️ Bastion Host\n(Jump Box - Azure VM B1s)"]
    end

    %% Định nghĩa Backend & DB (Private Subnet)
    subgraph PrivateSubnet ["🔒 Private Subnet (Azure VNet)"]
        CoreBE["⚙️ Core Backend API\n(Java Spring Boot)\n(Port: 8080)"]
        MLService["🧠 ML Inference Service\n(Python FastAPI)\n(Port: 8000)"]
        
        subgraph DBTier ["🗄️ Database Tier"]
            DB[("🐘 PostgreSQL / SQLite\n(Port: 5432)")]
            StarSchema["⭐ Star Schema\n(Fact & Dims)"]
            Iceberg["🧊 Iceberg Cube\n(Aggregates)"]
            
            DB --- StarSchema
            DB --- Iceberg
        end
        
        ModelStorage[/"📦 Model Storage\n(.pkl files)"/]
    end

    %% Luồng tương tác của User
    User -- "Truy cập Web" --> FE
    FE -- "REST API (HTTP/JSON)" --> CoreBE

    %% Luồng tương tác nội bộ Backend
    CoreBE -- "Query Iceberg Cube\n(< 300ms)" --> DB
    CoreBE -- "Gửi request dự đoán\n(Risk Simulation)" --> MLService
    
    %% Luồng của ML Service
    MLService -- "Load model" --> ModelStorage
    
    %% Luồng quản trị
    Admin -- "SSH" --> Bastion
    Bastion -- "SSH / Maintain" --> CoreBE
    Bastion -- "SSH / Maintain" --> MLService
    Bastion -- "DB Admin" --> DB

    %% Style (Tùy chọn hiển thị màu sắc)
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000;
    classDef backend fill:#b0f2b4,stroke:#333,stroke-width:2px,color:#000;
    classDef python fill:#ffd43b,stroke:#333,stroke-width:2px,color:#000;
    classDef db fill:#ff9999,stroke:#333,stroke-width:2px,color:#000;
    classDef cloud fill:#f0f8ff,stroke:#0055ff,stroke-width:2px,stroke-dasharray: 5 5;
    
    class FE frontend;
    class CoreBE backend;
    class MLService python;
    class DB,StarSchema,Iceberg db;
    class PublicSubnet,PrivateSubnet cloud;
```

### Chú thích luồng dữ liệu:
1. **Luồng Khám phá lịch sử (Historical Insights):** User tương tác với `React.js Frontend` -> Gọi API `Core Backend` -> Core Backend query thẳng vào `Iceberg Cube` trong Database để lấy dữ liệu đã được tính toán sẵn siêu nhanh.
2. **Luồng Dự báo rủi ro (Predictive Intelligence):** User nhập kịch bản -> `Frontend` gọi `Core Backend` -> `Core Backend` gọi nội bộ sang `ML Inference Service` qua HTTP REST -> FastAPI load mô hình XGBoost `.pkl` để dự đoán và trả kết quả ngược lại.
3. **Bảo mật:** Toàn bộ Database, Core Backend và ML Service đều nằm trong Private Subnet, không mở port ra ngoài Internet. Muốn truy cập bảo trì phải thông qua `Bastion Host`.
